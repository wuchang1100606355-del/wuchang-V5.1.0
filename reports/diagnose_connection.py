"""
診斷工具：檢查路由器 DDNS 連接問題
"""

import socket
import sys
import subprocess
import platform

def test_dns(hostname):
    """測試 DNS 解析"""
    print(f"\n[診斷] 測試 DNS 解析: {hostname}")
    try:
        ip = socket.gethostbyname(hostname)
        print(f"  [OK] DNS 解析成功: {hostname} -> {ip}")
        return ip
    except socket.gaierror as e:
        print(f"  [FAIL] DNS 解析失敗: {e}")
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
    print(f"\n[診斷] 測試 nslookup: {hostname}")
    try:
        result = subprocess.run(['nslookup', hostname], 
                              capture_output=True, text=True, timeout=5)
        print(f"  {result.stdout}")
        if result.returncode == 0:
            print(f"  [OK] nslookup 成功")
            return True
        else:
            print(f"  [FAIL] nslookup 失敗")
            print(f"  {result.stderr}")
            return False
    except Exception as e:
        print(f"  [ERROR] nslookup 測試錯誤: {e}")
        return False

def main():
    print("=" * 60)
    print("華碩路由器 DDNS 連接診斷工具")
    print("=" * 60)
    
    # 測試不同的域名變體
    hostnames = [
        "coffeeLofe.asuscomm.com",
        "coffeelofe.asuscomm.com",  # 全小寫
        "CoffeeLofe.asuscomm.com",  # 首字母大寫
    ]
    
    print("\n測試不同的域名格式...")
    for hostname in hostnames:
        print(f"\n{'='*60}")
        print(f"測試域名: {hostname}")
        print('='*60)
        
        # DNS 解析
        ip = test_dns(hostname)
        
        # nslookup
        test_nslookup(hostname)
        
        # Ping（如果 DNS 解析成功）
        if ip:
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
