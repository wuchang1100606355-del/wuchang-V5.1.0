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
import hashlib
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
UI_PROFILES_PATH = BASE_DIR / "ui_profiles.json"
AGENT_CONFIG_PATH = BASE_DIR / "agent_config.json"
AGENT_AUDIT_JSONL = BASE_DIR / "agent_audit.jsonl"
PII_AUDIT_JSONL = BASE_DIR / "pii_audit.jsonl"
AUTH_AUDIT_JSONL = BASE_DIR / "auth_audit.jsonl"
DEVICE_AUDIT_JSONL = BASE_DIR / "device_audit.jsonl"
CONSENT_AUDIT_JSONL = BASE_DIR / "consent_audit.jsonl"
VOUCHER_AUDIT_JSONL = BASE_DIR / "voucher_audit.jsonl"

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

def _sha256_text(s: str) -> str:
    h = hashlib.sha256()
    h.update((s or "").encode("utf-8", errors="replace"))
    return h.hexdigest()


def _now_epoch() -> int:
    return int(time.time())


def _session_account_id(handler: BaseHTTPRequestHandler) -> str:
    sess = _get_session(handler)
    return str((sess or {}).get("account_id") or "").strip()


# ===== 帳號（號碼）→權限 =====
SESSIONS: Dict[str, Dict[str, Any]] = {}


def _accounts_policy_path() -> Optional[Path]:
    """
    建議放在 Google Drive 同步資料夾（Workspace 私密區）：
    - WUCHANG_ACCOUNTS_PATH（優先）
    - 或 <WUCHANG_WORKSPACE_OUTDIR>/accounts_policy.json
    """
    p = (os.getenv("WUCHANG_ACCOUNTS_PATH") or "").strip()
    if p:
        return Path(p).expanduser().resolve()
    d = _pii_vault_dir()  # 同樣依賴 Workspace outdir
    if not d:
        return None
    return (d / "accounts_policy.json").resolve()


def _workspace_matching_path() -> Optional[Path]:
    """
    Google Workspace（Drive 同步）高度媒合設定檔：
    - WUCHANG_WORKSPACE_MATCHING_PATH（優先）
    - 或 <WUCHANG_WORKSPACE_OUTDIR>/workspace_matching.json
    """
    p = (os.getenv("WUCHANG_WORKSPACE_MATCHING_PATH") or "").strip()
    if p:
        return Path(p).expanduser().resolve()
    d = _workspace_outdir()
    if not d:
        return None
    return (d / "workspace_matching.json").resolve()


def _read_workspace_matching() -> Dict[str, Any]:
    p = _workspace_matching_path()
    if not p or not p.exists():
        return {"version": 1, "note": "workspace_matching.json not found", "accounts": [], "orgs": [], "devices": [], "node_ai_agents": [], "system_functions": []}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {"version": 1, "accounts": []}
    except Exception as e:
        return {"version": 1, "error": f"invalid_json: {e}", "accounts": []}


def _load_accounts_policy() -> Dict[str, Any]:
    p = _accounts_policy_path()
    if not p or not p.exists():
        return {"version": 1, "accounts": []}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {"version": 1, "accounts": []}
    except Exception:
        return {"version": 1, "accounts": []}


def _find_account(account_id: str) -> Optional[Dict[str, Any]]:
    aid = str(account_id or "").strip()
    if not aid:
        return None
    pol = _load_accounts_policy()
    accs = pol.get("accounts") if isinstance(pol.get("accounts"), list) else []
    for a in accs:
        if not isinstance(a, dict):
            continue
        if str(a.get("account_id") or "").strip() == aid:
            return a
    return None


def _new_session(account: Dict[str, Any]) -> str:
    sid = uuid.uuid4().hex
    perms = account.get("permissions") if isinstance(account.get("permissions"), list) else []
    SESSIONS[sid] = {
        "created_at": _job_now_iso(),
        "expires_at": time.time() + 8 * 3600,  # 8 小時
        "account_id": str(account.get("account_id") or ""),
        "label": str(account.get("label") or ""),
        "profile_id": str(account.get("profile_id") or "ops_admin"),
        "permissions": [str(x) for x in perms if str(x).strip()],
    }
    return sid


def _get_session(handler: BaseHTTPRequestHandler) -> Optional[Dict[str, Any]]:
    sid = str(handler.headers.get("X-Wuchang-Session") or "").strip()
    if not sid:
        return None
    s = SESSIONS.get(sid)
    if not s:
        return None
    if float(s.get("expires_at") or 0) < time.time():
        SESSIONS.pop(sid, None)
        return None
    return s


def _has_perm(sess: Optional[Dict[str, Any]], perm: str) -> bool:
    # 若未啟用帳號政策：視為單機模式，允許 read，其他按最小權限拒絕
    pol = _load_accounts_policy()
    enabled = bool((pol.get("accounts") or []))
    if not enabled:
        return perm == "read"
    if not sess:
        return False
    perms = sess.get("permissions") or []
    return perm in perms or "admin_all" in perms


def _require_perm(handler: BaseHTTPRequestHandler, perm: str) -> Optional[Dict[str, Any]]:
    sess = _get_session(handler)
    if not _has_perm(sess, perm):
        _json(handler, HTTPStatus.FORBIDDEN, {"ok": False, "error": "forbidden", "required": perm})
        return None
    return sess


def _require_any_perm(handler: BaseHTTPRequestHandler, perms: List[str]) -> Optional[Dict[str, Any]]:
    """
    允許多個權限其一通過（用於相容：pii_read vs pii_read_identifiable 等）。
    """
    sess = _get_session(handler)
    for p in perms:
        if _has_perm(sess, p):
            return sess
    _json(handler, HTTPStatus.FORBIDDEN, {"ok": False, "error": "forbidden", "required_any": perms})
    return None


def _pii_vault_dir() -> Optional[Path]:
    """
    個資保管：靠 Google Workspace（Drive 同步資料夾）落地。
    - 優先：WUCHANG_PII_OUTDIR（可指定更私密的子資料夾）
    - 其次：WUCHANG_WORKSPACE_OUTDIR
    """
    outdir = (os.getenv("WUCHANG_PII_OUTDIR") or os.getenv("WUCHANG_WORKSPACE_OUTDIR") or "").strip()
    if not outdir:
        return None
    return Path(outdir).expanduser().resolve()


def _vault_dir_general() -> Optional[Path]:
    """
    一般私密落地區（可用於票券/折扣碼等營運資料）：
    - 優先：WUCHANG_PII_OUTDIR
    - 其次：WUCHANG_WORKSPACE_OUTDIR
    """
    return _pii_vault_dir()


def _vault_safe_path(*parts: str) -> Path:
    root = _vault_dir_general()
    if not root:
        raise ValueError("missing_vault_outdir")
    p = (root / Path(*parts)).resolve()
    if root.resolve() not in p.parents and p != root.resolve():
        raise ValueError("invalid_vault_path")
    return p


