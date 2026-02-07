# 五常自動化公文與法務系統 (Wuchang Automated Official Document System) - 設計規格書

> **專利核心技術**：法務軍工廠 (Legal Arsenal) 自動生成引擎
> **目標**：賦予管委會與物業公司「自動化法律執行力」，降低法律成本，提升治理威信。

## 1. 系統概述

本系統將傳統需要律師或代書處理的基礎法律程序自動化。透過標準化的法律模板與 Odoo 資料庫的結合，系統能一鍵生成具備法律效力的文件，並自動管理發文流程。這不僅是「文書處理」，而是「權利主張」的自動化。

## 2. 核心功能模組

### 2.1 智能公文生成器 (Intelligent Document Generator)
- **多模板支援**：
    - **內部公告**：停水通知、施工公告（自動發送 App 推播 + 生成 PDF 供列印）。
    - **政府公函**：致函區公所、建管處、消防局的標準公文格式（函）。
    - **法律文件**：存證信函、支付命令聲請狀、強制執行聲請狀。
- **動態資料填充**：自動從住戶資料庫抓取姓名、地址、欠費金額、違規事項，填入法律模板。

### 2.2 法規戰自動化流程 (Legal Warfare Automation)
針對欠繳管理費或重大違規，系統執行以下標準作業程序 (SOP)：

1.  **階段一：溫馨提醒 (自動)**
    - 條件：欠費超過 1 個月。
    - 動作：App 推播 + Email 通知。
2.  **階段二：正式催告 (自動)**
    - 條件：欠費超過 2 個月。
    - 動作：生成**「催繳通知單」** PDF，通知物業列印投遞信箱，並拍照上傳存證。
3.  **階段三：存證信函 (半自動)**
    - 條件：欠費超過 3 個月 (符合公寓大廈管理條例第 21 條)。
    - 動作：生成**「存證信函」**，主委電子簽核後，系統串接郵局電子郵務系統（或生成格式供列印交寄）。
4.  **階段四：支付命令 (半自動)**
    - 條件：存證信函送達後 7 日仍未繳。
    - 動作：生成**「支付命令聲請狀」**，包含債權計算書、證物清單（系統自動彙整催繳紀錄與規約）。

### 2.3 公文收發管理 (Document Archive)
- **電子收發文簿**：自動編列文號（如：113常勝字第001號），取代紙本登記簿。
- **OCR 辨識歸檔**：收到的紙本公文掃描後，AI 自動辨識主旨、發文單位，並分派給相關委員傳閱。

## 3. 資料結構設計 (Data Structure)

```python
class OfficialDocument(models.Model):
    _name = 'wuchang.official.document'
    _description = '公文與法律文件'

    name = fields.Char(string='主旨', required=True)
    doc_type = fields.Selection([
        ('announcement', '內部公告'),
        ('official_letter', '對外公函'),
        ('legal_attest', '存證信函'),
        ('court_order', '支付命令')
    ], string='公文類型')
    
    # 發文資訊
    doc_number = fields.Char(string='發文字號', readonly=True) # 自動編碼
    recipient_id = fields.Many2one('res.partner', string='受文者')
    
    # 內容生成
    template_id = fields.Many2one('wuchang.doc.template', string='使用模板')
    content_html = fields.Html(string='公文內容')
    generated_pdf = fields.Binary(string='PDF 文件')
    
    # 流程狀態
    state = fields.Selection([
        ('draft', '草稿'),
        ('review', '主委審核中'),
        ('sent', '已發送/已交寄'),
        ('delivered', '已送達'),
        ('closed', '結案')
    ], default='draft')
    
    # 證據鏈 (Evidence Chain)
    attachment_ids = fields.Many2many('ir.attachment', string='附件/證物')
    delivery_proof = fields.Binary(string='送達回執')
```

## 4. 效益分析

- **省時**：過去處理一個欠費戶的法律程序需要 3-5 小時（找律師、寫狀紙、跑郵局），現在僅需 **5 分鐘**（系統生成、確認、列印）。
- **省錢**：大幅減少律師諮詢費與代書費。
- **威嚇力**：標準化、專業的法律文件能對違規住戶產生心理壓力，提高配合度。

## 5. 專利點總結

本系統的創新在於**「將法律程序封裝為軟體服務」 (Legal Process as a Service)**。不同於市面上的「公文管理系統」僅做收發文登記，五常系統能**主動生產**具備戰略價值的法律武器，是社區治理的強大後盾。
