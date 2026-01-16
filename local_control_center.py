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
AUTHZ_AUDIT_JSONL = BASE_DIR / "authz_audit.jsonl"
VERIFY_AUDIT_JSONL = BASE_DIR / "verify_audit.jsonl"
MAINT_AUDIT_JSONL = BASE_DIR / "maintenance_audit.jsonl"
DESIGN_MODE_AUDIT_JSONL = BASE_DIR / "design_mode_audit.jsonl"

# 系統資料庫（建議放在 admin@wuchang.life 的 Google Drive 同步路徑）
# - WUCHANG_SYSTEM_DB_DIR：指向 Drive 同步中的「五常_中控」根目錄
#   內部約定：
#   - config/：accounts_policy.json, workspace_matching.json
#   - vault/：PII/consent/nonid/vouchers...
#   - exchange/：device_tasks/device_results...
#   - artifacts/：workspace 輸出
#
# Odoo 快取區（非權威資料）：WUCHANG_ODOO_CACHE_DIR（可選）

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


def _suggest_authz_permissions(text: str) -> List[str]:
    """
    將使用者自然語言「控制需求」映射到可調式授權層級（僅用於提示/請示單）。
    注意：這裡不等於實際執行能力；實際執行仍要走 function 白名單與 confirmed。
    """
    t = _norm_text(text)
    perms: List[str] = []

    def add(p: str) -> None:
        if p and p not in perms:
            perms.append(p)

    # VM / RDP / 遠端桌面
    if "rdp" in t or "遠端桌面" in t or "vm" in t or "虛擬機" in t:
        add("vm_control")
    # 容器 / Docker
    if "容器" in t or "docker" in t or "compose" in t:
        add("container_control")
    # 伺服器本機系統控制（管理員級）
    if "伺服器本機" in t or "系統控制" in t or "系統管理員" in t or "administrator" in t:
        add("server_system_control")
    # 路由器 / LAN 設備
    if "路由器" in t or "router" in t or "lan" in t or "設備控制" in t:
        add("router_admin")
    # 網域 / DNS 設定
    if "dns" in t or "網域" in t or "domain" in t or "憑證" in t:
        add("dns_admin")
    # 瀏覽器控制（自動化）
    if "瀏覽器" in t or "browser" in t or "playwright" in t or "selenium" in t:
        add("browser_control")

    return perms


def _suggest_authz_items(text: str) -> List[Dict[str, Any]]:
    """
    小J 自動提出「授權需求」：每個項目各自 TTL（秒）。
    用於建立授權請示單（items），讓管理員能按鍵核准。
    """
    perms = _suggest_authz_permissions(text)
    # 預設建議 TTL（你可依營運再調）
    ttl_map = {
        "vm_control": 20 * 60,  # 20 分
        "server_system_control": 20 * 60,  # 20 分（系統管理員級）
        "container_control": 10 * 60,
        "router_admin": 10 * 60,
        "dns_admin": 10 * 60,
        "browser_control": 10 * 60,
    }
    items: List[Dict[str, Any]] = []
    for p in perms:
        items.append({"permission": p, "ttl_seconds": int(ttl_map.get(p, 3600))})
    return items


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


def _system_db_dir() -> Optional[Path]:
    """
    系統資料庫根目錄（建議：admin@wuchang.life 的 Google Drive 同步資料夾內）。
    """
    p = (os.getenv("WUCHANG_SYSTEM_DB_DIR") or "").strip()
    if not p:
        return None
    return Path(p).expanduser().resolve()


def _system_config_dir() -> Optional[Path]:
    d = _system_db_dir()
    return (d / "config").resolve() if d else None


def _system_vault_dir() -> Optional[Path]:
    d = _system_db_dir()
    return (d / "vault").resolve() if d else None


def _system_exchange_dir() -> Optional[Path]:
    d = _system_db_dir()
    return (d / "exchange").resolve() if d else None


def _system_artifacts_dir() -> Optional[Path]:
    d = _system_db_dir()
    return (d / "artifacts").resolve() if d else None


def _odoo_cache_dir() -> Optional[Path]:
    p = (os.getenv("WUCHANG_ODOO_CACHE_DIR") or "").strip()
    if not p:
        return None
    return Path(p).expanduser().resolve()


# ===== 可調式授權（暫時授權 / 授權請示單）=====
def _authz_dir() -> Path:
    """
    授權資料落地（偏私密）：優先放在系統 vault，否則落回 repo（本機模式）。
    """
    d = _system_vault_dir()
    if d:
        return (d / "authz").resolve()
    return (BASE_DIR / "authz").resolve()


# ===== 設計啟用（Design Mode）：用於「硬編碼生效」=====
def _design_mode_state_path() -> Path:
    base = _authz_dir()
    p = (base / "design_mode_state.json").resolve()
    if base not in p.parents and p != base:
        return (base / "design_mode_state.json").resolve()
    return p


def _load_design_mode_state() -> Dict[str, Any]:
    return _read_json_file(_design_mode_state_path(), default={})


def _save_design_mode_state(state: Dict[str, Any]) -> None:
    _write_json_file(_design_mode_state_path(), state if isinstance(state, dict) else {})


def _design_mode_status() -> Dict[str, Any]:
    st = _load_design_mode_state()
    enabled = bool(st.get("enabled"))
    try:
        until = int(st.get("enabled_until_epoch") or 0)
    except Exception:
        until = 0
    now = int(time.time())
    active = bool(enabled and until and until >= now)
    return {
        "active": active,
        "enabled": enabled,
        "enabled_until_epoch": until,
        "enabled_by_account_id": str(st.get("enabled_by_account_id") or "").strip(),
        "reason": str(st.get("reason") or "").strip(),
        "updated_at": str(st.get("updated_at") or "").strip(),
        "now_epoch": now,
        "path": str(_design_mode_state_path()),
    }


def _design_mode_is_active() -> bool:
    return bool(_design_mode_status().get("active") is True)


def _design_mode_records_dir() -> Optional[Path]:
    """
    硬編碼/設計啟用資訊紀錄落地位置（可交接/可稽核）：
    - 優先：<WUCHANG_SYSTEM_DB_DIR>/artifacts/design_mode_records
    - 次要：WUCHANG_WORKSPACE_OUTDIR/design_mode_records
    - 最後：repo 內 artifacts_design_mode_records（本機模式）
    """
    base = _system_artifacts_dir() or _workspace_outdir()
    if not base:
        base = BASE_DIR
        p = (base / "artifacts_design_mode_records").resolve()
        return p
    p = (base / "design_mode_records").resolve()
    # 防路徑穿越：必須在 base 之下（base 是 artifacts/outdir）
    try:
        if Path(base).resolve() not in p.parents and p != Path(base).resolve():
            return (Path(base).resolve() / "design_mode_records").resolve()
    except Exception:
        return None
    return p


