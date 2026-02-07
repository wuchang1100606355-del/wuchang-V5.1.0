# 🚀 五常 AI 系統遷移 - 一鍵啟動指南

> **親愛的妹妹**，系統遷移方案已完全準備好了！  
> 只需 3 個簡單步驟，就能開始遷移 ✨

---

## 📌 重要提醒

```
⚠️  開始前，請確保：
✓ 伺服器 192.168.50.249 已開啟且可訪問
✓ 有足夠的存儲空間（推薦 50GB+）
✓ 網絡連接穩定（推薦 100Mbps+ 帶寬）
✓ 本機 Docker 環境正常
✓ 有管理員權限運行 PowerShell
```

---

## 🎯 三步開始遷移

### 第 1 步：打開 PowerShell（管理員模式）

```powershell
# 按 Windows + X，選擇 "Windows PowerShell (管理員)" 或 Terminal (管理員)
# 或直接搜索並以管理員身份打開
```

### 第 2 步：進入項目目錄

```powershell
cd "C:\wuchang V5.1.0"
```

### 第 3 步：執行遷移

```powershell
# 🟢 完全自動遷移（推薦）
.\migrate_to_server.ps1 -Action prepare

# 稍後執行以下命令：
.\migrate_to_server.ps1 -Action backup
.\migrate_to_server.ps1 -Action migrate
.\migrate_to_server.ps1 -Action sync-all
.\migrate_to_server.ps1 -Action test
```

---

## 📊 預計時間

```
準備階段        : 30分鐘
備份階段        : 1-2小時 (取決於數據量)
數據傳輸        : 1-3小時 (取決於網絡速度)
伺服器恢復      : 1-2小時
同步配置        : 30分鐘
驗證測試        : 1小時
─────────────────────────
總計: 約 6-11 小時

💡 大部分時間是等待，你可以邊做邊看日誌
```

---

## 🔍 各階段說明

### 🟢 prepare (準備階段)

```powershell
.\migrate_to_server.ps1 -Action prepare
```

**功能**:

-   ✓ 檢查伺服器連接
-   ✓ 驗證網絡環境
-   ✓ 在伺服器上安裝必要軟件
-   ✓ 創建存儲目錄

**所需時間**: 30 分鐘

**如果出錯**:

-   檢查伺服器連接: `ping 192.168.50.249`
-   驗證 SSH: `ssh admin@192.168.50.249 "echo OK"`
-   查看日誌: `Get-Content "backups/migration_*.txt" -Tail 50`

---

### 🟢 backup (備份階段)

```powershell
.\migrate_to_server.ps1 -Action backup
```

**功能**:

-   ✓ 停止本機所有容器
-   ✓ 備份 Odoo 數據庫
-   ✓ 備份 Docker 數據卷
-   ✓ 備份項目文件

**所需時間**: 1-2 小時

**生成的備份**:

```
C:\wuchang V5.1.0\backups\migration_20260110_HHmmss\
├── odoo.sql                    # 數據庫備份
├── odoo-db-data.tar.gz         # 數據庫卷
├── odoo-web-data.tar.gz        # Web卷
├── caddy-data.tar.gz           # Caddy卷
└── *.zip                       # 項目文件
```

**備份大小**: 5GB+

**如果出錯**:

-   檢查磁盤空間: `Get-Volume | Format-Table -AutoSize`
-   驗證 Docker: `docker-compose ps`
-   查看詳細日誌: `docker-compose logs`

---

### 🟢 migrate (遷移階段)

```powershell
.\migrate_to_server.ps1 -Action migrate
```

**功能**:

-   ✓ 傳輸備份至伺服器
-   ✓ 在伺服器上恢復數據
-   ✓ 啟動伺服器容器
-   ✓ 驗證數據完整性

**所需時間**: 2-4 小時 (大部分為傳輸和恢復)

**預期輸出**:

```
[時間] ✓ 備份文件已傳輸
[時間] ✓ 數據庫已恢復
[時間] ✓ 容器已啟動
[時間] ✓ 數據完整性已驗證
```

**如果出錯**:

-   檢查伺服器存儲空間: `ssh admin@192.168.50.249 "df -h"`
-   查看容器日誌: `ssh admin@192.168.50.249 "docker-compose logs"`
-   驗證數據庫: `ssh admin@192.168.50.249 "docker ps"`

---

### 🟢 sync-all (同步配置)

```powershell
.\migrate_to_server.ps1 -Action sync-all
```

**功能**:

-   ✓ 配置 SMB 文件共享
-   ✓ 測試讀寫權限
-   ✓ 驗證雙向訪問

**所需時間**: 30 分鐘

**預期結果**:

```
Z:\ 驅動器已掛載並可訪問
✓ 讀寫測試通過
✓ 可以訪問伺服器文件
```

**如果出錯**:

-   檢查掛載: `Get-PSDrive Z`
-   驗證共享: `Test-Path "\\192.168.50.249\wuchang-storage"`
-   檢查防火牆: `Get-NetFirewallRule -DisplayName "*Samba*"`

---

### 🟢 test (驗證測試)

```powershell
.\migrate_to_server.ps1 -Action test
```

**功能**:

-   ✓ 測試 HTTP 訪問
-   ✓ 驗證 SSH 連接
-   ✓ 檢查文件共享
-   ✓ 驗證整個系統

**所需時間**: 30 分鐘

**預期結果**:

```
✓ HTTP訪問正常
✓ SSH連接正常
✓ 文件共享可用
✓ 系統就緒
```

---

## 🔄 啟動持續同步監視

遷移完成後，啟動同步監視器以保持本機與伺服器同步：

