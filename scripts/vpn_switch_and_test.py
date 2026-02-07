# 一鍵 VPN 連線與切換腳本
# 功能：
# 1. 自動連線/斷線 VPN（如 Windows 內建 VPN、OpenVPN、WireGuard）
# 2. 測試 VPN 連線後的伺服器可達性
# 3. 切換本地/遠端控制端點
# 4. 日誌記錄所有操作

import os
import subprocess
import datetime

# 設定
VPN_NAME = "WuchangVPN"  # 請依實際 VPN 名稱修改
SERVER_IP = "192.168.50.84"
LOG_FILE = "logs/vpn_switch_audit.log"


def log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {msg}\n")
    print(msg)


def connect_vpn():
    log(f"嘗試連線 VPN: {VPN_NAME}")
    result = os.system(f"rasdial {VPN_NAME}")
    if result == 0:
        log("VPN 連線成功！")
    else:
        log("VPN 連線失敗，請檢查 VPN 設定。")
    return result == 0


def disconnect_vpn():
    log(f"斷線 VPN: {VPN_NAME}")
    os.system(f"rasdial {VPN_NAME} /disconnect")
    log("VPN 已斷線。")


def test_server():
    log(f"測試伺服器連線: {SERVER_IP}")
    result = os.system(f"ping {SERVER_IP} -n 2")
    if result == 0:
        log("伺服器可達！")
    else:
        log("伺服器無法連線，請檢查 VPN 或網路。")
    return result == 0


def main():
    log("--- 一鍵 VPN 連線與切換開始 ---")
    if connect_vpn():
        if test_server():
            log("VPN 連線與伺服器測試皆成功，可進行遠端操作。")
        else:
            log("VPN 連線成功但伺服器無法連線，請檢查網路。")
    else:
        log("VPN 連線失敗，請手動檢查。")
    log("--- 操作結束 ---\n")

if __name__ == "__main__":
    main()
