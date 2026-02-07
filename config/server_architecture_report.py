"""
server_architecture_report.py

伺服器「機器可讀」系統架構回報（偏向容器/服務編排，盡量避免機密與個資）：
- Docker / Docker Compose 存在與版本
- 容器清單（name/image/status/ports 等）
- Compose 專案清單（若可取得）
- 從容器 port mapping 推測對外服務入口（不做 netstat 全盤掃描）

安全/隱私：
- 會對常見使用者家目錄路徑做去識別化（例如 C:\\Users\\<name>\\ → C:\\Users\\<REDACTED>\\）
- 不回傳環境變數明文、不讀取 secrets
"""

from __future__ import annotations

import json
import platform
import re
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _which(cmd: str) -> str:
    return shutil.which(cmd) or ""


def _run(args: List[str], timeout: int = 8) -> Dict[str, Any]:
    try:
        cp = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=max(1, int(timeout)),
            check=False,
        )
        return {
            "ok": True,
            "exit_code": int(cp.returncode),
            "stdout": cp.stdout or "",
            "stderr": cp.stderr or "",
        }
    except Exception as e:
        return {"ok": False, "exit_code": 3, "stdout": "", "stderr": f"exception: {e}"}


def _try_parse_json(s: str) -> Tuple[bool, Any]:
    s = (s or "").strip()
    if not s:
        return False, None
    try:
        return True, json.loads(s)
    except Exception:
        return False, None


def _parse_json_lines(s: str, limit: int = 500) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for line in (s or "").splitlines():
        line = line.strip()
        if not line:
            continue
        ok, obj = _try_parse_json(line)
        if ok and isinstance(obj, dict):
            out.append(obj)
        else:
            out.append({"_raw": line})
        if len(out) >= max(1, min(int(limit), 2000)):
            break
    return out


_RE_WIN_USER = re.compile(r"([A-Za-z]:\\Users\\)([^\\]+)\\", flags=re.IGNORECASE)
_RE_LINUX_HOME = re.compile(r"(/home/)([^/]+)/", flags=re.IGNORECASE)


def _redact_paths(text: str) -> str:
    if not text:
        return text
    text = _RE_WIN_USER.sub(r"\1<REDACTED>\\", text)
    text = _RE_LINUX_HOME.sub(r"\1<REDACTED>/", text)
    return text


def _redact_obj(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): _redact_obj(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_redact_obj(v) for v in obj]
    if isinstance(obj, str):
        return _redact_paths(obj)
    return obj


def _docker_json_format() -> str:
    # docker --format 支援 Go template；這個會輸出 JSON（每行一個物件）
    return "{{json .}}"


