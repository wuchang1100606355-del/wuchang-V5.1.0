import os
import time
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import socket
import json
from datetime import datetime

# 監控配置
MONITOR_PATH = r"C:\wuchang V5.1.0"
IGNORE_DIRS = [".git", ".venv", "__pycache__", "node_modules", ".wuchang_device"]
SERVER_PORT = 8766  # Cloud Sync Service Port
UI_PORT = 8765      # UI Control Port

class WuchangHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and not any(d in event.src_path for d in IGNORE_DIRS):
            print(f"📝 檔案變更: {event.src_path}")
            # 這裡可以加入通知同步服務的邏輯

    def on_created(self, event):
        if not event.is_directory and not any(d in event.src_path for d in IGNORE_DIRS):
            print(f"✨ 新增檔案: {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory and not any(d in event.src_path for d in IGNORE_DIRS):
            print(f"🗑️ 刪除檔案: {event.src_path}")

def check_process_handshake():
    """與工作程序進行握手協助"""
    
    # 1. 檢查 Cloud Sync Service (8766)
    sync_status = "❌ 未連線"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            if s.connect_ex(('localhost', SERVER_PORT)) == 0:
                sync_status = "✅ 運作中 (Listening)"
    except:
        pass

    # 2. 檢查 UI Control Service (8765)
    ui_status = "❌ 未連線"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            if s.connect_ex(('localhost', UI_PORT)) == 0:
                ui_status = "✅ 運作中 (Listening)"
    except:
        pass
        
    # 3. 檢查 Python 相關程序
    python_procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in proc.info['name'].lower():
                cmd = proc.info['cmdline']
                if cmd and len(cmd) > 1:
                    script = cmd[1]
                    if "cloud_sync_service.py" in script:
                        python_procs.append(f"☁️ Sync Service (PID: {proc.info['pid']})")
                    elif "local_ui_server.py" in script:
                        python_procs.append(f"🎮 UI Server (PID: {proc.info['pid']})")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    print(f"\n🤝 工作程序握手狀態報告 ({datetime.now().strftime('%H:%M:%S')})")
    print("-" * 50)
    print(f"Cloud Sync (8766): {sync_status}")
    print(f"UI Control (8765): {ui_status}")
    print(f"活躍程序: {', '.join(python_procs) if python_procs else '無'}")
    print("-" * 50 + "\n")

def start_file_monitor():
    """啟動檔案監控"""
    print(f"👀 啟動地端檔案監測: {MONITOR_PATH}")
    event_handler = WuchangHandler()
    observer = Observer()
    observer.schedule(event_handler, MONITOR_PATH, recursive=True)
    observer.start()
    
    try:
        while True:
            check_process_handshake()
            time.sleep(10) # 每 10 秒檢查一次握手狀態
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_file_monitor()
