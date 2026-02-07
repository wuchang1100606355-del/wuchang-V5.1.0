import datetime
import json

# 模擬 Odoo 的 Model 基類
class SimulatedModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def save(self):
        print(f"[{self.__class__.__name__}] Saved: {self.__dict__}")

# ==========================================
# 1. 五常會議系統 (Meeting System) 原型
# ==========================================

class MeetingResolution(SimulatedModel):
    """
    模擬會議決議模型
    """
    def execute(self):
        print(f"\n--- 正在執行決議: {self.name} ---")
        if self.resolution_type == 'fee_change':
            self._execute_fee_change()
        elif self.resolution_type == 'legal_action':
            self._execute_legal_action()
        else:
            print("未知決議類型")
        
        self.state = 'done'
        print(f"--- 決議執行完成: {self.state} ---\n")

    def _execute_fee_change(self):
        params = json.loads(self.execution_params)
        print(f">>> [會計模組] 正在更新管理費...")
        print(f">>> 目標: {params['target_group']}")
        print(f">>> 動作: 調漲 {params['percentage']}%")
        print(f">>> 結果: 所有 {params['target_group']} 的下期帳單已自動更新。")

    def _execute_legal_action(self):
        params = json.loads(self.execution_params)
        print(f">>> [法務模組] 啟動法律程序...")
        print(f">>> 對象: {params['target_resident']}")
        print(f">>> 違規: {params['violation']}")
        # 觸發公文系統
        doc = OfficialDocument(
            name=f"存證信函 - {params['target_resident']} {params['violation']}",
            doc_type='legal_attest',
            recipient=params['target_resident'],
            content_data=params
        )
        doc.generate_content()

# ==========================================
# 2. 五常公文系統 (Official Document System) 原型
# ==========================================

class OfficialDocument(SimulatedModel):
    """
    模擬公文系統模型
    """
    def generate_content(self):
        print(f"--- 正在生成公文: {self.name} ---")
        if self.doc_type == 'legal_attest':
            template = self._get_legal_attest_template()
            content = template.format(
                resident=self.content_data['target_resident'],
                violation=self.content_data['violation'],
                date=datetime.date.today()
            )
            self.content_html = content
            print(f">>> 公文內容預覽:\n{content}")
            print(">>> [系統] PDF 已生成並加密存檔。")
            print(">>> [系統] 已串接郵局 API 準備發送。")

    def _get_legal_attest_template(self):
        return """
        【存證信函】
        
        受文者：{resident} 先生/小姐
        日期：{date}
        
        主旨：台端 於本社區 {violation} 一事，請查照。
        
        說明：
        一、查 台端 為本社區住戶，依據《公寓大廈管理條例》及本社區規約，應遵守相關規定。
        二、經查，台端 {violation} 之行為已嚴重影響社區安寧與公共安全。
        三、特此函告，請於文到七日內改善，否則本管理委員會將依法訴追，絕不寬貸。
        
        五常社區管理委員會 主任委員 (電子簽章)
        """

# ==========================================
# 3. 模擬執行場景 (Simulation)
# ==========================================

def run_simulation():
    print("=== 五常智慧社區系統 - 極限優化原型展示 ===\n")

    # 場景 1: 管委會決議調漲管理費
    resolution1 = MeetingResolution(
        name="113年度管理費調整案",
        resolution_type="fee_change",
        execution_params=json.dumps({
            "target_group": "所有住戶",
            "percentage": 10
        }),
        state="approved"
    )
    resolution1.execute()

    # 場景 2: 針對違規住戶發出存證信函
    resolution2 = MeetingResolution(
        name="住戶王小明長期堆放雜物處置案",
        resolution_type="legal_action",
        execution_params=json.dumps({
            "target_resident": "王小明",
            "violation": "於梯間堆放雜物屢勸不聽"
        }),
        state="approved"
    )
    resolution2.execute()

if __name__ == "__main__":
    run_simulation()