def _workspace_outdir() -> Optional[Path]:
    """
    一般輸出/交換區：靠 Google Drive 同步資料夾落地。
    （用於「設備任務/回覆」等，不放 repo）
    """
    outdir = (os.getenv("WUCHANG_WORKSPACE_OUTDIR") or "").strip()
    if not outdir:
        return None
    return Path(outdir).expanduser().resolve()


def _workspace_safe_path(*parts: str) -> Path:
    """
    把檔案限制在 Workspace outdir 內，避免路徑穿越。
    """
    root = _workspace_outdir()
    if not root:
        raise ValueError("missing_workspace_outdir")
    p = (root / Path(*parts)).resolve()
    if root.resolve() not in p.parents and p != root.resolve():
        raise ValueError("invalid_workspace_path")
    return p


def _write_workspace_json(*, rel_dir: str, filename: str, payload: Dict[str, Any]) -> Path:
    p = _workspace_safe_path(rel_dir, filename)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def _list_workspace_json_files(*, rel_dir: str, limit: int = 200) -> List[Path]:
    root = _workspace_outdir()
    if not root:
        return []
    base = _workspace_safe_path(rel_dir)
    if not base.exists():
        return []
    files = sorted(base.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=False)
    return files[: max(1, min(int(limit), 2000))]


def _normalize_pii_class(v: str) -> str:
    """
    個資分類：
    - identifiable：可識別（姓名/電話/Email 等）
    - non_identifiable：不可識別（角色/值班方式/非特定個人聯繫方式等）
    """
    t = (v or "").strip().lower().replace("-", "_")
    if t in ("non_identifiable", "nonidentifiable", "public", "anon", "anonymized"):
        return "non_identifiable"
    return "identifiable"


def _pii_vault_path(pii_class: str = "identifiable") -> Optional[Path]:
    d = _pii_vault_dir()
    if not d:
        return None
    c = _normalize_pii_class(pii_class)
    # 相容：原本的 pii_contacts.json 視為 identifiable
    fname = "pii_contacts.json" if c == "identifiable" else "pii_contacts_non_identifiable.json"
    return (d / fname).resolve()


