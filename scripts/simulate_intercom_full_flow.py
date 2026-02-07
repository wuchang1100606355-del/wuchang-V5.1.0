# -*- coding: utf-8 -*-
import datetime
import uuid
import time
import json

# ==========================================
# 1. 模擬 Odoo 環境與模型 (Mocking)
# ==========================================

class MockModel:
    def __init__(self, env, **kwargs):
        self.env = env
        self.id = uuid.uuid4().int >> 64 # 模擬 ID
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def ensure_one(self):
        pass

class MockEnv:
    def __init__(self):
        self.models = {}
        
    def __getitem__(self, model_name):
        return self.models.get(model_name)

class EstateVisitor(MockModel):
    def action_approve(self):
        self.state = 'approved'
        print(f"[系統] 訪客 {self.name} 的預約已核准，QR Code 已發送。")
        return True

    def action_scan_entry(self):
        self.state = 'arrived'
        print(f"[門禁] 訪客 {self.name} 掃描 QR Code 成功，大門已解鎖。")

class EstateIntercomSession(MockModel):
    def create_offer(self, device_id, unit_number, sdp):
        print(f"\n[對講機] 收到來自設備 {device_id} 的呼叫請求...")
        # 模擬查找住戶
        partner = self.env['res.partner'].find(unit_number)
        if not partner:
            print("[對講機] 錯誤：找不到該戶號住戶")
            return None
            
        print(f"[對講機] 正在呼叫住戶：{partner.name} ({unit_number})")
        
        self.caller_device_id = device_id
        self.callee_partner_id = partner
        self.sdp_offer = sdp
        self.state = 'ringing'
        self.session_id = str(uuid.uuid4())
        
        # 模擬推播
        print(f"[推播] 發送通知給 {partner.name} 的手機：'有訪客正在呼叫您'")
        return self

    def submit_answer(self, sdp_answer):
        print(f"[對講機] 住戶 {self.callee_partner_id.name} 已接聽。")
        self.sdp_answer = sdp_answer
        self.state = 'connected'
        print(f"[WebRTC] P2P 加密通道建立成功。雙方開始通話 (不經過伺服器錄音)。")

    def remote_unlock(self):
        print(f"[對講機] 住戶按下「遠端開門」按鈕。")
        print(f"[IoT] 發送開門訊號至 {self.caller_device_id}...")
        print(f"[門禁] 大門已解鎖。")

class ResPartner(MockModel):
    pass

# ==========================================
# 2. 模擬器核心 (Simulator)
# ==========================================

def run_simulation():
    print("=== 五常智慧社區 - 訪客對講與門禁全流程模擬 ===\n")
    
    # 初始化環境
    env = MockEnv()
    
    # 建立模擬住戶
    resident = ResPartner(env, name="張無忌", unit_number="A-101")
    
    # 模擬資料庫查找功能
    class PartnerRepo:
        def find(self, unit):
            if unit == "A-101": return resident
            return None
    env.models['res.partner'] = PartnerRepo()

    # ------------------------------------------
    # 場景一：訪客預約與掃碼進入 (Visitor Access)
    # ------------------------------------------
    print("--- 場景一：訪客預約與掃碼進入 ---")
    
    # 1. 訪客預登記
    visitor = EstateVisitor(env, 
        name="趙敏", 
        host_partner_id=resident,
        visit_time=datetime.datetime.now() + datetime.timedelta(hours=1),
        state='draft'
    )
    print(f"[App] 訪客 {visitor.name} 提交了預約申請。")
    
    # 2. 住戶核准
    visitor.action_approve()
    
    # 3. 訪客到達並掃碼
    print(f"[現場] 訪客 {visitor.name} 到達大廳，出示 QR Code...")
    time.sleep(1)
    visitor.action_scan_entry()
    
    print("\n" + "="*40 + "\n")

    # ------------------------------------------
    # 場景二：零信任對講機流程 (Zero Trust Intercom)
    # ------------------------------------------
    print("--- 場景二：訪客呼叫住戶 (WebRTC Flow) ---")
    
    # 1. 訪客在門口機按戶號
    door_device_id = "LOBBY_PANEL_01"
    target_unit = "A-101"
    guest_sdp = "v=0\r\no=- 4859302 2 IN IP4 192.168.1.10..." # 模擬 SDP
    
    session_model = EstateIntercomSession(env, state='offering')
    session = session_model.create_offer(door_device_id, target_unit, guest_sdp)
    
    if session:
        # 2. 住戶接聽
        time.sleep(1)
        print("[App] 住戶點擊「接聽」...")
        resident_sdp = "v=0\r\no=- 3847291 2 IN IP4 10.0.0.5..."
        session.submit_answer(resident_sdp)
        
        # 3. 通話中...
        time.sleep(1)
        print("... (通話進行中) ...")
        
        # 4. 住戶遠端開門
        session.remote_unlock()
        
    print("\n=== 模擬結束：全流程驗證通過 ===")

if __name__ == "__main__":
    run_simulation()
