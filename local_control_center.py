"""
local_control_center.py

本機中控 UI（繁中）：
- 集中顯示「兩機（本機/伺服器）」互動狀態
- 提供一鍵執行：DNS 傳播檢查、推送（rules/kb）、查看稽核紀錄

安全前提：
- 只綁定 127.0.0.1（不對外網開放）
- 高風險動作（推送）會由 safe_sync_push.py 內建「無回應＝禁止」硬閘門擋下

啟動：
  python local_control_center.py --port 8788
  然後開： http://127.0.0.1:8788/
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import uuid
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen
from urllib.parse import parse_qs, urlparse

from risk_gate import check_server_health
from dns_propagation_check import DEFAULT_RESOLVERS, load_expected_from_config, query
from google_workspace_writer import write_workspace_artifact


BASE_DIR = Path(__file__).resolve().parent
UI_HTML = BASE_DIR / "wuchang_control_center.html"
DNS_CONFIG = BASE_DIR / "dns_records.json"
AUDIT_JSONL = BASE_DIR / "risk_action_audit.jsonl"
SNAPSHOT_DIR = BASE_DIR / "snapshots"
JOB_DIR = BASE_DIR / "jobs"
JOB_OUTBOX = JOB_DIR / "outbox"
JOB_SENT = JOB_DIR / "sent"
JOB_ARCHIVE = JOB_DIR / "archive"
JOB_AUDIT_JSONL = JOB_DIR / "job_audit.jsonl"
AGENT_CONFIG_PATH = BASE_DIR / "agent_config.json"
AGENT_AUDIT_JSONL = BASE_DIR / "agent_audit.jsonl"

# 小J 自然語言代理：高風險動作兩段式確認（記憶僅在本程序生命週期內）
PENDING_CONFIRM: Dict[str, Dict[str, Any]] = {}

# 小J 模型/模式（可由 UI 切換；預設不外送資料）
DEFAULT_AGENT_CONFIG: Dict[str, Any] = {
    "mode": "command",  # command | cloud_chat
    "model": "local_rule",
    "provider": "local",  # local | openai_compat
}
AGENT_CONFIG: Dict[str, Any] = dict(DEFAULT_AGENT_CONFIG)


def _load_agent_config() -> None:
    global AGENT_CONFIG
    try:
        if AGENT_CONFIG_PATH.exists():
            data = json.loads(AGENT_CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                # 僅允許覆蓋已知鍵
                for k in ("mode", "model", "provider"):
                    if k in data and isinstance(data.get(k), str):
                        AGENT_CONFIG[k] = str(data.get(k)).strip()
    except Exception:
        # 讀取失敗就用預設，不中斷服務
        AGENT_CONFIG = dict(DEFAULT_AGENT_CONFIG)


def _save_agent_config() -> None:
    AGENT_CONFIG_PATH.write_text(json.dumps(AGENT_CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")


def _available_models() -> List[Dict[str, str]]:
    """
    提供給 UI 的模型清單（字串值不代表一定可用；雲端模式需金鑰）。
    """
    return [
        {"id": "local_rule", "label": "本機規則（指揮/安全）", "provider": "local"},
        {"id": "gpt-4o-mini", "label": "雲端：gpt-4o-mini（快/省）", "provider": "openai_compat"},
        {"id": "gpt-4o", "label": "雲端：gpt-4o（強）", "provider": "openai_compat"},
        {"id": "gpt-4.1-mini", "label": "雲端：gpt-4.1-mini（平衡）", "provider": "openai_compat"},
        {"id": "custom", "label": "雲端：自訂模型名稱（OpenAI 相容）", "provider": "openai_compat"},
    ]


def _llm_env() -> Dict[str, str]:
    """
    OpenAI 相容端點（可換成自建/其他供應商）：
    - WUCHANG_LLM_BASE_URL：例如 https://api.openai.com/v1
    - WUCHANG_LLM_API_KEY：API Key
    - WUCHANG_LLM_MODEL：預設模型（若 UI 選 custom）
    """
    return {
        "base_url": (os.getenv("WUCHANG_LLM_BASE_URL") or "https://api.openai.com/v1").strip().rstrip("/"),
        "api_key": (os.getenv("WUCHANG_LLM_API_KEY") or "").strip(),
        "default_model": (os.getenv("WUCHANG_LLM_MODEL") or "gpt-4o-mini").strip(),
    }


def _call_openai_compat_chat(*, model: str, user_text: str, timeout_seconds: int = 20) -> str:
    env = _llm_env()
    if not env["api_key"]:
        raise RuntimeError("missing_WUCHANG_LLM_API_KEY")
    m = model if model and model != "custom" else env["default_model"]
    url = env["base_url"] + "/chat/completions"
    payload = {
        "model": m,
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是五常平台的「小J」助理。請用繁體中文回覆，語氣簡潔、可執行、以安全為先。"
                    "若涉及高風險動作（推送/重啟/部署/清快取/簽發憑證），請先提醒『無回應＝禁止高風險作業』。"
                    "若使用者只是問狀態/解釋，請給出結論 + 最短下一步。"
                ),
            },
            {"role": "user", "content": user_text},
        ],
    }
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(url, method="POST")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    req.add_header("Authorization", f"Bearer {env['api_key']}")
    try:
        with urlopen(req, data=raw, timeout=timeout_seconds) as resp:
            body = resp.read(1_000_000).decode("utf-8", errors="replace")
            data = json.loads(body)
    except URLError as e:
        raise RuntimeError(f"llm_network_error: {e}")
    except Exception as e:
        raise RuntimeError(f"llm_error: {e}")
    try:
        return str(data["choices"][0]["message"]["content"]).strip()
    except Exception:
        # 若格式不同，直接回傳 raw 摘要
        return "（雲端模型回應格式非預期，請改用本機規則模式或檢查 base_url）"


def _safe_filename(name: str) -> str:
    name = (name or "").strip()
    # 僅允許安全字元，避免路徑穿越
    name = "".join(ch for ch in name if ch.isalnum() or ch in ("-", "_", ".", "@"))
    return name[:120] if name else ""

def _norm_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip()).lower()


def _detect_intent(text: str) -> Dict[str, Any]:
    """
    小J 意圖解析（保守、可預測）：
    - dns_status / dns_expected
    - net_snapshot
    - push_rules / push_kb（高風險，需確認）
    - audit_tail
    - docs_show
    - jobs_list
    """
    t = _norm_text(text)

    # docs
    if "sop" in t or "risk_action_sop" in t or "風險" in t:
        return {"intent": "docs_show", "name": "RISK_ACTION_SOP.md"}
    if "憲法" in t or "constitution" in t or "agent_constitution" in t:
        return {"intent": "docs_show", "name": "AGENT_CONSTITUTION.md"}

    # audit
    if "稽核" in t or "audit" in t or "紀錄" in t:
        return {"intent": "audit_tail"}

    # jobs
    if "命令單" in t or "job" in t or "作業單" in t:
        if "已送" in t or "sent" in t:
            return {"intent": "jobs_list", "state": "sent"}
        if "封存" in t or "archive" in t:
            return {"intent": "jobs_list", "state": "archive"}
        return {"intent": "jobs_list", "state": "outbox"}

    # dns
    if "dns" in t or "解析" in t or "傳播" in t or "acme" in t or "憑證" in t:
        if "預期" in t or "expected" in t or "txt值" in t or "txt 值" in t:
            return {"intent": "dns_expected"}
        return {"intent": "dns_status"}

    # net snapshot
    if "快照" in t or "網路狀態" in t or "網路" in t and ("保存" in t or "存檔" in t or "snapshot" in t):
        return {"intent": "net_snapshot"}
    if "網路快照" in t:
        return {"intent": "net_snapshot"}

    # push (high risk)
    if "推送" in t or "同步" in t or "sync" in t or "push" in t:
        if "kb" in t or "索引" in t or "knowledge" in t:
            return {"intent": "push_kb"}
        return {"intent": "push_rules"}

    return {"intent": "unknown"}


def _little_j_reply_help() -> str:
    return (
        "我可以用自然語言幫你操作本機中控台。\n"
        "你可以說：\n"
        "- 檢查 DNS 傳播 / DNS 目前狀態\n"
        "- 載入 DNS 預期值\n"
        "- 做網路快照（並存檔）\n"
        "- 查看稽核紀錄\n"
        "- 推送 rules / 推送 kb（高風險：會先要求你確認）\n"
        "\n"
        "提醒：任何高風險作業前，仍遵守「無回應＝禁止高風險作業」。"
    )


def _format_dns_status(status: Dict[str, Any]) -> str:
    ready = status.get("ready_to_issue") is True
    mismatches = status.get("mismatches") or []
    resolvers = status.get("resolvers") or []
    lines = [
        "【DNS 傳播（_acme-challenge）】",
        f"判定：{'READY（可簽發）' if ready else 'NOT READY（先不要簽發）'}",
        f"Resolver：{'、'.join(resolvers) if resolvers else '（無）'}",
    ]
    if mismatches:
        lines.append("缺口/不一致：")
        for m in mismatches[:30]:
            lines.append(f"- {m}")
    else:
        lines.append("缺口/不一致：無")
    note = status.get("note")
    if note:
        lines.append(f"備註：{note}")
    return "\n".join(lines)


def _format_expected(expected: Dict[str, Any]) -> str:
    recs = expected.get("records") or []
    by: Dict[str, str] = {}
    for r in recs:
        qn = str(r.get("qname") or "")
        vals = r.get("expected_values") or []
        by[qn] = " | ".join([str(v) for v in vals])
    lines = [
        "【DNS 預期值（來自 dns_records.json）】",
        f"_acme-challenge：{by.get('_acme-challenge.wuchang.life') or '（無）'}",
        f"_acme-challenge.www：{by.get('_acme-challenge.www.wuchang.life') or '（無）'}",
    ]
    return "\n".join(lines)


def _make_confirm(session_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
    cid = uuid.uuid4().hex[:10]
    # 確認句：簡單、可語音口述
    profile = action.get("profile") or "rules"
    phrase = f"確認推送 {profile} {cid}"
    PENDING_CONFIRM[cid] = {
        "session_id": session_id,
        "created": time.time(),
        "action": action,
        "phrase": phrase,
    }
    return {"confirm_id": cid, "confirm_phrase": phrase}


def _consume_confirm(session_id: str, text: str) -> Optional[Dict[str, Any]]:
    t = _norm_text(text)
    m = re.search(r"(確認推送)\s+(rules|kb)\s+([0-9a-f]{6,16})", t, flags=re.IGNORECASE)
    if not m:
        return None
    cid = m.group(3)
    item = PENDING_CONFIRM.get(cid)
    if not item:
        return None
    if item.get("session_id") != session_id:
        return None
    # 10 分鐘逾時
    if time.time() - float(item.get("created") or 0) > 600:
        PENDING_CONFIRM.pop(cid, None)
        return None
    # profile 必須一致
    prof = (m.group(2) or "").lower()
    act = item.get("action") or {}
    if (act.get("profile") or "").lower() != prof:
        return None
    PENDING_CONFIRM.pop(cid, None)
    return act


def _json(handler: BaseHTTPRequestHandler, status: int, payload: Dict[str, Any]) -> None:
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)

def _append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _job_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _ensure_job_dirs() -> None:
    JOB_OUTBOX.mkdir(parents=True, exist_ok=True)
    JOB_SENT.mkdir(parents=True, exist_ok=True)
    JOB_ARCHIVE.mkdir(parents=True, exist_ok=True)


def _new_job_id() -> str:
    # 短 ID：便於口述/輸入
    return uuid.uuid4().hex[:12]


def _job_path(state: str, job_id: str) -> Path:
    base = JOB_OUTBOX if state == "outbox" else (JOB_SENT if state == "sent" else JOB_ARCHIVE)
    return (base / f"{job_id}.json").resolve()


def _write_job(state: str, job: Dict[str, Any]) -> Path:
    _ensure_job_dirs()
    job_id = str(job.get("id") or "").strip()
    if not job_id:
        raise ValueError("missing_job_id")
    p = _job_path(state, job_id)
    # 防路徑穿越：必須在 JOB_DIR 底下
    if JOB_DIR.resolve() not in p.parents:
        raise ValueError("invalid_job_path")
    p.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def _list_jobs(state: str = "outbox", limit: int = 50) -> List[Dict[str, Any]]:
    _ensure_job_dirs()
    base = JOB_OUTBOX if state == "outbox" else (JOB_SENT if state == "sent" else JOB_ARCHIVE)
    files = sorted(base.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    out: List[Dict[str, Any]] = []
    for p in files[: max(1, min(int(limit), 200))]:
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            out.append({"id": p.stem, "error": "invalid_json", "_path": str(p)})
    return out


def _find_job(job_id: str) -> Optional[Path]:
    _ensure_job_dirs()
    for base in (JOB_OUTBOX, JOB_SENT, JOB_ARCHIVE):
        p = (base / f"{job_id}.json").resolve()
        if p.exists():
            return p
    return None


def _move_job(job_id: str, to_state: str) -> Path:
    src = _find_job(job_id)
    if not src:
        raise FileNotFoundError("job_not_found")
    dst = _job_path(to_state, job_id)
    dst.parent.mkdir(parents=True, exist_ok=True)
    src.replace(dst)
    return dst


def _read_json(handler: BaseHTTPRequestHandler) -> Dict[str, Any]:
    try:
        length = int(handler.headers.get("Content-Length") or "0")
    except Exception:
        length = 0
    body = handler.rfile.read(length) if length > 0 else b""
    if not body:
        return {}
    return json.loads(body.decode("utf-8"))


def _serve_file(handler: BaseHTTPRequestHandler, path: Path, content_type: str) -> None:
    if not path.exists():
        handler.send_response(HTTPStatus.NOT_FOUND)
        handler.end_headers()
        return
    raw = path.read_bytes()
    handler.send_response(HTTPStatus.OK)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)


def _get_expected_acme(domain: str) -> Dict[str, Any]:
    """
    從 dns_records.json 取得 _acme-challenge 相關 TXT 的預期值（若存在）。
    """
    domain = (domain or "").strip().rstrip(".")
    expected: Dict[str, Any] = {"domain": domain, "records": []}
    if not DNS_CONFIG.exists():
        expected["error"] = "dns_records.json_not_found"
        return expected

    exp_map = load_expected_from_config(DNS_CONFIG)
    targets = [
        (f"_acme-challenge.{domain}", "TXT"),
        (f"_acme-challenge.www.{domain}", "TXT"),
    ]
    for qname, qtype in targets:
        vals = exp_map.get((qname, qtype))
        expected["records"].append(
            {
                "qname": qname,
                "qtype": qtype,
                "expected_values": vals or [],
            }
        )
    return expected


def _check_acme_propagation(domain: str, resolvers: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    以多個 resolver 查詢 _acme-challenge TXT，並給出「是否可簽發」判斷。
    """
    domain = (domain or "").strip().rstrip(".")
    resolvers = resolvers or list(DEFAULT_RESOLVERS)

    exp = _get_expected_acme(domain)
    records = exp.get("records") or []
    out: Dict[str, Any] = {"domain": domain, "resolvers": resolvers, "expected": exp, "results": []}

    ready = True
    mismatches: List[str] = []

    for rec in records:
        qname = str(rec.get("qname") or "")
        qtype = str(rec.get("qtype") or "TXT")
        expected_values = list(rec.get("expected_values") or [])
        per: Dict[str, Any] = {"qname": qname, "qtype": qtype, "expected_values": expected_values, "by_resolver": {}}

        # 查詢
        answers_by_resolver: Dict[str, List[str]] = {}
        for r in resolvers:
            res = query(qname=qname, qtype=qtype, resolver=r, timeout_seconds=4)
            answers_by_resolver[r] = res.answers
            per["by_resolver"][r] = {
                "ok": res.ok,
                "answers": res.answers,
                "error": res.error,
            }
            if not res.ok:
                ready = False
                mismatches.append(f"{qtype} {qname}: {r} no_answer")

        # 一致性（所有 resolver 回應相同）
        norm = [tuple(answers_by_resolver[r]) for r in resolvers]
        if norm:
            all_same = all(v == norm[0] for v in norm[1:])
            per["all_resolvers_same"] = all_same
            if not all_same:
                ready = False
                mismatches.append(f"{qtype} {qname}: resolvers_mismatch")
        else:
            per["all_resolvers_same"] = True

        # 需包含 expected token（容許多值，但至少包含）
        if expected_values:
            exp_set = set(expected_values)
            for r in resolvers:
                got = set(answers_by_resolver.get(r) or [])
                missing = sorted(list(exp_set - got))
                if missing:
                    ready = False
                    mismatches.append(f"{qtype} {qname}: {r} missing_expected={missing}")
                    per.setdefault("missing_expected_by_resolver", {})[r] = missing

        out["results"].append(per)

    out["ready_to_issue"] = ready and not exp.get("error")
    out["mismatches"] = mismatches
    out["note"] = (
        "本檢查只負責判斷 DNS-01（_acme-challenge TXT）是否已在多個公用 DNS 上一致可見。"
        "若 ready_to_issue=true，通常即可進行憑證簽發；反之請先完成 DNS 處置並等待 TTL 傳播。"
    )
    return out

