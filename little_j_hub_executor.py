"""
little_j_hub_executor.py

伺服器端「小J 執行器（控制 AI）」：
- 從 Hub inbox 讀取 jobs（機器可讀）
- 只執行 hub.confirmed=true 的工作（由人類端點核准）
- 依政策（workspace_matching.json / accounts_policy.json / consent_receipts.json）做白名單驗證
- 預設只做「預覽」，加 --execute 才會真的跑

重要：這裡的「完整權限」是 *可控的完整權限*（白名單 + 稽核 + 可停用），不是任意指令。
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List

from little_j_policy import PolicyStore, decide_execution


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def _write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def _append_jsonl(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.open("a", encoding="utf-8").write(json.dumps(obj, ensure_ascii=False) + "\n")


def _run(cmd: List[str], timeout: int = 180) -> Dict[str, Any]:
    try:
        cp = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        return {"ok": cp.returncode == 0, "returncode": cp.returncode, "stdout": cp.stdout or "", "stderr": cp.stderr or ""}
    except Exception as e:
        return {"ok": False, "returncode": 3, "stdout": "", "stderr": f"exception: {e}"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="little_j_hub")
    ap.add_argument("--execute", action="store_true", help="真的執行（否則只預覽）")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    inbox = (root / "inbox").resolve()
    archive = (root / "archive").resolve()
    audit = (root / "executor_audit.jsonl").resolve()
    inbox.mkdir(parents=True, exist_ok=True)
    archive.mkdir(parents=True, exist_ok=True)
    store = PolicyStore()

    # 全域緊急停用（kill switch）
    enabled = (os.getenv("WUCHANG_LJ_EXECUTOR_ENABLED") or "0").strip() in ("1", "true", "yes", "y")
    if args.execute and not enabled:
        _append_jsonl(audit, {"timestamp": _now_iso(), "kind": "executor_disabled", "note": "set WUCHANG_LJ_EXECUTOR_ENABLED=1 to allow execution"})
        args.execute = False

    files = sorted(inbox.glob("*.json"), key=lambda p: p.stat().st_mtime)
    for fp in files:
        try:
            job = _read_json(fp)
        except Exception:
            _append_jsonl(audit, {"timestamp": _now_iso(), "kind": "skip_invalid_json", "path": str(fp)})
            continue

        hub = job.get("hub") if isinstance(job.get("hub"), dict) else {}
        confirmed = bool(hub.get("confirmed") is True)
        job_id = str(job.get("id") or fp.stem)
        jtype = str(job.get("type") or "")

        if not confirmed:
            _append_jsonl(audit, {"timestamp": _now_iso(), "kind": "skip_not_confirmed", "job_id": job_id, "type": jtype})
            continue

        decision = decide_execution(store=store, job=job if isinstance(job, dict) else {})
        _append_jsonl(
            audit,
            {
                "timestamp": _now_iso(),
                "kind": "policy_decision",
                "job_id": job_id,
                "type": jtype,
                "decision": decision.__dict__,
            },
        )
        if not decision.ok:
            _append_jsonl(audit, {"timestamp": _now_iso(), "kind": "skip_policy_denied", "job_id": job_id, "reason": decision.reason})
            continue

        # 預設：只列出/預覽（計畫），不執行
        plan = {"job_id": job_id, "type": jtype, "function_id": decision.function_id, "note": "preview"}

        if jtype == "sync_push":
            # 建議策略：伺服器上用 git pull + 伺服器端部署腳本（或 safe_sync_push 的 server 版）
            plan = {
                "job_id": job_id,
                "type": "sync_push",
                "function_id": decision.function_id,
                "suggested": [["git", "pull", "--ff-only"]],
            }
        elif jtype == "odoo_cache_refresh":
            plan = {"job_id": job_id, "type": jtype, "function_id": decision.function_id, "suggested": [["touch", "odoo_cache_refresh_marker"]]}
        elif jtype in ("router_check", "router_restart"):
            plan = {"job_id": job_id, "type": jtype, "function_id": decision.function_id, "suggested": [["python", "router_connection.py"]]}
        elif jtype in ("gcp_check", "gcp_sync", "gcp_apply"):
            plan = {"job_id": job_id, "type": jtype, "function_id": decision.function_id, "suggested": [["gcloud", "auth", "list"]]}

        _append_jsonl(audit, {"timestamp": _now_iso(), "kind": "job_plan", "job_id": job_id, "plan": plan})

        if args.execute:
            # 僅示範：真的跑 git pull（sync_push）
            if jtype == "sync_push":
                started = _now_iso()
                res = _run(["git", "pull", "--ff-only"], timeout=180)
                finished = _now_iso()
                _append_jsonl(audit, {"timestamp": finished, "kind": "job_execute", "job_id": job_id, "result": res})

                # 寫回 job 狀態（供本機稽核複查）
                if isinstance(job, dict):
                    job.setdefault("executor", {})
                    ex = job.get("executor") if isinstance(job.get("executor"), dict) else {}
                    ex.update(
                        {
                            "executed_at": finished,
                            "started_at": started,
                            "ok": bool(res.get("ok") is True),
                            "returncode": int(res.get("returncode") or 0),
                        }
                    )
                    # 避免把 stdout/stderr 全量寫回 job（太大/可能含敏感）；只存摘要雜湊
                    ex["stdout_len"] = len(res.get("stdout") or "")
                    ex["stderr_len"] = len(res.get("stderr") or "")
                    job["executor"] = ex
                    job.setdefault("hub", {})
                    hub = job.get("hub") if isinstance(job.get("hub"), dict) else {}
                    hub["executed_at"] = finished
                    hub["executed_ok"] = bool(res.get("ok") is True)
                    job["hub"] = hub
                    _write_json(fp, job)

                # 成功才歸檔；失敗留在 inbox 供人工處理/重試
                if res.get("ok") is True:
                    dst = (archive / fp.name).resolve()
                    fp.replace(dst)
                    _append_jsonl(audit, {"timestamp": _now_iso(), "kind": "job_archived", "job_id": job_id, "to": str(dst)})
            else:
                # 其他類型先不直接執行（保守）；你可依你的伺服器實際環境把它們接到 systemd/docker/odoo/gcloud/路由器控制腳本
                _append_jsonl(audit, {"timestamp": _now_iso(), "kind": "job_execute_skipped_unimplemented", "job_id": job_id, "type": jtype})

        # archive 策略：
        # - 目前僅在 execute 且成功的 sync_push 會自動歸檔（可供稽核複查）


if __name__ == "__main__":
    main()