def _summarize_ports(port_text: str) -> Dict[str, Any]:
    """
    docker ps 的 Ports 欄位常見格式：
      "0.0.0.0:80->80/tcp, [::]:80->80/tcp"
    這裡只做「對外入口」摘要，不保證完整。
    """
    port_text = (port_text or "").strip()
    if not port_text:
        return {"exposed": False, "host_ports": [], "raw": ""}
    host_ports: List[str] = []
    for chunk in port_text.split(","):
        c = chunk.strip()
        if "->" in c and ":" in c:
            # 取 "x.x.x.x:PORT->" 或 "[::]:PORT->"
            left = c.split("->", 1)[0].strip()
            if ":" in left:
                hp = left.rsplit(":", 1)[-1].strip()
                if hp and hp.isdigit():
                    host_ports.append(hp)
    # 去重但保序
    seen = set()
    host_ports2: List[str] = []
    for p in host_ports:
        if p not in seen:
            seen.add(p)
            host_ports2.append(p)
    return {"exposed": True, "host_ports": host_ports2, "raw": port_text}


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
            "docker": _which("docker"),
            "docker_compose_legacy": _which("docker-compose"),
        },
        "architecture": {
            "containers": [],
            "compose_projects": [],
            "services_guess": [],
        },
        "notes": [],
    }

    docker_path = out["tools"]["docker"]
    if not docker_path:
        out["notes"].append("docker_not_found")
        return _redact_obj(out)

    # docker version / info（若支援）
    ver_run = _run(["docker", "version", "--format", _docker_json_format()], timeout=8)
    ok, ver_obj = _try_parse_json(ver_run.get("stdout", ""))
    out["docker"] = {
        "version": ver_obj if ok else {"_raw": (ver_run.get("stdout") or "").strip(), "stderr": (ver_run.get("stderr") or "").strip()},
    }

    info_run = _run(["docker", "info", "--format", _docker_json_format()], timeout=8)
    ok, info_obj = _try_parse_json(info_run.get("stdout", ""))
    # info 很大，只保留常用欄位（避免回傳過量/過敏感資訊）
    info_keep: Dict[str, Any] = {}
    if ok and isinstance(info_obj, dict):
        for k in (
            "ID",
            "ServerVersion",
            "OperatingSystem",
            "OSType",
            "Architecture",
            "NCPU",
            "MemTotal",
            "DockerRootDir",
            "Driver",
            "CgroupDriver",
            "DefaultAddressPools",
            "Plugins",
            "Swarm",
            "SecurityOptions",
            "Warnings",
        ):
            if k in info_obj:
                info_keep[k] = info_obj.get(k)
    else:
        info_keep = {"_raw": (info_run.get("stdout") or "").strip(), "stderr": (info_run.get("stderr") or "").strip()}
    out["docker"]["info"] = info_keep

    # containers（docker ps）
    ps_run = _run(["docker", "ps", "--no-trunc", "--format", _docker_json_format()], timeout=10)
    ps_items = _parse_json_lines(ps_run.get("stdout", ""), limit=500)
    containers: List[Dict[str, Any]] = []
    for it in ps_items:
        if not isinstance(it, dict):
            continue
        name = str(it.get("Names") or it.get("Name") or "").strip()
        image = str(it.get("Image") or "").strip()
        status = str(it.get("Status") or "").strip()
        ports = str(it.get("Ports") or "").strip()
        cid = str(it.get("ID") or "").strip()
        item = {
            "id": cid[:12] if cid else "",
            "name": name,
            "image": image,
            "status": status,
            "ports": _summarize_ports(ports),
        }
        containers.append(item)
    out["architecture"]["containers"] = containers

    # docker networks / volumes（僅列清單，不做 inspect）
    net_run = _run(["docker", "network", "ls", "--format", _docker_json_format()], timeout=8)
    nets = _parse_json_lines(net_run.get("stdout", ""), limit=200)
    out["docker"]["networks"] = [
        {"id": str(n.get("ID") or "")[:12], "name": str(n.get("Name") or ""), "driver": str(n.get("Driver") or ""), "scope": str(n.get("Scope") or "")}
        for n in nets
        if isinstance(n, dict)
    ]

    vol_run = _run(["docker", "volume", "ls", "--format", _docker_json_format()], timeout=8)
    vols = _parse_json_lines(vol_run.get("stdout", ""), limit=300)
    out["docker"]["volumes"] = [
        {"driver": str(v.get("Driver") or ""), "name": str(v.get("Name") or "")}
        for v in vols
        if isinstance(v, dict)
    ]

    # compose 專案（優先 docker compose；其次 docker-compose）
    compose_projects: List[Dict[str, Any]] = []
    compose_mode = ""
    # docker compose ls --format json
    comp_run = _run(["docker", "compose", "ls", "--format", "json"], timeout=10)
    ok, comp_obj = _try_parse_json(comp_run.get("stdout", ""))
    if comp_run.get("ok") and comp_run.get("exit_code") == 0 and ok and isinstance(comp_obj, list):
        compose_mode = "docker_compose_plugin"
        for p in comp_obj[:200]:
            if isinstance(p, dict):
                compose_projects.append(
                    {
                        "name": str(p.get("Name") or ""),
                        "status": str(p.get("Status") or ""),
                        "config_files": str(p.get("ConfigFiles") or ""),
                    }
                )
    else:
        legacy = out["tools"]["docker_compose_legacy"]
        if legacy:
            # docker-compose ls 很可能沒有 json 格式，退回純文字摘要
            comp2 = _run(["docker-compose", "ls"], timeout=10)
            compose_mode = "docker_compose_legacy"
            if comp2.get("exit_code") == 0:
                compose_projects.append({"_raw": (comp2.get("stdout") or "").strip()[:12000]})
            else:
                compose_projects.append({"_error": (comp2.get("stderr") or "").strip()[:12000]})
        else:
            compose_mode = "not_available"
    out["architecture"]["compose_projects"] = compose_projects
    out["docker"]["compose_mode"] = compose_mode

    # services_guess：用 host_ports 做最小推測（不等於真正對外暴露）
    guesses: List[Dict[str, Any]] = []
    for c in containers:
        ports = (c.get("ports") or {}) if isinstance(c.get("ports"), dict) else {}
        for hp in ports.get("host_ports") or []:
            guesses.append({"host_port": hp, "container": c.get("name") or "", "image": c.get("image") or ""})
    # 去重
    seen2 = set()
    uniq: List[Dict[str, Any]] = []
    for g in guesses:
        key = (g.get("host_port") or "", g.get("container") or "")
        if key in seen2:
            continue
        seen2.add(key)
        uniq.append(g)
    out["architecture"]["services_guess"] = uniq[:500]

    # 特別標註 Odoo（若可從容器名字猜出）
    odoo_like = [c for c in containers if "odoo" in str(c.get("name") or "").lower() or "odoo" in str(c.get("image") or "").lower()]
    if odoo_like:
        out["architecture"]["odoo_containers"] = odoo_like

    return _redact_obj(out)


if __name__ == "__main__":
    print(json.dumps(main(), ensure_ascii=False, indent=2))

