# Odoo 整合模組 - AI 小 J 專用金鑰配置

**版本**: 1.0.0  
**用途**: 在 Odoo 中配置 AI 小 J 專用的無限金鑰

---

## 📋 功能說明

本模組提供：

1. **系統參數配置**: 在 Odoo 中設定 AI 小 J 專用金鑰
2. **自動載入**: 時空系統自動從 Odoo 讀取金鑰
3. **專用授權**: 確保金鑰僅供 AI 小 J 使用

---

## 🔑 配置的金鑰

### API 金鑰（AI 小 J 專用）

- `ai.j.openai.api.key` - OpenAI API Key
- `ai.j.anthropic.api.key` - Anthropic API Key  
- `ai.j.google.api.key` - Google API Key

### 系統設定

- `spatiotemporal.system.enabled` - 時空系統啟用
- `ai.j.cloud.compute.enabled` - 雲端算力啟用
- `ai.j.spatiotemporal.authorization` - 授權等級

---

## 📦 安裝方式

### 方法 1: 作為 Odoo 模組安裝

1. 將 `odoo_integration` 目錄複製到 Odoo addons 目錄
2. 在 Odoo 中更新應用程式清單
3. 安裝「時空系統整合 - AI 小 J 專用」模組

### 方法 2: 手動載入系統參數

```bash
# 在 Odoo 中執行
odoo-bin -c odoo.conf -d your_database -u spatiotemporal_integration
```

---

## ⚙️ 設定金鑰

### 在 Odoo 介面中設定

1. 登入 Odoo
2. 前往「設定」>「技術」>「參數」>「系統參數」
3. 編輯以下參數並填入金鑰：
   - `ai.j.openai.api.key`
   - `ai.j.anthropic.api.key`
   - `ai.j.google.api.key`

### 透過 Python 設定

```python
# 在 Odoo shell 中
env['ir.config_parameter'].sudo().set_param('ai.j.openai.api.key', 'your-key-here')
env['ir.config_parameter'].sudo().set_param('ai.j.anthropic.api.key', 'your-key-here')
env['ir.config_parameter'].sudo().set_param('ai.j.google.api.key', 'your-key-here')
```

---

## 🔒 安全性

- 所有金鑰儲存在 Odoo 系統參數中
- 僅供 AI 小 J 使用
- 需要適當權限才能存取
- 建議設定為 `noupdate="1"` 防止意外修改

---

## 📝 使用範例

### 在 AI 小 J 中使用

```python
from odoo import models, api
from spatiotemporal_system.config.ai_j_integration import get_ai_j_spatiotemporal

class WuchangAILogic(models.AbstractModel):
    _name = 'wuchang.ai.logic'
    
    @api.model
    def use_spatiotemporal(self):
        # 取得時空整合實例（自動從 Odoo 讀取金鑰）
        st = get_ai_j_spatiotemporal(self.env)
        
        # 使用時空功能
        suggestions = st.suggest_event(
            event_type="meeting",
            participants=10,
            duration_hours=2
        )
        
        return suggestions
```

---

## ✅ 驗證設定

### 檢查金鑰是否已設定

```python
# 在 Odoo shell 中
config = env['ir.config_parameter'].sudo()
print("OpenAI:", bool(config.get_param('ai.j.openai.api.key')))
print("Anthropic:", bool(config.get_param('ai.j.anthropic.api.key')))
print("Google:", bool(config.get_param('ai.j.google.api.key')))
```

### 測試時空系統

```python
from spatiotemporal_system.config.ai_j_integration import get_ai_j_spatiotemporal

st = get_ai_j_spatiotemporal(env)
capabilities = st.get_capabilities()
print(capabilities)
```

---

**注意**: 這些金鑰是 AI 小 J 專用的無限金鑰，請妥善保管。


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:33:44
---
