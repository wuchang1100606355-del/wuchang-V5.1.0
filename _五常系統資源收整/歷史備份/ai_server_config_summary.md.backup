# AI 伺服器配置摘要

**設置時間**: 2026-01-07  
**目標端點**: `http://host.docker.internal:11434`

---

## ✅ 已完成的配置

### 1. 配置文件更新

已更新 `wuchang_os/addons/wuchang_core/data/system_params.xml`：

```xml
<!-- LLM 基礎 URL (用於 Ollama API 調用) -->
<record id="param_llm_base_url" model="ir.config_parameter">
    <field name="key">wuchang.llm_base_url</field>
    <field name="value">http://host.docker.internal:11434</field>
</record>

<!-- LLM 主機 (用於其他配置) -->
<record id="param_llm_host" model="ir.config_parameter">
    <field name="key">wuchang.llm.host</field>
    <field name="value">host.docker.internal:11434</field>
</record>
```

---

## 📋 配置項目

| 參數 | 值 | 用途 |
|------|-----|------|
| `wuchang.llm_base_url` | `http://host.docker.internal:11434` | Ollama API 調用端點 |
| `wuchang.llm.host` | `host.docker.internal:11434` | LLM 主機配置 |
| `wuchang.ai_mode` | `local_ollama` | AI 模式（本地優先） |

---

## 🔧 如何應用配置

### 方法一：模組升級（推薦）

如果配置是在模組初始化文件中，可以通過升級模組來應用：

```powershell
# 升級 wuchang_core 模組
docker-compose exec -T wuchang-web odoo -d <database_name> -u wuchang_core
```

### 方法二：手動設置（通過 Odoo 界面）

1. 登入 Odoo 後台
2. 進入 `設置 > 技術 > 參數 > 系統參數`
3. 搜索並編輯以下參數：
   - `wuchang.llm_base_url` = `http://host.docker.internal:11434`
   - `wuchang.llm.host` = `host.docker.internal:11434`
   - `wuchang.ai_mode` = `local_ollama`

### 方法三：SQL 直接更新

如果需要立即生效，可以通過 SQL 直接更新：

```sql
UPDATE ir_config_parameter 
SET value = 'http://host.docker.internal:11434' 
WHERE key = 'wuchang.llm_base_url';

UPDATE ir_config_parameter 
SET value = 'host.docker.internal:11434' 
WHERE key = 'wuchang.llm.host';

UPDATE ir_config_parameter 
SET value = 'local_ollama' 
WHERE key = 'wuchang.ai_mode';
```

---

## ✅ 驗證配置

### 1. 檢查配置文件

```bash
# 確認配置文件已更新
cat wuchang_os/addons/wuchang_core/data/system_params.xml | grep -A 2 "llm_base_url"
cat wuchang_os/addons/wuchang_core/data/system_params.xml | grep -A 2 "llm.host"
```

### 2. 檢查 Odoo 系統參數

登入 Odoo 後台，確認系統參數已正確設置。

### 3. 測試 AI 功能

嘗試使用 Mail Bot 或其他 AI 功能，確認能正常連接到 Ollama 服務。

---

## 📝 相關文件

- **配置文件**: `wuchang_os/addons/wuchang_core/data/system_params.xml`
- **AI 邏輯**: `wuchang_os/addons/wuchang_core/models/ai_logic.py`
- **設定介面**: `wuchang_os/addons/wuchang_core/models/settings.py`

---

## 💡 注意事項

1. **Docker 網絡**: `host.docker.internal` 用於 Docker 容器訪問主機服務
2. **Ollama 服務**: 確保 Ollama 服務運行在 `localhost:11434`
3. **重啟服務**: 如果配置未生效，可能需要重啟 Odoo 服務

---

**配置狀態**: ✅ 配置文件已更新  
**下一步**: 升級模組或手動設置系統參數以應用配置