def _tail_jsonl(path: Path, limit: int = 50, max_bytes: int = 128_000) -> List[Dict[str, Any]]:
    """
    讀取 JSONL 尾端 N 筆（避免整檔讀入）。
    若某行不是 JSON，就以 {"raw": "..."} 形式回傳。
    """
    if not path.exists():
        return []
    size = path.stat().st_size
    start = max(0, size - max_bytes)
    with path.open("rb") as f:
        f.seek(start)
        chunk = f.read()
    lines = chunk.splitlines()
    # 若不是從 0 開始，第一行可能被截斷，丟掉
    if start > 0 and lines:
        lines = lines[1:]
    out: List[Dict[str, Any]] = []
    for b in lines[-limit:]:
        try:
            s = b.decode("utf-8", errors="replace").strip()
        except Exception:
            s = repr(b)
        if not s:
            continue
        try:
            out.append(json.loads(s))
        except Exception:
            out.append({"raw": s})
    return out


def _run_script(args: List[str], timeout_seconds: int = 60) -> Dict[str, Any]:
    """
    用當前 Python 執行 repo 內腳本，回傳 stdout/stderr/exit_code。
    """
    try:
        cp = subprocess.run(
            [sys.executable, *args],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        return {"exit_code": cp.returncode, "stdout": cp.stdout or "", "stderr": cp.stderr or ""}
    except Exception as e:
        return {"exit_code": 3, "stdout": "", "stderr": f"exception: {e}"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            _serve_file(self, UI_HTML, "text/html; charset=utf-8")
            return

        if parsed.path == "/api/local/health":
            _json(self, HTTPStatus.OK, {"ok": True})
            return

        if parsed.path == "/api/net/snapshot":
            qs = parse_qs(parsed.query)
            # 允許沿用 UI 內填寫的 healthUrl；若未提供就只做本機網路/DNS/閘道探測
            health_url = (qs.get("health_url") or [""])[0].strip()
            domains = qs.get("domain") or []
            save = (qs.get("save") or ["1"])[0].strip().lower() in ("1", "true", "yes", "y")
            suggested = _safe_filename((qs.get("name") or [""])[0])

            args = ["network_snapshot.py"]
            if health_url:
                args += ["--health-url", health_url]
            if domains:
                args += ["--domains", *[d.strip() for d in domains if d.strip()]]

            saved_path = ""
            if save:
                SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
                ts = time.strftime("%Y%m%d_%H%M%S")
                fname = suggested or f"network_snapshot_{ts}.json"
                if not fname.lower().endswith(".json"):
                    fname += ".json"
                out_path = (SNAPSHOT_DIR / fname).resolve()
                # 防路徑穿越：必須在 SNAPSHOT_DIR 底下
                if SNAPSHOT_DIR.resolve() not in out_path.parents:
                    _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid_snapshot_name"})
                    return
                args += ["--out", str(out_path)]
                saved_path = str(out_path)

            res = _run_script(args, timeout_seconds=60)
            _json(self, HTTPStatus.OK, {"ok": True, "saved_path": saved_path, "run": res})
            return

        if parsed.path == "/api/server/health":
            qs = parse_qs(parsed.query)
            url = (qs.get("url") or [""])[0].strip()
            if not url:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_url"})
                return
            hc = check_server_health(url, timeout_seconds=3.0, retries=2)
            _json(self, HTTPStatus.OK, {"ok": True, "health": asdict(hc)})
            return

        if parsed.path == "/api/dns/expected":
            qs = parse_qs(parsed.query)
            domain = (qs.get("domain") or ["wuchang.life"])[0].strip()
            _json(self, HTTPStatus.OK, {"ok": True, "expected": _get_expected_acme(domain)})
            return

        if parsed.path == "/api/dns/acme_status":
            qs = parse_qs(parsed.query)
            domain = (qs.get("domain") or ["wuchang.life"])[0].strip()
            _json(self, HTTPStatus.OK, {"ok": True, "status": _check_acme_propagation(domain)})
            return

        if parsed.path == "/api/audit/tail":
            qs = parse_qs(parsed.query)
            name = (qs.get("file") or ["risk_action_audit.jsonl"])[0].strip()
            limit = int((qs.get("limit") or ["50"])[0])
            # 僅允許讀取 repo 內檔案（避免任意路徑）
            p = (BASE_DIR / name).resolve()
            if BASE_DIR not in p.parents and p != BASE_DIR:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid_path"})
                return
            items = _tail_jsonl(p, limit=max(1, min(limit, 200)))
            _json(self, HTTPStatus.OK, {"ok": True, "file": str(p), "items": items})
            return

        if parsed.path == "/api/docs":
            qs = parse_qs(parsed.query)
            which = (qs.get("name") or ["RISK_ACTION_SOP.md"])[0].strip()
            p = (BASE_DIR / which).resolve()
            if not p.exists() or (BASE_DIR not in p.parents and p != BASE_DIR):
                _json(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})
                return
            text = p.read_text(encoding="utf-8", errors="replace")
            _json(self, HTTPStatus.OK, {"ok": True, "name": which, "text": text})
            return

        if parsed.path == "/api/agent/models":
            env = _llm_env()
            _json(
                self,
                HTTPStatus.OK,
                {
                    "ok": True,
                    "current": dict(AGENT_CONFIG),
                    "models": _available_models(),
                    "cloud_enabled": bool(env.get("api_key")),
                    "cloud_base_url": env.get("base_url"),
                },
            )
            return

        if parsed.path == "/api/agent/config":
            _json(self, HTTPStatus.OK, {"ok": True, "config": dict(AGENT_CONFIG)})
            return

        if parsed.path == "/api/jobs/list":
            qs = parse_qs(parsed.query)
            state = (qs.get("state") or ["outbox"])[0].strip()
            limit = int((qs.get("limit") or ["50"])[0])
            if state not in ("outbox", "sent", "archive"):
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid_state"})
                return
            items = _list_jobs(state=state, limit=limit)
            _json(self, HTTPStatus.OK, {"ok": True, "state": state, "items": items})
            return

        if parsed.path == "/api/jobs/get":
            qs = parse_qs(parsed.query)
            job_id = (qs.get("id") or [""])[0].strip()
            if not job_id:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_id"})
                return
            p = _find_job(job_id)
            if not p:
                _json(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})
                return
            try:
                job = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                _json(self, HTTPStatus.OK, {"ok": True, "id": job_id, "error": "invalid_json", "path": str(p)})
                return
            _json(self, HTTPStatus.OK, {"ok": True, "id": job_id, "path": str(p), "job": job})
            return

        self.send_response(HTTPStatus.NOT_FOUND)
        self.end_headers()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/agent/config":
            data = _read_json(self)
            mode = str(data.get("mode") or "").strip()
            model = str(data.get("model") or "").strip()
            provider = str(data.get("provider") or "").strip()
            actor = str(data.get("actor") or "ops").strip() or "ops"

            # allowlist
            if mode and mode not in ("command", "cloud_chat"):
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid_mode"})
                return
            if provider and provider not in ("local", "openai_compat"):
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid_provider"})
                return

            if mode:
                AGENT_CONFIG["mode"] = mode
            if model:
                AGENT_CONFIG["model"] = model
            if provider:
                AGENT_CONFIG["provider"] = provider

            try:
                _save_agent_config()
            except Exception as e:
                _json(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error": f"save_failed: {e}"})
                return

            _append_jsonl(
                AGENT_AUDIT_JSONL,
                {"timestamp": _job_now_iso(), "kind": "agent_config_updated", "actor": actor, "config": dict(AGENT_CONFIG)},
            )
            _json(self, HTTPStatus.OK, {"ok": True, "config": dict(AGENT_CONFIG)})
            return

        if parsed.path == "/api/jobs/create":
            data = _read_json(self)
            job_type = str(data.get("type") or "").strip()
            actor = str(data.get("actor") or "ops").strip() or "ops"
            domain = str(data.get("domain") or "wuchang.life").strip() or "wuchang.life"
            node = data.get("node") if isinstance(data.get("node"), dict) else {}
            params = data.get("params") if isinstance(data.get("params"), dict) else {}
            if not job_type:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_type"})
                return

            job_id = _new_job_id()
            job = {
                "id": job_id,
                "created_at": _job_now_iso(),
                "type": job_type,
                "requested_by": actor,
                "domain": domain,
                "node": node,
                "params": params,
                "policy": {
                    "no_response_no_high_risk_action": True,
                    "requires_confirmation": True if job_type in ("sync_push", "deploy", "restart", "clear_cache", "issue_cert") else False,
                },
                "status": {"state": "outbox"},
            }
            p = _write_job("outbox", job)
            _append_jsonl(JOB_AUDIT_JSONL, {"timestamp": _job_now_iso(), "kind": "job_created", "job_id": job_id, "type": job_type, "actor": actor})
            _json(self, HTTPStatus.OK, {"ok": True, "job_id": job_id, "path": str(p), "job": job})
            return

        if parsed.path == "/api/jobs/move":
            data = _read_json(self)
            job_id = str(data.get("id") or "").strip()
            to_state = str(data.get("to") or "").strip()
            actor = str(data.get("actor") or "ops").strip() or "ops"
            if not job_id or to_state not in ("sent", "archive", "outbox"):
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid_args"})
                return
            try:
                p = _move_job(job_id, to_state=to_state)
            except FileNotFoundError:
                _json(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})
                return
            _append_jsonl(JOB_AUDIT_JSONL, {"timestamp": _job_now_iso(), "kind": "job_moved", "job_id": job_id, "to": to_state, "actor": actor})
            _json(self, HTTPStatus.OK, {"ok": True, "id": job_id, "to": to_state, "path": str(p)})
            return

        if parsed.path == "/api/agent/chat":
            data = _read_json(self)
            text = str(data.get("text") or "").strip()
            session_id = str(data.get("session_id") or "default").strip()[:80]
            domain = str(data.get("domain") or "wuchang.life").strip() or "wuchang.life"
            health_url = str(data.get("health_url") or os.getenv("WUCHANG_HEALTH_URL") or "").strip()
            copy_to = str(data.get("copy_to") or os.getenv("WUCHANG_COPY_TO") or "").strip()
            actor = str(data.get("actor") or "ops").strip() or "ops"
            node = data.get("node") if isinstance(data.get("node"), dict) else {}
            agent_mode = str(data.get("agent_mode") or AGENT_CONFIG.get("mode") or "command").strip()
            agent_model = str(data.get("agent_model") or AGENT_CONFIG.get("model") or "local_rule").strip()
            agent_provider = str(data.get("agent_provider") or AGENT_CONFIG.get("provider") or "local").strip()

            if not text:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_text"})
                return

            # 若是雲端對話模式：只用於一般問答；涉及動作仍走本機白名單（可控）
            # 判斷是否為「純問答」：意圖 unknown 才交給模型
            intent_peek = _detect_intent(text)
            if agent_mode == "cloud_chat" and (intent_peek.get("intent") == "unknown"):
                env = _llm_env()
                if not env.get("api_key"):
                    _json(
                        self,
                        HTTPStatus.OK,
                        {
                            "ok": True,
                            "executed": False,
                            "reply": "你已切換到「雲端對話模式」，但目前未設定 WUCHANG_LLM_API_KEY，所以我不會外送任何內容。請先設定金鑰或切回「本機指揮模式」。",
                            "agent": {"mode": agent_mode, "model": agent_model, "provider": agent_provider},
                        },
                    )
                    return
                try:
                    reply_text = _call_openai_compat_chat(model=agent_model, user_text=text, timeout_seconds=20)
                except Exception as e:
                    reply_text = f"雲端模型呼叫失敗：{e}\n建議：切回本機指揮模式，或檢查 WUCHANG_LLM_BASE_URL / WUCHANG_LLM_API_KEY。"
                _json(
                    self,
                    HTTPStatus.OK,
                    {
                        "ok": True,
                        "executed": True,
                        "reply": reply_text,
                        "agent": {"mode": agent_mode, "model": agent_model, "provider": agent_provider},
                    },
                )
                return

            # 先處理「確認推送 …」的第二段確認
            confirmed_action = _consume_confirm(session_id=session_id, text=text)
            if confirmed_action:
                profile = str(confirmed_action.get("profile") or "rules").strip()
                args = ["safe_sync_push.py", "--profile", profile, "--actor", actor]
                if health_url:
                    args += ["--health-url", health_url]
                if copy_to:
                    args += ["--copy-to", copy_to]
                run = _run_script(args, timeout_seconds=180)
                reply = (
                    f"已收到確認，準備推送：{profile}\n"
                    f"- 依規則：會先做 health 檢查；若無回應/不可驗證將自動中止並留痕。\n"
                    f"- 執行結果 exit_code={run.get('exit_code')}"
                )
                _json(
                    self,
                    HTTPStatus.OK,
                    {
                        "ok": True,
                        "reply": reply,
                        "executed": True,
                        "action": {"type": "sync_push", "profile": profile},
                        "run": run,
                        "agent": {"mode": agent_mode, "model": agent_model, "provider": agent_provider},
                    },
                )
                return

            intent = intent_peek
            it = str(intent.get("intent") or "unknown")

            # 讓回覆可以帶一點「前文脈絡」：目前選取節點
            node_name = str(node.get("name") or "").strip()
            node_id = str(node.get("id") or "").strip()
            prefix = f"（節點：{node_name or '未指定'}）\n" if (node_name or node_id) else ""

            if it == "dns_status":
                status = _check_acme_propagation(domain)
                reply = prefix + _format_dns_status(status)
                _json(self, HTTPStatus.OK, {"ok": True, "reply": reply, "executed": True, "status": status, "agent": {"mode": agent_mode, "model": agent_model, "provider": agent_provider}})
                return

            if it == "dns_expected":
                exp = _get_expected_acme(domain)
                reply = prefix + _format_expected(exp)
                _json(self, HTTPStatus.OK, {"ok": True, "reply": reply, "executed": True, "expected": exp, "agent": {"mode": agent_mode, "model": agent_model, "provider": agent_provider}})
                return

            if it == "net_snapshot":
                # 一律存檔（避免「目前環境」丟失），檔名可由使用者另外指定
                SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
                ts = time.strftime("%Y%m%d_%H%M%S")
                fname = f"network_snapshot_{ts}.json"
                out_path = (SNAPSHOT_DIR / fname).resolve()
                args = ["network_snapshot.py", "--out", str(out_path)]
                if health_url:
                    args += ["--health-url", health_url]
                run = _run_script(args, timeout_seconds=60)
                reply = (
                    prefix
                    + "【網路快照】已產生並存檔\n"
                    + f"- 路徑：{out_path}\n"
                    + (f"- 伺服器健康檢查：已檢查（URL 已提供）\n" if health_url else "- 伺服器健康檢查：未檢查（未提供 health URL）\n")
                    + f"- exit_code={run.get('exit_code')}"
                )
                _json(self, HTTPStatus.OK, {"ok": True, "reply": reply, "executed": True, "saved_path": str(out_path), "run": run, "agent": {"mode": agent_mode, "model": agent_model, "provider": agent_provider}})
                return

            if it == "audit_tail":
                items = _tail_jsonl(AUDIT_JSONL, limit=20)
                if not items:
                    reply = prefix + "【稽核】目前沒有紀錄。"
                else:
                    lines = []
                    for x in items[-20:]:
                        ts = x.get("timestamp") or x.get("time") or "（無時間）"
                        kind = x.get("kind") or x.get("action_type") or "（未知）"
                        actor2 = x.get("actor") or "（未知操作者）"
                        result = x.get("result") or x.get("status") or "（無結果）"
                        lines.append(f"- {ts}｜{kind}｜操作者={actor2}｜結果={result}")
                    reply = prefix + "【稽核摘要（最新在下方）】\n" + "\n".join(lines)
                _json(self, HTTPStatus.OK, {"ok": True, "reply": reply, "executed": True, "items": items, "agent": {"mode": agent_mode, "model": agent_model, "provider": agent_provider}})
                return

            if it == "jobs_list":
                state = str(intent.get("state") or "outbox").strip()
                if state not in ("outbox", "sent", "archive"):
                    state = "outbox"
                items = _list_jobs(state=state, limit=10)
                if not items:
                    reply = prefix + f"【命令單】{state} 目前沒有紀錄。"
                else:
                    lines = []
                    for j in items[:10]:
                        jid = j.get("id") or "unknown"
                        jtype = j.get("type") or "（未知）"
                        by = j.get("requested_by") or "（未知）"
                        at = j.get("created_at") or "（無時間）"
                        lines.append(f"- {jid}｜{jtype}｜{by}｜{at}")
                    reply = prefix + f"【命令單清單：{state}】\n" + "\n".join(lines) + "\n\n（你也可以在 UI 的「命令單收件匣」直接點選查看。）"
                _json(self, HTTPStatus.OK, {"ok": True, "reply": reply, "executed": True, "state": state, "items": items, "agent": {"mode": agent_mode, "model": agent_model, "provider": agent_provider}})
                return

            if it == "docs_show":
                name = str(intent.get("name") or "RISK_ACTION_SOP.md").strip()
                p = (BASE_DIR / name).resolve()
                if not p.exists() or (BASE_DIR not in p.parents and p != BASE_DIR):
                    _json(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})
                    return
                text2 = p.read_text(encoding="utf-8", errors="replace")
                reply = prefix + f"已載入文件：{name}\n（內容已回傳，可在右側文件區查看）"
                _json(self, HTTPStatus.OK, {"ok": True, "reply": reply, "executed": True, "doc": {"name": name, "text": text2}, "agent": {"mode": agent_mode, "model": agent_model, "provider": agent_provider}})
                return

            if it in ("push_rules", "push_kb"):
                profile = "kb" if it == "push_kb" else "rules"
                # 新策略：預設產生「命令單（Job）」交由伺服器執行（更穩、更可控、更易稽核）
                # 本機只負責：生成/排程/留痕；不直接做高風險動作（除非你明確要求「立即在本機執行」）
                job_id = _new_job_id()
                job = {
                    "id": job_id,
                    "created_at": _job_now_iso(),
                    "type": "sync_push",
                    "requested_by": actor,
                    "domain": domain,
                    "node": {"id": node.get("id"), "name": node.get("name")} if isinstance(node, dict) else {},
                    "params": {
                        "profile": profile,
                        "health_url": health_url or "",
                        "copy_to": copy_to or "",
                        "actor": actor,
                        "note": "由本機中控台小J產生命令單；建議由伺服器端執行器拉取並執行。",
                    },
                    "policy": {
                        "no_response_no_high_risk_action": True,
                        "requires_confirmation": True,
                        "two_phase_confirm": True,
                    },
                    "status": {"state": "outbox"},
                }
                p = _write_job("outbox", job)
                _append_jsonl(JOB_AUDIT_JSONL, {"timestamp": _job_now_iso(), "kind": "job_created", "job_id": job_id, "type": "sync_push", "actor": actor})

                reply = prefix + (
                    f"我已為你建立【推送命令單】（建議交由伺服器執行）：\n"
                    f"- profile：{profile}\n"
                    f"- job_id：{job_id}\n"
                    f"- 位置：{p}\n"
                    "\n"
                    "下一步（建議）：把命令單同步到伺服器的 job inbox，讓伺服器端執行器去跑。\n"
                    "提醒：任何執行端仍必須遵守「無回應＝禁止高風險作業」。"
                )
                _json(self, HTTPStatus.OK, {"ok": True, "reply": reply, "executed": True, "job": job, "job_path": str(p), "agent": {"mode": agent_mode, "model": agent_model, "provider": agent_provider}})
                return

            # unknown
            _json(self, HTTPStatus.OK, {"ok": True, "reply": prefix + _little_j_reply_help(), "executed": False, "intent": it, "agent": {"mode": agent_mode, "model": agent_model, "provider": agent_provider}})
            return

        if parsed.path == "/api/run/dns_check":
            data = _read_json(self)
            domain = str(data.get("domain") or "wuchang.life").strip()
            only_acme = bool(data.get("check_acme", True))
            args = ["dns_propagation_check.py", "--domain", domain, "--config", "dns_records.json"]
            if only_acme:
                args.append("--check-acme")
            res = _run_script(args, timeout_seconds=60)
            _json(self, HTTPStatus.OK, {"ok": True, "run": res})
            return

        if parsed.path == "/api/run/sync_push":
            data = _read_json(self)
            profile = str(data.get("profile") or "rules").strip()
            if profile not in ("rules", "kb"):
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid_profile"})
                return
            health_url = str(data.get("health_url") or os.getenv("WUCHANG_HEALTH_URL") or "").strip()
            copy_to = str(data.get("copy_to") or os.getenv("WUCHANG_COPY_TO") or "").strip()
            actor = str(data.get("actor") or "ops").strip()

            # 允許不填：工具本身會依「無回應＝禁止」中止並留下稽核
            args = ["safe_sync_push.py", "--profile", profile, "--actor", actor]
            if health_url:
                args += ["--health-url", health_url]
            if copy_to:
                args += ["--copy-to", copy_to]

            res = _run_script(args, timeout_seconds=180)
            _json(self, HTTPStatus.OK, {"ok": True, "run": res})
            return

        if parsed.path == "/api/workspace/write":
            data = _read_json(self)
            kind = str(data.get("kind") or "little_j").strip()
            title = str(data.get("title") or "control_center").strip()
            content = str(data.get("content") or "").strip()
            meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}

            outdir = os.getenv("WUCHANG_WORKSPACE_OUTDIR") or ""
            webhook = os.getenv("WUCHANG_WORKSPACE_WEBHOOK_URL") or ""

            if not outdir and not webhook:
                # 沒有設定就不寫入（避免寫到未知位置）
                _json(
                    self,
                    HTTPStatus.BAD_REQUEST,
                    {
                        "ok": False,
                        "error": "missing_workspace_config",
                        "hint": "set WUCHANG_WORKSPACE_OUTDIR to a Google Drive synced folder (recommended), or set WUCHANG_WORKSPACE_WEBHOOK_URL",
                    },
                )
                return

            res = write_workspace_artifact(
                kind=kind,
                title=title,
                content=content,
                meta=meta,
                outdir=outdir or None,
                webhook_url=webhook or None,
            )
            _json(self, HTTPStatus.OK, {"ok": True, "result": res.__dict__})
            return

        self.send_response(HTTPStatus.NOT_FOUND)
        self.end_headers()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8788)
    args = ap.parse_args()

    if not UI_HTML.exists():
        raise SystemExit(f"missing UI file: {UI_HTML}")

    _load_agent_config()
    httpd = ThreadingHTTPServer(("127.0.0.1", int(args.port)), Handler)
    print(f"[ok] local control center: http://127.0.0.1:{args.port}/")
    httpd.serve_forever()


if __name__ == "__main__":
    main()

