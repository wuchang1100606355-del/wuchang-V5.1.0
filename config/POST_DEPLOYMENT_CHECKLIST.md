# 部署後工作項目清單

## 📋 部署後必須完成的工作

### ✅ 階段 1：基本驗證（立即執行）

#### 1.1 服務健康檢查
- [ ] **檢查容器狀態**
  ```bash
  docker ps
  docker-compose -f docker-compose.cloud.yml ps
  ```
  - [ ] 確認所有容器都在運行（Status: Up）
  - [ ] 確認沒有容器異常退出

- [ ] **檢查服務端口**
  ```bash
  netstat -an | findstr :8069
  netstat -an | findstr :5432
  ```
  - [ ] Odoo 服務端口 8069 正常監聽
  - [ ] 資料庫端口 5432 正常監聽

- [ ] **測試服務連接**
  ```bash
  curl http://localhost:8069
  ```
  - [ ] Odoo 服務可以正常訪問
  - [ ] 沒有錯誤訊息

#### 1.2 資料庫連接測試
- [ ] **測試資料庫連接**
  ```bash
  docker exec wuchang-db psql -U odoo -d postgres -c "SELECT version();"
  ```
  - [ ] 資料庫可以正常連接
  - [ ] 可以執行 SQL 查詢

- [ ] **檢查資料庫資料**
  ```bash
  docker exec wuchang-db psql -U odoo -d postgres -c "\dt"
  ```
  - [ ] 確認資料庫表結構正常

#### 1.3 Google Drive 儲存驗證
- [ ] **檢查 Google Drive 路徑**
  ```bash
  Test-Path "J:\共用雲端硬碟\五常雲端空間"
  ```
  - [ ] 路徑存在且可訪問

- [ ] **檢查資料夾結構**
  ```bash
  Get-ChildItem "J:\共用雲端硬碟\五常雲端空間" -Recurse -Directory
  ```
  - [ ] 所有必要的資料夾都存在
  - [ ] 容器可以寫入資料夾

- [ ] **測試檔案寫入**
  ```bash
  # 在容器中測試寫入
  docker exec wuchang-web touch /var/lib/odoo/test.txt
  ```
  - [ ] 可以正常寫入檔案
  - [ ] 檔案出現在 Google Drive 中

---

### ✅ 階段 2：外網訪問設定（如果需要）

#### 2.1 Cloudflare Tunnel 設定
- [ ] **完成 Cloudflare 帳號設定**
  - [ ] 建立 Cloudflare 帳號
  - [ ] 新增網域到 Cloudflare
  - [ ] 更新 DNS 設定

- [ ] **建立 Cloudflare Tunnel**
  ```bash
  cloudflared tunnel login
  cloudflared tunnel create wuchang-tunnel
  ```
  - [ ] 成功登入 Cloudflare
  - [ ] 成功建立隧道

- [ ] **配置 DNS 記錄**
  ```bash
  cloudflared tunnel route dns wuchang-tunnel app.wuchang.org.tw
  ```
  - [ ] DNS 記錄已配置
  - [ ] 域名解析正常

- [ ] **複製憑證檔案**
  - [ ] 找到憑證檔案：`%USERPROFILE%\.cloudflared\<tunnel-id>.json`
  - [ ] 複製到：`cloudflared/credentials.json`
  - [ ] 更新 `cloudflared/config.yml` 中的隧道 ID

- [ ] **測試外網訪問**
  ```bash
  curl https://app.wuchang.org.tw
  ```
  - [ ] 外網可以正常訪問
  - [ ] HTTPS 證書正常

#### 2.2 防火牆設定
- [ ] **檢查防火牆規則**
  - [ ] 確認本地端口已開放（8069, 5432）
  - [ ] 確認 Cloudflare Tunnel 可以正常連接

---

### ✅ 階段 3：安全設定（重要）

#### 3.1 密碼和認證
- [ ] **修改預設密碼**
  - [ ] Odoo 管理員密碼
  - [ ] 資料庫密碼（如果使用預設值）
  - [ ] 其他服務的管理密碼

- [ ] **設定 API 金鑰**
  - [ ] 生成安全的 API 金鑰
  - [ ] 儲存在安全的位置
  - [ ] 不要提交到版本控制

#### 3.2 資料庫安全
- [ ] **檢查資料庫權限**
  ```bash
  docker exec wuchang-db psql -U odoo -d postgres -c "\du"
  ```
  - [ ] 確認只有必要的用戶
  - [ ] 確認權限設定正確

- [ ] **設定資料庫備份**
  - [ ] 配置自動備份腳本
  - [ ] 測試備份還原流程
  - [ ] 確認備份同步到 Google Drive

#### 3.3 網路安全
- [ ] **檢查暴露的端口**
  ```bash
  netstat -an | findstr LISTENING
  ```
  - [ ] 只開放必要的端口
  - [ ] 不需要的服務已關閉

- [ ] **設定訪問控制**
  - [ ] 限制管理介面訪問（如果可能）
  - [ ] 設定 IP 白名單（如果需要）

---

### ✅ 階段 4：監控和日誌（建議）

