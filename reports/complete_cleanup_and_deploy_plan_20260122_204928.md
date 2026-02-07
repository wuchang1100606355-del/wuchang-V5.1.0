# 完整容器卸載與重新部署計畫

**建立時間:** 2026-01-22 20:49:28
**狀態:** ⚠️ 等待 Docker Desktop 啟動

---

## 📋 執行計畫

### 前置條件
- [x] ✅ 容器卸載腳本已準備
- [x] ✅ 部署腳本已準備
- [ ] ⚠️ **Docker Desktop 需要啟動**（目前未運行）

---

## 階段 1: 完整卸載 🧹

### 1.1 停止所有容器
`powershell
docker-compose down -v
`
**說明:** 停止所有容器並移除相關 Volumes

### 1.2 移除相關 Volumes
`powershell
docker volume ls -q --filter "name=wuchang" | ForEach-Object { docker volume rm  }
`
**說明:** 移除所有 Wuchang 相關的 Volumes

### 1.3 移除相關 Networks
`powershell
docker network ls -q --filter "name=wuchang" | ForEach-Object { docker network rm  }
`
**說明:** 移除所有 Wuchang 相關的 Networks

### 1.4 清理未使用的資源
`powershell
docker system prune -f --volumes
`
**說明:** 清理所有未使用的 Docker 資源

### 1.5 驗證清理結果
`powershell
docker ps -a --filter "name=wuchang"
`
**說明:** 確認所有容器已清理

---

## 階段 2: 重新部署 🚀

### 2.1 構建並啟動容器
`powershell
docker-compose up -d --build
`
**說明:** 重新構建並啟動所有容器

### 2.2 等待容器啟動
**時間:** 約 30-60 秒
**檢查:** 
`powershell
docker-compose ps
`

### 2.3 驗證服務狀態
- [ ] 資料庫容器運行正常
- [ ] Odoo 容器運行正常
- [ ] 其他服務容器運行正常

---

## 階段 3: 安裝模組 📦

### 3.1 安裝 Wuchang 模組
`powershell
python scripts/install_wuchang_modules_v2.py
`
**說明:** 安裝所有 Wuchang 相關模組

### 3.2 修復 IDE 模組
`powershell
python scripts/fix_odoo_ide_extension.py
`
**說明:** 修復 Odoo IDE 延伸模組安裝問題

### 3.3 驗證模組安裝
`powershell
python scripts/check_module_installation.py
`
**說明:** 驗證所有模組正確安裝

---

## 階段 4: 驗證與優化 ✅

### 4.1 服務驗證
- [ ] Odoo 後台可正常訪問 (http://localhost:8069)
- [ ] 資料庫連接正常
- [ ] 所有模組狀態正常

### 4.2 配置優化
- [x] ✅ Pyright 配置已建立
- [ ] 確認 Docker Compose 配置正確
- [ ] 確認環境變數設定正確

---

## ⚠️ 重要提醒

### 執行前必須完成
1. **啟動 Docker Desktop**
   - 開啟 Docker Desktop 應用程式
   - 等待完全啟動（約 30-60 秒）
   - 驗證: docker ps

2. **確認工作目錄**
   - 確保在正確的工作目錄: G:\共用雲端硬碟\五常雲端空間
   - 確認 docker-compose.yml 存在

3. **備份重要資料**（如需要）
   - 資料庫備份
   - 重要配置檔案

---

## 📝 快速執行腳本

### 完整卸載
`powershell
# 停止並移除所有容器和 Volumes
docker-compose down -v

# 清理未使用的資源
docker system prune -f --volumes
`

### 重新部署
`powershell
# 構建並啟動容器
docker-compose up -d --build

# 等待容器啟動後檢查狀態
Start-Sleep -Seconds 30
docker-compose ps
`

### 安裝模組
`powershell
# 安裝 Wuchang 模組
python scripts/install_wuchang_modules_v2.py

# 修復 IDE 模組
python scripts/fix_odoo_ide_extension.py
`

---

## 🔄 自動執行腳本

已準備自動執行腳本：
- **Python 腳本:** scripts/complete_cleanup_and_deploy.py
- **執行方式:** python scripts/complete_cleanup_and_deploy.py

**注意:** 執行前請確保 Docker Desktop 已啟動

---

## 📊 預期結果

完成後應達到：
- ✅ 所有舊容器已完全清理
- ✅ 新容器正常運行
- ✅ 所有 Wuchang 模組已安裝
- ✅ Odoo IDE 模組問題已修復
- ✅ 服務可正常訪問

---

**建立者:** 地端小J
**最後更新:** 2026-01-22 20:49:28
