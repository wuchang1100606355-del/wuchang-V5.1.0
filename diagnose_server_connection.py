#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
伺服器連線診斷工具
診斷 192.168.50.249 無法連線的原因
"""

import socket
import subprocess
import sys
import time
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed

SERVER_IP = "192.168.50.249"
PORTS_TO_CHECK = [22, 80, 443, 8069, 8080, 8766, 3001, 5432, 3389, 5900]

def print_section(title):
    """打印章節標題"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_result(label, status, details=""):
    """打印結果"""
    status_symbol = "[OK]" if status else "[FAIL]"
    status_color = "\033[92m" if status else "\033[91m"
    reset_color = "\033[0m"
    print(f"{status_color}{status_symbol}{reset_color} {label}")
    if details:
        print(f"    {details}")

def test_ping(ip):
    """測試 ping"""
    print_section("1. 基本連線測試 (Ping)")
    
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ["ping", "-n", "4", ip],
                capture_output=True,
                text=True,
                timeout=10
            )
        else:
            result = subprocess.run(
                ["ping", "-c", "4", ip],
                capture_output=True,
                text=True,
                timeout=10
            )
        
        if result.returncode == 0:
            print_result("Ping 測試", True, "伺服器可達")
            # 提取延遲信息
            output = result.stdout
            if "平均" in output or "Average" in output:
                for line in output.split("\n"):
                    if "平均" in line or "Average" in line:
                        print(f"    {line.strip()}")
            return True
        else:
            print_result("Ping 測試", False, "無法 ping 通伺服器")
            print(f"    輸出: {result.stdout[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print_result("Ping 測試", False, "Ping 超時")
        return False
    except Exception as e:
        print_result("Ping 測試", False, f"錯誤: {e}")
        return False

def test_port(ip, port, timeout=3):
    """測試單個端口"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def scan_ports(ip, ports):
    """掃描端口"""
    print_section("2. 端口掃描")
    print(f"掃描目標: {ip}")
    print(f"掃描端口: {', '.join(map(str, ports))}")
    print()
    
    open_ports = []
    closed_ports = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_port = {
            executor.submit(test_port, ip, port): port 
            for port in ports
        }
        
        for future in as_completed(future_to_port):
            port = future_to_port[future]
            try:
                is_open = future.result()
                if is_open:
                    open_ports.append(port)
                    print_result(f"端口 {port}", True, "開啟")
                else:
                    closed_ports.append(port)
                    print(f"   端口 {port}: [CLOSED]")
            except Exception as e:
                closed_ports.append(port)
                print(f"   端口 {port}: [ERROR] {e}")
    
    print()
    if open_ports:
        print_result("可用端口", True, f"{len(open_ports)} 個端口開啟: {open_ports}")
    else:
        print_result("可用端口", False, "沒有發現開啟的端口")
    
    return open_ports, closed_ports

def test_ssh(ip):
    """測試 SSH 連線"""
    print_section("3. SSH 連線測試")
    
    # 測試端口 22
    ssh_open = test_port(ip, 22, timeout=5)
    print_result("SSH 端口 (22)", ssh_open)
    
    if ssh_open:
        print("    嘗試 SSH 連線...")
        try:
            import paramiko
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 嘗試常見用戶名
            users = ["admin", "wuchang", "user", "ubuntu", "debian", "root"]
            connected = False
            
            for user in users:
                try:
                    print(f"    嘗試用戶: {user}...", end=" ")
                    client.connect(ip, username=user, timeout=5)
                    print("[OK]")
                    print_result("SSH 認證", True, f"用戶 {user} 可連線")
                    connected = True
                    
                    # 執行簡單命令測試
                    stdin, stdout, stderr = client.exec_command("hostname; whoami; uname -a")
                    output = stdout.read().decode()
                    print(f"    伺服器信息:")
                    for line in output.strip().split("\n"):
                        print(f"      {line}")
                    
                    client.close()
                    break
                except paramiko.AuthenticationException:
                    print("[AUTH FAIL]")
                except Exception as e:
                    print(f"[ERROR: {str(e)[:30]}]")
            
            if not connected:
                print_result("SSH 認證", False, "無法使用常見用戶名連線")
                print("    提示: 需要正確的用戶名和密碼或 SSH 密鑰")
                
        except ImportError:
            print("    [INFO] paramiko 未安裝，跳過 SSH 認證測試")
            print("    安裝: pip install paramiko")
        except Exception as e:
            print_result("SSH 連線", False, f"錯誤: {e}")
    else:
        print("    [INFO] SSH 端口未開啟，跳過 SSH 認證測試")

def check_network_info():
    """檢查網絡信息"""
    print_section("4. 本地網絡配置")
    
    try:
        if platform.system() == "Windows":
            # 獲取本機 IP
            result = subprocess.run(
                ["ipconfig"],
                capture_output=True,
                text=True
            )
            output = result.stdout
            
            # 查找 IPv4 地址
            lines = output.split("\n")
            in_adapter = False
            for line in lines:
                if "適配器" in line or "Adapter" in line:
                    in_adapter = True
                if in_adapter and "IPv4" in line:
                    ip_line = line.strip()
                    print(f"    本機 IP: {ip_line}")
                    if "192.168.50" in ip_line:
                        print_result("網段檢查", True, "本機在 192.168.50.x 網段")
                    break
            
            # 檢查 ARP 表
            print("\n    檢查 ARP 表...")
            result = subprocess.run(
                ["arp", "-a", SERVER_IP],
                capture_output=True,
                text=True
            )
            if SERVER_IP in result.stdout:
                print_result("ARP 表", True, "找到伺服器 MAC 地址")
                for line in result.stdout.split("\n"):
                    if SERVER_IP in line:
                        print(f"      {line.strip()}")
            else:
                print_result("ARP 表", False, "ARP 表中沒有伺服器記錄")
                
        else:
            # Linux/Mac
            result = subprocess.run(
                ["ip", "addr", "show"],
                capture_output=True,
                text=True
            )
            print(result.stdout[:500])
            
    except Exception as e:
        print_result("網絡信息", False, f"錯誤: {e}")

def check_firewall():
    """檢查防火牆"""
    print_section("5. 防火牆檢查")
    
    if platform.system() == "Windows":
        try:
            result = subprocess.run(
                ["netsh", "advfirewall", "show", "allprofiles", "state"],
                capture_output=True,
                text=True
            )
            if "ON" in result.stdout or "開啟" in result.stdout:
                print_result("Windows 防火牆", True, "防火牆已開啟")
                print("    提示: 檢查防火牆規則是否允許連線到伺服器")
            else:
                print_result("Windows 防火牆", False, "防火牆已關閉")
        except Exception as e:
            print(f"    [INFO] 無法檢查防火牆: {e}")
    else:
        print("    [INFO] 請手動檢查防火牆設置 (ufw/iptables)")

def check_routing():
    """檢查路由"""
    print_section("6. 路由檢查")
    
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ["route", "print"],
                capture_output=True,
                text=True
            )
            output = result.stdout
            
            # 查找到 192.168.50.0 網段的路由
            if "192.168.50" in output:
                print_result("路由表", True, "找到到伺服器網段的路由")
                for line in output.split("\n"):
                    if "192.168.50" in line:
                        print(f"      {line.strip()}")
            else:
                print_result("路由表", False, "沒有找到到伺服器網段的路由")
        else:
            result = subprocess.run(
                ["ip", "route", "show"],
                capture_output=True,
                text=True
            )
            if "192.168.50" in result.stdout:
                print_result("路由表", True, "找到到伺服器網段的路由")
                print(result.stdout)
            else:
                print_result("路由表", False, "沒有找到到伺服器網段的路由")
    except Exception as e:
        print_result("路由檢查", False, f"錯誤: {e}")

def generate_report(ping_result, open_ports, closed_ports):
    """生成診斷報告"""
    print_section("診斷報告總結")
    
    print("\n檢查結果:")
    print(f"  1. Ping 測試: {'通過' if ping_result else '失敗'}")
    print(f"  2. 端口掃描: {len(open_ports)} 個開啟, {len(closed_ports)} 個關閉")
    
    print("\n可能的原因:")
    
    if not ping_result:
        print("  [1] 伺服器可能未啟動或網絡不通")
        print("      - 檢查伺服器是否正在運行")
        print("      - 檢查網絡線路連接")
        print("      - 檢查路由器設置")
    
    if not open_ports:
        print("  [2] 所有端口都無法連接")
        print("      - 伺服器可能未啟動服務")
        print("      - 防火牆可能阻擋了所有端口")
        print("      - 服務可能監聽在其他端口")
    
    if ping_result and not open_ports:
        print("  [3] 可以 ping 通但端口無法連接")
        print("      - 伺服器防火牆可能阻擋了端口")
        print("      - 服務可能未啟動")
        print("      - 服務可能監聽在 localhost 而非 0.0.0.0")
    
    if 22 in closed_ports:
        print("  [4] SSH 端口 (22) 無法連接")
        print("      - 檢查伺服器 SSH 服務是否啟動: sudo systemctl status sshd")
        print("      - 檢查防火牆規則: sudo ufw status")
    
    print("\n建議操作:")
    print("  1. 確認伺服器正在運行")
    print("  2. 在伺服器上檢查服務狀態:")
    print("     - docker ps")
    print("     - netstat -tlnp | grep 8069")
    print("     - sudo systemctl status <service>")
    print("  3. 檢查伺服器防火牆:")
    print("     - sudo ufw status")
    print("     - sudo iptables -L -n")
    print("  4. 檢查服務監聽地址:")
    print("     - 確認服務監聽在 0.0.0.0 而非 127.0.0.1")
    print()

def main():
    """主函數"""
    print("=" * 80)
    print("  伺服器連線診斷工具")
    print(f"  目標伺服器: {SERVER_IP}")
    print("=" * 80)
    
    # 1. Ping 測試
    ping_result = test_ping(SERVER_IP)
    
    # 2. 端口掃描
    open_ports, closed_ports = scan_ports(SERVER_IP, PORTS_TO_CHECK)
    
    # 3. SSH 測試
    if 22 in PORTS_TO_CHECK:
        test_ssh(SERVER_IP)
    
    # 4. 網絡信息
    check_network_info()
    
    # 5. 防火牆檢查
    check_firewall()
    
    # 6. 路由檢查
    check_routing()
    
    # 7. 生成報告
    generate_report(ping_result, open_ports, closed_ports)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] 診斷已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
