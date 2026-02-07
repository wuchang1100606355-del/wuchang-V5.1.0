# LLM 模型升級執行指南

**建立時間：** 2026-01-20  
**目標：** 升級本地模型從 qwen2:0.5b 到 qwen2:7b

---

## 🔍 當前狀況

**檢查結果：** 目前未找到運行中的 Ollama 容器

**可能原因：**
- 容器在其他主機運行
- 容器未啟動
- 容器名稱不同

---

## 📋 執行步驟

### 步驟 1：找到 Ollama 容器

**在運行 Odoo 系統的主機上執行：**

```bash
# 查看所有容器
docker ps -a

# 查找 ollama 相關容器
docker ps -a | findstr ollama
```

**或檢查服務：**
```bash
# 檢查端口 11434 是否被占用
netstat -ano | findstr 11434
```

---

### 步驟 2：下載 qwen2:7b 模型

**找到容器名稱後，執行：**

```bash
docker exec <容器名稱> ollama pull qwen2:7b
```

**範例：**
```bash
docker exec wuchangv510-ollama-1 ollama pull qwen2:7b
```

**預期輸出：**
```
pulling manifest
pulling ... 
verifying sha256 digest
writing manifest
success
```

**下載時間：** 約 10-30 分鐘（取決於網路速度）

---

### 步驟 3：測試模型

**執行測試：**

```bash
docker exec <容器名稱> ollama run qwen2:7b "Hello, how are you?"
```

**預期輸出：**
```
Hello! I'm doing well, thank you for asking...
```

---

### 步驟 4：更新系統配置

**執行配置更新腳本：**

```bash
python scripts/update_llm_config_after_upgrade.py
```

**或手動更新：**

**檔案 1：`config/ai_agents/double_j_appearance.json`**
```json
"llm_model": {
  "local": "qwen2:7b",  // 從 qwen2:0.5b 改為 qwen2:7b
  "cloud_fallback": "Vertex AI"
}
```

**檔案 2：`config/ai_agents/double_j_appearance.yaml`**
```yaml
llm_model:
  local: "qwen2:7b"  # 從 qwen2:0.5b 改為 qwen2:7b
  cloud_fallback: "Vertex AI"
```

**檔案 3：`wuchang_os/addons/wuchang_core/data/system_params.xml`**
- 找到 `wuchang.ollama_model` 參數
- 更新為 `qwen2:7b`

---

## ✅ 驗證升級

### 檢查模型已安裝

```bash
docker exec <容器名稱> ollama list
```

**預期看到：**
```
NAME           ID              SIZE    MODIFIED
qwen2:0.5b     ...            352 MB  ...
qwen2:7b       ...            4.5 GB  ...  ← 新模型
```

---

### 檢查配置已更新

**檢查 JSON 配置：**
```bash
# Windows PowerShell
Select-String -Path "config/ai_agents/double_j_appearance.json" -Pattern "qwen2:7b"
```

---

## 🔄 如果容器未運行

### 啟動現有容器

```bash
# 找到容器名稱
docker ps -a | findstr ollama

# 啟動容器
docker start <容器名稱>
```

---

### 重新建立容器（如需要）

```bash
docker run -d \
  --name wuchangv510-ollama-1 \
  -p 11434:11434 \
  -v ollama-data:/root/.ollama \
  ollama/ollama:latest
```

---

## 📊 升級前後對比

| 項目 | 升級前 | 升級後 |
|------|--------|--------|
| **模型** | qwen2:0.5b | qwen2:7b |
| **參數** | 0.5B | 7B |
| **大小** | 352MB | ~4.5GB |
| **記憶體需求** | 2-4GB | 12-16GB |
| **能力** | 基礎 | 中高階 |

---

## 💡 執行建議

### 推薦執行順序

1. ✅ **確認容器狀態**
   ```bash
   docker ps -a | findstr ollama
   ```

2. ✅ **下載模型**
   ```bash
   docker exec <容器名稱> ollama pull qwen2:7b
   ```

3. ✅ **測試模型**
   ```bash
   docker exec <容器名稱> ollama run qwen2:7b "Hello"
   ```

4. ✅ **更新配置**
   ```bash
   python scripts/update_llm_config_after_upgrade.py
   ```

5. ✅ **重新啟動服務**（如需要）
   ```bash
   docker restart <容器名稱>
   ```

---

## 📝 完整命令範例

**假設容器名稱是 `wuchangv510-ollama-1`：**

```bash
# 1. 確認容器運行
docker ps | findstr ollama

# 2. 查看當前模型
docker exec wuchangv510-ollama-1 ollama list

# 3. 下載新模型
docker exec wuchangv510-ollama-1 ollama pull qwen2:7b

# 4. 測試新模型
docker exec wuchangv510-ollama-1 ollama run qwen2:7b "Hello"

# 5. 更新配置
python scripts/update_llm_config_after_upgrade.py

# 6. 驗證配置
docker exec wuchangv510-ollama-1 ollama list
```

---

## ⚠️ 注意事項

1. **記憶體需求**
   - qwen2:7b 需要 12-16GB 記憶體
   - 如果系統記憶體不足，可能影響其他服務

2. **下載時間**
   - 模型約 4-5GB，下載需要時間
   - 請確保網路連線穩定

3. **儲存空間**
   - 需要額外 4-5GB 儲存空間
   - 地端檔案已在雲端，空間應該充足

---

**建立時間：** 2026-01-20  
**狀態：** 準備執行，等待確認容器狀態 ✅
