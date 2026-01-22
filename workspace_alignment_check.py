"""
workspace_alignment_check.py

用來確認「Google Workspace（Drive 同步）」環境是否與五常系統功能精準對齊。

原則：
- 只做檢查與建議，不會修改任何檔案
- 輸出 JSON，便於 UI 顯示/稽核
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


BASE_DIR = Path(__file__).resolve().parent


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _env(name: str) -> str:
    return (os.getenv(name) or "").strip()


def _p(s: str) -> Optional[Path]:
    if not s:
        return None
    return Path(s).expanduser().resolve()


def _exists(p: Optional[Path]) -> bool:
    try:
        return bool(p and p.exists())
    except Exception:
        return False


def _is_under_repo(p: Optional[Path]) -> bool:
    if not p:
        return False
    try:
        return BASE_DIR in p.parents or p == BASE_DIR
    except Exception:
        return False


def main() -> Dict[str, Any]:
    out: Dict[str, Any] = {"ok": True, "timestamp": _now_iso(), "checks": [], "warnings": [], "missing": []}

    system_db_dir = _p(_env("WUCHANG_SYSTEM_DB_DIR"))
    workspace_outdir = _p(_env("WUCHANG_WORKSPACE_OUTDIR")) or (system_db_dir / "artifacts" if system_db_dir else None)
    pii_outdir = _p(_env("WUCHANG_PII_OUTDIR")) or (system_db_dir / "vault" if system_db_dir else None) or workspace_outdir
    exchange_dir = _p(_env("WUCHANG_WORKSPACE_EXCHANGE_DIR")) or (system_db_dir / "exchange" if system_db_dir else None) or workspace_outdir
    config_dir = (system_db_dir / "config") if system_db_dir else None
    accounts_path = _p(_env("WUCHANG_ACCOUNTS_PATH")) or (config_dir / "accounts_policy.json" if config_dir else None) or (pii_outdir / "accounts_policy.json" if pii_outdir else None)
    matching_path = _p(_env("WUCHANG_WORKSPACE_MATCHING_PATH")) or (config_dir / "workspace_matching.json" if config_dir else None) or (workspace_outdir / "workspace_matching.json" if workspace_outdir else None)
    odoo_cache_dir = _p(_env("WUCHANG_ODOO_CACHE_DIR"))

    def add_check(name: str, ok: bool, detail: Dict[str, Any]) -> None:
        out["checks"].append({"name": name, "ok": ok, **detail})
        if not ok:
            out["ok"] = False

    # 基本資料夾
    add_check("system_db_dir", _exists(system_db_dir), {"path": str(system_db_dir or ""), "env": "WUCHANG_SYSTEM_DB_DIR (recommended)"})
    add_check("workspace_outdir", _exists(workspace_outdir), {"path": str(workspace_outdir or ""), "env": "WUCHANG_WORKSPACE_OUTDIR"})
    add_check("pii_outdir", _exists(pii_outdir), {"path": str(pii_outdir or ""), "env": "WUCHANG_PII_OUTDIR (optional)"})
    add_check("exchange_dir", _exists(exchange_dir), {"path": str(exchange_dir or ""), "env": "WUCHANG_WORKSPACE_EXCHANGE_DIR (optional)"})
    add_check("odoo_cache_dir", _exists(odoo_cache_dir) or True, {"path": str(odoo_cache_dir or ""), "env": "WUCHANG_ODOO_CACHE_DIR (optional)", "note": "Odoo 快取區（非權威資料）"})

    # 建議不要落在 repo 內
    for nm, pth in (("system_db_dir", system_db_dir), ("workspace_outdir", workspace_outdir), ("pii_outdir", pii_outdir), ("exchange_dir", exchange_dir), ("odoo_cache_dir", odoo_cache_dir)):
        if _is_under_repo(pth):
            out["warnings"].append(f"{nm} 位於 repo 內（不建議）：{pth}")

    # 設定檔
    add_check("accounts_policy", _exists(accounts_path), {"path": str(accounts_path or ""), "hint": "請把 accounts_policy.json 放到 Drive 同步夾，或用 WUCHANG_ACCOUNTS_PATH 指定"})
    add_check("workspace_matching", _exists(matching_path), {"path": str(matching_path or ""), "hint": "請把 workspace_matching.json 放到 Drive 同步夾，或用 WUCHANG_WORKSPACE_MATCHING_PATH 指定"})

    # Vault 檔（可識別/不可識別）
    pii_ident = (pii_outdir / "pii_contacts.json") if pii_outdir else None
    pii_non = (pii_outdir / "pii_contacts_non_identifiable.json") if pii_outdir else None
    consent = (pii_outdir / "consent_receipts.json") if pii_outdir else None
    acct_nonid = (pii_outdir / "account_profiles_non_identifiable.json") if pii_outdir else None
    vouchers = (pii_outdir / "commerce" / "vouchers.json") if pii_outdir else None

    add_check("pii_contacts_identifiable", _exists(pii_ident) or True, {"path": str(pii_ident or ""), "note": "可選：第一次存才會生成"})
    add_check("pii_contacts_non_identifiable", _exists(pii_non) or True, {"path": str(pii_non or ""), "note": "可選：第一次存才會生成"})
    add_check("consent_receipts", _exists(consent) or True, {"path": str(consent or ""), "note": "可選：第一次同意才會生成"})
    add_check("account_profiles_non_identifiable", _exists(acct_nonid) or True, {"path": str(acct_nonid or ""), "note": "可選：第一次存才會生成"})
    add_check("vouchers_store", _exists(vouchers) or True, {"path": str(vouchers or ""), "note": "可選：第一次建立票券才會生成"})

    # Exchange 交換區（device）
    device_tasks = (exchange_dir / "device_tasks") if exchange_dir else None
    device_results = (exchange_dir / "device_results") if exchange_dir else None
    add_check("device_tasks_dir", _exists(device_tasks) or True, {"path": str(device_tasks or ""), "note": "可選：第一次建立設備任務才會生成"})
    add_check("device_results_dir", _exists(device_results) or True, {"path": str(device_results or ""), "note": "可選：第一次設備回覆才會生成"})

    # 建議對齊指令（PowerShell）
    out["suggested_powershell"] = [
        'setx WUCHANG_SYSTEM_DB_DIR "C:\\Users\\<你>\\Google Drive\\五常_中控"',
        'setx WUCHANG_WORKSPACE_OUTDIR "C:\\Users\\<你>\\Google Drive\\五常_中控\\artifacts"',
        'setx WUCHANG_WORKSPACE_EXCHANGE_DIR "C:\\Users\\<你>\\Google Drive\\五常_中控\\exchange"',
        'setx WUCHANG_PII_OUTDIR "C:\\Users\\<你>\\Google Drive\\五常_中控\\vault"',
        'setx WUCHANG_ACCOUNTS_PATH "C:\\Users\\<你>\\Google Drive\\五常_中控\\config\\accounts_policy.json"',
        'setx WUCHANG_WORKSPACE_MATCHING_PATH "C:\\Users\\<你>\\Google Drive\\五常_中控\\config\\workspace_matching.json"',
        'setx WUCHANG_ODOO_CACHE_DIR "D:\\odoo_cache\\wuchang"  # 可選：快取區',
    ]

    return out


if __name__ == "__main__":
    print(json.dumps(main(), ensure_ascii=False, indent=2))

