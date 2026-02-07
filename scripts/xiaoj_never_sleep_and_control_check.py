import os
import time
import socket
import logging
import subprocess

LOG_FILE = "xiaoj_never_sleep.log"
CONTROL_CHECK_INTERVAL = 60  # 每 60 秒檢查一次
ALERT_FILE = "xiaoj_control_alert.txt"

def is_admin():
    """檢查是否有系統管理員權限 (Windows/Linux)"""
    try:
        if os.name == 'nt':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception:
        return False

def check_server_control():
    """檢查伺服器主要資源是否可控 (如檔案、網路、主要服務)"""
    try:
        # 檢查本地網路
        socket.gethostbyname("localhost")
        # 檢查重要檔案可寫
        with open(LOG_FILE, "a") as f:
            f.write("control check at %s\n" % time.ctime())
        # 檢查 Python 服務是否可執行
        result = subprocess.run(["python", "--version"], capture_output=True)
        if result.returncode != 0:
            return False
        return True
    except Exception as e:
        logging.error(f"控制權檢查失敗: {e}")
        return False

def alert_and_recover():
    """發出警告並嘗試自我修復"""
    with open(ALERT_FILE, "a") as f:
        f.write(f"[警告] 小J失去伺服器控制權: {time.ctime()}\n")
    # 嘗試重啟本服務（僅示範，實際可根據需要擴充）
    logging.warning("小J失去控制權，已發出警告並嘗試自我修復。")

def main():
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')
    print("小J永不休眠守護進程啟動！")
    while True:
        if not is_admin():
            logging.error("小J未取得系統管理員權限！")
            alert_and_recover()
        elif not check_server_control():
            logging.error("小J失去伺服器控制權！")
            alert_and_recover()
        else:
            logging.info("小J控制權正常，持續守護中。")
        time.sleep(CONTROL_CHECK_INTERVAL)

if __name__ == "__main__":
    main()
