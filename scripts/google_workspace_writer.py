"""
google_workspace_writer.py

把「中控/小J代理輸出」寫入 Google Workspace 的最小落地方式。

設計原則（避免你再做大量設定）：
1) 優先使用「本機資料夾輸出」：把檔案寫到一個資料夾，該資料夾若位於 Google Drive for desktop 的同步路徑，
   就會自動進入 Google Workspace Drive（最省事、零 API 金鑰）。
2) 可選：Webhook（例如 Apps Script Web App）— 若你已經有 URL，可用 HTTP POST 推送。

環境變數：
- WUCHANG_WORKSPACE_OUTDIR：寫入檔案的目錄（建議指到 Google Drive 同步資料夾下的某個子資料夾）
- WUCHANG_WORKSPACE_WEBHOOK_URL：可選，若提供就會同時 POST 一份 JSON（不含任何秘密）

注意：
- 本模組不處理 OAuth，不寫入任何憑證。
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _safe_name(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return "unknown"
    s = re.sub(r"[^\w\-\.\(\)\u4e00-\u9fff]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s[:80] if len(s) > 80 else s


@dataclass
class WorkspaceWriteResult:
    ok: bool
    out_path: str | None
    webhook_ok: bool | None
    error: str | None = None


def write_workspace_artifact(
    *,
    kind: str,
    title: str,
    content: str,
    meta: Optional[Dict[str, Any]] = None,
    outdir: Optional[str] = None,
    webhook_url: Optional[str] = None,
) -> WorkspaceWriteResult:
    """
    寫入一份「可稽核」的輸出到 Workspace。
    - 檔案：Markdown（.md）+ JSON（.json）
    - webhook：POST JSON（可選）
    """
    kind2 = _safe_name(kind)
    title2 = _safe_name(title)
    ts = now_iso().replace(":", "").replace("+", "p")

    outdir2 = outdir or (Path.cwd() / "workspace_out").as_posix()
    p = Path(outdir2).expanduser()
    p.mkdir(parents=True, exist_ok=True)

    base = f"{ts}__{kind2}__{title2}"
    md_path = p / f"{base}.md"
    json_path = p / f"{base}.json"

    payload = {
        "timestamp": now_iso(),
        "kind": kind,
        "title": title,
        "meta": meta or {},
        "content": content,
    }

    try:
        md_path.write_text(
            "# 小J 代理輸出（自動落地）\n\n"
            f"- time: {payload['timestamp']}\n"
            f"- kind: {kind}\n"
            f"- title: {title}\n\n"
            "## 內容\n\n"
            f"{content}\n\n"
            "## meta\n\n"
            "```json\n"
            f"{json.dumps(payload.get('meta') or {}, ensure_ascii=False, indent=2)}\n"
            "```\n",
            encoding="utf-8",
        )
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        return WorkspaceWriteResult(ok=False, out_path=None, webhook_ok=None, error=f"write_failed: {e}")

    wh_ok: bool | None = None
    if webhook_url:
        try:
            req = Request(webhook_url, method="POST")
            req.add_header("Content-Type", "application/json; charset=utf-8")
            raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            with urlopen(req, data=raw, timeout=6) as resp:
                wh_ok = 200 <= int(getattr(resp, "status", 200)) < 300
        except URLError:
            wh_ok = False
        except Exception:
            wh_ok = False

    return WorkspaceWriteResult(ok=True, out_path=str(md_path), webhook_ok=wh_ok)

