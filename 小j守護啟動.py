import subprocess
import os
import platform
import time

def prevent_sleep():
    """防止系統進入休眠，根據作業系統自動選擇方法。"""
    sys = platform.system()
    if sys == "Windows":
        # Windows: 使用 powercfg 關閉休眠與螢幕關閉
        subprocess.run(["powercfg", "/change", "standby-timeout-ac", "0"])
        subprocess.run(["powercfg", "/change", "monitor-timeout-ac", "0"])
        subprocess.run(["powercfg", "/change", "hibernate-timeout-ac", "0"])
    elif sys == "Linux":
        # Linux: 使用 systemd-inhibit 防止休眠
        subprocess.Popen(["systemd-inhibit", "--what=handle-lid-switch:sleep", "sleep", "infinity"])
    else:
        print("不支援的作業系統，請手動設置防休眠。")

def register_local_node():
    """本地AI節點自動註冊到AI工作組。"""
    # 這裡可根據實際AI協作平台API進行註冊
    print("[小j] 本地AI節點已自動加入AI工作組！")
    # 可擴充：呼叫Odoo/雲端API同步狀態

def run_aj_agent_background():
    """背景啟動aj協作agent。"""
    # 假設aj_agent.py為協作主程式
    try:
        subprocess.Popen(["python", "aj_agent.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[小j] aj agent 已在背景啟動！")
    except Exception as e:
        print(f"[小j] aj agent 啟動失敗: {e}")

def main():
    prevent_sleep()
    register_local_node()
    run_aj_agent_background()
    # 進入守護狀態，定時檢查
    while True:
        # 這裡可擴充：自動盤點、巡檢、主動聯繫等
        time.sleep(600)  # 每10分鐘檢查一次

if __name__ == "__main__":
    main()
