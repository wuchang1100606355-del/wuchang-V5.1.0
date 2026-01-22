# 雲端部署指南

## 🚀 快速開始

### 步驟 1：檢查環境

```bash
# 執行部署檢查
python cloud_deployment.py
```

這會自動檢查：
- ✅ Docker 是否安裝
- ✅ Google Drive 路徑是否正確
- ✅ 必要的資料夾是否存在
- ✅ Cloudflare Tunnel 配置狀態

### 步驟 2：選擇部署方式

#### 方式 A：本地部署（不含外網訪問）

```bash
# 啟動本地服務
docker-compose -f docker-compose.unified.yml up -d

# 訪問服務
# 本地: http://localhost:8069
```

#### 方式 B：完整雲端部署（含外網訪問）

**先完成 Cloudflare Tunnel 設定：**

1. **安裝 cloudflared**
   ```bash
   # Windows: 下載 https://github.com/cloudflare/cloudflared/releases
   # 或使用 Docker
   docker pull cloudflare/cloudflared:latest
   ```

2. **登入 Cloudflare**
   ```bash
   cloudflared tunnel login
   ```

3. **建立隧道**
   ```bash
   cloudflared tunnel create wuchang-tunnel
   ```

4. **配置 DNS**
   ```bash
   cloudflared tunnel route dns wuchang-tunnel app.wuchang.org.tw
   ```

5. **複製憑證**
   - 憑證位置：`%USERPROFILE%\.cloudflared\<tunnel-id>.json`
   - 複製到：`cloudflared/credentials.json`

6. **更新配置**
   - 編輯 `cloudflared/config.yml`
   - 將 `<tunnel-id>` 替換為實際的隧道 ID

**然後啟動完整服務：**

```bash
# 啟動完整雲端服務
docker-compose -f docker-compose.cloud.yml up -d

# 訪問服務
# 本地: http://localhost:8069
# 外網: https://app.wuchang.org.tw
```

---

## 📋 部署架構

### 本地部署架構

```
本機/伺服器
    ↓
Docker 容器
    ├── wuchang-web (Odoo) - 端口 8069
    └── wuchang-db (PostgreSQL) - 端口 5432
    ↓
Google Drive 儲存
    └── J:/共用雲端硬碟/五常雲端空間
```

### 完整雲端部署架構

```
Internet
    ↓
Cloudflare Tunnel (cloudflared)
    ↓
Docker 容器網路
    ├── wuchang-web (Odoo) - 端口 8069
    └── wuchang-db (PostgreSQL) - 端口 5432
    ↓
Google Drive 儲存
    └── J:/共用雲端硬碟/五常雲端空間
```

---

## 🔧 配置檔案說明

### docker-compose.unified.yml
- **用途**：本地部署（不含外網訪問）
- **服務**：Odoo + PostgreSQL
- **儲存**：Google Drive 統一儲存

### docker-compose.cloud.yml
- **用途**：完整雲端部署（含外網訪問）
- **服務**：Cloudflare Tunnel + Odoo + PostgreSQL
- **儲存**：Google Drive 統一儲存
- **外網訪問**：通過 Cloudflare Tunnel

---

## ✅ 部署檢查清單

### 部署前檢查

- [ ] Docker 已安裝並運行
- [ ] Google Drive 已安裝並同步
- [ ] Google Drive 路徑正確：`J:\共用雲端硬碟\五常雲端空間`
- [ ] 必要的資料夾已建立
- [ ] 網路連接正常

### 外網訪問檢查（可選）

- [ ] Cloudflare 帳號已建立
- [ ] 域名已添加到 Cloudflare
- [ ] Cloudflare Tunnel 已建立
- [ ] DNS 記錄已配置
- [ ] 憑證檔案已複製

---

## 🚀 部署步驟詳解

### 1. 本地部署

```bash
# 1. 檢查環境
python cloud_deployment.py

# 2. 啟動服務
docker-compose -f docker-compose.unified.yml up -d

# 3. 檢查狀態
docker ps

# 4. 查看日誌
docker logs wuchang-web
docker logs wuchang-db

# 5. 訪問服務
# 瀏覽器打開: http://localhost:8069
```

