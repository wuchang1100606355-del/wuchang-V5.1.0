"""
risk_gate.py

高風險作業「硬閘門」：無回應＝禁止執行。

定位：
- 專門給「同步推送 / 索引重建 / 清快取 / 部署 / 重啟」等工具調用
- 強制落地：任何關鍵確認只要無回應/不可驗證，立刻中止並留下稽核紀錄（JSONL）
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def sha256_file(path: str | Path) -> str:
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def append_audit_jsonl(audit_path: str | Path, record: Dict[str, Any]) -> None:
    p = Path(audit_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


@dataclass
class HealthCheckResult:
    ok: bool
    status: int
    content_type: str
    body_preview: str


def _decode_preview(raw: bytes, max_len: int = 500) -> str:
    try:
        s = raw.decode("utf-8", errors="replace")
    except Exception:
        s = repr(raw[:max_len])
    s = s.replace("\r", "").strip()
    if len(s) > max_len:
        return s[: max_len - 3] + "..."
    return s


def check_server_health(
    health_url: str,
    timeout_seconds: float = 3.0,
    retries: int = 2,
    headers: Optional[Dict[str, str]] = None,
) -> HealthCheckResult:
    """
    強制健康檢查：只要不可達/超時/非 2xx → 視為「無回應/不可驗證」。
    """
    last_err: str | None = None
    for attempt in range(1, retries + 1):
        try:
            req = Request(health_url, method="GET")
            req.add_header("Accept", "application/json, text/plain;q=0.9, */*;q=0.8")
            if headers:
                for k, v in headers.items():
                    req.add_header(k, v)

            with urlopen(req, timeout=timeout_seconds) as resp:
                status = int(getattr(resp, "status", 200))
                ct = str(resp.headers.get("Content-Type") or "")
                raw = resp.read(4096) or b""
                preview = _decode_preview(raw)
                ok = 200 <= status < 300
                return HealthCheckResult(ok=ok, status=status, content_type=ct, body_preview=preview)
        except HTTPError as e:
            last_err = f"HTTPError: {getattr(e, 'code', 'unknown')}"
        except URLError as e:
            last_err = f"URLError: {e}"
        except Exception as e:
            last_err = f"Exception: {e}"

        # 短暫退避
        if attempt < retries:
            time.sleep(0.3)

    return HealthCheckResult(ok=False, status=0, content_type="", body_preview=last_err or "no_response")


class RiskGateError(RuntimeError):
    pass


def require_responsive_or_abort(
    *,
    health_url: str,
    audit_path: str | Path,
    action_type: str,
    actor: str,
    machines: str = "local->server",
    timeout_seconds: float = 3.0,
    retries: int = 2,
    extra: Optional[Dict[str, Any]] = None,
) -> HealthCheckResult:
    """
    依 SOP：「無回應＝禁止」的落地函式。
    - 成功：回傳 HealthCheckResult(ok=True)
    - 失敗：寫入 audit 並 raise RiskGateError（呼叫端必須中止）
    """
    hc = check_server_health(health_url, timeout_seconds=timeout_seconds, retries=retries)
    record: Dict[str, Any] = {
        "timestamp": now_iso(),
        "kind": "risk_gate_health_check",
        "action_type": action_type,
        "actor": actor,
        "machines": machines,
        "health_url": health_url,
        "result": "ok" if hc.ok else "blocked_no_response",
        "evidence": {
            "status": hc.status,
            "content_type": hc.content_type,
            "body_preview": hc.body_preview,
        },
    }
    if extra:
        record["extra"] = extra
    append_audit_jsonl(audit_path, record)

    if not hc.ok:
        raise RiskGateError(
            f"blocked: server health check not ok (no_response/unverifiable). "
            f"status={hc.status} preview={hc.body_preview!r}"
        )
    return hc