```powershell
.\sync_with_server.ps1 -Mode watch

# 此命令會：
# - 每5分鐘自動同步一次
# - 推送本機更改到伺服器
# - 拉取伺服器更改到本機
# - 按 Ctrl+C 停止
```

---

## ✅ 驗證遷移成功

### 檢查 1: 訪問 Odoo

```powershell
# 打開瀏覽器訪問
http://192.168.50.249:8069

# 用以下默認憑證登入
用戶名: admin
密碼: admin
```

### 檢查 2: 文件共享

```powershell
# 驗證Z:\ 驅動器存在
Test-Path Z:\

# 查看共享文件
Get-ChildItem Z:\

# 創建測試文件
Set-Content Z:\test.txt "遷移成功"
```

### 檢查 3: 數據庫

```powershell
# 驗證數據庫中的數據
ssh admin@192.168.50.249 "docker exec wuchangv510-db-1 psql -U odoo -c 'SELECT COUNT(*) FROM ir_module_module;'"
```

### 檢查 4: 容器狀態

```powershell
# 查看伺服器容器
ssh admin@192.168.50.249 "docker-compose ps"

# 預期看到所有容器都是 "Up"
```

---

## 📱 實時監控

在遷移過程中監控進度：

```powershell
# 監控日誌輸出
Get-Content "backups/migration_*.txt" -Tail 20 -Wait

# 監控容器日誌
ssh admin@192.168.50.249 "docker-compose logs -f wuchang-web"

# 監控同步進度
.\sync_with_server.ps1 -Mode config
```

---

## 🆘 快速故障排除

### "無法連接伺服器"

```powershell
ping 192.168.50.249
ssh admin@192.168.50.249 "echo OK"

# 如果失敗，檢查:
# 1. 伺服器是否開啟
# 2. 網絡連接是否正常
# 3. 防火牆是否允許SSH
```

### "Docker 容器無法啟動"

```powershell
ssh admin@192.168.50.249 "docker-compose logs wuchang-web"

# 查看具體錯誤信息
ssh admin@192.168.50.249 "docker ps -a"
```

### "文件同步失敗"

```powershell
# 檢查驅動器掛載
Get-PSDrive Z

# 重新掛載
$cred = Get-Credential -UserName wuchang
Remove-PSDrive Z -Force
New-PSDrive -Name Z -PSProvider FileSystem -Root "\\192.168.50.249\wuchang-storage" -Credential $cred -Persist
```

### "完整故障排除"

查看 `MIGRATION_QUICK_START.md` 的故障排除部分

---

## 💾 緊急回滾

如果任何時候出現問題，可以回滾到備份：

```powershell
# 立即停止遷移
# Ctrl+C 中止當前操作

# 執行緊急回滾
.\migrate_to_server.ps1 -Action rollback

# 這將：
# - 停止伺服器容器
# - 恢復本機備份
# - 重啟本機容器
# - 驗證系統恢復
```

---

## 📚 更多文檔

| 文檔                                  | 用途               |
| ------------------------------------- | ------------------ |
| `MIGRATION_PLAN_SERVER_DEPLOYMENT.md` | 完整的詳細實施方案 |
| `MIGRATION_QUICK_START.md`            | 命令速查表         |
| `MIGRATION_CHECKLIST.md`              | 完整檢查清單       |
| `MIGRATION_COMPLETE_SUMMARY.md`       | 方案總結           |
| `SYSTEM_DIAGNOSTICS.md`               | 系統診斷信息       |

---

## 🎬 完整命令序列

快速複製粘貼執行：

```powershell
# 1. 準備
cd "C:\wuchang V5.1.0"
.\migrate_to_server.ps1 -Action prepare

# 等待... (30分鐘)

# 2. 備份
.\migrate_to_server.ps1 -Action backup

# 等待... (1-2小時)

# 3. 遷移
.\migrate_to_server.ps1 -Action migrate

# 等待... (2-4小時)

# 4. 同步配置
.\migrate_to_server.ps1 -Action sync-all

# 5. 測試
.\migrate_to_server.ps1 -Action test

# 6. 啟動監視 (背景運行)
Start-Job { cd "C:\wuchang V5.1.0"; .\sync_with_server.ps1 -Mode watch }

# 完成！
```

---

## 📊 期望時間線

```
09:00 - 開始準備階段 (prepare)          30分鐘
09:30 - 開始備份階段 (backup)           1-2小時
11:30 - 開始遷移階段 (migrate)          2-4小時
15:30 - 開始同步配置 (sync-all)         30分鐘
16:00 - 驗證測試 (test)                30分鐘
16:30 - 完成並啟動監視 ✅

總耗時: 約 7-9 小時
```

---

## 🎉 成功指標

遷移成功的標誌：

```
✅ 伺服器上所有容器都在運行
✅ 可以訪問 http://192.168.50.249:8069
✅ 可以用默認憑證登入Odoo
✅ Z:\ 驅動器可以訪問
✅ 文件可以雙向同步
✅ 數據庫中有完整的數據
✅ 沒有明顯的錯誤日誌
```

---

## 💬 最後的話

妹妹已經為你準備好了一切！這套方案經過精心設計，包含：

-   ✨ 完全自動化的遷移腳本
-   📚 詳細的文檔和指南
-   🔄 雙向數據同步機制
-   🛡️ 多層備份和恢復方案
-   📊 完整的監控和診斷工具

**你只需要按照這個指南一步步執行，就能成功遷移整個系統！**

有任何問題，查看對應的文檔，所有答案都在那裡。

祝你遷移順利！🚀

---

**準備好開始了嗎？**

```powershell
cd "C:\wuchang V5.1.0"
.\migrate_to_server.ps1 -Action prepare
```

加油！💪

---

_最後更新: 2026-01-10_  
_版本: v1.0_  
_準備者: 小 j (GitHub Copilot)_
