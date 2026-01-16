"""
server_inventory.py

伺服器「機器可讀」資訊回報（非機密）：
- OS / Python / 時間 / 目錄
- 常見部署工具是否存在：git / docker / docker compose / systemctl / nginx / gcloud
- 可選：檢查 Odoo URL 是否可達（只回 status，不回內容）

注意：
- 不回傳環境變數明文（避免洩漏）
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import socket
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.request import Request, urlopen


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _which(cmd: str) -> str:
    p = shutil.which(cmd)
    return p or ""


def _http_head(url: str, timeout: int = 3) -> Dict[str, Any]:
    url = (url or "").strip()
    if not url:
        return {"ok": False, "error": "missing_url"}
    try:
        req = Request(url, method="HEAD")
        with urlopen(req, timeout=timeout) as resp:
            return {"ok": True, "status": int(getattr(resp, "status", 200))}
    except Exception as e:
        return {"ok": False, "error": f"request_failed: {e}"}


def main() -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "ok": True,
        "timestamp": _now_iso(),
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": sys.version.split()[0],
        },
        "paths": {
            "cwd": str(Path.cwd().resolve()),
            "script_dir": str(Path(__file__).resolve().parent),
        },
        "tools": {
            "git": _which("git"),
            "docker": _which("docker"),
            "docker_compose": _which("docker-compose"),
            "systemctl": _which("systemctl"),
            "nginx": _which("nginx"),
            "gcloud": _which("gcloud"),
        },
        "env_presence": {
            "WUCHANG_SYSTEM_DB_DIR": bool(os.getenv("WUCHANG_SYSTEM_DB_DIR")),
            "WUCHANG_ODOO_CACHE_DIR": bool(os.getenv("WUCHANG_ODOO_CACHE_DIR")),
            "WUCHANG_HUB_TOKEN": bool(os.getenv("WUCHANG_HUB_TOKEN")),
            "WUCHANG_LJ_EXECUTOR_ENABLED": bool(os.getenv("WUCHANG_LJ_EXECUTOR_ENABLED")),
        },
    }

    odoo_url = (os.getenv("WUCHANG_ODOO_URL") or "").strip()
    if odoo_url:
        out["odoo"] = {"url": odoo_url, "head": _http_head(odoo_url)}

    return out


if __name__ == "__main__":
    print(json.dumps(main(), ensure_ascii=False, indent=2))

