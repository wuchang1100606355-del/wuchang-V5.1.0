# 完整容器卸載與重新部署指南

**建立時間：** 2026-01-20  
**目的：** 完整卸載容器後重新部署，包含 LLM 模型升級

---

## ⚠️ 重要提醒

### 執行前準備

1. **備份重要數據**
   - ✅ 資料庫備份（腳本會自動執行）
   - ✅ 配置檔案備份
   - ✅ 上傳檔案備份

2. **確認服務狀態**
   - 確認當前沒有重要任務在執行
   - 通知相關使用者（如需要）

3. **預留時間**
   - 卸載：5-10 分鐘
   - 重新部署：10-20 分鐘
   - 模型下載：10-30 分鐘
   - **總計：約 30-60 分鐘**

---

## 📋 執行步驟

### 階段 1：完整卸載容器

**執行腳本：**
```powershell
.\scripts\complete_container_cleanup.ps1
```

**腳本功能：**
- ✅ 自動備份資料庫
- ✅ 停止所有容器
- ✅ 移除所有容器
- ✅ 清理未使用的資源
- ✅ 保留數據和配置檔案

**執行過程：**
1. 確認執行（輸入 'YES'）
2. 自動備份資料庫
3. 列出所有容器
4. 停止所有容器
5. 移除所有容器
6. 清理未使用的資源

---

### 階段 2：重新部署容器

**執行腳本：**
```powershell
.\scripts\redeploy_containers.ps1
```

**腳本功能：**
- ✅ 選擇 docker-compose 檔案
- ✅ 啟動所有容器
- ✅ 自動下載 qwen2:7b 模型
- ✅ 測試模型功能
- ✅ 更新系統配置

**執行過程：**
1. 選擇 docker-compose 檔案
2. 啟動容器
3. 檢查容器狀態
4. 下載 LLM 模型（qwen2:7b）
5. 測試模型
6. 更新系統配置

---

## 🔍 詳細流程

### 步驟 1：執行卸載

```powershell
# 執行卸載腳本
.\scripts\complete_container_cleanup.ps1
```

**預期輸出：**
- 備份目錄建立
- 資料庫備份完成
- 容器停止和移除
- 清理完成

---

### 步驟 2：執行重新部署

```powershell
# 執行重新部署腳本
.\scripts\redeploy_containers.ps1
```

**預期輸出：**
- 容器啟動成功
- 模型下載完成
- 配置更新完成

---

## 📊 容器清單

### 預期重新部署的容器

根據之前的報告，系統包含以下容器：

1. **wuchangv510-wuchang-web-1** - Odoo ERP
2. **wuchangv510-db-1** - PostgreSQL 資料庫
3. **wuchangv510-ollama-1** - Ollama LLM ⭐（重點）
4. **wuchangv510-open-webui-1** - Open WebUI
5. **wuchangv510-portainer-1** - Portainer
6. **wuchangv510-caddy-1** - Caddy 反向代理
7. **wuchangv510-caddy-ui-1** - Caddy UI
8. **wuchangv510-cloudflared-1** - Cloudflare Tunnel
9. **wuchangv510-uptime-kuma-1** - Uptime Kuma

---

## ✅ 驗證檢查

### 部署後檢查

**1. 檢查容器狀態**
```bash
docker ps
```

**預期：** 所有容器狀態為 "Up"

---

**2. 檢查服務連接**

- **Odoo:** http://localhost:8069
- **Portainer:** http://localhost:9000
- **Open WebUI:** http://localhost:8080
- **Uptime Kuma:** http://localhost:3001

---

**3. 檢查 LLM 模型**

```bash
docker exec <ollama容器名稱> ollama list
```

**預期看到：**
- qwen2:0.5b（舊模型）
- qwen2:7b（新模型）✅

---

**4. 測試 LLM 模型**

```bash
docker exec <ollama容器名稱> ollama run qwen2:7b "Hello"
```

---

**5. 檢查配置檔案**

確認以下檔案已更新：
- `config/ai_agents/double_j_appearance.json`
- `config/ai_agents/double_j_appearance.yaml`

---

## 🔄 數據恢復

### 如果需要恢復數據

**資料庫恢復：**
```bash
# 找到備份檔案
# 位置：backups/container_cleanup_YYYYMMDD_HHMMSS/database_backup_*.sql

# 恢復資料庫
docker exec -i <db容器名稱> psql -U odoo -d postgres < <備份檔案>
```

---

## ⚠️ 注意事項

### 數據安全

1. **備份位置**
   - 備份會自動儲存在 `backups/container_cleanup_YYYYMMDD_HHMMSS/`
   - 請確認備份檔案存在

2. **Volume 數據**
   - Docker Volume 數據會保留
   - 容器移除不會影響 Volume

3. **配置檔案**
   - 所有配置檔案會保留
   - 不會被刪除

---

### 可能遇到的問題

**問題 1：容器啟動失敗**
- 檢查 docker-compose 檔案
- 查看容器日誌：`docker logs <容器名稱>`
- 檢查端口衝突

**問題 2：模型下載失敗**
- 檢查網路連線
- 確認儲存空間充足
- 稍後手動執行：`docker exec <容器> ollama pull qwen2:7b`

**問題 3：配置更新失敗**
- 手動更新配置檔案
- 參考：`reports/EXECUTE_LLM_UPGRADE_NOW.md`

---

## 📋 執行檢查清單

### 卸載前

- [ ] 確認沒有重要任務在執行
- [ ] 通知相關使用者（如需要）
- [ ] 確認備份腳本可用
- [ ] 確認有足夠時間（30-60分鐘）

### 卸載中

- [ ] 執行卸載腳本
- [ ] 確認備份完成
- [ ] 確認容器已停止
- [ ] 確認容器已移除

### 重新部署中

- [ ] 選擇正確的 docker-compose 檔案
- [ ] 確認容器啟動成功
- [ ] 確認模型下載完成
- [ ] 確認配置更新完成

### 部署後

- [ ] 檢查所有服務正常運行
- [ ] 測試 LLM 模型功能
- [ ] 驗證系統功能
- [ ] 檢查日誌是否有錯誤

---

## 🎯 預期結果

### 完成後狀態

**容器：**
- ✅ 所有容器重新部署
- ✅ 容器狀態正常
- ✅ 服務可正常訪問

**LLM 模型：**
- ✅ qwen2:7b 已下載
- ✅ 模型測試通過
- ✅ 系統配置已更新

**系統：**
- ✅ 所有服務正常運行
- ✅ 數據完整保留
- ✅ 配置正確更新

---

## 💡 執行建議

### 推薦執行時間

- **最佳時間：** 非工作時間或維護時段
- **預留時間：** 至少 1 小時
- **通知：** 如有使用者，請提前通知

### 執行順序

1. **先執行卸載** - 確保數據備份
2. **再執行部署** - 重新建立環境
3. **最後驗證** - 確認一切正常

---

## ✅ 總結

### 執行命令

```powershell
# 1. 完整卸載
.\scripts\complete_container_cleanup.ps1

# 2. 重新部署（包含模型升級）
.\scripts\redeploy_containers.ps1
```

### 預期時間

- **卸載：** 5-10 分鐘
- **部署：** 10-20 分鐘
- **模型下載：** 10-30 分鐘
- **總計：** 30-60 分鐘

---

**建立時間：** 2026-01-20  
**狀態：** 準備執行 ✅  
**建議：** 在非工作時間執行，預留足夠時間 ⭐⭐⭐⭐⭐
