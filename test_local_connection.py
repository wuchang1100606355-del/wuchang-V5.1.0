"""
測試本地網路連接（如果路由器在本地網路中）
"""

import socket
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import sys
import io

urllib3.disable_warnings(InsecureRequestWarning)

# Force UTF-8 output so captured logs don't become mojibake on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

def get_local_ip_range():
    """獲取本地 IP 範圍"""
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"本機 IP: {local_ip}")
    
    # 提取網段（假設是 /24）
    ip_parts = local_ip.split('.')
    base_ip = '.'.join(ip_parts[:3])
    return base_ip

def test_local_router():
    """測試本地路由器連接"""
    print("=" * 60)
    print("測試本地路由器連接")
    print("=" * 60)
    
    base_ip = get_local_ip_range()
    print(f"\n掃描網段: {base_ip}.x")
    print("常見路由器 IP: 192.168.1.1, 192.168.0.1, 10.0.0.1")
    
    common_ips = [
        "192.168.1.1",
        "192.168.0.1", 
        "10.0.0.1",
        f"{base_ip}.1"
    ]
    
    ports = [8443, 443, 8080, 80]
    
    print("\n測試常見路由器 IP 和端口...")
    for ip in common_ips:
        for port in ports:
            protocol = "https" if port in [8443, 443] else "http"
            url = f"{protocol}://{ip}:{port}"
            
            try:
                # Routers may respond with 200/302/401/403 depending on auth settings.
                response = requests.get(url, verify=False, timeout=2, allow_redirects=False)
                if response.status_code in (200, 302, 401, 403):
                    server = response.headers.get("Server", "")
                    location = response.headers.get("Location", "")
                    ct = response.headers.get("Content-Type", "")
                    print(f"\n[發現] {url} - 狀態碼: {response.status_code}")
                    if server:
                        print(f"  Server: {server}")
                    if location:
                        print(f"  Location: {location}")
                    if ct:
                        print(f"  Content-Type: {ct}")

                    # Heuristic confirmation (best-effort)
                    body = (response.text or "").lower()
                    if "asus" in body or "asus" in server.lower() or "asus" in location.lower():
                        print("  [確認] 可能是華碩路由器（偵測到 asus 標記）")
                    else:
                        print("  [INFO] 裝置已回應，但頁面未包含 asus 字樣（可能需要登入或是不同品牌介面）")

                    return ip, port, protocol
            except Exception:
                continue
    
    print("\n未找到本地路由器")
    return None, None, None

def main():
    print("\n注意: DDNS 域名無法解析到公網 IP")
    print("這可能意味著:")
    print("  1. DDNS 服務未正確配置")
    print("  2. 路由器未連接到公網")
    print("  3. 只能在本地網路訪問")
    print()
    
    # 測試本地連接
    ip, port, protocol = test_local_router()
    
    if ip:
        print(f"\n建議: 使用本地 IP {ip}:{port} 連接路由器")
        print(f"URL: {protocol}://{ip}:{port}")

if __name__ == "__main__":
    main()
