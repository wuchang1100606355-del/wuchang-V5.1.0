import requests
import time
import subprocess
import json
import argparse
import sys
import socket

# 妹妹 POS/客顯 代理程式
# 用於接收 VM 指令並控制本地瀏覽器

parser = argparse.ArgumentParser(description='Sister Agent')
parser.add_argument('--device', type=str, default='POS',
                    choices=['POS', 'CUSTOMER'], help='Device type (POS or CUSTOMER)')
parser.add_argument('--vm-url', type=str,
                    default='http://localhost:8080', help='Server VM base URL')
parser.add_argument('--hostname', type=str,
                    default=socket.gethostname(), help='Device hostname')
args = parser.parse_args()

DEVICE_TYPE = args.device
VM_URL = args.vm_url
POLL_URL = f"{VM_URL}/wuchang/sister/poll"
REGISTER_URL = f"{VM_URL}/devices/register"
HEARTBEAT_URL = f"{VM_URL}/devices/heartbeat"

print(f"[*] 妹妹【{DEVICE_TYPE}】代理程式啟動")
print(f"[*] 正在連接 VM: {VM_URL}")


def execute_command(cmd):
    try:
        cmd_type = cmd.get('type')
        params = cmd.get('params', {})

        if cmd_type == 'SYNC_UI':
            url = params.get('url') or (
                pos_url if DEVICE_TYPE == 'POS' else customer_url)
            print(f"[!] 執行指令: 同步 UI -> {url}")
            # 使用 chrome 開啟網址
            subprocess.Popen(
                ['start', 'chrome', '--fullscreen', url], shell=True)

        elif cmd_type == 'RELOAD':
            print("[!] 執行指令: 重新整理頁面")
            # 這裡可以使用 pyatogui 或其他方式發送 F5，暫時用重啟瀏覽器模擬
            url = pos_url if DEVICE_TYPE == 'POS' else customer_url
            subprocess.Popen(
                ['start', 'chrome', '--fullscreen', url], shell=True)

    except Exception as e:
        print(f"[x] 指令執行失敗: {e}")


pos_url = "http://localhost:8069/pos/ui"
customer_url = "http://localhost:8069/pos/customer_display"
device_id = None

# Register device
try:
    reg_resp = requests.post(REGISTER_URL, json={
        'device_type': DEVICE_TYPE,
        'hostname': args.hostname
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
        # 發送簡單的 JSON POST
        resp = requests.post(
            POLL_URL, json={'device_type': DEVICE_TYPE}, timeout=10)

        if resp.status_code == 200:
            data = resp.json()

            # 更新配置
            config = data.get('config', {})
            if config.get('pos_url'):
                pos_url = config['pos_url']
            if config.get('customer_url'):
                customer_url = config['customer_url']

            commands = data.get('commands', [])
            for cmd in commands:
                execute_command(cmd)
        elif resp.status_code == 404:
            print("[?] VM 路由未就緒 (404)，等待中...")
        else:
            print(f"[?] VM 回傳異常狀態碼: {resp.status_code}")

    except Exception as e:
        print(f"[x] 連線異常: {e}")
    # Heartbeat
    try:
        if device_id:
            hb = requests.post(HEARTBEAT_URL, json={
                               'device_id': device_id}, timeout=5)
            if not hb.ok:
                print(f"[?] 心跳回傳: {hb.status_code}")
    except Exception as e:
        print(f"[x] 心跳異常: {e}")

    time.sleep(5)
