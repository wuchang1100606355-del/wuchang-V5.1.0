# 五常智慧會議系統 (Wuchang Intelligent Meeting System) - 設計規格書

> **專利核心技術**：Code as Law (程式即法律) 自動執行架構
> **目標**：超越市面競品（如智生活），將會議從「紀錄工具」升級為「治理自動化核心」。

## 1. 系統概述

本系統旨在解決傳統社區管理中「決議難以落實」與「紀錄難以追溯」的痛點。透過將會議決議結構化，系統能直接驅動 Odoo ERP 的運作，實現「開完會，事就做完了」的極致效率。

## 2. 核心功能模組

### 2.1 智能議程管理 (Smart Agenda)
- **自動排程**：根據法規（如區權會每年一次、管委會每月一次）自動生成會議行事曆。
- **議題收集池**：住戶透過 App 提交的「意見反應」自動轉為待審議題，避免被吃案。
- **引用法源**：每個議題自動關聯《公寓大廈管理條例》或《社區規約》相關條文，供委員決策參考（AI 輔助）。

### 2.2 決議即執行引擎 (Resolution-to-Action Engine) **[核心差異化功能]**
這是本系統最強大的功能，將自然語言的決議轉化為系統指令。

| 決議類型 | 傳統方式 | 五常系統方式 (自動化) |
| :--- | :--- | :--- |
| **財務調整** | 人工修改 Excel，下月生效 | **Action**: `account.move` <br> **Logic**: 自動調整下期管理費金額，並發送通知。 |
| **修繕執行** | 打電話叫廠商，手寫紀錄 | **Action**: `maintenance.request` <br> **Logic**: 自動生成維修工單，派發給簽約廠商，並追蹤完工照。 |
| **規約變更** | 修改 Word 檔，印出來貼公告 | **Action**: `document.update` <br> **Logic**: 自動更新電子規約版本，推播給全體住戶，舊版自動歸檔。 |
| **違規處置** | 保全去貼勸導單 | **Action**: `legal.warning` <br> **Logic**: 自動生成存證信函 PDF，進入公文發送流程。 |

### 2.3 AI 會議秘書 (AI Meeting Secretary)
- **即時語音轉錄**：會議錄音即時轉文字（Local Whisper 模型，保障隱私）。
- **決議提取**：LLM 自動分析對話，提取「決議事項」與「待辦人」。
- **防呆機制**：若決議違反法規（如：決議禁止養寵物但未經規約程序），AI 立即發出「適法性警告」。

## 3. 資料結構設計 (Data Structure)

```python
class MeetingResolution(models.Model):
    _name = 'wuchang.meeting.resolution'
    _description = '會議決議'

    name = fields.Char(string='決議標題', required=True)
    meeting_id = fields.Many2one('wuchang.meeting', string='所屬會議')
    
    # 專利核心：決議類型與自動化參數
    resolution_type = fields.Selection([
        ('fee_change', '費用調整'),
        ('maintenance', '修繕工程'),
        ('rule_change', '規約變更'),
        ('legal_action', '法務行動'),
        ('general', '一般事項')
    ], string='決議類型', required=True)
    
    # 結構化參數 (JSON)，用於驅動不同模組
    execution_params = fields.Json(string='執行參數')
    # 例如: {"target_model": "account.move", "action": "update_price", "value": 1000}

    # 執行狀態
    state = fields.Selection([
        ('draft', '草稿'),
        ('approved', '已通過'),
        ('executing', '執行中'),
        ('done', '已完成'),
        ('failed', '執行失敗')
    ], default='draft')
    
    execution_log = fields.Text(string='執行日誌')
```

## 4. 使用者體驗 (UX)

1.  **會前**：委員收到 App 通知，點選連結預覽議程與相關報表（財務報表自動掛載）。
2.  **會中**：投影大螢幕顯示「即時決議看板」，主委喊「通過」，秘書點一下，系統顯示「已排程執行」。
3.  **會後**：住戶 App 收到「會議懶人包」（AI 生成），並看到決議執行進度條。

## 5. 與智生活之比較

| 功能 | 智生活 | 五常智慧系統 |
| :--- | :--- | :--- |
| **會議記錄** | PDF 下載 (死文件) | **活數據 (Live Data)**，可追蹤、可執行 |
| **執行力** | 靠人工 | **靠系統自動化 (Automation)** |
| **法規依循** | 無 | **內建法規資料庫**，防範違法決議 |
