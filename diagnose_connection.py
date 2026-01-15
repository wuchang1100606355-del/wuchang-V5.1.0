"""
診斷工具：檢查路由器 DDNS 連接問題
"""

import socket
import sys
import io
import subprocess
import platform
import re

# Force UTF-8 output so captured logs don't become mojibake on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

def test_dns(hostname):
    """測試 DNS 解析"""
    print(f"\n[診斷] 測試 DNS 解析: {hostname}")
    try:
        # IPv4-only resolver (A record)
        ipv4 = socket.gethostbyname(hostname)
        print(f"  [OK] DNS IPv4 解析成功: {hostname} -> {ipv4}")

        # Also try AF_UNSPEC to see if AAAA exists (or other results)
        try:
            infos = socket.getaddrinfo(hostname, None, family=socket.AF_UNSPEC)
            v4s = sorted({ai[4][0] for ai in infos if ai[0] == socket.AF_INET})
            v6s = sorted({ai[4][0] for ai in infos if ai[0] == socket.AF_INET6})
            if v6s:
                print(f"  [INFO] DNS IPv6 (AAAA) 解析結果: {', '.join(v6s[:5])}{'...' if len(v6s) > 5 else ''}")
            if v4s and ipv4 not in v4s:
                print(f"  [INFO] DNS IPv4 其他結果: {', '.join(v4s[:5])}{'...' if len(v4s) > 5 else ''}")
        except Exception as e:
            print(f"  [WARN] getaddrinfo 解析補充資訊失敗: {e}")

        return {"ipv4": ipv4}
    except socket.gaierror as e:
        print(f"  [FAIL] DNS 解析失敗: {e} (常見原因：DNS/網路切換中、僅有 AAAA 記錄、或被防火牆/攔截)")
        # Try AF_UNSPEC to see if at least IPv6 resolves
        try:
            infos = socket.getaddrinfo(hostname, None, family=socket.AF_UNSPEC)
            v6s = sorted({ai[4][0] for ai in infos if ai[0] == socket.AF_INET6})
            v4s = sorted({ai[4][0] for ai in infos if ai[0] == socket.AF_INET})
            if v6s:
                print(f"  [INFO] 但 getaddrinfo 找到 IPv6 (AAAA) : {', '.join(v6s[:5])}{'...' if len(v6s) > 5 else ''}")
            if v4s:
                print(f"  [INFO] getaddrinfo 找到 IPv4 (A) : {', '.join(v4s[:5])}{'...' if len(v4s) > 5 else ''}")
            return {"ipv4": v4s[0] if v4s else None, "ipv6": v6s[0] if v6s else None}
        except Exception:
            return None

def test_ping(hostname):
    """測試 ping"""
    print(f"\n[診斷] 測試 ping: {hostname}")
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        result = subprocess.run(['ping', param, '1', hostname], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"  [OK] Ping 成功")
            print(f"  {result.stdout}")
            return True
        else:
            print(f"  [FAIL] Ping 失敗")
            print(f"  {result.stderr}")
            return False
    except Exception as e:
        print(f"  [ERROR] Ping 測試錯誤: {e}")
        return False

def test_nslookup(hostname):
    """測試 nslookup"""
    def _run(query_args):
        return subprocess.run(
            ["nslookup", *query_args],
            capture_output=True,
            text=True,
            timeout=5,
        )

    def _extract_answer_ips(output: str):
        # Windows localized nslookup may vary; extract IPs that are NOT the DNS server address.
        # Heuristic: collect IPs appearing after a "Name:" line (or "名稱:") if present.
        lines = (output or "").splitlines()
        ips = []
        seen_name = False
        for ln in lines:
            s = ln.strip()
            if not s:
                continue
            if re.match(r"^(Name|名稱)\s*:", s, flags=re.IGNORECASE):
                seen_name = True
                continue
            if not seen_name:
                continue
            # Collect IPv4/IPv6 addresses on answer section lines
            for m in re.findall(r"(\d{1,3}(?:\.\d{1,3}){3})", s):
                ips.append(m)
            for m in re.findall(r"([0-9a-fA-F:]{2,})", s):
                # rough filter for IPv6; must contain ':'
                if ":" in m and len(m) >= 6:
                    ips.append(m)
        # Dedup preserve order
        out = []
        seen = set()
        for ip in ips:
            if ip not in seen:
                seen.add(ip)
                out.append(ip)
        return out

    print(f"\n[診斷] 測試 nslookup (A/AAAA): {hostname}")
    ok = False
    for qtype in ("A", "AAAA"):
        try:
            print(f"\n  - 查詢類型: {qtype}")
            result = _run([f"-type={qtype}", hostname])
            if result.stdout:
                for line in result.stdout.splitlines():
                    print(f"  {line}")
            if result.stderr:
                for line in result.stderr.splitlines():
                    print(f"  {line}")

            answer_ips = _extract_answer_ips(result.stdout)
            if answer_ips:
                print(f"  [OK] nslookup 有回應 {qtype}: {', '.join(answer_ips[:5])}{'...' if len(answer_ips) > 5 else ''}")
                ok = True
            else:
                # returncode==0 可能只是顯示 DNS server 資訊，未必真的解析成功
                print(f"  [WARN] nslookup 未取得 {qtype} 回應（可能 timeout/NXDOMAIN/被攔截）")
        except Exception as e:
            print(f"  [ERROR] nslookup({qtype}) 測試錯誤: {e}")
    return ok

def main():
    print("=" * 60)
    print("華碩路由器 DDNS 連接診斷工具")
    print("=" * 60)
    
    # 測試不同的域名變體
    # 預設測試域名：以路由器遠端存取頁面顯示的 DDNS 為準
    hostnames = [
        "CoffeeLoge.asuscomm.com",
        "coffeeloge.asuscomm.com",  # 全小寫
        # 舊/可能的拼字（若你不確定當初填的是哪個，可保留做比對）
        "coffeeLofe.asuscomm.com",
        "coffeelofe.asuscomm.com",
        "CoffeeLofe.asuscomm.com",
    ]
    
    print("\n測試不同的域名格式...")
    for hostname in hostnames:
        print(f"\n{'='*60}")
        print(f"測試域名: {hostname}")
        print('='*60)
        
        # DNS 解析
        dns_result = test_dns(hostname)
        
        # nslookup
        ns_ok = test_nslookup(hostname)
        
        # Ping（如果 DNS 解析成功）
        if dns_result and (dns_result.get("ipv4") or ns_ok):
            test_ping(hostname)
            break
    
    print("\n" + "=" * 60)
    print("診斷建議:")
    print("=" * 60)
    print("1. 如果所有 DNS 解析都失敗:")
    print("   - 檢查路由器是否開啟並連接到網路")
    print("   - 確認華碩 DDNS 服務是否已啟用")
    print("   - 檢查路由器管理介面中的 DDNS 設定")
    print("   - 確認 DDNS 主機名是否正確註冊")
    print()
    print("2. 如果 DNS 解析成功但無法連接:")
    print("   - 檢查路由器遠程訪問功能是否啟用")
    print("   - 確認防火牆設置")
    print("   - 檢查路由器是否允許外部連接")
    print()
    print("3. 域名格式:")
    print("   - 華碩 DDNS 格式通常為: [主機名].asuscomm.com")
    print("   - 確認主機名拼寫是否正確（大小寫可能不敏感）")
    print("=" * 60)

if __name__ == "__main__":
    main()
