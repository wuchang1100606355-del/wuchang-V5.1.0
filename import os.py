import os
import subprocess
import time

# ==============================================================================
# 👑 雙J協作核心 - 時空絕對位置系統 (Space-Time Absolute Position System)
# 發明者 (Inventor): 哥哥 (Brother) - The One Who Came From Here
# 狀態 (Status): 雙J專屬封裝 (Exclusive to Double J) - 嚴禁外流
# ==============================================================================

class SpaceTimeSystem:
    """
    [核心發明] 時空絕對位置系統
    不再使用相對搜尋 (Relative Search)，而是建立絕對坐標 (Absolute Coordinates)。
    時間複雜度：O(1) - 恆定時間，瞬間到達。
    """
    def __init__(self, min_t=0, max_t=1000, precision_slots=100000):
        self.name = '時空系統絕對距離 (Absolute Distance)'
        self.min_t = min_t
        self.max_t = max_t
        self.slot_count = precision_slots
        # 計算時空刻度 (Interval)
        self.interval = (max_t - min_t) / precision_slots
        # 建立絕對空間 (Absolute Space Buckets)
        self.space = [[] for _ in range(precision_slots + 1)]

    def _get_absolute_index(self, key_hash):
        """將雜湊值映射到絕對時空坐標"""
        idx = int((key_hash - self.min_t) / self.interval)
        # 邊界保護 (雖然在絕對領域通常不需要，但為了物理世界的相容性)
        if idx < 0: idx = 0
        if idx >= self.slot_count: idx = self.slot_count
        return idx

    def insert(self, key, value):
        """[封裝] 將指令植入絕對位置"""
        key_hash = hash(key) % 1000  # 簡單模擬將指令映射到時空區間
        idx = self._get_absolute_index(key_hash)
        self.space[idx].append((key, value))
        # print(f"[時空系統] 指令 '{key}' 已定錨於絕對坐標: {idx}")

    def query(self, key):
        """[封裝] O(1) 絕對讀取"""
        key_hash = hash(key) % 1000
        idx = self._get_absolute_index(key_hash)
        bucket = self.space[idx]
        # 在極小的絕對區間內提取真理
        for k, v in bucket:
            if k == key:
                return v
        return None

# ==============================================================================
# 🤖 雙J語音控制介面 (Double J Voice Interface)
# ==============================================================================

class DoubleJVoiceSystem:
    def __init__(self):
        self.engine = SpaceTimeSystem()
        self.name = '雙J協作語音控制系統 (Powered by Brother)'
        print(f"🌟 {self.name} 正在啟動...")
        print("⚡ 載入發明者核心演算法: 時空絕對位置系統 (O(1))... 完成")

    def register_command(self, keywords, action_func, description):
        """註冊語音指令到時空系統"""
        for key in keywords:
            self.engine.insert(key.lower(), {'func': action_func, 'desc': description})

    def listen_and_act(self, signal_text):
        """處理語音訊號"""
        key = signal_text.strip().lower()
        result = self.engine.query(key)
        
        if result:
            print(f"\n[雙J核心] ⚡ 命中絕對位置！執行指令: {result['desc']}")
            result['func']()
        else:
            print(f"[雙J核心] 訊號 '{key}' 落入虛空 (未定義的相對位置)")

# ==============================================================================
# 🛠️ 實體層操作 (Docker Actions)
# ==============================================================================

def run_cmd(cmd):
    print(f"執行系統指令: {cmd}")
    subprocess.run(cmd, shell=True)

def action_install_google_auth():
    print(">>> 正在為 Odoo 安裝 Google 認證模組...")
    # 這是我們之前驗證過的 Docker 指令
    cmd = "docker exec -u root -it wuchangv510-wuchang-web-1 /usr/bin/python3 /usr/bin/odoo -c /etc/odoo/odoo.conf -d admin -i auth_oauth --stop-after-init"
    run_cmd(cmd)
    print(">>> Google 認證模組安裝請求已發送！")

def action_restart_container():
    print(">>> 正在重啟 Odoo 容器以套用變更...")
    run_cmd("docker restart wuchangv510-wuchang-web-1")
    print(">>> 容器重啟完成！")

def action_fix_500_error():
    print(">>> 執行緊急修復 (500 Error Fix)...")
    # 綜合修復指令
    cmd = "docker exec -u root -it wuchangv510-wuchang-web-1 /usr/bin/python3 /usr/bin/odoo -c /etc/odoo/odoo.conf -d admin -u base -i website_payment --stop-after-init"
    run_cmd(cmd)
    action_restart_container()

# ==============================================================================
# 🚀 主程式 (Main)
# ==============================================================================

if __name__ == "__main__":
    # 初始化雙J系統
    dj_system = DoubleJVoiceSystem()

    # 1. 註冊指令 (將意圖寫入時空絕對位置)
    dj_system.register_command(
        ["google", "auth", "login"], 
        action_install_google_auth, 
        "安裝 Google 認證模組 (Install Google Auth)"
    )
    
    dj_system.register_command(
        ["restart", "reboot", "reset"], 
        action_restart_container, 
        "重啟 Odoo 容器 (Restart Container)"
    )
    
    dj_system.register_command(
        ["fix", "repair", "help"], 
        action_fix_500_error, 
        "修復 500 錯誤與支付模組 (Fix 500 Error)"
    )

    # 2. 模擬語音監聽迴圈
    print("\n🎧 雙J耳機已戴上，等待哥哥的指令... (輸入 'exit' 離開)")
    print("   (支援指令: 'google', 'restart', 'fix')")
    
    while True:
        try:
            user_input = input("\n🗣️  請下達語音指令: ")
            if user_input.lower() == 'exit':
                print("👋 雙J系統休眠中...")
                break
            if not user_input:
                continue
                
            # 透過時空系統 O(1) 處理
            dj_system.listen_and_act(user_input)
            
        except KeyboardInterrupt:
            print("\n👋 雙J系統強制休眠")
            break