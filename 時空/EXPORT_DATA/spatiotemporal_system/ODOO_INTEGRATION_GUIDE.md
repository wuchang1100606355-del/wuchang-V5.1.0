# Odoo 整合指南 - AI 小 J 專用金鑰配置

**版本**: 1.0.0  
**日期**: 2026-01-18  
**用途**: 在 Odoo 中配置 AI 小 J 專用的無限金鑰

---

## 📋 概述

本指南說明如何在 Odoo 系統參數中配置 AI 小 J 專用的無限金鑰，讓時空系統可以從 Odoo 讀取這些金鑰。

---

## 🔑 需要配置的金鑰

### API 金鑰（AI 小 J 專用）

| 系統參數鍵 | 說明 | 範例值 |
|-----------|------|--------|
| `ai.j.openai.api.key` | OpenAI API Key | `sk-...` |
| `ai.j.anthropic.api.key` | Anthropic API Key | `sk-ant-...` |
| `ai.j.google.api.key` | Google API Key | `AIza...` |

### 系統設定

| 系統參數鍵 | 說明 | 預設值 |
|-----------|------|--------|
| `spatiotemporal.system.enabled` | 時空系統啟用 | `True` |
| `ai.j.spatiotemporal.authorization` | 授權等級 | `full` |
| `ai.j.cloud.compute.enabled` | 雲端算力啟用 | `True` |
| `spatiotemporal.system.version` | 系統版本 | `1.0.0` |

---

## 🚀 快速設定

### 方法 1: 自動設定腳本（推薦）

```powershell
# 執行設定腳本
cd "C:\wuchang V5.1.0\spatiotemporal_system"
.\scripts\setup_odoo_keys.ps1
```

或使用 Python 腳本：

```bash
# 在 Odoo shell 中執行
python spatiotemporal_system/scripts/setup_odoo_keys.py
```

### 方法 2: 手動在 Odoo 中設定

1. **登入 Odoo**
   ```
   http://localhost:8069/web/login
   ```

2. **前往系統參數**
   - 設定 > 技術 > 參數 > 系統參數

3. **建立或編輯參數**
   
   點擊「建立」或搜尋現有參數，填入以下值：

   **OpenAI API Key**
   - 鍵: `ai.j.openai.api.key`
   - 值: `您的 OpenAI API Key`

   **Anthropic API Key**
   - 鍵: `ai.j.anthropic.api.key`
   - 值: `您的 Anthropic API Key`

   **Google API Key**
   - 鍵: `ai.j.google.api.key`
   - 值: `您的 Google API Key`

### 方法 3: 透過 Odoo Shell

```python
# 在 Odoo shell 中
env['ir.config_parameter'].sudo().set_param('ai.j.openai.api.key', 'your-key-here')
env['ir.config_parameter'].sudo().set_param('ai.j.anthropic.api.key', 'your-key-here')
env['ir.config_parameter'].sudo().set_param('ai.j.google.api.key', 'your-key-here')
env.cr.commit()
```

---

## ✅ 驗證設定

### 檢查參數是否已設定

```python
# 在 Odoo shell 中
config = env['ir.config_parameter'].sudo()
print("OpenAI:", bool(config.get_param('ai.j.openai.api.key')))
print("Anthropic:", bool(config.get_param('ai.j.anthropic.api.key')))
print("Google:", bool(config.get_param('ai.j.google.api.key')))
```

### 測試時空系統讀取

```python
from spatiotemporal_system.config.ai_j_integration import get_ai_j_spatiotemporal

# 從 Odoo 環境取得整合實例
st = get_ai_j_spatiotemporal(env)

# 查看能力（應顯示從 Odoo 讀取的配置）
capabilities = st.get_capabilities()
print(capabilities)
```

---

## 🔒 安全性說明

### 金鑰保護

- ✅ 所有金鑰儲存在 Odoo 系統參數中
- ✅ 僅供 AI 小 J 使用（參數鍵以 `ai.j.` 開頭）
- ✅ 需要適當權限才能存取
- ✅ 建議設定為 `noupdate="1"` 防止意外修改

### 權限控制

在 Odoo 中，系統參數的存取需要：
- **讀取**: 技術設定權限
- **寫入**: 系統管理員權限

---

## 📝 在 AI 小 J 中使用

### 在 Odoo 模型中

```python
from odoo import models, api
from spatiotemporal_system.config.ai_j_integration import get_ai_j_spatiotemporal

class WuchangAILogic(models.AbstractModel):
    _name = 'wuchang.ai.logic'
    
    @api.model
    def use_spatiotemporal(self):
        # 自動從 Odoo 讀取金鑰
        st = get_ai_j_spatiotemporal(self.env)
        
        # 使用時空功能
        suggestions = st.suggest_event(
            event_type="meeting",
            participants=10,
            duration_hours=2
        )
        
        return suggestions
```

### 在外部腳本中

```python
# 需要先建立 Odoo 環境
import odoo
from odoo import api, SUPERUSER_ID

odoo.tools.config.parse_config(['-d', 'your_database'])
registry = odoo.registry(odoo.tools.config['db_name'])
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    from spatiotemporal_system.config.ai_j_integration import get_ai_j_spatiotemporal
    st = get_ai_j_spatiotemporal(env)
    
    # 使用時空功能
    capabilities = st.get_capabilities()
```

---

## 🔄 更新金鑰

### 更新單一金鑰

```python
# 在 Odoo shell 中
env['ir.config_parameter'].sudo().set_param('ai.j.openai.api.key', 'new-key-here')
env.cr.commit()
```

### 批量更新

```python
# 在 Odoo shell 中
config = env['ir.config_parameter'].sudo()
keys = {
    'ai.j.openai.api.key': 'new-openai-key',
    'ai.j.anthropic.api.key': 'new-anthropic-key',
    'ai.j.google.api.key': 'new-google-key'
}
for key, value in keys.items():
    config.set_param(key, value)
env.cr.commit()
```

---

## 📊 系統參數清單

完整的系統參數清單請參考：
`spatiotemporal_system/odoo_integration/system_params_spatiotemporal.xml`

---

## 🆘 故障排除

### 問題：無法讀取金鑰

**解決方案**:
1. 檢查參數鍵是否正確
2. 確認有適當權限
3. 檢查 Odoo 環境是否正確傳遞

### 問題：金鑰無效

**解決方案**:
1. 確認金鑰格式正確
2. 檢查金鑰是否過期
3. 驗證金鑰權限設定

---

**注意**: 這些金鑰是 AI 小 J 專用的無限金鑰，請妥善保管並僅在 Odoo 系統參數中設定。


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:33:43
---
