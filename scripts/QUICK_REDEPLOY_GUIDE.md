# 快速重新部署指南

**執行時間：** 約 30-60 分鐘  
**目的：** 完整卸載並重新部署所有容器，升級 LLM 模型

---

## 🚀 快速執行（兩步完成）

### 步驟 1：完整卸載

```powershell
.\scripts\complete_container_cleanup.ps1
```

**執行時：**
- 輸入 `YES` 確認
- 等待備份和卸載完成

---

### 步驟 2：重新部署

```powershell
.\scripts\redeploy_containers.ps1
```

**執行時：**
- 選擇 docker-compose 檔案（預設：docker-compose.yml）
- 輸入 `Y` 確認
- 等待容器啟動和模型下載

---

## 📋 完整命令

```powershell
# 1. 卸載所有容器
.\scripts\complete_container_cleanup.ps1

# 2. 重新部署（包含模型升級）
.\scripts\redeploy_containers.ps1
```

---

## ✅ 驗證部署

### 檢查容器

```bash
docker ps
```

**預期看到：**
- wuchangv510-wuchang-web-1 (Odoo)
- wuchangv510-db-1 (PostgreSQL)
- wuchangv510-ollama-1 (Ollama) ⭐
- 其他服務容器

---

### 檢查 LLM 模型

```bash
docker exec wuchangv510-ollama-1 ollama list
```

**預期看到：**
- qwen2:0.5b
- qwen2:7b ✅（新模型）

---

### 測試服務

- **Odoo:** http://localhost:8069
- **Ollama API:** http://localhost:11434
- **Portainer:** http://localhost:9000

---

**詳細指南：** `reports/COMPLETE_CONTAINER_CLEANUP_AND_REDEPLOY.md`