def _read_pii_vault(pii_class: str = "identifiable") -> Dict[str, Any]:
    p = _pii_vault_path(pii_class)
    if not p or not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_pii_vault(pii_class: str, vault: Dict[str, Any]) -> Optional[Path]:
    p = _pii_vault_path(pii_class)
    if not p:
        return None
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(vault, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def _digits_only(s: str) -> str:
    return "".join(ch for ch in (s or "") if ch.isdigit())


def _phone_last4(s: str) -> str:
    d = _digits_only(s)
    return d[-4:] if len(d) >= 4 else d


def _mask_phone_keep_last4(s: str) -> str:
    last4 = _phone_last4(s)
    if not last4:
        return ""
    return f"****{last4}"


def _mask_name(s: str) -> str:
    t = (s or "").strip()
    if not t:
        return ""
    if len(t) == 1:
        return t + "＊"
    return t[0] + ("＊" * (len(t) - 1))


def _match_name_mask(mask: str, name: str) -> bool:
    """
    姓名遮罩比對：
    - mask 可含 '*' 或 '＊' 當萬用字元
    - 逐字比對（mask 比 name 短也可，只比對 mask 長度）
    """
    m = (mask or "").strip()
    n = (name or "").strip()
    if not m:
        return True
    if not n:
        return False
    wild = {"*", "＊", "x", "X"}
    for i, ch in enumerate(m):
        if i >= len(n):
            return False
        if ch in wild:
            continue
        if ch != n[i]:
            return False
    return True


# ===== 會員折扣票券 / 商品券 / 折扣碼（預留模組） =====
def _voucher_store_path() -> Optional[Path]:
    try:
        return _vault_safe_path("commerce", "vouchers.json")
    except Exception:
        return None


def _read_voucher_store() -> Dict[str, Any]:
    p = _voucher_store_path()
    if not p or not p.exists():
        return {"version": 1, "vouchers": {}}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data.setdefault("version", 1)
            data.setdefault("vouchers", {})
            if not isinstance(data.get("vouchers"), dict):
                data["vouchers"] = {}
            return data
        return {"version": 1, "vouchers": {}}
    except Exception:
        return {"version": 1, "vouchers": {}}


def _write_voucher_store(store: Dict[str, Any]) -> Optional[Path]:
    p = _voucher_store_path()
    if not p:
        return None
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def _voucher_code_hash(code_plain: str) -> str:
    c = (code_plain or "").strip()
    return _sha256_text(c)


def _voucher_code_mask(code_plain: str) -> str:
    c = (code_plain or "").strip()
    if not c:
        return ""
    tail = c[-4:] if len(c) >= 4 else c
    return "****" + tail


def _voucher_is_valid_now(v: Dict[str, Any]) -> bool:
    if not isinstance(v, dict):
        return False
    st = str(v.get("status") or "active").strip().lower()
    if st != "active":
        return False
    now = _now_epoch()
    vf = int(v.get("valid_from_epoch") or 0)
    vu = int(v.get("valid_until_epoch") or 0)
    if vf and now < vf:
        return False
    if vu and now > vu:
        return False
    return True


def _job_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


# ===== 不可識別個資（帳號編號 account_id 為主鍵，用於習慣分析/系統改版參考） =====
def _account_nonid_profile_path() -> Optional[Path]:
    d = _pii_vault_dir()
    if not d:
        return None
    return (d / "account_profiles_non_identifiable.json").resolve()


def _age_to_band(age_years: int) -> str:
    a = int(age_years)
    if a < 0:
        return ""
    if a <= 12:
        return "0-12"
    if a <= 17:
        return "13-17"
    if a <= 24:
        return "18-24"
    if a <= 34:
        return "25-34"
    if a <= 44:
        return "35-44"
    if a <= 54:
        return "45-54"
    if a <= 64:
        return "55-64"
    return "65+"


def _sanitize_account_nonid_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    僅允許「不可識別」欄位；拒絕姓名/電話/Email/生日等。
    - gender: unknown|male|female|non_binary|other
    - age_band: 0-12|13-17|18-24|25-34|35-44|45-54|55-64|65+（或用 age_years 自動轉）
    - habits: 文字摘要（不要包含個資）
    - tags: 字串陣列（不要包含個資）
    """
    if not isinstance(profile, dict):
        return {}

    # block obvious identifiable keys
    for k in ("name", "phone", "email", "birthday", "birth", "dob", "address", "id_number", "ssn"):
        if k in profile:
            profile.pop(k, None)

    gender = str(profile.get("gender") or "").strip().lower()
    if gender not in ("unknown", "male", "female", "non_binary", "other"):
        gender = "unknown" if gender else ""

    age_band = str(profile.get("age_band") or profile.get("age_range") or "").strip()
    age_years_raw = profile.get("age_years") if "age_years" in profile else profile.get("age")
    if age_years_raw is not None and str(age_years_raw).strip() != "":
        try:
            age_band2 = _age_to_band(int(age_years_raw))
            if age_band2:
                age_band = age_band2
        except Exception:
            pass
    if age_band not in ("0-12", "13-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"):
        age_band = ""

    habits = str(profile.get("habits") or profile.get("note") or "").strip()
    if len(habits) > 2000:
        habits = habits[:2000]

    tags_in = profile.get("tags") if isinstance(profile.get("tags"), list) else []
    tags: List[str] = []
    for t in tags_in[:30]:
        s = str(t).strip()
        if not s:
            continue
        if len(s) > 40:
            s = s[:40]
        tags.append(s)

    out: Dict[str, Any] = {}
    if gender:
        out["gender"] = gender
    if age_band:
        out["age_band"] = age_band
    if habits:
        out["habits"] = habits
    if tags:
        out["tags"] = tags
    return out


def _read_account_nonid_profiles() -> Dict[str, Any]:
    p = _account_nonid_profile_path()
    if not p or not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_account_nonid_profiles(vault: Dict[str, Any]) -> Optional[Path]:
    p = _account_nonid_profile_path()
    if not p:
        return None
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(vault, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


# ===== 同意（Consent）：告知範圍/用途 → 徵求同意 → 才能使用 =====
CONSENT_POLICY_VERSION = 1
DEFAULT_CONSENT_POLICY: Dict[str, Any] = {
    "policy_version": CONSENT_POLICY_VERSION,
    "scope": "account_non_identifiable_profile",
    "purposes": [
        "usage_analytics",  # 使用習慣分析（系統改版參考）
        "system_improvement",  # 系統升級/調整
    ],
    "data_fields": [
        "gender",  # 性別
        "age_band",  # 年齡區間（非生日）
        "habits",  # 習慣摘要
        "tags",  # 非識別標籤
    ],
    "not_collect": [
        "birthday", "birth_date", "dob",  # 出生年月日
        "name", "phone", "email", "address",  # 可識別資料
    ],
    "storage": "Google Drive synced folder (WUCHANG_WORKSPACE_OUTDIR or WUCHANG_PII_OUTDIR)",
    "sharing": "none_by_default",
    "retention_days": 365,
    "rights": [
        "可隨時撤回同意（撤回後停止使用）",
        "可要求刪除（清除）不可識別個資檔內該帳號資料",
        "可查詢目前保存的不可識別個資內容",
    ],
}


def _consent_vault_path() -> Optional[Path]:
    d = _pii_vault_dir()
    if not d:
        return None
    return (d / "consent_receipts.json").resolve()


def _read_consent_vault() -> Dict[str, Any]:
    p = _consent_vault_path()
    if not p or not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_consent_vault(vault: Dict[str, Any]) -> Optional[Path]:
    p = _consent_vault_path()
    if not p:
        return None
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(vault, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def _consent_is_effective(rec: Dict[str, Any]) -> bool:
    if not isinstance(rec, dict):
        return False
    if rec.get("revoked_at"):
        return False
    exp = rec.get("expires_at_epoch")
    try:
        if exp and time.time() > float(exp):
            return False
    except Exception:
        pass
    if int(rec.get("policy_version") or 0) != CONSENT_POLICY_VERSION:
        return False
    if rec.get("scope") != DEFAULT_CONSENT_POLICY.get("scope"):
        return False
    return rec.get("granted") is True


def _get_consent_for_account(account_id: str) -> Dict[str, Any]:
    vault = _read_consent_vault()
    rec = vault.get(account_id) if isinstance(vault.get(account_id), dict) else {}
    return rec or {}


def _require_consent(handler: BaseHTTPRequestHandler, *, account_id: str, scope: str) -> bool:
    """
    硬閘門：未同意 → 不允許使用「不可識別個資」功能。
    """
    rec = _get_consent_for_account(account_id)
    ok = _consent_is_effective(rec) and rec.get("scope") == scope
    if ok:
        return True
    _json(
        handler,
        HTTPStatus.FORBIDDEN,
        {
            "ok": False,
            "error": "consent_required",
            "scope": scope,
            "policy": DEFAULT_CONSENT_POLICY,
            "current_consent": {"exists": bool(rec), "revoked": bool(rec.get("revoked_at")), "policy_version": rec.get("policy_version")},
        },
    )
    return False


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
            if not _require_perm(self, "read"):
                return
            _json(self, HTTPStatus.OK, {"ok": True})
            return

        if parsed.path == "/api/net/snapshot":
            if not _require_perm(self, "read"):
                return
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
            if not _require_perm(self, "read"):
                return
            qs = parse_qs(parsed.query)
            url = (qs.get("url") or [""])[0].strip()
            if not url:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_url"})
                return
            hc = check_server_health(url, timeout_seconds=3.0, retries=2)
            _json(self, HTTPStatus.OK, {"ok": True, "health": asdict(hc)})
            return

        if parsed.path == "/api/dns/expected":
            if not _require_perm(self, "read"):
                return
            qs = parse_qs(parsed.query)
            domain = (qs.get("domain") or ["wuchang.life"])[0].strip()
            _json(self, HTTPStatus.OK, {"ok": True, "expected": _get_expected_acme(domain)})
            return

        if parsed.path == "/api/dns/acme_status":
            if not _require_perm(self, "read"):
                return
            qs = parse_qs(parsed.query)
            domain = (qs.get("domain") or ["wuchang.life"])[0].strip()
            _json(self, HTTPStatus.OK, {"ok": True, "status": _check_acme_propagation(domain)})
            return

        if parsed.path == "/api/audit/tail":
            if not _require_perm(self, "read"):
                return
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
            if not _require_perm(self, "read"):
                return
            qs = parse_qs(parsed.query)
            which = (qs.get("name") or ["RISK_ACTION_SOP.md"])[0].strip()
            p = (BASE_DIR / which).resolve()
            if not p.exists() or (BASE_DIR not in p.parents and p != BASE_DIR):
                _json(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})
                return
            text = p.read_text(encoding="utf-8", errors="replace")
            _json(self, HTTPStatus.OK, {"ok": True, "name": which, "text": text})
            return

        if parsed.path == "/api/ui/profiles":
            if not _require_perm(self, "read"):
                return
            if not UI_PROFILES_PATH.exists():
                _json(self, HTTPStatus.OK, {"ok": True, "version": 1, "profiles": []})
                return
            try:
                data = json.loads(UI_PROFILES_PATH.read_text(encoding="utf-8"))
            except Exception as e:
                _json(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error": f"invalid_ui_profiles_json: {e}"})
                return
            _json(self, HTTPStatus.OK, {"ok": True, **(data if isinstance(data, dict) else {"profiles": []})})
            return

        if parsed.path == "/api/pii/get":
            # 可識別/不可識別分層（相容舊權限：pii_read）
            qs = parse_qs(parsed.query)
            pii_class = _normalize_pii_class((qs.get("class") or ["identifiable"])[0])
            if not _require_any_perm(self, [f"pii_read_{pii_class}", "pii_read"]):
                return
            node_id = (qs.get("node_id") or [""])[0].strip()
            if not node_id:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_node_id"})
                return
            vault_path = _pii_vault_path(pii_class)
            if not vault_path:
                _json(
                    self,
                    HTTPStatus.BAD_REQUEST,
                    {
                        "ok": False,
                        "error": "missing_workspace_outdir",
                        "hint": "set WUCHANG_WORKSPACE_OUTDIR (Google Drive synced folder) or WUCHANG_PII_OUTDIR",
                    },
                )
                return
            vault = _read_pii_vault(pii_class)
            contact = vault.get(node_id) if isinstance(vault.get(node_id), dict) else None
            _json(
                self,
                HTTPStatus.OK,
                {"ok": True, "node_id": node_id, "pii_class": pii_class, "contact": contact or {}, "vault_path": str(vault_path)},
            )
            return

        if parsed.path == "/api/profile/nonid/get":
            # 帳號層級不可識別個資：以登入帳號編號 account_id 為主鍵
            sess = _require_any_perm(self, ["pii_read_non_identifiable", "pii_read"])
            if not sess:
                return
            account_id = str((sess or {}).get("account_id") or "").strip()
            if not account_id:
                _json(self, HTTPStatus.FORBIDDEN, {"ok": False, "error": "forbidden", "required": "login"})
                return
            if not _require_consent(self, account_id=account_id, scope="account_non_identifiable_profile"):
                return
            vault_path = _account_nonid_profile_path()
            if not vault_path:
                _json(
                    self,
                    HTTPStatus.BAD_REQUEST,
                    {"ok": False, "error": "missing_workspace_outdir", "hint": "set WUCHANG_WORKSPACE_OUTDIR or WUCHANG_PII_OUTDIR"},
                )
                return
            vault = _read_account_nonid_profiles()
            profile = vault.get(account_id) if isinstance(vault.get(account_id), dict) else {}
            _json(self, HTTPStatus.OK, {"ok": True, "account_id": account_id, "profile": profile or {}, "vault_path": str(vault_path)})
            return

        if parsed.path == "/api/consent/policy":
            if not _require_perm(self, "read"):
                return
            _json(self, HTTPStatus.OK, {"ok": True, "policy": DEFAULT_CONSENT_POLICY})
            return

        if parsed.path == "/api/consent/status":
            sess = _get_session(self)
            if not sess:
                _json(self, HTTPStatus.FORBIDDEN, {"ok": False, "error": "forbidden", "required": "login"})
                return
            account_id = str((sess or {}).get("account_id") or "").strip()
            if not account_id:
                _json(self, HTTPStatus.FORBIDDEN, {"ok": False, "error": "forbidden", "required": "login"})
                return
            rec = _get_consent_for_account(account_id)
            _json(
                self,
                HTTPStatus.OK,
                {
                    "ok": True,
                    "account_id": account_id,
                    "effective": _consent_is_effective(rec),
                    "scope": DEFAULT_CONSENT_POLICY.get("scope"),
                    "consent": {
                        "granted": bool(rec.get("granted")),
                        "granted_at": rec.get("granted_at"),
                        "revoked_at": rec.get("revoked_at"),
                        "expires_at_epoch": rec.get("expires_at_epoch"),
                        "source": rec.get("source"),
                        "policy_version": rec.get("policy_version"),
                    },
                    "vault_path": str(_consent_vault_path() or ""),
                },
            )
            return

        if parsed.path == "/api/auth/status":
            pol = _load_accounts_policy()
            enabled = bool((pol.get("accounts") or []))
            sess = _get_session(self)
            _json(
                self,
                HTTPStatus.OK,
                {
                    "ok": True,
                    "accounts_enabled": enabled,
                    "session": sess or {},
                    "policy_path": str(_accounts_policy_path() or ""),
                },
            )
            return

        if parsed.path == "/api/agent/models":
            if not _require_perm(self, "read"):
                return
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
            if not _require_perm(self, "read"):
                return
            _json(self, HTTPStatus.OK, {"ok": True, "config": dict(AGENT_CONFIG)})
            return

        if parsed.path == "/api/workspace/matching":
            if not _require_perm(self, "read"):
                return
            p = _workspace_matching_path()
            _json(self, HTTPStatus.OK, {"ok": True, "path": str(p or ""), "data": _read_workspace_matching()})
            return

        if parsed.path == "/api/vouchers/list":
            # 預留：票券/折扣碼清單（不回傳明文折扣碼）
            if not _require_any_perm(self, ["voucher_read", "voucher_manage", "read"]):
                return
            qs = parse_qs(parsed.query)
            owner = (qs.get("owner_account_id") or [""])[0].strip()
            sess_aid = _session_account_id(self)
            # 若指定查詢他人 owner：必須 voucher_manage
            if owner and sess_aid and owner != sess_aid:
                if not _require_any_perm(self, ["voucher_manage"]):
                    return
            store = _read_voucher_store()
            vouchers = store.get("vouchers") if isinstance(store.get("vouchers"), dict) else {}
            items: List[Dict[str, Any]] = []
            for vid, v in vouchers.items():
                if not isinstance(v, dict):
                    continue
                if owner and str(v.get("owner_account_id") or "").strip() != owner:
                    continue
                # 永遠不回傳 code_hash
                safe = dict(v)
                safe.pop("code_hash", None)
                safe["voucher_id"] = str(vid)
                safe["valid_now"] = _voucher_is_valid_now(v)
                items.append(safe)
            _json(self, HTTPStatus.OK, {"ok": True, "count": len(items), "items": items, "store_path": str(_voucher_store_path() or "")})
            return

        if parsed.path == "/api/jobs/list":
            if not _require_any_perm(self, ["job_read", "read"]):
                return
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
            if not _require_any_perm(self, ["job_read", "read"]):
                return
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
        if parsed.path == "/api/device/request":
            # 建立「請使用者設備/帳號自行完成」的任務：靠 Drive 同步交付/回收（合規：最小資料）
            if not _require_perm(self, "device_request"):
                return
            data = _read_json(self)
            device_id = str(data.get("device_id") or "").strip() or "user_device"
            action = str(data.get("action") or "").strip() or "device_ai_task"
            prompt = str(data.get("prompt") or "").strip()
            actor = str(data.get("actor") or "ops").strip() or "ops"
            domain = str(data.get("domain") or "wuchang.life").strip() or "wuchang.life"
            node = data.get("node") if isinstance(data.get("node"), dict) else {}
            sess = _get_session(self)
            account_id = str((sess or {}).get("account_id") or "").strip()
            actor = f"acct:{account_id}" if account_id else actor

            outdir = _workspace_outdir()
            if not outdir:
                _json(
                    self,
                    HTTPStatus.BAD_REQUEST,
                    {"ok": False, "error": "missing_workspace_outdir", "hint": "set WUCHANG_WORKSPACE_OUTDIR (Google Drive synced folder)"},
                )
                return

            job_id = _new_job_id()
            token = uuid.uuid4().hex  # 一次性回覆憑證（只寫入任務檔，回收後可撤回）
            token_sha = _sha256_text(token)
            expires_at = time.time() + 24 * 3600  # 24 小時（可調）

            task = {
                "kind": "wuchang_device_task",
                "job_id": job_id,
                "device_id": device_id,
                "action": action,
                "prompt": prompt,
                "requester_account_id": account_id,
                "consent": {
                    "required": True,
                    "scope": DEFAULT_CONSENT_POLICY.get("scope"),
                    "policy": DEFAULT_CONSENT_POLICY,
                    "how_to": "設備端應顯示 policy（用途/範圍/使用權利/保存期限），取得使用者明確同意後再執行；並將同意結果回寫到回覆檔。",
                },
                "constraints": {
                    "compliance": [
                        "最小資料（不要包含個資/憑證/金鑰）",
                        "若涉及個資：請只寫入 PII Vault（由本機 UI 另外輸入），不要放在回覆檔",
                        "若需雲端 AI：使用設備端的官方 App/帳號完成（例如手機 Gemini），本系統不代管該帳號 token",
                    ],
                    "redact_required": True,
                },
                "deliver": {
                    "result_dir": "device_results",
                    "expected_format": "json",
                },
                "reply_token": token,
                "expires_at_epoch": int(expires_at),
                "created_at": _job_now_iso(),
            }

            # 任務檔寫入 Drive 同步夾：手機/設備可直接看到並處理
            task_path = _write_workspace_json(rel_dir="device_tasks", filename=f"{job_id}.json", payload=task)

            job = {
                "id": job_id,
                "created_at": _job_now_iso(),
                "type": "device_request",
                "requested_by": actor,
                "requester_account_id": account_id,
                "domain": domain,
                "node": node,
                "params": {
                    "device_id": device_id,
                    "action": action,
                    "task_relpath": str(Path("device_tasks") / f"{job_id}.json"),
                    "result_rel_dir": "device_results",
                    "token_sha256": token_sha,
                    "token_expires_at_epoch": int(expires_at),
                },
                "policy": {
                    "no_response_no_high_risk_action": True,
                    "requires_confirmation": False,  # 這裡是「委派請求」，非直接高風險執行
                    "pii_must_stay_local_or_vault": True,
                },
                "status": {"state": "outbox", "device_task_written": True, "device_done": False},
            }
            p = _write_job("outbox", job)
            _append_jsonl(JOB_AUDIT_JSONL, {"timestamp": _job_now_iso(), "kind": "job_created", "job_id": job_id, "type": "device_request", "actor": actor})
            _append_jsonl(DEVICE_AUDIT_JSONL, {"timestamp": _job_now_iso(), "kind": "device_task_written", "job_id": job_id, "device_id": device_id, "task_relpath": str(task_path)})

            # 注意：回覆 token 需要交付給設備（此回應會顯示在 UI）；請勿貼到雲端聊天。
            _json(
                self,
                HTTPStatus.OK,
                {
                    "ok": True,
                    "job_id": job_id,
                    "job_path": str(p),
                    "task_path": str(task_path),
                    "device_reply_token": token,
                    "hint": "把任務檔交給設備（Drive 同步），設備完成後把回覆 json 放到 device_results/<job_id>.json，並包含 reply_token。",
                    "job": job,
                },
            )
            return

        if parsed.path == "/api/device/import_results":
            # 從 Drive 同步夾匯入設備回覆（只存摘要/雜湊，避免把敏感內容寫進 repo）
            if not _require_perm(self, "job_manage"):
                return
            data = _read_json(self)
            limit = int(data.get("limit") or 200)

            outdir = _workspace_outdir()
            if not outdir:
                _json(
                    self,
                    HTTPStatus.BAD_REQUEST,
                    {"ok": False, "error": "missing_workspace_outdir", "hint": "set WUCHANG_WORKSPACE_OUTDIR (Google Drive synced folder)"},
                )
                return

            files = _list_workspace_json_files(rel_dir="device_results", limit=limit)
            imported: List[Dict[str, Any]] = []
            skipped: List[Dict[str, Any]] = []
            for fp in files:
                try:
                    raw = fp.read_text(encoding="utf-8")
                    obj = json.loads(raw)
                except Exception as e:
                    skipped.append({"file": str(fp), "error": f"invalid_json: {e}"})
                    continue

                job_id = str(obj.get("job_id") or fp.stem).strip()
                token = str(obj.get("reply_token") or "").strip()
                artifact = obj.get("artifact") if isinstance(obj.get("artifact"), dict) else {}
                note = str(obj.get("note") or "").strip()

                jp = _find_job(job_id)
                if not jp:
                    skipped.append({"file": str(fp), "job_id": job_id, "error": "job_not_found"})
                    continue

                try:
                    job = json.loads(jp.read_text(encoding="utf-8"))
                except Exception:
                    skipped.append({"file": str(fp), "job_id": job_id, "error": "job_invalid_json"})
                    continue

                expected_sha = str(((job.get("params") or {}).get("token_sha256")) or "").strip().lower()
                exp_until = int(((job.get("params") or {}).get("token_expires_at_epoch")) or 0)
                if exp_until and time.time() > exp_until:
                    skipped.append({"file": str(fp), "job_id": job_id, "error": "token_expired"})
                    continue
                if expected_sha:
                    if not token or _sha256_text(token).lower() != expected_sha:
                        skipped.append({"file": str(fp), "job_id": job_id, "error": "bad_token"})
                        continue

                digest = _sha256_text(raw)
                job.setdefault("status", {})
                job["status"]["device_done"] = True
                job["status"]["device_result_received_at"] = _job_now_iso()
                job["status"]["device_result_sha256"] = digest
                # 只存 artifact 的參考資訊（不要存全文結果）
                job["device_result"] = {
                    "artifact": {
                        "kind": str(artifact.get("kind") or "workspace_file"),
                        "path": str(artifact.get("path") or ""),
                        "sha256": str(artifact.get("sha256") or ""),
                    },
                    "note": note[:400],
                }
                jp.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")

                # 搬移回覆檔，避免重複匯入
                try:
                    dst = _workspace_safe_path("device_results_imported", fp.name)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    fp.replace(dst)
                    moved_to = str(dst)
                except Exception:
                    moved_to = ""

                _append_jsonl(DEVICE_AUDIT_JSONL, {"timestamp": _job_now_iso(), "kind": "device_result_imported", "job_id": job_id, "sha256": digest, "moved_to": moved_to})
                imported.append({"job_id": job_id, "file": str(fp), "sha256": digest, "moved_to": moved_to})

            _json(self, HTTPStatus.OK, {"ok": True, "imported": imported, "skipped": skipped, "count": {"imported": len(imported), "skipped": len(skipped)}})
            return

        if parsed.path == "/api/auth/login":
            data = _read_json(self)
            account_id = str(data.get("account_id") or "").strip()
            pin = str(data.get("pin") or "").strip()
            acc = _find_account(account_id)
            if not acc:
                _json(self, HTTPStatus.FORBIDDEN, {"ok": False, "error": "invalid_account"})
                return
            pin_sha = str(acc.get("pin_sha256") or "").strip().lower()
            if pin_sha:
                if _sha256_text(pin).lower() != pin_sha:
                    _json(self, HTTPStatus.FORBIDDEN, {"ok": False, "error": "invalid_pin"})
                    return
            sid = _new_session(acc)
            _append_jsonl(
                AUTH_AUDIT_JSONL,
                {"timestamp": _job_now_iso(), "kind": "login", "account_id": account_id, "profile_id": str(acc.get("profile_id") or ""), "session": sid[:8]},
            )
            _json(self, HTTPStatus.OK, {"ok": True, "session_id": sid, "profile_id": str(acc.get("profile_id") or "ops_admin"), "label": str(acc.get("label") or "")})
            return

        if parsed.path == "/api/auth/logout":
            sess = _get_session(self)
            sid = str(self.headers.get("X-Wuchang-Session") or "").strip()
            if sid:
                SESSIONS.pop(sid, None)
            _append_jsonl(AUTH_AUDIT_JSONL, {"timestamp": _job_now_iso(), "kind": "logout", "account_id": (sess or {}).get("account_id") if sess else ""})
            _json(self, HTTPStatus.OK, {"ok": True})
            return
        if parsed.path == "/api/agent/config":
            if not _require_perm(self, "agent_config"):
                return
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
            if not _require_perm(self, "job_create"):
                return
            data = _read_json(self)
            job_type = str(data.get("type") or "").strip()
            sess = _get_session(self)
            account_id = str((sess or {}).get("account_id") or "").strip()
            actor = str(data.get("actor") or "ops").strip() or "ops"
            actor = f"acct:{account_id}" if account_id else actor
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
                "requester_account_id": account_id,
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
            _append_jsonl(
                JOB_AUDIT_JSONL,
                {"timestamp": _job_now_iso(), "kind": "job_created", "job_id": job_id, "type": job_type, "actor": actor, "account_id": account_id},
            )
            _json(self, HTTPStatus.OK, {"ok": True, "job_id": job_id, "path": str(p), "job": job})
            return

        if parsed.path == "/api/jobs/move":
            if not _require_perm(self, "job_manage"):
                return
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

        if parsed.path == "/api/pii/set":
            data = _read_json(self)
            pii_class = _normalize_pii_class(str(data.get("pii_class") or data.get("class") or "identifiable"))
            if not _require_any_perm(self, [f"pii_write_{pii_class}", "pii_write"]):
                return
            node_id = str(data.get("node_id") or "").strip()
            actor = str(data.get("actor") or "ops").strip() or "ops"
            contact = data.get("contact") if isinstance(data.get("contact"), dict) else None
            if not node_id:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_node_id"})
                return
            vault_path = _pii_vault_path(pii_class)
            if not vault_path:
                _json(
                    self,
                    HTTPStatus.BAD_REQUEST,
                    {
                        "ok": False,
                        "error": "missing_workspace_outdir",
                        "hint": "set WUCHANG_WORKSPACE_OUTDIR (Google Drive synced folder) or WUCHANG_PII_OUTDIR",
                    },
                )
                return

            # 寫入 vault（僅存必要欄位）
            vault = _read_pii_vault(pii_class)
            if contact is None:
                vault.pop(node_id, None)
                action = "deleted"
                digest = ""
            else:
                if pii_class == "identifiable":
                    safe = {
                        "name": str(contact.get("name") or "").strip(),
                        "phone": str(contact.get("phone") or "").strip(),
                        "email": str(contact.get("email") or "").strip(),
                    }
                else:
                    safe = {
                        "role": str(contact.get("role") or "").strip(),
                        "note": str(contact.get("note") or "").strip(),
                    }
                vault[node_id] = safe
                action = "upserted"
                digest = _sha256_text(json.dumps(safe, ensure_ascii=False, sort_keys=True))

            p = _write_pii_vault(pii_class, vault)
            # 稽核不寫入明文個資，只寫 node_id + digest
            _append_jsonl(
                PII_AUDIT_JSONL,
                {
                    "timestamp": _job_now_iso(),
                    "kind": "pii_vault_update",
                    "actor": actor,
                    "node_id": node_id,
                    "pii_class": pii_class,
                    "action": action,
                    "sha256": digest,
                },
            )
            _json(
                self,
                HTTPStatus.OK,
                {"ok": True, "node_id": node_id, "pii_class": pii_class, "action": action, "vault_path": str(p) if p else str(vault_path)},
            )
            return

        if parsed.path == "/api/pii/match":
            # 部分個資比對（不回傳明文姓名/電話）
            # 例：手機後四碼 + 姓名遮罩（張＊）
            if not _require_any_perm(self, ["pii_read_identifiable", "pii_read"]):
                return
            data = _read_json(self)
            node_id = str(data.get("node_id") or "").strip()
            if not node_id:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_node_id"})
                return
            phone_last4 = _digits_only(str(data.get("phone_last4") or "")).strip()
            name_mask = str(data.get("name_mask") or "").strip()

            vault_path = _pii_vault_path("identifiable")
            if not vault_path:
                _json(
                    self,
                    HTTPStatus.BAD_REQUEST,
                    {"ok": False, "error": "missing_workspace_outdir", "hint": "set WUCHANG_WORKSPACE_OUTDIR or WUCHANG_PII_OUTDIR"},
                )
                return
            vault = _read_pii_vault("identifiable")
            contact = vault.get(node_id) if isinstance(vault.get(node_id), dict) else {}
            name = str((contact or {}).get("name") or "").strip()
            phone = str((contact or {}).get("phone") or "").strip()

            stored_last4 = _phone_last4(phone)
            phone_ok = True
            if phone_last4:
                phone_ok = stored_last4 == phone_last4[-4:]
            name_ok = _match_name_mask(name_mask, name)
            overall = bool(phone_ok and name_ok)

            # 稽核不存明文
            digest = _sha256_text(json.dumps({"node_id": node_id, "phone_last4": phone_last4[-4:], "name_mask": name_mask}, ensure_ascii=False, sort_keys=True))
            _append_jsonl(
                PII_AUDIT_JSONL,
                {"timestamp": _job_now_iso(), "kind": "pii_partial_match", "node_id": node_id, "sha256": digest, "result": overall},
            )

            _json(
                self,
                HTTPStatus.OK,
                {
                    "ok": True,
                    "node_id": node_id,
                    "match": overall,
                    "checks": {"phone_last4": phone_ok, "name_mask": name_ok},
                    "preview": {"name_masked": _mask_name(name), "phone_masked": _mask_phone_keep_last4(phone)},
                },
            )
            return

        if parsed.path == "/api/vouchers/upsert":
            # 預留：建立/更新票券（折扣碼只接收明文 → 存 hash+mask，不回傳明文）
            if not _require_any_perm(self, ["voucher_manage"]):
                return
            data = _read_json(self)
            voucher_id = str(data.get("voucher_id") or "").strip() or _new_job_id()
            vtype = str(data.get("type") or "discount_code").strip()
            if vtype not in ("discount_code", "coupon_ticket", "product_voucher"):
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid_type"})
                return
            owner = str(data.get("owner_account_id") or "").strip()
            code_plain = str(data.get("code_plain") or "").strip()
            code_hash = _voucher_code_hash(code_plain) if code_plain else ""
            code_masked = _voucher_code_mask(code_plain) if code_plain else str(data.get("code_masked") or "").strip()

            sess_aid = _session_account_id(self)
            actor = f"acct:{sess_aid}" if sess_aid else "ops"

            store = _read_voucher_store()
            vouchers = store.get("vouchers") if isinstance(store.get("vouchers"), dict) else {}
            prev = vouchers.get(voucher_id) if isinstance(vouchers.get(voucher_id), dict) else {}

            v: Dict[str, Any] = dict(prev) if isinstance(prev, dict) else {}
            v.update(
                {
                    "type": vtype,
                    "owner_account_id": owner,
                    "status": str(data.get("status") or v.get("status") or "active"),
                    "code_masked": code_masked,
                    "updated_at": _job_now_iso(),
                    "updated_by": actor,
                }
            )
            if code_hash:
                v["code_hash"] = code_hash

            # value / constraints / meta（預留結構）
            if isinstance(data.get("value"), dict):
                v["value"] = data.get("value")
            if isinstance(data.get("constraints"), dict):
                v["constraints"] = data.get("constraints")
            if isinstance(data.get("meta"), dict):
                v["meta"] = data.get("meta")

            # validity shortcuts
            if data.get("valid_from_epoch") is not None:
                try:
                    v["valid_from_epoch"] = int(data.get("valid_from_epoch"))
                except Exception:
                    pass
            if data.get("valid_until_epoch") is not None:
                try:
                    v["valid_until_epoch"] = int(data.get("valid_until_epoch"))
                except Exception:
                    pass

            vouchers[voucher_id] = v
            store["vouchers"] = vouchers
            p = _write_voucher_store(store)
            digest = _sha256_text(json.dumps({"voucher_id": voucher_id, "type": vtype, "owner": owner, "code_masked": code_masked}, ensure_ascii=False, sort_keys=True))
            _append_jsonl(VOUCHER_AUDIT_JSONL, {"timestamp": _job_now_iso(), "kind": "voucher_upsert", "actor": actor, "voucher_id": voucher_id, "sha256": digest})

            safe = dict(v)
            safe.pop("code_hash", None)
            _json(self, HTTPStatus.OK, {"ok": True, "voucher_id": voucher_id, "voucher": safe, "store_path": str(p or "")})
            return

        if parsed.path == "/api/vouchers/validate":
            # 預留：驗證折扣碼是否存在且有效（不改狀態）
            if not _require_any_perm(self, ["voucher_read", "voucher_manage"]):
                return
            data = _read_json(self)
            code_plain = str(data.get("code_plain") or "").strip()
            voucher_id = str(data.get("voucher_id") or "").strip()
            if not code_plain and not voucher_id:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_code_or_voucher_id"})
                return
            store = _read_voucher_store()
            vouchers = store.get("vouchers") if isinstance(store.get("vouchers"), dict) else {}
            target: Optional[Dict[str, Any]] = None
            if voucher_id and isinstance(vouchers.get(voucher_id), dict):
                target = vouchers.get(voucher_id)
            elif code_plain:
                h = _voucher_code_hash(code_plain)
                for vid, v in vouchers.items():
                    if not isinstance(v, dict):
                        continue
                    if str(v.get("code_hash") or "") == h:
                        target = dict(v)
                        target["voucher_id"] = str(vid)
                        break
            if not target:
                _json(self, HTTPStatus.OK, {"ok": True, "match": False, "valid_now": False})
                return
            vid2 = str(target.get("voucher_id") or voucher_id or "")
            safe = dict(target)
            safe.pop("code_hash", None)
            _json(self, HTTPStatus.OK, {"ok": True, "match": True, "valid_now": _voucher_is_valid_now(target), "voucher": safe, "voucher_id": vid2})
            return

        if parsed.path == "/api/vouchers/redeem":
            # 預留：兌換（會把狀態改成 redeemed）
            if not _require_any_perm(self, ["voucher_redeem", "voucher_manage"]):
                return
            data = _read_json(self)
            code_plain = str(data.get("code_plain") or "").strip()
            voucher_id = str(data.get("voucher_id") or "").strip()
            if not code_plain and not voucher_id:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_code_or_voucher_id"})
                return
            store = _read_voucher_store()
            vouchers = store.get("vouchers") if isinstance(store.get("vouchers"), dict) else {}
            vid = voucher_id
            v: Optional[Dict[str, Any]] = vouchers.get(vid) if vid and isinstance(vouchers.get(vid), dict) else None
            if not v and code_plain:
                h = _voucher_code_hash(code_plain)
                for k, vv in vouchers.items():
                    if isinstance(vv, dict) and str(vv.get("code_hash") or "") == h:
                        vid = str(k)
                        v = vv
                        break
            if not v:
                _json(self, HTTPStatus.OK, {"ok": True, "redeemed": False, "error": "not_found"})
                return
            # 驗證 code（若有提供）
            if code_plain:
                if str(v.get("code_hash") or "") != _voucher_code_hash(code_plain):
                    _json(self, HTTPStatus.OK, {"ok": True, "redeemed": False, "error": "bad_code"})
                    return
            if not _voucher_is_valid_now(v):
                _json(self, HTTPStatus.OK, {"ok": True, "redeemed": False, "error": "not_valid_now"})
                return
            sess_aid = _session_account_id(self)
            actor = f"acct:{sess_aid}" if sess_aid else "ops"
            v["status"] = "redeemed"
            v["redeemed_at"] = _job_now_iso()
            v["redeemed_by"] = actor
            vouchers[vid] = v
            store["vouchers"] = vouchers
            p = _write_voucher_store(store)
            digest = _sha256_text(json.dumps({"voucher_id": vid, "redeemed_by": actor}, ensure_ascii=False, sort_keys=True))
            _append_jsonl(VOUCHER_AUDIT_JSONL, {"timestamp": _job_now_iso(), "kind": "voucher_redeem", "actor": actor, "voucher_id": vid, "sha256": digest})
            safe = dict(v)
            safe.pop("code_hash", None)
            _json(self, HTTPStatus.OK, {"ok": True, "redeemed": True, "voucher_id": vid, "voucher": safe, "store_path": str(p or "")})
            return

        if parsed.path == "/api/profile/nonid/set":
            # 帳號層級不可識別個資：只允許寫自己的 account_id（除非 admin_all）
            sess = _require_any_perm(self, ["pii_write_non_identifiable", "pii_write"])
            if not sess:
                return
            account_id = str((sess or {}).get("account_id") or "").strip()
            if not account_id:
                _json(self, HTTPStatus.FORBIDDEN, {"ok": False, "error": "forbidden", "required": "login"})
                return
            if not _require_consent(self, account_id=account_id, scope="account_non_identifiable_profile"):
                return

            data = _read_json(self)
            actor = str(data.get("actor") or "ops").strip() or "ops"
            actor = f"acct:{account_id}"
            raw_profile = data.get("profile") if isinstance(data.get("profile"), dict) else None

            vault_path = _account_nonid_profile_path()
            if not vault_path:
                _json(
                    self,
                    HTTPStatus.BAD_REQUEST,
                    {"ok": False, "error": "missing_workspace_outdir", "hint": "set WUCHANG_WORKSPACE_OUTDIR or WUCHANG_PII_OUTDIR"},
                )
                return

            vault = _read_account_nonid_profiles()
            if raw_profile is None:
                vault.pop(account_id, None)
                action = "deleted"
                digest = ""
                saved = {}
            else:
                saved = _sanitize_account_nonid_profile(raw_profile)
                vault[account_id] = saved
                action = "upserted"
                digest = _sha256_text(json.dumps(saved, ensure_ascii=False, sort_keys=True))

            p = _write_account_nonid_profiles(vault)
            _append_jsonl(
                PII_AUDIT_JSONL,
                {
                    "timestamp": _job_now_iso(),
                    "kind": "account_nonid_profile_update",
                    "actor": actor,
                    "account_id": account_id,
                    "pii_class": "non_identifiable",
                    "action": action,
                    "sha256": digest,
                },
            )
            _json(self, HTTPStatus.OK, {"ok": True, "account_id": account_id, "action": action, "profile": saved, "vault_path": str(p) if p else str(vault_path)})
            return

        if parsed.path == "/api/consent/grant":
            sess = _get_session(self)
            if not sess:
                _json(self, HTTPStatus.FORBIDDEN, {"ok": False, "error": "forbidden", "required": "login"})
                return
            account_id = str((sess or {}).get("account_id") or "").strip()
            if not account_id:
                _json(self, HTTPStatus.FORBIDDEN, {"ok": False, "error": "forbidden", "required": "login"})
                return
            data = _read_json(self)
            actor = f"acct:{account_id}"
            scope = str(data.get("scope") or DEFAULT_CONSENT_POLICY.get("scope") or "").strip()
            if scope != DEFAULT_CONSENT_POLICY.get("scope"):
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid_scope"})
                return
            # 必須明確確認（ack=true），避免誤觸
            ack = bool(data.get("ack") is True)
            if not ack:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_ack", "hint": "set ack=true after showing policy to user"})
                return

            vault_path = _consent_vault_path()
            if not vault_path:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_workspace_outdir"})
                return
            vault = _read_consent_vault()
            expires_at = time.time() + int(DEFAULT_CONSENT_POLICY.get("retention_days") or 365) * 86400
            rec = {
                "account_id": account_id,
                "scope": scope,
                "policy_version": CONSENT_POLICY_VERSION,
                "granted": True,
                "granted_at": _job_now_iso(),
                "expires_at_epoch": int(expires_at),
                "revoked_at": "",
                "source": str(data.get("source") or "ui").strip(),
                "purposes": list(DEFAULT_CONSENT_POLICY.get("purposes") or []),
                "data_fields": list(DEFAULT_CONSENT_POLICY.get("data_fields") or []),
            }
            vault[account_id] = rec
            p = _write_consent_vault(vault)
            digest = _sha256_text(json.dumps(rec, ensure_ascii=False, sort_keys=True))
            _append_jsonl(CONSENT_AUDIT_JSONL, {"timestamp": _job_now_iso(), "kind": "consent_granted", "actor": actor, "account_id": account_id, "scope": scope, "policy_version": CONSENT_POLICY_VERSION, "sha256": digest})
            _json(self, HTTPStatus.OK, {"ok": True, "account_id": account_id, "effective": True, "scope": scope, "vault_path": str(p) if p else str(vault_path)})
            return

        if parsed.path == "/api/consent/revoke":
            sess = _get_session(self)
            if not sess:
                _json(self, HTTPStatus.FORBIDDEN, {"ok": False, "error": "forbidden", "required": "login"})
                return
            account_id = str((sess or {}).get("account_id") or "").strip()
            if not account_id:
                _json(self, HTTPStatus.FORBIDDEN, {"ok": False, "error": "forbidden", "required": "login"})
                return
            actor = f"acct:{account_id}"
            vault_path = _consent_vault_path()
            if not vault_path:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_workspace_outdir"})
                return
            vault = _read_consent_vault()
            rec = vault.get(account_id) if isinstance(vault.get(account_id), dict) else {}
            if rec:
                rec["revoked_at"] = _job_now_iso()
                rec["granted"] = False
                vault[account_id] = rec
                p = _write_consent_vault(vault)
                digest = _sha256_text(json.dumps(rec, ensure_ascii=False, sort_keys=True))
            else:
                p = _write_consent_vault(vault)
                digest = ""
            _append_jsonl(CONSENT_AUDIT_JSONL, {"timestamp": _job_now_iso(), "kind": "consent_revoked", "actor": actor, "account_id": account_id, "scope": DEFAULT_CONSENT_POLICY.get("scope"), "sha256": digest})
            _json(self, HTTPStatus.OK, {"ok": True, "account_id": account_id, "effective": False, "vault_path": str(p) if p else str(vault_path)})
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
            sess = _get_session(self)
            account_id = str((sess or {}).get("account_id") or "").strip()
            if account_id:
                actor = f"acct:{account_id}"

            if not text:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_text"})
                return

            # 若是雲端對話模式：只用於一般問答；涉及動作仍走本機白名單（可控）
            # 判斷是否為「純問答」：意圖 unknown 才交給模型
            intent_peek = _detect_intent(text)
            # 若已啟用帳號政策：所有功能對接都依賴編號（必須先登入）
            pol = _load_accounts_policy()
            accounts_enabled = bool((pol.get("accounts") or []))
            if accounts_enabled and not sess:
                _json(self, HTTPStatus.FORBIDDEN, {"ok": False, "error": "forbidden", "required": "read"})
                return

            # 依意圖做權限門檻（避免繞過 job_create/pii/workspace 等）
            it0 = str(intent_peek.get("intent") or "unknown")
            if it0 in ("push_rules", "push_kb"):
                if not _require_perm(self, "job_create"):
                    return
            else:
                # 其他查詢/說明類：read
                if not _require_perm(self, "read"):
                    return
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
                        "account_id": account_id,
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
                    "requester_account_id": account_id,
                    "domain": domain,
                    "node": {"id": node.get("id"), "name": node.get("name")} if isinstance(node, dict) else {},
                    "params": {
                        "profile": profile,
                        "health_url": health_url or "",
                        "copy_to": copy_to or "",
                        "actor": actor,
                        "account_id": account_id,
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
                _append_jsonl(
                    JOB_AUDIT_JSONL,
                    {"timestamp": _job_now_iso(), "kind": "job_created", "job_id": job_id, "type": "sync_push", "actor": actor, "account_id": account_id},
                )

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
            if not _require_perm(self, "high_risk_execute_local"):
                return
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
            if not _require_perm(self, "workspace_write"):
                return
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

