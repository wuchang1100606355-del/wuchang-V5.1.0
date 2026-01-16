"""
little_j_hub_server.py

伺服器端「小J 匯集區（Hub）」：
- 作為機器可讀的專用交流區（inbox/outbox/archive）
- 接收本機送來的 jobs（命令單）與設備回覆摘要
- 不直接自動執行高風險動作（執行交給 little_j_hub_executor.py，且需 confirmed=true）

安全：
- 使用共享 token（Header: X-LittleJ-Token）做最小驗證
- 記錄稽核（JSONL），避免寫入秘密/個資明文

啟動（伺服器）：
  export WUCHANG_HUB_TOKEN="...長字串..."
  python little_j_hub_server.py --bind 127.0.0.1 --port 8799 --root ./little_j_hub
"""

from __future__ import annotations

import argparse
import json
import os
import time
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _json(handler: BaseHTTPRequestHandler, status: int, payload: Dict[str, Any]) -> None:
    raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)


def _read_json(handler: BaseHTTPRequestHandler) -> Dict[str, Any]:
    try:
        length = int(handler.headers.get("Content-Length") or "0")
    except Exception:
        length = 0
    body = handler.rfile.read(length) if length > 0 else b""
    if not body:
        return {}
    return json.loads(body.decode("utf-8", errors="replace"))


