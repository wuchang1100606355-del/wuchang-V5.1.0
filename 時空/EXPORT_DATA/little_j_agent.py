import os
import time
import json
import threading
from datetime import datetime
from 小j_最小時空系統 import MinimalSpacetimeSystem

class LittleJExecutionBody:
    """
    核心小j 內部執行體 (Execution Body)
    
    職責：
    1. 維持系統心跳 (Heartbeat)
    2. 執行週期性任務 (Scheduler)
    3. 監聽與響應指令 (Command Listener)
    4. 確保所有決策與行動納入時空審計 (Spacetime Audit)
    """
    def __init__(self):
        self.spacetime = MinimalSpacetimeSystem()
        self.is_running = False
        self.agent_id = "Little-J-Core-Agent-001"
        self.tasks = []

    def start(self):
        """啟動執行體"""
        self.is_running = True
        self.log_audit("agent_start", f"核心執行體 {self.agent_id} 已啟動，進入活躍狀態。")
        
        # 啟動心跳線程
        heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        heartbeat_thread.start()
        
        print(f"[{datetime.now()}] {self.agent_id} is running...")
        
        try:
            while self.is_running:
                # 模擬主迴圈監聽任務 (這裡可以擴充為讀取任務隊列)
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """停止執行體"""
        self.is_running = False
        self.log_audit("agent_stop", f"核心執行體 {self.agent_id} 已接收停止信號，正在關閉。")
        print(f"[{datetime.now()}] {self.agent_id} stopped.")

    def _heartbeat_loop(self):
        """背景心跳迴圈"""
        while self.is_running:
            # 每 60 秒發送一次存活訊號 (模擬縮短為 10 秒以便測試)
            self.log_audit("heartbeat", f"{self.agent_id} 系統運作正常，資源監控：OK")
            time.sleep(10)

    def log_audit(self, event_type, content):
        """寫入時空審計日誌"""
        self.spacetime.log_event(event_type, content, actor=self.agent_id)
        print(f"[Audit] {event_type}: {content}")

    def register_task(self, task_name, task_func):
        """註冊新任務"""
        self.tasks.append({"name": task_name, "func": task_func})
        self.log_audit("task_register", f"已註冊新任務：{task_name}")

if __name__ == "__main__":
    agent = LittleJExecutionBody()
    
    # 範例：註冊一個簡單的監控任務
    def monitor_portal():
        if os.path.exists("spacetime_launch.html"):
            return "Portal 頁面存在"
        return "Portal 頁面遺失！"
        
    agent.register_task("Check-Portal-Status", monitor_portal)
    
    # 啟動代理 (在實際部署時可作為服務運行)
    # 為了演示，我們讓它運行幾秒後自動停止
    print("--- 啟動演示模式 (運行 15 秒) ---")
    
    # 使用線程啟動以便主程序可以控制停止
    agent_thread = threading.Thread(target=agent.start)
    agent_thread.start()
    
    time.sleep(15)
    agent.stop()
    agent_thread.join()


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:04:03
---