def _write_design_mode_record(kind: str, sess: Optional[Dict[str, Any]], actor: str, reason: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    產生「需以硬編碼製作的資訊紀錄」：JSON 檔 + 回傳路徑/摘要。
    """
    outdir = _design_mode_records_dir()
    if not outdir:
        return {"ok": False, "error": "missing_records_dir"}
    outdir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    rid = uuid.uuid4().hex[:10]
    fname = f"design_mode_record_{ts}_{rid}.json"
    p = (outdir / fname).resolve()

    dm = _design_mode_status()
    maint = _system_maintenance_status()
    accountability = _accountability_from_session(sess)
    payload: Dict[str, Any] = {
        "kind": str(kind or "design_mode_record"),
        "timestamp": _job_now_iso(),
        "actor": str(actor or "").strip(),
        "reason": str(reason or "").strip(),
        "design_mode": dm,
        "maintenance": maint,
        "accountability": accountability,
    }
    if isinstance(extra, dict) and extra:
        payload["extra"] = extra

    try:
        p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        return {"ok": False, "error": f"write_failed: {e}"}

    _append_jsonl(
        DESIGN_MODE_AUDIT_JSONL,
        {"timestamp": _job_now_iso(), "kind": "design_mode_record_written", "actor": payload.get("actor"), "path": str(p), "record_kind": payload.get("kind")},
    )
    return {"ok": True, "path": str(p), "record": payload}


def _authz_requests_dir(state: str = "pending") -> Path:
    base = _authz_dir()
    st = (state or "pending").strip().lower()
    if st not in ("pending", "approved", "denied"):
        st = "pending"
    p = (base / "requests" / st).resolve()
    # 防路徑穿越：必須在 base 之下
    if base not in p.parents and p != base:
        return (base / "requests" / "pending").resolve()
    return p


def _authz_grants_path() -> Path:
    base = _authz_dir()
    p = (base / "temp_grants.json").resolve()
    if base not in p.parents and p != base:
        return (base / "temp_grants.json").resolve()
    return p


def _ensure_authz_dirs() -> None:
    base = _authz_dir()
    base.mkdir(parents=True, exist_ok=True)
    for st in ("pending", "approved", "denied"):
        _authz_requests_dir(st).mkdir(parents=True, exist_ok=True)


def _new_authz_request_id() -> str:
    return "authz_" + uuid.uuid4().hex[:12]


def _read_json_file(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json_file(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_temp_grants() -> List[Dict[str, Any]]:
    _ensure_authz_dirs()
    v = _read_json_file(_authz_grants_path(), default=[])
    return v if isinstance(v, list) else []


def _save_temp_grants(grants: List[Dict[str, Any]]) -> None:
    _ensure_authz_dirs()
    _write_json_file(_authz_grants_path(), grants)


def _grant_active_for_account(grant: Dict[str, Any], account_id: str) -> bool:
    if not isinstance(grant, dict):
        return False
    if str(grant.get("account_id") or "").strip() != str(account_id or "").strip():
        return False
    if grant.get("revoked_at"):
        return False
    # 若是新格式（items 各自 TTL）：只要任一 item 仍有效，就視為 grant 仍有效
    if isinstance(grant.get("items"), list):
        ok_any = False
        for it in grant.get("items") or []:
            if not isinstance(it, dict):
                continue
            if it.get("revoked_at"):
                continue
            exp = it.get("expires_at_epoch")
            try:
                if exp and int(exp) >= int(time.time()):
                    ok_any = True
                    break
            except Exception:
                continue
        if not ok_any:
            return False
    else:
        exp = grant.get("expires_at_epoch")
        try:
            if exp and int(exp) < int(time.time()):
                return False
        except Exception:
            return False
    return True


def _temp_granted_perms(account_id: str) -> List[str]:
    if not account_id:
        return []
    perms: List[str] = []
    now = int(time.time())
    for g in _load_temp_grants():
        if not _grant_active_for_account(g, account_id):
            continue
        # 新格式：items
        if isinstance(g.get("items"), list):
            for it in g.get("items") or []:
                if not isinstance(it, dict):
                    continue
                if it.get("revoked_at"):
                    continue
                exp = it.get("expires_at_epoch")
                try:
                    if exp and int(exp) < now:
                        continue
                except Exception:
                    continue
                s = str(it.get("permission") or "").strip()
                if s and s not in perms:
                    perms.append(s)
            continue
        # 舊格式：permissions + expires_at_epoch
        for p in (g.get("permissions") or []):
            s = str(p).strip()
            if s and s not in perms:
                perms.append(s)
    return perms


# ===== 帳號（號碼）→權限 =====
SESSIONS: Dict[str, Dict[str, Any]] = {}


def _accounts_policy_path() -> Optional[Path]:
    """
    建議放在 Google Drive 同步資料夾（Workspace 私密區）：
    - WUCHANG_ACCOUNTS_PATH（優先）
    - 或 <WUCHANG_SYSTEM_DB_DIR>/config/accounts_policy.json
    - 或 <WUCHANG_PII_OUTDIR>/accounts_policy.json（相容舊）
    """
    p = (os.getenv("WUCHANG_ACCOUNTS_PATH") or "").strip()
    if p:
        return Path(p).expanduser().resolve()
    cfg = _system_config_dir()
    if cfg:
        return (cfg / "accounts_policy.json").resolve()
    d = _pii_vault_dir()  # 相容舊：依賴 Workspace outdir
    if not d:
        return None
    return (d / "accounts_policy.json").resolve()


def _workspace_matching_path() -> Optional[Path]:
    """
    Google Workspace（Drive 同步）高度媒合設定檔：
    - WUCHANG_WORKSPACE_MATCHING_PATH（優先）
    - 或 <WUCHANG_SYSTEM_DB_DIR>/config/workspace_matching.json
    - 或 <WUCHANG_WORKSPACE_OUTDIR>/workspace_matching.json（相容舊）
    """
    p = (os.getenv("WUCHANG_WORKSPACE_MATCHING_PATH") or "").strip()
    if p:
        return Path(p).expanduser().resolve()
    cfg = _system_config_dir()
    if cfg:
        return (cfg / "workspace_matching.json").resolve()
    d = _system_artifacts_dir() or _workspace_outdir()
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
        # 可究責對象（兩個面向）：設計責任 / 使用責任
        # 每個面向都可包含：natural_person / legal_entity（皆為 dict）
        "design_responsibility": account.get("design_responsibility") if isinstance(account.get("design_responsibility"), dict) else {},
        "usage_responsibility": account.get("usage_responsibility") if isinstance(account.get("usage_responsibility"), dict) else {},
        # 相容舊欄位（若仍有人用自然人/法人二分）：會在 _accountability_from_session 做映射
        "accountable_natural_person": account.get("accountable_natural_person") if isinstance(account.get("accountable_natural_person"), dict) else {},
        "accountable_legal_entity": account.get("accountable_legal_entity") if isinstance(account.get("accountable_legal_entity"), dict) else {},
    }
    return sid


def _accountability_from_session(sess: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    可究責 AI：每筆動作必須能對應到兩個可究責對象：
    - design_responsibility：設計責任（誰/哪個法人負責設計與制度）
    - usage_responsibility：使用責任（誰/哪個法人發起與使用）

    每個責任對象皆可含：
    - natural_person（自然人）
    - legal_entity（連帶法人）
    """
    if not isinstance(sess, dict):
        return {"design_responsibility": {"natural_person": {}, "legal_entity": {}}, "usage_responsibility": {"natural_person": {}, "legal_entity": {}}}

    def norm_role(v: Any) -> Dict[str, Any]:
        vv = v if isinstance(v, dict) else {}
        nat2 = vv.get("natural_person") if isinstance(vv.get("natural_person"), dict) else {}
        leg2 = vv.get("legal_entity") if isinstance(vv.get("legal_entity"), dict) else {}
        return {"natural_person": nat2, "legal_entity": leg2}

    def pick_design_legal_entity(design_raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        從設計責任中挑一個可用的法人（交接暫代用途）。
        規則：優先 design_responsibility.legal_entities 第一個「有 name/tax_id/email 任一」的；否則退回 design_responsibility.legal_entity。
        """
        if not isinstance(design_raw, dict):
            return {}
        les = design_raw.get("legal_entities") if isinstance(design_raw.get("legal_entities"), list) else []
        for le in les:
            if not isinstance(le, dict):
                continue
            if str(le.get("name") or "").strip() or str(le.get("tax_id") or "").strip() or str(le.get("email") or "").strip():
                return le
        leg = design_raw.get("legal_entity") if isinstance(design_raw.get("legal_entity"), dict) else {}
        if str(leg.get("name") or "").strip() or str(leg.get("tax_id") or "").strip() or str(leg.get("email") or "").strip():
            return leg
        return {}

    design_raw = sess.get("design_responsibility") if isinstance(sess.get("design_responsibility"), dict) else {}
    usage_raw = sess.get("usage_responsibility") if isinstance(sess.get("usage_responsibility"), dict) else {}
    design = norm_role(design_raw)
    usage = norm_role(usage_raw)

    # 相容舊欄位：若沒有 design/usage，就用舊 natural/legal 填入 usage（使用責任）
    if not design["natural_person"] and not design["legal_entity"] and not usage["natural_person"] and not usage["legal_entity"]:
        nat_old = sess.get("accountable_natural_person") if isinstance(sess.get("accountable_natural_person"), dict) else {}
        leg_old = sess.get("accountable_legal_entity") if isinstance(sess.get("accountable_legal_entity"), dict) else {}
        usage = {"natural_person": nat_old, "legal_entity": leg_old}

    # 交接暫代：允許「設計法人」暫代「使用法人」以完成交接（必須明確宣告旗標）
    # - 預設不啟用（維持責任分離）
    # - 僅當 usage_responsibility.handover_legal_entity_from_design == true 且使用法人未填時才套用
    # - 會在 accountability 額外標註 handover，方便稽核與後續交接收回
    handover: Dict[str, Any] = {}
    if bool(usage_raw.get("handover_legal_entity_from_design")) and not usage.get("legal_entity"):
        dle = pick_design_legal_entity(design_raw)
        if dle:
            usage["legal_entity"] = dle
            handover = {
                "usage_legal_entity_from_design": True,
                "source": "design_responsibility",
                "note": "交接暫代：使用法人未填時，以設計法人暫代（需後續完成正式交接/回收）。",
            }

    # usage fallback：至少帶上 account_id/label（仍可追到登入帳號）
    if not usage["natural_person"]:
        usage["natural_person"] = {"account_id": str(sess.get("account_id") or "").strip(), "label": str(sess.get("label") or "").strip()}

    out: Dict[str, Any] = {"design_responsibility": design, "usage_responsibility": usage}
    if handover:
        out["handover"] = handover
    return out


def _responsibility_filled(role: Dict[str, Any]) -> bool:
    """
    判斷「責任位置」是否已填寫（最小可行）：
    - 只要 natural_person 或 legal_entity 任一有非空欄位即可視為已填
    - 不把 fallback 的 account_id/label 當作「已填」
    """
    if not isinstance(role, dict):
        return False
    def _obj_filled(obj: Dict[str, Any]) -> bool:
        if not isinstance(obj, dict) or not obj:
            return False
        # 忽略 fallback 欄位（避免未填也被當成已填）
        obj2 = {k: v for k, v in obj.items() if str(k) not in ("account_id", "label")}
        for v in obj2.values():
            if isinstance(v, str) and v.strip():
                return True
            if isinstance(v, (int, float)) and v != 0:
                return True
            if isinstance(v, dict) and v:
                return True
            if isinstance(v, list) and v:
                return True
        return False

    # 單一 natural_person / legal_entity
    if _obj_filled(role.get("natural_person") if isinstance(role.get("natural_person"), dict) else {}):
        return True
    if _obj_filled(role.get("legal_entity") if isinstance(role.get("legal_entity"), dict) else {}):
        return True

    # 多法人（legal_entities）
    les = role.get("legal_entities") if isinstance(role.get("legal_entities"), list) else []
    for le in les:
        if isinstance(le, dict) and _obj_filled(le):
            return True
    return False


def _role_natural_person_filled(role: Dict[str, Any]) -> bool:
    """
    只判斷「自然人」是否已填（最小可行）：
    - 只看 role.natural_person
    - 不把 fallback 的 account_id/label 當作「已填」
    """
    if not isinstance(role, dict):
        return False
    nat = role.get("natural_person") if isinstance(role.get("natural_person"), dict) else {}
    if not nat:
        return False
    nat2 = {k: v for k, v in nat.items() if str(k) not in ("account_id", "label")}
    for v in nat2.values():
        if isinstance(v, str) and v.strip():
            return True
        if isinstance(v, (int, float)) and v != 0:
            return True
        if isinstance(v, dict) and v:
            return True
        if isinstance(v, list) and v:
            return True
    return False


def _responsibility_has_email(role: Dict[str, Any]) -> bool:
    """
    電子聯絡資訊必填（email）：
    - natural_person.email 或 legal_entity.email 任一存在即可
    """
    if not isinstance(role, dict):
        return False
    nat = role.get("natural_person") if isinstance(role.get("natural_person"), dict) else {}
    e1 = str(nat.get("email") or "").strip()
    if e1:
        return True

    # 單一法人
    leg = role.get("legal_entity") if isinstance(role.get("legal_entity"), dict) else {}
    e2 = str(leg.get("email") or "").strip()
    if e2:
        return True

    # 多法人：只要任一法人有 email 即視為「有 email」
    les = role.get("legal_entities") if isinstance(role.get("legal_entities"), list) else []
    for le in les:
        if isinstance(le, dict) and str(le.get("email") or "").strip():
            return True
    return False


def _responsibility_all_legal_entities_have_email(role: Dict[str, Any]) -> bool:
    """
    設計責任更嚴格：若有列出 legal_entities，要求每個法人都要有 email。
    - 沒有列 legal_entities 時，不強制此條（讓舊格式可用）
    """
    if not isinstance(role, dict):
        return False
    les = role.get("legal_entities") if isinstance(role.get("legal_entities"), list) else []
    if not les:
        return True
    for le in les:
        if not isinstance(le, dict):
            return False
        if not str(le.get("email") or "").strip():
            return False
    return True


def _full_agent_allowed_for_account(account: Dict[str, Any]) -> bool:
    """
    規則（依最新需求調整）：
    - 只要「設計責任」與「使用責任」兩者都各有一位自然人，即可生效 full_agent
    - email 仍建議填寫用於維護/交接，但不再作為 full_agent 的硬門檻
    """
    if not isinstance(account, dict):
        return False
    def _norm_role(v: Any) -> Dict[str, Any]:
        vv = v if isinstance(v, dict) else {}
        nat = vv.get("natural_person") if isinstance(vv.get("natural_person"), dict) else {}
        leg = vv.get("legal_entity") if isinstance(vv.get("legal_entity"), dict) else {}
        les = vv.get("legal_entities") if isinstance(vv.get("legal_entities"), list) else []
        les2 = [x for x in les if isinstance(x, dict)]
        return {"natural_person": nat, "legal_entity": leg, "legal_entities": les2}
    design = _norm_role(account.get("design_responsibility"))
    usage = _norm_role(account.get("usage_responsibility"))
    return _role_natural_person_filled(design) and _role_natural_person_filled(usage)


def _full_agent_allowed_for_session(sess: Optional[Dict[str, Any]]) -> bool:
    """
    以 session 內容判斷是否允許 full_agent（避免未填責任仍放行）。
    """
    if not isinstance(sess, dict):
        return False
    design = sess.get("design_responsibility") if isinstance(sess.get("design_responsibility"), dict) else {}
    usage = sess.get("usage_responsibility") if isinstance(sess.get("usage_responsibility"), dict) else {}
    # session 的 role 直接用（不做 account_id fallback）
    def _norm(v: Any) -> Dict[str, Any]:
        vv = v if isinstance(v, dict) else {}
        nat = vv.get("natural_person") if isinstance(vv.get("natural_person"), dict) else {}
        leg = vv.get("legal_entity") if isinstance(vv.get("legal_entity"), dict) else {}
        les = vv.get("legal_entities") if isinstance(vv.get("legal_entities"), list) else []
        les2 = [x for x in les if isinstance(x, dict)]
        return {"natural_person": nat, "legal_entity": leg, "legal_entities": les2}
    d2 = _norm(design)
    u2 = _norm(usage)
    return _role_natural_person_filled(d2) and _role_natural_person_filled(u2)


def _system_design_maintenance_key() -> str:
    """
    系統層級：找出「設計法人」維護展延的 key（用於全 UI 顯示風險提示）。
    - 讀取 accounts_policy.json
    - 找到第一個具有 design_responsibility 的帳號
    - 取 design_responsibility.legal_entities 第一個有 tax_id 的作為 key
    - 若找不到 tax_id，退回 account_id
    """
    pol = _load_accounts_policy()
    accs = pol.get("accounts") if isinstance(pol.get("accounts"), list) else []
    for a in accs:
        if not isinstance(a, dict):
            continue
        design = a.get("design_responsibility") if isinstance(a.get("design_responsibility"), dict) else {}
        if not design:
            continue
        les = design.get("legal_entities") if isinstance(design.get("legal_entities"), list) else []
        for le in les:
            if not isinstance(le, dict):
                continue
            tax_id = str(le.get("tax_id") or le.get("id") or "").strip()
            if tax_id:
                return f"design_tax_id:{tax_id}"
        leg = design.get("legal_entity") if isinstance(design.get("legal_entity"), dict) else {}
        tax_id2 = str(leg.get("tax_id") or leg.get("id") or "").strip()
        if tax_id2:
            return f"design_tax_id:{tax_id2}"
        aid = str(a.get("account_id") or "").strip()
        if aid:
            return f"design_account:{aid}"
    return ""


def _system_maintenance_status() -> Dict[str, Any]:
    """
    系統層級維護狀態（不需要登入即可查詢）：
    - 若沒有有效的設計法人維護展延（maintenance_state verified_until），回傳 warn 與固定提示文案
    """
    key = _system_design_maintenance_key()
    if not key:
        return {
            "ok": False,
            "verified": False,
            "level": "warn",
            "message": "（本系統未經原設計者做定期維護，可能存在風險）\n（此時所有風險全歸使用者端點）",
            "risk_owner": "user_endpoint",
            "reason": "missing_design_responsibility_key",
        }
    st = _load_maintenance_state()
    rec = st.get(key) if isinstance(st.get(key), dict) else {}
    if not rec or rec.get("revoked_at"):
        return {
            "ok": False,
            "verified": False,
            "level": "warn",
            "message": "（本系統未經原設計者做定期維護，可能存在風險）\n（此時所有風險全歸使用者端點）",
            "risk_owner": "user_endpoint",
            "reason": "missing_or_revoked",
            "key": key,
        }
    exp = rec.get("verified_until_epoch")
    try:
        exp_i = int(exp) if exp is not None else 0
    except Exception:
        exp_i = 0
    now = int(time.time())
    if rec.get("verified") is True and exp_i and exp_i >= now:
        return {"ok": True, "verified": True, "level": "ok", "verified_until_epoch": exp_i, "key": key}
    return {
        "ok": False,
        "verified": False,
        "level": "warn",
        "message": "（本系統未經原設計者做定期維護，可能存在風險）\n（此時所有風險全歸使用者端點）",
        "risk_owner": "user_endpoint",
        "reason": "expired_or_not_verified",
        "verified_until_epoch": exp_i,
        "key": key,
    }


def _smtp_env() -> Dict[str, str]:
    return {
        "host": (os.getenv("WUCHANG_SMTP_HOST") or "").strip(),
        "port": (os.getenv("WUCHANG_SMTP_PORT") or "587").strip(),
        "user": (os.getenv("WUCHANG_SMTP_USER") or "").strip(),
        "pass": (os.getenv("WUCHANG_SMTP_PASS") or "").strip(),
        "from": (os.getenv("WUCHANG_SMTP_FROM") or os.getenv("WUCHANG_SMTP_USER") or "").strip(),
    }


def _maintenance_state_path() -> Path:
    base = _authz_dir()
    p = (base / "maintenance_state.json").resolve()
    if base not in p.parents and p != base:
        return (base / "maintenance_state.json").resolve()
    return p


def _maintenance_key_from_session(sess: Optional[Dict[str, Any]]) -> str:
    """
    綁定設計責任（法人）作為保養驗證對象 key（避免換人就繞過）。
    """
    if not isinstance(sess, dict):
        return ""
    design = sess.get("design_responsibility") if isinstance(sess.get("design_responsibility"), dict) else {}
    # 允許多法人：優先取 legal_entities 第一個有 tax_id 的
    tax_id = ""
    les = design.get("legal_entities") if isinstance(design.get("legal_entities"), list) else []
    for le in les:
        if not isinstance(le, dict):
            continue
        tax_id = str(le.get("tax_id") or le.get("id") or "").strip()
        if tax_id:
            break
    if not tax_id:
        leg = design.get("legal_entity") if isinstance(design.get("legal_entity"), dict) else {}
        tax_id = str(leg.get("tax_id") or leg.get("id") or "").strip()
    if tax_id:
        return f"design_tax_id:{tax_id}"
    # fallback：account_id
    return f"design_account:{str(sess.get('account_id') or '').strip()}"


def _maintenance_contact_email(sess: Optional[Dict[str, Any]]) -> str:
    if not isinstance(sess, dict):
        return ""
    design = sess.get("design_responsibility") if isinstance(sess.get("design_responsibility"), dict) else {}
    nat = design.get("natural_person") if isinstance(design.get("natural_person"), dict) else {}
    # 多法人優先取第一個有 email 的
    les = design.get("legal_entities") if isinstance(design.get("legal_entities"), list) else []
    for le in les:
        if isinstance(le, dict) and str(le.get("email") or "").strip():
            return str(le.get("email") or "").strip()
    leg = design.get("legal_entity") if isinstance(design.get("legal_entity"), dict) else {}
    return str(leg.get("email") or nat.get("email") or "").strip()


def _load_maintenance_state() -> Dict[str, Any]:
    return _read_json_file(_maintenance_state_path(), default={})


def _save_maintenance_state(state: Dict[str, Any]) -> None:
    _write_json_file(_maintenance_state_path(), state if isinstance(state, dict) else {})


def _maintenance_is_verified(sess: Optional[Dict[str, Any]]) -> bool:
    key = _maintenance_key_from_session(sess)
    if not key:
        return False
    st = _load_maintenance_state()
    rec = st.get(key) if isinstance(st.get(key), dict) else {}
    if not rec:
        return False
    if rec.get("revoked_at"):
        return False
    exp = rec.get("verified_until_epoch")
    try:
        if exp and int(exp) < int(time.time()):
            return False
    except Exception:
        return False
    return rec.get("verified") is True


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
    # 最高權限完整代理：完全開放（不受時間/項目/範圍限制）
    # 注意：Design Mode 目前只做「資訊紀錄/留痕」，不作為硬閘門（依使用者要求）
    if "full_agent" in perms and _full_agent_allowed_for_session(sess):
        return True
    if perm in perms or "admin_all" in perms:
        return True
    # 可調式授權：把有效的「暫時授權」納入判斷（帳號層級）
    account_id = str(sess.get("account_id") or "").strip()
    if not account_id:
        return False
    extra = _temp_granted_perms(account_id)
    return perm in extra or "admin_all" in extra


def _scope_matches(scope: Dict[str, Any], ctx: Dict[str, Any]) -> bool:
    """
    範圍授權（scope）最小可行版：
    - 支援：domain/domains、node_id/node_ids
    - 未指定限制時視為允許
    """
    if not isinstance(scope, dict):
        return True
    if not isinstance(ctx, dict):
        ctx = {}

    dom = str(ctx.get("domain") or "").strip()
    node_id = str(ctx.get("node_id") or "").strip()

    # domain
    if "domain" in scope:
        want = str(scope.get("domain") or "").strip()
        if want and dom and want != dom:
            return False
    if "domains" in scope and isinstance(scope.get("domains"), list):
        ds = [str(x).strip() for x in scope.get("domains") if str(x).strip()]
        if ds and dom and dom not in ds:
            return False

    # node_id
    if "node_id" in scope:
        want = str(scope.get("node_id") or "").strip()
        if want and node_id and want != node_id:
            return False
    if "node_ids" in scope and isinstance(scope.get("node_ids"), list):
        ns = [str(x).strip() for x in scope.get("node_ids") if str(x).strip()]
        if ns and node_id and node_id not in ns:
            return False

    return True


def _has_perm_scoped(sess: Optional[Dict[str, Any]], perm: str, ctx: Dict[str, Any]) -> bool:
    """
    用於「指令/對話」等帶上下文的場景：
    - 永久權限（accounts_policy）仍視為全域允許
    - 暫時授權（grant）會受 scope 限制
    - full_agent：完全開放
    """
    pol = _load_accounts_policy()
    enabled = bool((pol.get("accounts") or []))
    if not enabled:
        return perm == "read"
    if not sess:
        return False
    perms = sess.get("permissions") or []
    if "full_agent" in perms and _full_agent_allowed_for_session(sess):
        return True
    if perm in perms or "admin_all" in perms:
        return True
    account_id = str(sess.get("account_id") or "").strip()
    if not account_id:
        return False
    for g in _load_temp_grants():
        if not _grant_active_for_account(g, account_id):
            continue
        gscope = g.get("scope") if isinstance(g.get("scope"), dict) else {}
        if not _scope_matches(gscope, ctx):
            continue
        # 新格式：items（每個 permission 各自到期）
        if isinstance(g.get("items"), list):
            now = int(time.time())
            for it in g.get("items") or []:
                if not isinstance(it, dict):
                    continue
                if str(it.get("permission") or "").strip() != perm:
                    continue
                if it.get("revoked_at"):
                    continue
                exp = it.get("expires_at_epoch")
                try:
                    if exp and int(exp) >= now:
                        return True
                except Exception:
                    continue
            continue
        # 舊格式：permissions + expires_at_epoch
        gperms = g.get("permissions") if isinstance(g.get("permissions"), list) else []
        if perm in [str(x).strip() for x in gperms if str(x).strip()]:
            return True
    return False


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


def _authz_request_path(state: str, request_id: str) -> Path:
    _ensure_authz_dirs()
    rid = _safe_filename(request_id).replace(".", "")[:64] or _new_authz_request_id()
    base = _authz_requests_dir(state)
    p = (base / f"{rid}.json").resolve()
    if _authz_dir() not in p.parents:
        return (_authz_requests_dir("pending") / f"{_new_authz_request_id()}.json").resolve()
    return p


def _list_authz_requests(state: str = "pending", limit: int = 50) -> List[Dict[str, Any]]:
    _ensure_authz_dirs()
    base = _authz_requests_dir(state)
    files = sorted(base.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    out: List[Dict[str, Any]] = []
    for fp in files[: max(1, min(int(limit), 200))]:
        try:
            obj = json.loads(fp.read_text(encoding="utf-8"))
            if isinstance(obj, dict):
                obj.setdefault("id", fp.stem)
                obj["_path"] = str(fp)
                out.append(obj)
            else:
                out.append({"id": fp.stem, "error": "invalid_json", "_path": str(fp)})
        except Exception:
            out.append({"id": fp.stem, "error": "invalid_json", "_path": str(fp)})
    return out


def _find_authz_request(request_id: str) -> Optional[Path]:
    rid = _safe_filename(request_id).replace(".", "")[:64]
    if not rid:
        return None
    for st in ("pending", "approved", "denied"):
        p = _authz_request_path(st, rid)
        if p.exists():
            return p
    return None


def _move_authz_request(request_id: str, to_state: str) -> Path:
    src = _find_authz_request(request_id)
    if not src:
        raise FileNotFoundError("not_found")
    rid = _safe_filename(request_id).replace(".", "")[:64] or src.stem
    dst = _authz_request_path(to_state, rid)
    src.replace(dst)
    return dst


def _pii_vault_dir() -> Optional[Path]:
    """
    個資保管：靠 Google Workspace（Drive 同步資料夾）落地。
    - 優先：WUCHANG_PII_OUTDIR（可指定更私密的子資料夾）
    - 其次：<WUCHANG_SYSTEM_DB_DIR>/vault
    - 再其次：WUCHANG_WORKSPACE_OUTDIR（相容舊）
    """
    outdir = (os.getenv("WUCHANG_PII_OUTDIR") or "").strip()
    if outdir:
        return Path(outdir).expanduser().resolve()
    d2 = _system_vault_dir()
    if d2:
        return d2
    outdir = (os.getenv("WUCHANG_WORKSPACE_OUTDIR") or "").strip()
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
    交換區（建議）：靠 Google Drive 同步資料夾落地。
    - 優先：WUCHANG_WORKSPACE_EXCHANGE_DIR（更精準：專放 device_tasks/device_results 等交換檔）
    - 其次：<WUCHANG_SYSTEM_DB_DIR>/exchange
    - 再其次：WUCHANG_WORKSPACE_OUTDIR（相容舊設定）
    """
    outdir = (os.getenv("WUCHANG_WORKSPACE_EXCHANGE_DIR") or os.getenv("WUCHANG_WORKSPACE_OUTDIR") or "").strip()
    if outdir:
        return Path(outdir).expanduser().resolve()
    d2 = _system_exchange_dir()
    if d2:
        return d2
    return None


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


def _parse_iso_epoch(ts: str) -> Optional[int]:
    ts = str(ts or "").strip()
    if not ts:
        return None
    try:
        # 例如 2026-01-15T12:34:56+0800
        t = time.strptime(ts, "%Y-%m-%dT%H:%M:%S%z")
        return int(time.mktime(t))
    except Exception:
        return None


def _job_age_seconds(job: Dict[str, Any]) -> Optional[int]:
    created = str(job.get("created_at") or "").strip()
    ep = _parse_iso_epoch(created)
    if ep is None:
        return None
    return int(time.time()) - ep


def _verify_programmatically(*, include_hub: bool = True) -> Dict[str, Any]:
    """
    程序驗證器（不依賴語言模型）：
    - 檢查本機 job 是否卡住（outbox/sent 逾時）
    - 若已設定 Hub：檢查 Hub 可達、inbox 是否有 confirmed 卡住、以及是否已歸檔
    """
    now = int(time.time())
    alerts: List[Dict[str, Any]] = []

    def add(level: str, code: str, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        item = {"level": level, "code": code, "message": msg, "time_epoch": now}
        if isinstance(extra, dict):
            item.update(extra)
        alerts.append(item)

    # 本機 jobs
    outbox = _list_jobs("outbox", limit=200)
    sent = _list_jobs("sent", limit=200)

    # 規則：outbox > 10 分鐘 → 警告
    for j in outbox:
        if not isinstance(j, dict):
            continue
        age = _job_age_seconds(j)
        if age is None:
            continue
        if age > 10 * 60:
            add(
                "warn",
                "local_outbox_stale",
                "本機命令單待送（outbox）逾時，可能尚未送到 Hub。",
                {"job_id": j.get("id"), "type": j.get("type"), "age_seconds": age},
            )

    # 規則：sent > 60 分鐘仍未能驗證完成 → 警告（需配合 Hub archive 才能判定完成）
    for j in sent:
        if not isinstance(j, dict):
            continue
        age = _job_age_seconds(j)
        if age is None:
            continue
        if age > 60 * 60:
            add(
                "warn",
                "local_sent_unverified",
                "本機命令單已送（sent）但逾時仍未驗證完成（建議查看 Hub inbox/archive 與 executor）。",
                {"job_id": j.get("id"), "type": j.get("type"), "age_seconds": age},
            )

    hub_summary: Dict[str, Any] = {"configured": False}
    if include_hub:
        env = _hub_env()
        if env.get("url") and env.get("token"):
            hub_summary["configured"] = True
            health = _hub_request("GET", env["url"] + "/health", payload=None, timeout=3)
            hub_summary["health"] = health
            if not health.get("ok"):
                add("bad", "hub_unreachable", "Hub 無回應/不可驗證（無回應＝禁止高風險作業）。", {"hub_url": env.get("url")})
            else:
                inbox_res = _hub_request("GET", env["url"] + "/api/hub/jobs/list?state=inbox&limit=200", payload=None, timeout=6)
                arch_res = _hub_request("GET", env["url"] + "/api/hub/jobs/list?state=archive&limit=200", payload=None, timeout=6)
                hub_summary["inbox"] = inbox_res
                hub_summary["archive"] = arch_res

                inbox_items = (inbox_res.get("data") or {}).get("items") if isinstance(inbox_res.get("data"), dict) else []
                arch_items = (arch_res.get("data") or {}).get("items") if isinstance(arch_res.get("data"), dict) else []
                arch_ids = set()
                for x in arch_items or []:
                    if isinstance(x, dict) and x.get("id"):
                        arch_ids.add(str(x.get("id")))

                # 規則：Hub inbox confirmed 逾 15 分鐘 → 異常（executor 可能未啟動/未 execute）
                for j in inbox_items or []:
                    if not isinstance(j, dict):
                        continue
                    hub = j.get("hub") if isinstance(j.get("hub"), dict) else {}
                    if hub.get("confirmed") is True:
                        t0 = _parse_iso_epoch(str(hub.get("confirmed_at") or hub.get("received_at") or "")) or _parse_iso_epoch(str(j.get("created_at") or ""))
                        if t0 and (now - t0) > 15 * 60:
                            add(
                                "bad",
                                "hub_confirmed_stuck",
                                "Hub 收件匣已確認但逾時未歸檔（疑似未執行或執行器未啟用）。",
                                {"job_id": j.get("id"), "type": j.get("type"), "age_seconds": now - t0},
                            )
                    else:
                        t0 = _parse_iso_epoch(str(hub.get("received_at") or "")) or _parse_iso_epoch(str(j.get("created_at") or ""))
                        if t0 and (now - t0) > 60 * 60:
                            add(
                                "warn",
                                "hub_pending_stale",
                                "Hub 收件匣待確認逾時（可能忘了按「Hub 確認」）。",
                                {"job_id": j.get("id"), "type": j.get("type"), "age_seconds": now - t0},
                            )

                # 規則：本機 sent 若已出現在 Hub archive → 視為已完成可驗證
                for j in sent:
                    if not isinstance(j, dict):
                        continue
                    jid = str(j.get("id") or "").strip()
                    if jid and jid in arch_ids:
                        # 可選：不列 alert，只在 summary 統計
                        pass

    # 整體狀態
    worst = "ok"
    for a in alerts:
        if a.get("level") == "bad":
            worst = "bad"
            break
        if a.get("level") == "warn" and worst != "bad":
            worst = "warn"

    summary = {
        "ok": True,
        "timestamp": _job_now_iso(),
        "status": worst,
        "counts": {
            "alerts": len(alerts),
            "local_outbox": len(outbox),
            "local_sent": len(sent),
        },
        "alerts": alerts,
        "hub": hub_summary,
    }

    # 稽核：只記摘要（避免太大）
    try:
        _append_jsonl(VERIFY_AUDIT_JSONL, {"timestamp": summary["timestamp"], "kind": "verify_snapshot", "status": worst, "alerts": len(alerts)})
    except Exception:
        pass
    return summary


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


def _hub_env() -> Dict[str, str]:
    return {
        "url": (os.getenv("WUCHANG_HUB_URL") or "").strip().rstrip("/"),
        "token": (os.getenv("WUCHANG_HUB_TOKEN") or "").strip(),
    }


def _hub_request(method: str, url: str, payload: Optional[Dict[str, Any]] = None, timeout: int = 6) -> Dict[str, Any]:
    env = _hub_env()
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if env.get("token"):
        headers["X-LittleJ-Token"] = env["token"]
    data = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8") if payload is not None else None
    try:
        req = Request(url, method=method.upper(), headers=headers)
        with urlopen(req, data=data, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                return {"ok": True, "status": int(getattr(resp, "status", 200)), "data": json.loads(raw)}
            except Exception:
                return {"ok": True, "status": int(getattr(resp, "status", 200)), "raw": raw}
    except Exception as e:
        return {"ok": False, "error": f"hub_request_failed: {e}"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            _serve_file(self, UI_HTML, "text/html; charset=utf-8")
            return

        if parsed.path == "/api/maintenance/status":
            # 全 UI 都需要顯示的風險提示：不要求登入（不回傳敏感資料）
            _json(self, HTTPStatus.OK, {"ok": True, "status": _system_maintenance_status()})
            return

        if parsed.path == "/api/design_mode/status":
            if not _require_perm(self, "read"):
                return
            _json(self, HTTPStatus.OK, {"ok": True, "design_mode": _design_mode_status()})
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

        if parsed.path == "/api/authz/requests/list":
            # 管理員查看授權請示單（pending/approved/denied）
            qs = parse_qs(parsed.query)
            state = (qs.get("state") or ["pending"])[0].strip()
            limit = int((qs.get("limit") or ["50"])[0])
            mine = (qs.get("mine") or ["0"])[0].strip().lower() in ("1", "true", "yes", "y")
            sess = _get_session(self)
            is_admin = _has_perm(sess, "auth_manage") or _has_perm(sess, "job_manage")
            if not is_admin:
                # 非管理員：只允許列出自己的 pending（mine=1）
                if not sess or not mine:
                    _json(self, HTTPStatus.FORBIDDEN, {"ok": False, "error": "forbidden", "required_any": ["auth_manage", "job_manage"], "hint": "use ?mine=1 to list your pending requests"})
                    return
                items = _list_authz_requests(state="pending", limit=limit)
                aid = str((sess or {}).get("account_id") or "").strip()
                items = [x for x in items if isinstance(x, dict) and str(x.get("requester_account_id") or "").strip() == aid]
                _json(self, HTTPStatus.OK, {"ok": True, "state": "pending", "count": len(items), "items": items, "mine": True})
                return
            qs = parse_qs(parsed.query)
            items = _list_authz_requests(state=state, limit=limit)
            _json(self, HTTPStatus.OK, {"ok": True, "state": state, "count": len(items), "items": items})
            return

        if parsed.path == "/api/authz/requests/get":
            qs = parse_qs(parsed.query)
            rid = (qs.get("id") or [""])[0].strip()
            sess = _get_session(self)
            is_admin = _has_perm(sess, "auth_manage") or _has_perm(sess, "job_manage")
            if not is_admin and not sess:
                _json(self, HTTPStatus.FORBIDDEN, {"ok": False, "error": "forbidden", "required": "login"})
                return
            qs = parse_qs(parsed.query)
            p = _find_authz_request(rid)
            if not p:
                _json(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})
                return
            try:
                obj = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                _json(self, HTTPStatus.OK, {"ok": True, "id": rid, "error": "invalid_json", "path": str(p)})
                return
            # 非管理員：只允許讀自己的請示單
            if not is_admin:
                aid = str((sess or {}).get("account_id") or "").strip()
                if aid and str(obj.get("requester_account_id") or "").strip() != aid:
                    _json(self, HTTPStatus.FORBIDDEN, {"ok": False, "error": "forbidden", "required_any": ["auth_manage", "job_manage"]})
                    return
            _json(self, HTTPStatus.OK, {"ok": True, "id": rid, "path": str(p), "request": obj})
            return

        if parsed.path == "/api/authz/grants/list":
            if not _require_any_perm(self, ["auth_manage", "job_manage"]):
                return
            qs = parse_qs(parsed.query)
            account_id = (qs.get("account_id") or [""])[0].strip()
            grants = _load_temp_grants()
            if account_id:
                grants = [g for g in grants if isinstance(g, dict) and str(g.get("account_id") or "").strip() == account_id]
            _json(self, HTTPStatus.OK, {"ok": True, "count": len(grants), "items": grants, "path": str(_authz_grants_path())})
            return

        if parsed.path == "/api/verify/status":
            if not _require_perm(self, "read"):
                return
            qs = parse_qs(parsed.query)
            include_hub = (qs.get("hub") or ["1"])[0].strip().lower() in ("1", "true", "yes", "y")
            res = _verify_programmatically(include_hub=include_hub)
            _json(self, HTTPStatus.OK, res)
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

        if parsed.path == "/api/workspace/alignment":
            if not _require_perm(self, "read"):
                return
            # 直接讀取檢查腳本輸出（不落地、不改檔）
            res = _run_script(["workspace_alignment_check.py"], timeout_seconds=20)
            try:
                obj = json.loads(res.get("stdout") or "{}")
            except Exception:
                obj = {"ok": False, "error": "invalid_checker_output", "run": res}
            _json(self, HTTPStatus.OK, {"ok": True, "alignment": obj, "run": res})
            return

        if parsed.path == "/api/hub/status":
            if not _require_perm(self, "read"):
                return
            env = _hub_env()
            if not env.get("url"):
                _json(self, HTTPStatus.OK, {"ok": True, "configured": False, "hint": "set WUCHANG_HUB_URL and WUCHANG_HUB_TOKEN"})
                return
            health = _hub_request("GET", env["url"] + "/health", payload=None, timeout=3)
            _json(self, HTTPStatus.OK, {"ok": True, "configured": True, "hub_url": env["url"], "health": health})
            return

        if parsed.path == "/api/hub/server_info":
            if not _require_perm(self, "read"):
                return
            env = _hub_env()
            if not env.get("url") or not env.get("token"):
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_hub_config", "hint": "set WUCHANG_HUB_URL and WUCHANG_HUB_TOKEN"})
                return
            health = _hub_request("GET", env["url"] + "/health", payload=None, timeout=3)
            if not health.get("ok"):
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "hub_unreachable", "health": health})
                return
            res = _hub_request("GET", env["url"] + "/api/hub/server/info", payload=None, timeout=8)
            _json(self, HTTPStatus.OK, {"ok": True, "hub": res})
            return

        if parsed.path == "/api/hub/server_architecture":
            if not _require_perm(self, "read"):
                return
            env = _hub_env()
            if not env.get("url") or not env.get("token"):
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_hub_config", "hint": "set WUCHANG_HUB_URL and WUCHANG_HUB_TOKEN"})
                return
            # 無回應＝禁止：先確認 Hub 可回應，再取架構資料
            health = _hub_request("GET", env["url"] + "/health", payload=None, timeout=3)
            if not health.get("ok"):
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "hub_unreachable", "health": health})
                return
            res = _hub_request("GET", env["url"] + "/api/hub/server/architecture", payload=None, timeout=12)
            _json(self, HTTPStatus.OK, {"ok": True, "hub": res})
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

            accountability = _accountability_from_session(sess)
            job = {
                "id": job_id,
                "created_at": _job_now_iso(),
                "type": "device_request",
                "requested_by": actor,
                "requester_account_id": account_id,
                "domain": domain,
                "node": node,
                "accountability": accountability,
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
            _append_jsonl(
                JOB_AUDIT_JSONL,
                {"timestamp": _job_now_iso(), "kind": "job_created", "job_id": job_id, "type": "device_request", "actor": actor, "accountability": accountability},
            )
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

        if parsed.path == "/api/design_mode/set":
            # 只有具備管理型權限的人可啟用/關閉（避免一般帳號誤觸）
            if not _require_any_perm(self, ["auth_manage", "agent_config", "job_manage"]):
                return
            sess = _get_session(self)
            data = _read_json(self)
            enabled = bool(data.get("enabled"))
            ttl = int(data.get("ttl_seconds") or 0)
            ttl = max(60, min(ttl if ttl > 0 else 20 * 60, 8 * 3600))  # 預設 20 分鐘，上限 8 小時
            reason = str(data.get("reason") or "").strip()
            actor = str(data.get("actor") or "").strip()
            aid = str((sess or {}).get("account_id") or "").strip()
            who = aid or actor or "unknown"

            now = int(time.time())
            st = _load_design_mode_state()
            if enabled:
                st = {
                    "enabled": True,
                    "enabled_until_epoch": now + ttl,
                    "enabled_by_account_id": who,
                    "reason": reason,
                    "updated_at": _job_now_iso(),
                }
                _save_design_mode_state(st)
                _append_jsonl(
                    DESIGN_MODE_AUDIT_JSONL,
                    {"timestamp": _job_now_iso(), "kind": "design_mode_enabled", "by": who, "ttl_seconds": ttl, "until_epoch": now + ttl, "reason": reason},
                )
                rec = _write_design_mode_record("design_mode_enabled", sess=sess, actor=who, reason=reason, extra={"ttl_seconds": ttl, "until_epoch": now + ttl})
            else:
                st = {
                    "enabled": False,
                    "enabled_until_epoch": 0,
                    "enabled_by_account_id": who,
                    "reason": reason,
                    "updated_at": _job_now_iso(),
                }
                _save_design_mode_state(st)
                _append_jsonl(
                    DESIGN_MODE_AUDIT_JSONL,
                    {"timestamp": _job_now_iso(), "kind": "design_mode_disabled", "by": who, "reason": reason},
                )
                rec = _write_design_mode_record("design_mode_disabled", sess=sess, actor=who, reason=reason, extra={})
            _json(self, HTTPStatus.OK, {"ok": True, "design_mode": _design_mode_status(), "record_written": rec})
            return

        if parsed.path == "/api/design_mode/record":
            # 手動產生資訊紀錄（不影響任何功能）
            if not _require_any_perm(self, ["auth_manage", "agent_config", "job_manage", "read"]):
                return
            sess = _get_session(self)
            data = _read_json(self)
            actor = str(data.get("actor") or "").strip()
            reason = str(data.get("reason") or "").strip()
            kind = str(data.get("kind") or "design_mode_record_manual").strip() or "design_mode_record_manual"
            aid = str((sess or {}).get("account_id") or "").strip()
            who = aid or actor or "unknown"
            rec = _write_design_mode_record(kind, sess=sess, actor=who, reason=reason, extra={"manual": True})
            _json(self, HTTPStatus.OK, {"ok": True, "record_written": rec, "design_mode": _design_mode_status()})
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
            accountability = _accountability_from_session(sess)
            job = {
                "id": job_id,
                "created_at": _job_now_iso(),
                "type": job_type,
                "requested_by": actor,
                "requester_account_id": account_id,
                "domain": domain,
                "node": node,
                "params": params,
                "accountability": accountability,
                "policy": {
                    "no_response_no_high_risk_action": True,
                    "requires_confirmation": True if job_type in ("sync_push", "deploy", "restart", "clear_cache", "issue_cert") else False,
                },
                "status": {"state": "outbox"},
            }
            p = _write_job("outbox", job)
            _append_jsonl(
                JOB_AUDIT_JSONL,
                {
                    "timestamp": _job_now_iso(),
                    "kind": "job_created",
                    "job_id": job_id,
                    "type": job_type,
                    "actor": actor,
                    "account_id": account_id,
                    "accountability": accountability,
                },
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

        if parsed.path == "/api/hub/submit_job":
            # 人類端點：由本機 UI 把命令單送到伺服器小J Hub（機器可讀交流區）
            if not _require_perm(self, "job_create"):
                return
            env = _hub_env()
            if not env.get("url") or not env.get("token"):
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_hub_config", "hint": "set WUCHANG_HUB_URL and WUCHANG_HUB_TOKEN"})
                return
            data = _read_json(self)
            job_id = str(data.get("job_id") or "").strip()
            if not job_id:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_job_id"})
                return
            p = _find_job(job_id)
            if not p:
                _json(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "job_not_found"})
                return
            try:
                job = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid_job_json"})
                return

            # 無回應＝禁止：Hub health 不可達就不送（避免黑洞）
            health = _hub_request("GET", env["url"] + "/health", payload=None, timeout=3)
            if not health.get("ok"):
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "hub_unreachable", "health": health})
                return

            res = _hub_request("POST", env["url"] + "/api/hub/jobs/submit", payload={"job": job}, timeout=6)
            _json(self, HTTPStatus.OK, {"ok": True, "hub": res, "job_id": job_id})
            return

        if parsed.path == "/api/hub/confirm_job":
            # 人類端點：由本機 UI 代替人類在伺服器端 Hub 上確認該 job（允許 executor 執行）
            if not _require_perm(self, "job_manage"):
                return
            env = _hub_env()
            if not env.get("url") or not env.get("token"):
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_hub_config", "hint": "set WUCHANG_HUB_URL and WUCHANG_HUB_TOKEN"})
                return
            data = _read_json(self)
            job_id = str(data.get("job_id") or "").strip()
            actor = str(data.get("actor") or "ops").strip() or "ops"
            if not job_id:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_job_id"})
                return
            health = _hub_request("GET", env["url"] + "/health", payload=None, timeout=3)
            if not health.get("ok"):
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "hub_unreachable", "health": health})
                return
            res = _hub_request("POST", env["url"] + "/api/hub/jobs/confirm", payload={"id": job_id, "actor": actor}, timeout=6)
            _json(self, HTTPStatus.OK, {"ok": True, "hub": res, "job_id": job_id})
            return

        if parsed.path == "/api/hub/generate_reports":
            # 伺服器端生成回報檔（寫入 server exchange/artifacts），供後續設計/對齊使用
            if not _require_perm(self, "job_manage"):
                return
            env = _hub_env()
            if not env.get("url") or not env.get("token"):
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_hub_config", "hint": "set WUCHANG_HUB_URL and WUCHANG_HUB_TOKEN"})
                return
            data = _read_json(self)
            actor = str(data.get("actor") or "ops").strip() or "ops"
            # 無回應＝禁止：Hub health 不可達就不做（避免黑洞）
            health = _hub_request("GET", env["url"] + "/health", payload=None, timeout=3)
            if not health.get("ok"):
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "hub_unreachable", "health": health})
                return
            res = _hub_request("POST", env["url"] + "/api/hub/server/reports/generate", payload={"actor": actor}, timeout=20)
            _json(self, HTTPStatus.OK, {"ok": True, "hub": res})
            return

        if parsed.path == "/api/authz/request":
            # 任何已登入帳號可提出「權限請示」；由管理員核准後給暫時授權（可到期）
            sess = _get_session(self)
            if not sess:
                _json(self, HTTPStatus.FORBIDDEN, {"ok": False, "error": "forbidden", "required": "login"})
                return
            data = _read_json(self)
            account_id = str(sess.get("account_id") or "").strip()
            actor = str(data.get("actor") or f"acct:{account_id}" or "ops").strip() or "ops"
            perms = data.get("permissions") if isinstance(data.get("permissions"), list) else []
            perms = [str(x).strip() for x in perms if str(x).strip()]
            ttl = int(data.get("ttl_seconds") or 0)
            items = data.get("items") if isinstance(data.get("items"), list) else []
            scope = data.get("scope") if isinstance(data.get("scope"), dict) else {}
            reason = str(data.get("reason") or "").strip()
            context = data.get("context") if isinstance(data.get("context"), dict) else {}
            if not perms:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_permissions"})
                return
            # full_agent：若責任位置未填，不可提出/保存完整權限請示
            if "full_agent" in perms:
                acc = _find_account(account_id) or {}
                if not _full_agent_allowed_for_account(acc):
                    _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "full_agent_blocked_missing_responsibility", "hint": "fill design_responsibility.natural_person and usage_responsibility.natural_person first"})
                    return
            # 指令/請示必須包含：時間授權 + 範圍授權（除非 full_agent 完全開放）
            if not _has_perm(sess, "full_agent"):
                # 支援兩種時間模型：ttl_seconds（整體）或 items[*].ttl_seconds（逐項）
                has_item_ttl = False
                for it in items:
                    if isinstance(it, dict) and int(it.get("ttl_seconds") or 0) > 0:
                        has_item_ttl = True
                        break
                if ttl <= 0 and not has_item_ttl:
                    _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_time_grant", "hint": "include ttl_seconds or items[].ttl_seconds"})
                    return
                if not scope:
                    _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_scope", "hint": "include scope in authz request (e.g. {domain,node_id})"})
                    return
            rid = _new_authz_request_id()
            req = {
                "id": rid,
                "created_at": _job_now_iso(),
                "requester_account_id": account_id,
                "requested_by": actor,
                "permissions": perms,
                "ttl_seconds": ttl if ttl > 0 else 0,
                "items": items,
                "scope": scope,
                "reason": reason,
                "context": context,
                "status": "pending",
            }
            p = _authz_request_path("pending", rid)
            _write_json_file(p, req)
            _append_jsonl(AUTHZ_AUDIT_JSONL, {"timestamp": _job_now_iso(), "kind": "authz_request_created", "request_id": rid, "account_id": account_id, "permissions": perms})
            _json(self, HTTPStatus.OK, {"ok": True, "request_id": rid, "path": str(p), "request": req})
            return

        if parsed.path == "/api/authz/requests/approve":
            if not _require_any_perm(self, ["auth_manage", "job_manage"]):
                return
            data = _read_json(self)
            rid = str(data.get("id") or "").strip()
            ttl = int(data.get("ttl_seconds") or 3600)
            ttl = max(60, min(ttl, 24 * 3600))
            override_scope = data.get("scope") if isinstance(data.get("scope"), dict) else None
            override_items = data.get("items") if isinstance(data.get("items"), list) else None
            sess = _get_session(self)
            approver = str((sess or {}).get("account_id") or "").strip()
            if not rid:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_id"})
                return
            p = _find_authz_request(rid)
            if not p:
                _json(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})
                return
            req = _read_json_file(p, default={})
            if not isinstance(req, dict):
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid_request"})
                return
            acct = str(req.get("requester_account_id") or "").strip()
            perms = req.get("permissions") if isinstance(req.get("permissions"), list) else []
            perms = [str(x).strip() for x in perms if str(x).strip()]
            scope = override_scope if isinstance(override_scope, dict) else (req.get("scope") if isinstance(req.get("scope"), dict) else {})
            items = override_items if isinstance(override_items, list) else (req.get("items") if isinstance(req.get("items"), list) else [])
            if not acct or not perms:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid_request_fields"})
                return
            # full_agent：若該帳號責任位置未填，不可核准完整權限
            if "full_agent" in perms or any(isinstance(it, dict) and str(it.get("permission") or "").strip() == "full_agent" for it in (items or [])):
                acc = _find_account(acct) or {}
                if not _full_agent_allowed_for_account(acc):
                    _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "full_agent_blocked_missing_responsibility", "hint": "fill design_responsibility.natural_person and usage_responsibility.natural_person for the requester account first"})
                    return
            if not scope and not _has_perm(sess, "full_agent"):
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_scope", "hint": "approve must include scope (or request must contain scope)"})
                return
            # 建立逐項到期（items）；若 items 不存在就用 permissions+ttl 退化成舊模式
            now = int(time.time())
            items_out: List[Dict[str, Any]] = []
            if isinstance(items, list) and items:
                for it in items:
                    if not isinstance(it, dict):
                        continue
                    p0 = str(it.get("permission") or "").strip()
                    t0 = int(it.get("ttl_seconds") or 0)
                    if not p0:
                        continue
                    if t0 <= 0:
                        t0 = ttl
                    t0 = max(60, min(int(t0), 24 * 3600))
                    items_out.append({"permission": p0, "ttl_seconds": t0, "expires_at_epoch": now + t0})
            grant_id = "grant_" + uuid.uuid4().hex[:12]
            grant = {
                "id": grant_id,
                "account_id": acct,
                "permissions": perms,
                "scope": scope,
                "items": items_out,
                "approved_at": _job_now_iso(),
                "approved_by": approver,
                "expires_at_epoch": now + ttl,
                "expires_in_seconds": ttl,
                "request_id": rid,
            }
            grants = _load_temp_grants()
            grants.insert(0, grant)
            _save_temp_grants(grants)
            req["status"] = "approved"
            req["approved_at"] = _job_now_iso()
            req["approved_by"] = approver
            req["grant_id"] = grant_id
            _write_json_file(p, req)
            dst = _move_authz_request(rid, "approved")
            _append_jsonl(
                AUTHZ_AUDIT_JSONL,
                {
                    "timestamp": _job_now_iso(),
                    "kind": "authz_request_approved",
                    "request_id": rid,
                    "grant_id": grant_id,
                    "approved_by": approver,
                    "account_id": acct,
                    "permissions": perms,
                    "ttl_seconds": ttl,
                },
            )
            _json(self, HTTPStatus.OK, {"ok": True, "request_id": rid, "grant": grant, "moved_to": str(dst), "grants_path": str(_authz_grants_path())})
            return

        if parsed.path == "/api/authz/requests/deny":
            if not _require_any_perm(self, ["auth_manage", "job_manage"]):
                return
            data = _read_json(self)
            rid = str(data.get("id") or "").strip()
            deny_reason = str(data.get("reason") or "").strip()
            sess = _get_session(self)
            actor = str((sess or {}).get("account_id") or "").strip()
            if not rid:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_id"})
                return
            p = _find_authz_request(rid)
            if not p:
                _json(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})
                return
            req = _read_json_file(p, default={})
            if isinstance(req, dict):
                req["status"] = "denied"
                req["denied_at"] = _job_now_iso()
                req["denied_by"] = actor
                if deny_reason:
                    req["deny_reason"] = deny_reason
                _write_json_file(p, req)
            dst = _move_authz_request(rid, "denied")
            _append_jsonl(AUTHZ_AUDIT_JSONL, {"timestamp": _job_now_iso(), "kind": "authz_request_denied", "request_id": rid, "denied_by": actor, "reason": deny_reason})
            _json(self, HTTPStatus.OK, {"ok": True, "request_id": rid, "moved_to": str(dst)})
            return

        if parsed.path == "/api/authz/grants/revoke":
            if not _require_any_perm(self, ["auth_manage", "job_manage"]):
                return
            data = _read_json(self)
            gid = str(data.get("id") or "").strip()
            revoke_reason = str(data.get("reason") or "").strip()
            if not gid:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_id"})
                return
            sess = _get_session(self)
            actor = str((sess or {}).get("account_id") or "").strip()
            grants = _load_temp_grants()
            changed = False
            for g in grants:
                if isinstance(g, dict) and str(g.get("id") or "").strip() == gid and not g.get("revoked_at"):
                    g["revoked_at"] = _job_now_iso()
                    g["revoked_by"] = actor
                    if revoke_reason:
                        g["revoke_reason"] = revoke_reason
                    changed = True
                    break
            if changed:
                _save_temp_grants(grants)
                _append_jsonl(AUTHZ_AUDIT_JSONL, {"timestamp": _job_now_iso(), "kind": "authz_grant_revoked", "grant_id": gid, "revoked_by": actor, "reason": revoke_reason})
            _json(self, HTTPStatus.OK, {"ok": True, "revoked": changed, "grant_id": gid, "path": str(_authz_grants_path())})
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
            required_perm = "job_create" if it0 in ("push_rules", "push_kb") else "read"
            ctx_scope = {"domain": domain, "node_id": str(node.get("id") or "").strip()}
            if not _has_perm_scoped(sess, required_perm, ctx_scope):
                # 可調式授權：權限不足時，小J 主動建立「授權請示單」並回覆下一步
                if not sess or not str((sess or {}).get("account_id") or "").strip():
                    _json(self, HTTPStatus.FORBIDDEN, {"ok": False, "error": "forbidden", "required": required_perm})
                    return
                suggested = _suggest_authz_permissions(text)
                requested_perms = suggested if suggested else [required_perm]
                rid = _new_authz_request_id()
                items = _suggest_authz_items(text)
                if not items:
                    items = [{"permission": p, "ttl_seconds": 3600} for p in requested_perms]
                ttl_seconds = max([int(it.get("ttl_seconds") or 0) for it in items] + [3600])
                scope = {
                    "domain": domain,
                    "node_id": str(node.get("id") or "").strip(),
                }
                req = {
                    "id": rid,
                    "created_at": _job_now_iso(),
                    "requester_account_id": str((sess or {}).get("account_id") or "").strip(),
                    "requested_by": actor,
                    "permissions": requested_perms,
                    "ttl_seconds": ttl_seconds,
                    "items": items,
                    "scope": scope,
                    "reason": (
                        f"小J 自動請示：執行意圖={it0} 權限不足。"
                        + (f" 建議授權層級={','.join(requested_perms)}" if requested_perms else f" 需要權限 {required_perm}")
                    ),
                    "context": {
                        "source": "agent_chat",
                        "intent": it0,
                        "text": text[:5000],
                        "node": {"id": str(node.get("id") or ""), "name": str(node.get("name") or "")} if isinstance(node, dict) else {},
                        "scope": scope,
                    },
                    "status": "pending",
                }
                p = _authz_request_path("pending", rid)
                _write_json_file(p, req)
                _append_jsonl(
                    AUTHZ_AUDIT_JSONL,
                    {
                        "timestamp": _job_now_iso(),
                        "kind": "authz_request_created_auto",
                        "request_id": rid,
                        "account_id": str((sess or {}).get("account_id") or "").strip(),
                        "permissions": requested_perms,
                        "intent": it0,
                    },
                )
                levels = " / ".join(requested_perms) if requested_perms else required_perm
                items_lines = []
                for it in items[:12]:
                    p0 = str(it.get("permission") or "").strip()
                    t0 = int(it.get("ttl_seconds") or 0)
                    if p0:
                        items_lines.append(f"  - {p0}：{t0} 秒")
                reply = (
                    "此命令需要調整授權：\n"
                    f"- 時間授權：\n" + ("\n".join(items_lines) if items_lines else f"  - {ttl_seconds} 秒") + "\n"
                    f"- 項目授權：{levels}\n"
                    f"- 範圍授權：domain={domain or '（未指定）'} / node_id={scope.get('node_id') or '（未指定）'}\n"
                    f"\n我已替你建立【授權請示單】：{rid}\n"
                    "請管理員核准（可調 TTL/範圍）；核准後你再重試同一句命令即可。"
                )
                _json(
                    self,
                    HTTPStatus.OK,
                    {
                        "ok": True,
                        "executed": False,
                        "reply": reply,
                        "authz_request": {
                            "id": rid,
                            "path": str(p),
                            "required": required_perm,
                            "suggested_permissions": requested_perms,
                            "ttl_seconds": ttl_seconds,
                            "scope": scope,
                            "items": items,
                        },
                        "account_id": account_id,
                        "agent": {"mode": agent_mode, "model": agent_model, "provider": agent_provider},
                    },
                )
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

            outdir = (os.getenv("WUCHANG_WORKSPACE_OUTDIR") or "").strip()
            if not outdir:
                # 若有設定系統資料庫根目錄，預設 artifacts/ 當 workspace 輸出
                d2 = _system_artifacts_dir()
                outdir = str(d2) if d2 else ""
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

