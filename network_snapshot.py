"""
network_snapshot.py

本機網路快照（可留痕、可回滾）：
- 取得本機網路介面與預設閘道（Windows 會盡量用 PowerShell Get-NetIPConfiguration）
- 解析/查詢 DNS（socket / nslookup）
- 檢查 hosts 是否覆寫 wuchang.life 相關網域
- （可選）對伺服器 health URL 做健康檢查（僅觀測，不做任何變更）

用法：
  python network_snapshot.py --health-url https://wuchang.life/health
  python network_snapshot.py --domains wuchang.life www.wuchang.life
  python network_snapshot.py --out network_snapshot.json
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import socket
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

try:
    from risk_gate import check_server_health, now_iso
except Exception:
    check_server_health = None  # type: ignore

    def now_iso() -> str:  # type: ignore
        return time.strftime("%Y-%m-%dT%H:%M:%S%z")


@dataclass
class CmdResult:
    ok: bool
    cmd: List[str]
    exit_code: int
    stdout: str
    stderr: str


def _run(cmd: List[str], timeout_seconds: int = 8) -> CmdResult:
    try:
        cp = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        return CmdResult(
            ok=(cp.returncode == 0),
            cmd=cmd,
            exit_code=cp.returncode,
            stdout=cp.stdout or "",
            stderr=cp.stderr or "",
        )
    except Exception as e:
        return CmdResult(ok=False, cmd=cmd, exit_code=3, stdout="", stderr=f"exception: {e}")


def _read_hosts_overrides(domains: List[str]) -> Dict[str, Any]:
    """
    只回報指定 domains 是否出現在 hosts 中（避免把整個 hosts 全吐出來）。
    """
    domains = [d.strip().lower().rstrip(".") for d in domains if d.strip()]
    out: Dict[str, Any] = {"path": None, "matches": []}
    if not domains:
        return out

    candidates = []
    if sys.platform == "win32":
        candidates.append(Path(r"C:\Windows\System32\drivers\etc\hosts"))
    # 其他平台
    candidates.append(Path("/etc/hosts"))

    hosts_path = next((p for p in candidates if p.exists()), None)
    out["path"] = str(hosts_path) if hosts_path else None
    if not hosts_path:
        return out

    text = hosts_path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        # 常見格式：<ip> <host1> <host2>...
        parts = re.split(r"\s+", s)
        if len(parts) < 2:
            continue
        ip = parts[0]
        hosts = [h.strip().lower().rstrip(".") for h in parts[1:] if h.strip()]
        for d in domains:
            if d in hosts:
                out["matches"].append({"domain": d, "ip": ip})
    return out


def _socket_resolve(domain: str) -> Dict[str, Any]:
    domain = domain.strip().rstrip(".")
    out: Dict[str, Any] = {"domain": domain, "ok": False, "addrs": [], "error": None}
    try:
        infos = socket.getaddrinfo(domain, None)
        addrs = sorted({i[4][0] for i in infos if i and i[4]})
        out["addrs"] = addrs
        out["ok"] = bool(addrs)
        return out
    except Exception as e:
        out["error"] = str(e)
        return out


def _nslookup(domain: str) -> Dict[str, Any]:
    # Windows/Unix 都可用 nslookup（若環境缺少，會被記錄為失敗）
    res = _run(["nslookup", domain], timeout_seconds=8)
    return {"domain": domain, "ok": res.ok, "exit_code": res.exit_code, "stdout": res.stdout, "stderr": res.stderr}


def _get_netipconfig_json() -> Optional[Any]:
    if sys.platform != "win32":
        return None
    ps = (
        "Get-NetIPConfiguration | "
        "Select-Object InterfaceAlias,InterfaceDescription,IPv4Address,IPv4DefaultGateway,DnsServer | "
        "ConvertTo-Json -Depth 6"
    )
    res = _run(["powershell", "-NoProfile", "-Command", ps], timeout_seconds=10)
    if not res.ok or not res.stdout.strip():
        return None
    try:
        return json.loads(res.stdout)
    except Exception:
        return None


def _extract_default_gateway(netip: Any) -> Optional[str]:
    """
    從 Get-NetIPConfiguration JSON 抽 IPv4DefaultGateway.NextHop。
    """
    if not netip:
        return None
    items = netip if isinstance(netip, list) else [netip]
    for it in items:
        gw = it.get("IPv4DefaultGateway") if isinstance(it, dict) else None
        if isinstance(gw, dict):
            hop = (gw.get("NextHop") or "").strip()
            if hop:
                return hop
    return None


def _probe_router_http(gateway_ip: Optional[str]) -> Dict[str, Any]:
    """
    只做「可達性」探測，不嘗試登入、不送變更。
    """
    out: Dict[str, Any] = {"gateway": gateway_ip, "probes": []}
    if not gateway_ip:
        return out

    # 常見路由器管理入口（保守：只做 GET /）
    targets: List[Tuple[str, int]] = [
        ("http", 80),
        ("https", 443),
        ("https", 8443),
        ("http", 8080),
    ]
    for scheme, port in targets:
        url = f"{scheme}://{gateway_ip}:{port}/"
        try:
            # 用 curl 會比較好，但不保證存在；這裡用 powershell 的 Invoke-WebRequest 也不保證。
            # 保險起見只做 TCP 探測：Test-NetConnection (Windows)；非 Windows 則跳過。
            if sys.platform == "win32":
                ps = f"Test-NetConnection -ComputerName {gateway_ip} -Port {port} | ConvertTo-Json -Depth 4"
                r = _run(["powershell", "-NoProfile", "-Command", ps], timeout_seconds=8)
                probe: Dict[str, Any] = {"url": url, "ok": False, "detail": None, "error": None}
                if r.ok and r.stdout.strip():
                    try:
                        j = json.loads(r.stdout)
                        probe["detail"] = j
                        probe["ok"] = bool(j.get("TcpTestSucceeded") is True)
                    except Exception:
                        probe["error"] = "invalid_json_from_Test-NetConnection"
                else:
                    probe["error"] = r.stderr.strip() or "Test-NetConnection_failed"
                out["probes"].append(probe)
            else:
                out["probes"].append({"url": url, "ok": False, "error": "non_windows_skip"})
        except Exception as e:
            out["probes"].append({"url": url, "ok": False, "error": str(e)})
    return out


def build_snapshot(*, health_url: str = "", domains: Optional[List[str]] = None) -> Dict[str, Any]:
    domains = domains or ["wuchang.life", "www.wuchang.life", "odoo.wuchang.life", "admin.wuchang.life"]
    domains = [d.strip() for d in domains if d.strip()]

    netip = _get_netipconfig_json()
    gateway = _extract_default_gateway(netip)

    snap: Dict[str, Any] = {
        "timestamp": now_iso(),
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "user": os.getenv("USERNAME") or os.getenv("USER") or "",
        },
        "windows_netipconfiguration": netip,
        "default_gateway_ipv4": gateway,
        "hosts_overrides": _read_hosts_overrides(domains),
        "dns": {
            "socket": [_socket_resolve(d) for d in domains],
            "nslookup": [_nslookup(d) for d in domains],
        },
        "router_probe": _probe_router_http(gateway),
    }

    if health_url:
        if check_server_health is None:
            snap["server_health"] = {"ok": False, "error": "risk_gate_unavailable", "health_url": health_url}
        else:
            hc = check_server_health(health_url, timeout_seconds=3.0, retries=2)
            snap["server_health"] = {"health_url": health_url, "result": asdict(hc)}
    return snap


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--health-url", default="", help="伺服器 health URL（僅檢查回應，不做變更）")
    ap.add_argument("--domains", nargs="*", default=None, help="要解析/查詢的網域清單")
    ap.add_argument("--out", default="", help="輸出 JSON 檔路徑（不填則只印到 stdout）")
    args = ap.parse_args(argv)

    snap = build_snapshot(health_url=str(args.health_url or "").strip(), domains=args.domains)
    raw = json.dumps(snap, ensure_ascii=False, indent=2)

    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(raw, encoding="utf-8")

    print(raw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