def _append_jsonl(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.open("a", encoding="utf-8").write(json.dumps(obj, ensure_ascii=False) + "\n")


def _safe_id(s: str) -> str:
    s = (s or "").strip()
    s = "".join(ch for ch in s if ch.isalnum() or ch in ("-", "_"))
    return s[:64]


class Hub:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.inbox = (self.root / "inbox").resolve()
        self.archive = (self.root / "archive").resolve()
        self.audit = (self.root / "hub_audit.jsonl").resolve()
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.archive.mkdir(parents=True, exist_ok=True)

    def job_path(self, state: str, job_id: str) -> Path:
        base = self.inbox if state == "inbox" else self.archive
        p = (base / f"{job_id}.json").resolve()
        if self.root not in p.parents and p != self.root:
            raise ValueError("invalid_path")
        return p

    def list_jobs(self, state: str = "inbox", limit: int = 50) -> List[Dict[str, Any]]:
        base = self.inbox if state == "inbox" else self.archive
        files = sorted(base.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        out: List[Dict[str, Any]] = []
        for fp in files[: max(1, min(int(limit), 500))]:
            try:
                out.append(json.loads(fp.read_text(encoding="utf-8")))
            except Exception:
                out.append({"id": fp.stem, "error": "invalid_json", "_path": str(fp)})
        return out

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        for st in ("inbox", "archive"):
            p = self.job_path(st, job_id)
            if p.exists():
                try:
                    return json.loads(p.read_text(encoding="utf-8"))
                except Exception:
                    return {"id": job_id, "error": "invalid_json", "_path": str(p)}
        return None

    def write_job(self, job: Dict[str, Any]) -> Path:
        job_id = _safe_id(str(job.get("id") or "")) or uuid.uuid4().hex[:12]
        job["id"] = job_id
        p = self.job_path("inbox", job_id)
        p.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")
        return p

    def move_to_archive(self, job_id: str) -> Path:
        src = self.job_path("inbox", job_id)
        if not src.exists():
            raise FileNotFoundError("not_found")
        dst = self.job_path("archive", job_id)
        src.replace(dst)
        return dst


class Handler(BaseHTTPRequestHandler):
    hub: Hub

    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def _auth_ok(self) -> bool:
        token = (os.getenv("WUCHANG_HUB_TOKEN") or "").strip()
        if not token:
            # 若伺服器端未設定 token，就不允許任何寫入（只允許 /health）
            return False
        got = str(self.headers.get("X-LittleJ-Token") or "").strip()
        return got == token

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            _json(self, HTTPStatus.OK, {"ok": True, "time": _now_iso()})
            return

        if not self._auth_ok():
            _json(self, HTTPStatus.FORBIDDEN, {"ok": False, "error": "forbidden"})
            return

        if parsed.path == "/api/hub/server/info":
            # 伺服器回報非機密資訊，供本機開發者 UI/小J 對齊環境與控制腳本
            try:
                # 直接執行同目錄腳本，避免額外依賴
                import subprocess
                import sys

                cp = subprocess.run(
                    [sys.executable, str(Path(__file__).resolve().parent / "server_inventory.py")],
                    capture_output=True,
                    text=True,
                    timeout=8,
                    check=False,
                )
                try:
                    info = json.loads(cp.stdout or "{}")
                except Exception:
                    info = {"ok": False, "error": "invalid_inventory_output", "stdout": cp.stdout, "stderr": cp.stderr}
            except Exception as e:
                info = {"ok": False, "error": f"inventory_failed: {e}"}
            _json(self, HTTPStatus.OK, {"ok": True, "info": info})
            return

        if parsed.path == "/api/hub/server/architecture":
            # 伺服器回報「系統架構」（偏容器/編排/port 映射），供本機先理解再設計
            try:
                import subprocess
                import sys

                cp = subprocess.run(
                    [sys.executable, str(Path(__file__).resolve().parent / "server_architecture_report.py")],
                    capture_output=True,
                    text=True,
                    timeout=12,
                    check=False,
                )
                try:
                    arch = json.loads(cp.stdout or "{}")
                except Exception:
                    arch = {"ok": False, "error": "invalid_architecture_output", "stdout": cp.stdout, "stderr": cp.stderr}
            except Exception as e:
                arch = {"ok": False, "error": f"architecture_failed: {e}"}
            _json(self, HTTPStatus.OK, {"ok": True, "architecture": arch})
            return

        if parsed.path == "/api/hub/jobs/list":
            qs = parse_qs(parsed.query)
            state = (qs.get("state") or ["inbox"])[0].strip()
            limit = int((qs.get("limit") or ["50"])[0])
            if state not in ("inbox", "archive"):
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid_state"})
                return
            items = self.hub.list_jobs(state=state, limit=limit)
            _json(self, HTTPStatus.OK, {"ok": True, "state": state, "items": items})
            return

        if parsed.path == "/api/hub/jobs/get":
            qs = parse_qs(parsed.query)
            job_id = (qs.get("id") or [""])[0].strip()
            if not job_id:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_id"})
                return
            job = self.hub.get_job(job_id)
            if not job:
                _json(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})
                return
            _json(self, HTTPStatus.OK, {"ok": True, "job": job})
            return

        _json(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if not self._auth_ok():
            _json(self, HTTPStatus.FORBIDDEN, {"ok": False, "error": "forbidden"})
            return

        if parsed.path == "/api/hub/server/reports/generate":
            # 伺服器端生成「機器可讀回報檔」到指定位置（預設安全目錄）
            data = _read_json(self)
            actor = _safe_id(str(data.get("actor") or "ops"))
            ts = time.strftime("%Y%m%d_%H%M%S")

            # 目標路徑策略（偏保守且可預期）：
            # 1) 若設定 WUCHANG_SYSTEM_DB_DIR：寫入 <system_db>\exchange\server_reports\
            # 2) 否則若為 Windows：寫入 C:\wuchang_system_db\exchange\server_reports\
            # 3) 否則：寫入 <hub_root>\exchange\server_reports\
            base = (os.getenv("WUCHANG_SYSTEM_DB_DIR") or "").strip()
            if base:
                out_dir = (Path(base).expanduser().resolve() / "exchange" / "server_reports").resolve()
            else:
                sys_drive = (os.getenv("SystemDrive") or "").strip()
                is_windows = (os.name == "nt") or (sys_drive.upper().startswith("C:"))
                if is_windows:
                    drive = sys_drive if sys_drive else "C:"
                    out_dir = (Path(f"{drive}/wuchang_system_db") / "exchange" / "server_reports").resolve()
                else:
                    out_dir = (self.hub.root / "exchange" / "server_reports").resolve()
            out_dir.mkdir(parents=True, exist_ok=True)

            try:
                import subprocess
                import sys

                script_dir = Path(__file__).resolve().parent

                # 1) inventory
                cp1 = subprocess.run(
                    [sys.executable, str(script_dir / "server_inventory.py")],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                )
                try:
                    inv = json.loads(cp1.stdout or "{}")
                except Exception:
                    inv = {"ok": False, "error": "invalid_inventory_output", "stdout": cp1.stdout, "stderr": cp1.stderr}

                # 2) architecture
                cp2 = subprocess.run(
                    [sys.executable, str(script_dir / "server_architecture_report.py")],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    check=False,
                )
                try:
                    arch = json.loads(cp2.stdout or "{}")
                except Exception:
                    arch = {"ok": False, "error": "invalid_architecture_output", "stdout": cp2.stdout, "stderr": cp2.stderr}

                inv_path = (out_dir / f"server_inventory__{ts}.json").resolve()
                arch_path = (out_dir / f"server_architecture__{ts}.json").resolve()
                index_path = (out_dir / "server_reports__latest.json").resolve()

                inv_path.write_text(json.dumps(inv, ensure_ascii=False, indent=2), encoding="utf-8")
                arch_path.write_text(json.dumps(arch, ensure_ascii=False, indent=2), encoding="utf-8")
                index = {
                    "ok": True,
                    "generated_at": _now_iso(),
                    "actor": actor,
                    "paths": {
                        "inventory": str(inv_path),
                        "architecture": str(arch_path),
                    },
                }
                index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

                _append_jsonl(
                    self.hub.audit,
                    {
                        "timestamp": _now_iso(),
                        "kind": "server_reports_generated",
                        "actor": actor,
                        "out_dir": str(out_dir),
                        "inventory_path": str(inv_path),
                        "architecture_path": str(arch_path),
                    },
                )

                _json(
                    self,
                    HTTPStatus.OK,
                    {
                        "ok": True,
                        "out_dir": str(out_dir),
                        "inventory_path": str(inv_path),
                        "architecture_path": str(arch_path),
                        "index_path": str(index_path),
                        "inventory_ok": bool(inv.get("ok") is True),
                        "architecture_ok": bool(arch.get("ok") is True),
                    },
                )
                return
            except Exception as e:
                _append_jsonl(self.hub.audit, {"timestamp": _now_iso(), "kind": "server_reports_generate_failed", "actor": actor, "error": str(e)})
                _json(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error": f"server_reports_generate_failed: {e}"})
                return

        if parsed.path == "/api/hub/jobs/submit":
            data = _read_json(self)
            job = data.get("job") if isinstance(data.get("job"), dict) else None
            if not job:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_job"})
                return
            # 伺服器端強制加入接收資訊（不信任外部）
            job.setdefault("hub", {})
            job["hub"].update({"received_at": _now_iso(), "state": "inbox", "confirmed": False})
            p = self.hub.write_job(job)
            _append_jsonl(self.hub.audit, {"timestamp": _now_iso(), "kind": "job_received", "job_id": job.get("id"), "path": str(p)})
            _json(self, HTTPStatus.OK, {"ok": True, "job_id": job.get("id"), "path": str(p)})
            return

        if parsed.path == "/api/hub/jobs/confirm":
            data = _read_json(self)
            job_id = _safe_id(str(data.get("id") or ""))
            actor = _safe_id(str(data.get("actor") or "ops"))
            if not job_id:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_id"})
                return
            job = self.hub.get_job(job_id)
            if not isinstance(job, dict) or job.get("error"):
                _json(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})
                return
            # 只允許確認 inbox 內的工作
            p = self.hub.job_path("inbox", job_id)
            if not p.exists():
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "not_in_inbox"})
                return
            job.setdefault("hub", {})
            job["hub"]["confirmed"] = True
            job["hub"]["confirmed_at"] = _now_iso()
            job["hub"]["confirmed_by"] = actor
            p.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")
            _append_jsonl(self.hub.audit, {"timestamp": _now_iso(), "kind": "job_confirmed", "job_id": job_id, "actor": actor})
            _json(self, HTTPStatus.OK, {"ok": True, "id": job_id, "confirmed": True})
            return

        if parsed.path == "/api/hub/jobs/archive":
            data = _read_json(self)
            job_id = _safe_id(str(data.get("id") or ""))
            actor = _safe_id(str(data.get("actor") or "ops"))
            if not job_id:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_id"})
                return
            try:
                dst = self.hub.move_to_archive(job_id)
            except FileNotFoundError:
                _json(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})
                return
            _append_jsonl(self.hub.audit, {"timestamp": _now_iso(), "kind": "job_archived", "job_id": job_id, "actor": actor, "path": str(dst)})
            _json(self, HTTPStatus.OK, {"ok": True, "id": job_id, "to": "archive"})
            return

        _json(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bind", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8799)
    ap.add_argument("--root", default="little_j_hub")
    args = ap.parse_args()

    hub = Hub(Path(args.root))
    Handler.hub = hub
    httpd = ThreadingHTTPServer((str(args.bind), int(args.port)), Handler)
    print(f"[ok] little_j hub: http://{args.bind}:{args.port} (root={hub.root})")
    httpd.serve_forever()


if __name__ == "__main__":
    main()