#### 4.1 日誌設定
- [ ] **檢查日誌輸出**
  ```bash
  docker logs wuchang-web --tail 100
  docker logs wuchang-db --tail 100
  docker logs wuchang-cloudflared --tail 100
  ```
  - [ ] 確認沒有錯誤訊息
  - [ ] 確認日誌正常輸出

- [ ] **設定日誌輪轉**
  - [ ] 配置日誌檔案大小限制
  - [ ] 設定日誌保留時間
  - [ ] 確認日誌儲存在 Google Drive

#### 4.2 監控設定
- [ ] **設定健康檢查**
  - [ ] 配置服務健康檢查端點
  - [ ] 設定監控告警（如果使用 Uptime Kuma）

- [ ] **監控資源使用**
  ```bash
  docker stats
  ```
  - [ ] 檢查 CPU 和記憶體使用
  - [ ] 檢查磁碟空間使用
  - [ ] 設定資源使用告警

---

### ✅ 階段 5：備份和恢復（重要）

#### 5.1 備份設定
- [ ] **配置自動備份**
  - [ ] 設定資料庫自動備份
  - [ ] 設定檔案自動備份
  - [ ] 確認備份腳本正常運行

- [ ] **測試備份流程**
  ```bash
  python backup_to_gdrive.py
  ```
  - [ ] 備份可以正常執行
  - [ ] 備份檔案出現在 Google Drive
  - [ ] 備份檔案可以正常還原

#### 5.2 恢復測試
- [ ] **測試資料恢復**
  - [ ] 模擬資料遺失情況
  - [ ] 測試從備份恢復資料
  - [ ] 確認恢復流程正常

---

### ✅ 階段 6：效能優化（可選）

#### 6.1 資料庫優化
- [ ] **檢查資料庫效能**
  ```bash
  docker exec wuchang-db psql -U odoo -d postgres -c "SELECT * FROM pg_stat_activity;"
  ```
  - [ ] 檢查慢查詢
  - [ ] 優化索引

#### 6.2 容器資源限制
- [ ] **設定資源限制**
  - [ ] 設定 CPU 限制
  - [ ] 設定記憶體限制
  - [ ] 監控資源使用情況

---

### ✅ 階段 7：文檔和記錄（建議）

#### 7.1 更新文檔
- [ ] **記錄部署資訊**
  - [ ] 記錄部署時間
  - [ ] 記錄部署版本
  - [ ] 記錄配置變更

- [ ] **更新操作手冊**
  - [ ] 更新服務訪問方式
  - [ ] 更新管理員資訊
  - [ ] 更新故障排除指南

#### 7.2 建立運行記錄
- [ ] **建立運行日誌**
  - [ ] 記錄服務啟動時間
  - [ ] 記錄重要操作
  - [ ] 記錄問題和解決方案

---

## 🎯 優先級分類

### 🔴 高優先級（必須完成）
1. 服務健康檢查
2. 資料庫連接測試
3. Google Drive 儲存驗證
4. 修改預設密碼
5. 設定資料庫備份

### 🟡 中優先級（建議完成）
1. Cloudflare Tunnel 設定（如果需要外網訪問）
2. 日誌設定
3. 監控設定
4. 測試備份恢復

### 🟢 低優先級（可選）
1. 效能優化
2. 文檔更新
3. 資源限制設定

---

## 📝 快速檢查腳本

建立 `check_deployment.py` 自動檢查所有項目：

```bash
python check_deployment.py
```

這會自動檢查：
- ✅ 容器狀態
- ✅ 服務連接
- ✅ 資料庫健康
- ✅ Google Drive 儲存
- ✅ 外網訪問（如果已配置）

---

## 🆘 常見問題處理

### 問題 1：容器無法啟動
**檢查項目：**
- [ ] 檢查 Docker 是否運行
- [ ] 檢查端口是否被占用
- [ ] 檢查日誌錯誤訊息
- [ ] 檢查 Google Drive 路徑

### 問題 2：服務無法訪問
**檢查項目：**
- [ ] 檢查容器狀態
- [ ] 檢查端口監聽
- [ ] 檢查防火牆設定
- [ ] 檢查服務日誌

### 問題 3：資料庫連接失敗
**檢查項目：**
- [ ] 檢查資料庫容器狀態
- [ ] 檢查資料庫密碼
- [ ] 檢查網路連接
- [ ] 檢查資料庫日誌

---

## 📚 相關資源

- `CLOUD_DEPLOYMENT_GUIDE.md` - 完整部署指南
- `EXTERNAL_ACCESS_SETUP.md` - 外網訪問設定
- `UNIFIED_STORAGE_GUIDE.md` - 統一儲存指南
- `backup_to_gdrive.py` - 備份腳本

---

## ✅ 完成確認

部署後工作完成後，請確認：

- [ ] 所有高優先級項目已完成
- [ ] 服務可以正常訪問
- [ ] 備份可以正常執行
- [ ] 安全設定已完成
- [ ] 文檔已更新

**部署完成時間：** _______________

**完成人員：** _______________

**備註：** _______________
