import socket
import threading
import time
from queue import Queue

TARGET_IP = "192.168.50.249"
PORTS_TO_SCAN = [
    22, 80, 443,      # Standard
    3001,             # Kuma
    5432,             # PostgreSQL
    8069,             # Odoo
    8080,             # AI/Web
    8765,             # Local UI Server
    8766,             # Cloud Sync Service
    3389,             # RDP
    5900,             # VNC
    9000, 9090        # Misc
]

print(f"🚀 開始主動掃描目標: {TARGET_IP}")
print(f"🎯 掃描端口: {PORTS_TO_SCAN}")

results = {}

def scan_port(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0) # 2 seconds timeout
        result = s.connect_ex((TARGET_IP, port))
        if result == 0:
            print(f"✅ 端口 {port} 開啟")
            results[port] = True
        else:
            # print(f"❌ 端口 {port} 關閉或過濾")
            results[port] = False
        s.close()
    except Exception as e:
        print(f"⚠️ 端口 {port} 掃描錯誤: {e}")
        results[port] = False

threads = []
for port in PORTS_TO_SCAN:
    t = threading.Thread(target=scan_port, args=(port,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("\n📊 掃描結果摘要:")
open_ports = [p for p, is_open in results.items() if is_open]
if open_ports:
    print(f"🟢 發現開啟端口: {open_ports}")
else:
    print("🔴 未發現開啟端口 (目標可能離線或防火牆阻擋)")

# 嘗試 Ping (雖然之前失敗了，但再試一次作為確認)
import subprocess
try:
    print("\n📡 嘗試 Ping 測試...")
    output = subprocess.check_output(["ping", "-n", "2", TARGET_IP], stderr=subprocess.STDOUT)
    print(output.decode('big5', errors='ignore'))
except subprocess.CalledProcessError as e:
    print("❌ Ping 失敗 (可能禁用了 ICMP)")
