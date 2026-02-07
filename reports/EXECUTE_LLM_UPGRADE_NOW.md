# 立即執行本地 LLM 模型升級

**建立時間：** 2026-01-20  
**執行計劃：** 按規劃執行，更新本地模型

---

## 🚀 立即執行步驟

### 方式 1：使用 PowerShell 腳本（推薦）⭐⭐⭐⭐⭐

**執行命令：**
```powershell
.\scripts\execute_local_llm_upgrade.ps1
```

**腳本功能：**
- ✅ 自動檢查 Ollama 容器狀態
- ✅ 顯示當前已安裝的模型
- ✅ 提供模型選擇選單
- ✅ 自動下載和測試模型
- ✅ 顯示後續配置步驟

---

### 方式 2：手動執行命令

**1. 檢查 Ollama 容器**
```bash
docker ps | grep ollama
```

**2. 查看當前模型**
```bash
docker exec <容器名稱> ollama list
```

**3. 下載 qwen2:7b 模型（推薦）**
```bash
docker exec <容器名稱> ollama pull qwen2:7b
```

**或下載其他模型：**
```bash
# 輕量級選項
docker exec <容器名稱> ollama pull qwen2:1.5b

# 其他選項
docker exec <容器名稱> ollama pull llama3.1:8b
docker exec <容器名稱> ollama pull mistral:7b
```

**4. 測試模型**
```bash
docker exec <容器名稱> ollama run qwen2:7b "Hello, how are you?"
```

---

## 📋 推薦升級方案

### 推薦：qwen2:7b ⭐⭐⭐⭐⭐

**理由：**
- ✅ 能力提升 14倍（相較於 0.5B）
- ✅ 本地儲存空間充足（地端檔案在雲端）
- ✅ 完全免費（開源模型）
- ✅ 立即可用

**規格：**
- 大小：約 4-5GB
- 記憶體需求：12-16GB
- 參數：7B

---

## 🔧 更新系統配置

### 檔案 1：`config/ai_agents/double_j_appearance.json`

**修改前：**
```json
"llm_model": {
  "local": "qwen2:0.5b",
  "cloud_fallback": "Vertex AI"
}
```

**修改後：**
```json
"llm_model": {
  "local": "qwen2:7b",
  "cloud_fallback": "Vertex AI"
}
```

---

### 檔案 2：`config/ai_agents/double_j_appearance.yaml`

**修改前：**
```yaml
llm_model:
  local: "qwen2:0.5b"
  cloud_fallback: "Vertex AI"
```

**修改後：**
```yaml
llm_model:
  local: "qwen2:7b"
  cloud_fallback: "Vertex AI"
```

---

### 檔案 3：`wuchang_os/addons/wuchang_core/data/system_params.xml`

**找到以下參數並更新：**
```xml
<record id="param_ollama_model" model="ir.config_parameter">
    <field name="key">wuchang.ollama_model</field>
    <field name="value">qwen2:7b</field>  <!-- 從 qwen2:0.5b 改為 qwen2:7b -->
</record>
```

---

## ✅ 執行檢查清單

### 升級前
- [ ] 確認 Ollama 容器運行中
- [ ] 檢查可用儲存空間
- [ ] 確認網路連線正常

### 升級中
- [ ] 下載模型（可能需要 10-30 分鐘）
- [ ] 測試模型功能
- [ ] 確認模型可用

### 升級後
- [ ] 更新系統配置檔案
- [ ] 重新啟動相關服務
- [ ] 測試實際應用場景
- [ ] 驗證效能提升

---

## 💡 執行建議

### 立即執行

**推薦順序：**

1. **執行升級腳本**
   ```powershell
   .\scripts\execute_local_llm_upgrade.ps1
   ```

2. **等待下載完成**
   - qwen2:7b 約 4-5GB，下載時間取決於網路速度

3. **更新配置檔案**
   - 使用文字編輯器更新上述三個檔案

4. **重新啟動服務**
   - 重啟 Odoo 容器或其他相關服務

---

## 📊 預期效果

### 能力提升

| 項目 | 升級前 (0.5B) | 升級後 (7B) | 提升 |
|------|--------------|-------------|------|
| **參數** | 0.5B | 7B | **14倍** |
| **記憶體需求** | 2-4GB | 12-16GB | - |
| **推理能力** | 基礎 | 中高階 | **大幅提升** |
| **複雜任務** | 有限 | 優秀 | **大幅提升** |

---

## ⚠️ 注意事項

### 記憶體考量

**當前系統：32GB RAM**

**建議分配：**
- Odoo: 8GB
- PostgreSQL: 8GB
- Ollama LLM (7B): 12-16GB ⚠️（可能較緊張）
- 其他服務: 4-8GB

**建議：**
- 如果記憶體不足，可先升級到 qwen2:1.5b
- 或等待未來記憶體升級到 64GB

---

## 🎯 執行計劃總結

### 現在執行

1. ✅ **下載 qwen2:7b 模型**
2. ✅ **測試模型功能**
3. ✅ **更新系統配置**

### 之後觀察

1. 📊 **監控記憶體使用量**
2. ⚡ **測試推理速度**
3. 💡 **評估是否需要硬體升級**

### 未來採購

1. 📦 **根據實際使用情況決定採購項目**
2. 💰 **記憶體升級（如需要）**
3. 🚀 **GPU 加速（如需要）**

---

**建立時間：** 2026-01-20  
**執行狀態：** 準備執行 ✅  
**推薦模型：** qwen2:7b ⭐⭐⭐⭐⭐
