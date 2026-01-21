"""
little_j_policy.py

小J 控制平面：把「功能（function_id）」與「權限/風險/同意/確認」統一管理。

用途：
- 供伺服器端 executor 使用：驗證 job 是否可執行、是否需要同意/確認
- 資料來源（建議）：WUCHANG_SYSTEM_DB_DIR 下的 config/vault

注意：
- 本模組不處理任何秘密（只讀設定、回傳決策）
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _now_epoch() -> int:
    return int(time.time())


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_get_list(d: Dict[str, Any], key: str) -> List[Any]:
    v = d.get(key)
    return v if isinstance(v, list) else []


def _safe_get_dict(d: Dict[str, Any], key: str) -> Dict[str, Any]:
    v = d.get(key)
    return v if isinstance(v, dict) else {}


@dataclass
class PolicyDecision:
    ok: bool
    reason: str
    function_id: str = ""
    risk_level: str = ""
    requires_confirm: bool = False
    requires_consent_scope: str = ""


class PolicyStore:
    def __init__(self) -> None:
        self.system_db_dir = Path(os.getenv("WUCHANG_SYSTEM_DB_DIR") or "").expanduser().resolve() if os.getenv("WUCHANG_SYSTEM_DB_DIR") else None

    def _config_dir(self) -> Optional[Path]:
        return (self.system_db_dir / "config").resolve() if self.system_db_dir else None

    def _vault_dir(self) -> Optional[Path]:
        return (self.system_db_dir / "vault").resolve() if self.system_db_dir else None

    def accounts_policy_path(self) -> Optional[Path]:
        p = (os.getenv("WUCHANG_ACCOUNTS_PATH") or "").strip()
        if p:
            return Path(p).expanduser().resolve()
        cfg = self._config_dir()
        return (cfg / "accounts_policy.json").resolve() if cfg else None

    def workspace_matching_path(self) -> Optional[Path]:
        p = (os.getenv("WUCHANG_WORKSPACE_MATCHING_PATH") or "").strip()
        if p:
            return Path(p).expanduser().resolve()
        cfg = self._config_dir()
        return (cfg / "workspace_matching.json").resolve() if cfg else None

    def consent_path(self) -> Optional[Path]:
        vault = self._vault_dir()
        return (vault / "consent_receipts.json").resolve() if vault else None

    def load_accounts(self) -> Dict[str, Any]:
        p = self.accounts_policy_path()
        if not p or not p.exists():
            return {"version": 1, "accounts": []}
        try:
            return _read_json(p)
        except Exception:
            return {"version": 1, "accounts": []}

    def load_matching(self) -> Dict[str, Any]:
        p = self.workspace_matching_path()
        if not p or not p.exists():
            return {"version": 1, "system_functions": [], "node_ai_agents": []}
        try:
            return _read_json(p)
        except Exception:
            return {"version": 1, "system_functions": [], "node_ai_agents": []}

    def load_consent(self) -> Dict[str, Any]:
        p = self.consent_path()
        if not p or not p.exists():
            return {}
        try:
            v = _read_json(p)
            return v if isinstance(v, dict) else {}
        except Exception:
            return {}

    def account_permissions(self, account_id: str) -> List[str]:
        pol = self.load_accounts()
        for a in _safe_get_list(pol, "accounts"):
            if isinstance(a, dict) and str(a.get("account_id") or "").strip() == str(account_id or "").strip():
                perms = a.get("permissions")
                return [str(x) for x in perms] if isinstance(perms, list) else []
        return []

    def function_catalog(self) -> Dict[str, Dict[str, Any]]:
        m = self.load_matching()
        cat: Dict[str, Dict[str, Any]] = {}
        for f in _safe_get_list(m, "system_functions"):
            if not isinstance(f, dict):
                continue
            fid = str(f.get("function_id") or "").strip()
            if fid:
                cat[fid] = f
        return cat

    def node_allowed_functions(self, node_id: str) -> List[str]:
        m = self.load_matching()
        for a in _safe_get_list(m, "node_ai_agents"):
            if not isinstance(a, dict):
                continue
            if str(a.get("node_id") or "").strip() == str(node_id or "").strip():
                return [str(x) for x in (a.get("allowed_function_ids") or []) if str(x).strip()]
        return []

    def consent_effective(self, account_id: str, scope: str) -> bool:
        if not scope:
            return True
        vault = self.load_consent()
        rec = vault.get(str(account_id or "").strip())
        if not isinstance(rec, dict):
            return False
        if rec.get("revoked_at"):
            return False
        exp = rec.get("expires_at_epoch")
        try:
            if exp and _now_epoch() > int(exp):
                return False
        except Exception:
            return False
        if str(rec.get("scope") or "") != scope:
            return False
        return rec.get("granted") is True


def job_type_to_function_id(job_type: str) -> str:
    t = str(job_type or "").strip().lower()
    # 對齊你目前系統常見 job types
    if t == "sync_push":
        return "job_create_sync_push"
    if t == "device_request":
        return "device_request"
    if t in ("odoo_cache_refresh", "odoo_cache_rebuild"):
        return "odoo_cache_refresh"
    if t in ("router_check", "router_restart", "router_ddns_check"):
        return "router_admin"
    if t in ("gcp_check", "gcp_sync", "gcp_apply"):
        return "gcp_admin"
    if t in ("voucher_upsert", "voucher_redeem"):
        return "voucher_discount_code"
    return t  # 預設：用 type 當 function_id


def decide_execution(*, store: PolicyStore, job: Dict[str, Any]) -> PolicyDecision:
    job_type = str(job.get("type") or "").strip()
    fid = job_type_to_function_id(job_type)
    requester = str(job.get("requester_account_id") or "").strip()
    node = job.get("node") if isinstance(job.get("node"), dict) else {}
    node_id = str(node.get("id") or "").strip()

    # 必須有 requester（完整控管要可追溯）
    if not requester:
        return PolicyDecision(ok=False, reason="missing_requester_account_id", function_id=fid)

    perms = store.account_permissions(requester)
    if not perms:
        return PolicyDecision(ok=False, reason="unknown_account_or_no_permissions", function_id=fid)
    if "admin_all" in perms:
        # 超管仍走白名單/同意/確認
        pass

    # function catalog（白名單）
    cat = store.function_catalog()
    f = cat.get(fid)
    if not f:
        return PolicyDecision(ok=False, reason="function_not_in_catalog", function_id=fid)

    risk = str(f.get("risk_level") or "").strip().lower() or "unknown"
    consent_scope = str(f.get("requires_consent_scope_optional") or "").strip()

    # 節點限制：若有 node_id，必須在 node_ai_agents.allowed_function_ids 內
    if node_id:
        allowed = store.node_allowed_functions(node_id)
        if allowed and fid not in allowed:
            return PolicyDecision(ok=False, reason="function_not_allowed_for_node", function_id=fid, risk_level=risk)

    # 權限映射（最小可行）：用 function_id 對到 permissions（可在 matching 內擴充）
    # 這裡先用慣例：<prefix>_admin / voucher_* / job_create 等
    if fid in ("job_create_sync_push", "sync_push"):
        if "job_create" not in perms and "admin_all" not in perms:
            return PolicyDecision(ok=False, reason="missing_permission_job_create", function_id=fid, risk_level=risk)
    if fid.startswith("voucher_"):
        need = "voucher_manage" if job_type == "voucher_upsert" else "voucher_redeem"
        if need not in perms and "admin_all" not in perms:
            return PolicyDecision(ok=False, reason=f"missing_permission_{need}", function_id=fid, risk_level=risk)
    if fid == "gcp_admin":
        if "gcp_admin" not in perms and "admin_all" not in perms:
            return PolicyDecision(ok=False, reason="missing_permission_gcp_admin", function_id=fid, risk_level=risk)
    if fid == "router_admin":
        if "router_admin" not in perms and "admin_all" not in perms:
            return PolicyDecision(ok=False, reason="missing_permission_router_admin", function_id=fid, risk_level=risk)
    if fid == "odoo_cache_refresh":
        if "odoo_admin" not in perms and "admin_all" not in perms:
            return PolicyDecision(ok=False, reason="missing_permission_odoo_admin", function_id=fid, risk_level=risk)

    # 同意
    if consent_scope and not store.consent_effective(requester, consent_scope):
        return PolicyDecision(ok=False, reason="consent_required", function_id=fid, risk_level=risk, requires_consent_scope=consent_scope)

    # 是否需要確認（高風險/或 function 設定）
    requires_confirm = True if risk in ("high", "critical") else False
    return PolicyDecision(ok=True, reason="allowed", function_id=fid, risk_level=risk, requires_confirm=requires_confirm, requires_consent_scope=consent_scope)