### 2. 完整雲端部署

```bash
# 1. 完成 Cloudflare Tunnel 設定（見上方）

# 2. 啟動完整服務
docker-compose -f docker-compose.cloud.yml up -d

# 3. 檢查所有服務
docker ps

# 4. 查看 Cloudflare Tunnel 日誌
docker logs wuchang-cloudflared

# 5. 訪問服務
# 本地: http://localhost:8069
# 外網: https://app.wuchang.org.tw
```

---

## 🔍 驗證部署

### 檢查容器狀態

```bash
# 查看所有容器
docker ps

# 查看特定容器
docker ps --filter "name=wuchang"

# 查看容器日誌
docker logs wuchang-web
docker logs wuchang-db
docker logs wuchang-cloudflared
```

### 檢查服務健康

```bash
# 檢查 Odoo 服務
curl http://localhost:8069

# 檢查資料庫連接
docker exec wuchang-db psql -U odoo -d postgres -c "SELECT version();"
```

### 檢查外網訪問（如果已配置）

```bash
# 檢查 Cloudflare Tunnel 狀態
docker logs wuchang-cloudflared

# 測試外網訪問
curl https://app.wuchang.org.tw
```

---

## 🛠️ 故障排除

### 問題 1：容器無法啟動

**解決方案：**
```bash
# 查看詳細錯誤
docker-compose -f docker-compose.unified.yml up

# 檢查端口是否被占用
netstat -an | findstr :8069
netstat -an | findstr :5432

# 停止並重新啟動
docker-compose -f docker-compose.unified.yml down
docker-compose -f docker-compose.unified.yml up -d
```

### 問題 2：Google Drive 路徑錯誤

**解決方案：**
```bash
# 檢查路徑是否存在
Test-Path "J:\共用雲端硬碟\五常雲端空間"

# 重新建立資料夾結構
python unified_storage_setup.py
```

### 問題 3：Cloudflare Tunnel 無法連接

**解決方案：**
```bash
# 檢查配置檔案
cat cloudflared/config.yml

# 檢查憑證檔案
cat cloudflared/credentials.json

# 測試隧道連接
cloudflared tunnel run
```

### 問題 4：外網無法訪問

**解決方案：**
```bash
# 檢查 DNS 記錄
nslookup app.wuchang.org.tw

# 檢查 Cloudflare Tunnel 狀態
docker logs wuchang-cloudflared

# 檢查防火牆設定
```

---

## 📊 監控與維護

### 查看服務狀態

```bash
# 查看所有服務狀態
docker-compose -f docker-compose.cloud.yml ps

# 查看資源使用
docker stats
```

### 備份資料

```bash
# 執行備份
python backup_to_gdrive.py

# 備份會自動同步到 Google Drive
```

### 更新服務

```bash
# 停止服務
docker-compose -f docker-compose.cloud.yml down

# 拉取最新映像
docker-compose -f docker-compose.cloud.yml pull

# 重新啟動
docker-compose -f docker-compose.cloud.yml up -d
```

---

## 🎯 部署完成後

### 本地訪問
- Odoo ERP: http://localhost:8069

### 外網訪問（如果已配置）
- Odoo ERP: https://app.wuchang.org.tw

### 資料儲存
- 共享資料：`J:\共用雲端硬碟\五常雲端空間\containers\`
- 備份資料：`J:\共用雲端硬碟\五常雲端空間\backups\`
- 本地資料庫：`C:\wuchang V5.1.0\wuchang-V5.1.0\local_storage\database\`

---

## 📚 相關檔案

- `docker-compose.unified.yml` - 本地部署配置
- `docker-compose.cloud.yml` - 完整雲端部署配置
- `cloud_deployment.py` - 部署自動化腳本
- `cloudflared/config.yml` - Cloudflare Tunnel 配置
- `cloudflared/README.md` - Cloudflare Tunnel 設定說明
- `unified_storage_config.json` - 統一儲存配置

---

## 🆘 需要幫助？

1. 查看日誌：`docker logs <容器名稱>`
2. 檢查配置：確認所有配置檔案正確
3. 重新部署：`docker-compose down && docker-compose up -d`
4. 查看文件：參考相關的 README 和指南
