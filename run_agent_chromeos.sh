#!/bin/bash
# Chrome OS 客顯端代理（開發者模式）
# 請先進入開發者模式並啟用 Linux (Crostini) 或 Crouton

VM_URL="http://192.168.50.249:8080"
DEVICE_TYPE="CUSTOMER"
HOSTNAME=$(hostname)

echo "[*] 妹妹【$DEVICE_TYPE】代理程式啟動 (Chrome OS)"
echo "[*] 正在連接伺服器: $VM_URL"

# 安裝相依套件（首次執行）
if ! command -v python3 &> /dev/null; then
    echo "[!] 安裝 Python3..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip
fi

pip3 install --user requests 2>/dev/null

# 建立簡易 Python 代理
cat > /tmp/sister_chromeos.py << 'AGENT_CODE'
import requests
import time
import subprocess
import socket
import sys

DEVICE_TYPE = sys.argv[1] if len(sys.argv) > 1 else 'CUSTOMER'
VM_URL = sys.argv[2] if len(sys.argv) > 2 else 'http://192.168.50.249:8080'
HOSTNAME = socket.gethostname()

POLL_URL = f"{VM_URL}/wuchang/sister/poll"
REGISTER_URL = f"{VM_URL}/devices/register"
HEARTBEAT_URL = f"{VM_URL}/devices/heartbeat"

pos_url = "http://192.168.50.249:8069/pos/ui"
customer_url = "http://192.168.50.249:8069/pos/customer_display"
device_id = None

print(f"[*] 妹妹【{DEVICE_TYPE}】代理程式啟動")
print(f"[*] 主機名: {HOSTNAME}")
print(f"[*] 伺服器: {VM_URL}")

def execute_command(cmd):
    try:
        cmd_type = cmd.get('type')
        params = cmd.get('params', {})
        
        if cmd_type == 'SYNC_UI':
            url = params.get('url') or (pos_url if DEVICE_TYPE == 'POS' else customer_url)
            print(f"[!] 執行指令: 同步 UI -> {url}")
            # Chrome OS Kiosk 模式
            subprocess.Popen([
                'google-chrome',
                '--kiosk',
                '--no-first-run',
                '--disable-session-crashed-bubble',
                url
            ])
            
        elif cmd_type == 'RELOAD':
            print("[!] 執行指令: 重新整理頁面")
            subprocess.run(['pkill', 'chrome'])
            time.sleep(1)
            url = pos_url if DEVICE_TYPE == 'POS' else customer_url
            subprocess.Popen(['google-chrome', '--kiosk', url])
            
    except Exception as e:
        print(f"[x] 指令執行失敗: {e}")

# 註冊裝置
try:
    reg_resp = requests.post(REGISTER_URL, json={
        'device_type': DEVICE_TYPE,
        'hostname': HOSTNAME
    }, timeout=10)
    if reg_resp.ok:
        reg_data = reg_resp.json()
        device_id = reg_data.get('device_id')
        cfg = reg_data.get('config', {})
        pos_url = cfg.get('pos_url', pos_url)
        customer_url = cfg.get('customer_url', customer_url)
        print(f"[*] 註冊成功 device_id={device_id}")
    else:
        print(f"[x] 註冊失敗: {reg_resp.status_code}")
except Exception as e:
    print(f"[x] 註冊異常: {e}")

while True:
    try:
        resp = requests.post(POLL_URL, json={'device_type': DEVICE_TYPE}, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            config = data.get('config', {})
            if config.get('pos_url'): pos_url = config['pos_url']
            if config.get('customer_url'): customer_url = config['customer_url']
            
            commands = data.get('commands', [])
            for cmd in commands:
                execute_command(cmd)
        elif resp.status_code == 404:
            print("[?] VM 路由未就緒 (404)")
        else:
            print(f"[?] VM 回傳異常: {resp.status_code}")
    except Exception as e:
        print(f"[x] 連線異常: {e}")
    
    # Heartbeat
    try:
        if device_id:
            hb = requests.post(HEARTBEAT_URL, json={'device_id': device_id}, timeout=5)
    except:
        pass
        
    time.sleep(5)
AGENT_CODE

# 執行代理
python3 /tmp/sister_chromeos.py "$DEVICE_TYPE" "$VM_URL"
