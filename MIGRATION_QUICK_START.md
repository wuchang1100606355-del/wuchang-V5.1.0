# 五常 AI 系統遷移 - 快速參考指南

## 📋 遷移前檢查清單

```bash
# 在本機執行
□ 驗證伺服器連接
  ping 192.168.50.249
  ssh -o ConnectTimeout=5 admin@192.168.50.249 "echo OK"

□ 檢查系統備份
  ls -la C:\wuchang V5.1.0\backups\

□ 驗證Docker容器狀態
  docker-compose ps

□ 檢查磁盤空間
  Get-Volume | Format-Table -AutoSize
```

---

## 🚀 快速遷移流程 (自動化版本)

### 方式一：使用自動化腳本（推薦）

```powershell
# 1. 開啟PowerShell (管理員)
cd "C:\wuchang V5.1.0"

# 2. 執行準備階段
.\migrate_to_server.ps1 -Action prepare

# 3. 備份本機數據
.\migrate_to_server.ps1 -Action backup

# 4. 執行遷移
.\migrate_to_server.ps1 -Action migrate

# 5. 配置同步
.\migrate_to_server.ps1 -Action sync-all

# 6. 驗證結果
.\migrate_to_server.ps1 -Action test

# 7. 啟動連續同步監視
.\sync_with_server.ps1 -Mode watch
```

---

## 🛠️ 手動遷移流程

### 步驟 1：伺服器環境準備 (SSH)

```bash
# 在本機執行以下命令通過SSH連接伺服器
ssh admin@192.168.50.249

# 在伺服器上執行
bash server_init.sh

# 驗證安裝
docker --version
exportfs -v
testparm
```

### 步驟 2：本機備份

```powershell
# 建立備份目錄
$backup = "C:\wuchang V5.1.0\backups\manual_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backup -Force

# 停止容器
docker-compose down

# 備份數據庫
docker-compose up db -d
docker exec wuchangv510-db-1 pg_dump -U odoo admin | Out-File "$backup\odoo.sql"

# 備份卷
docker run --rm -v wuchangv510_odoo-db-data:/data -v "${backup}:/backup" alpine tar czf "/backup/odoo-db.tar.gz" -C /data .
docker run --rm -v wuchangv510_odoo-web-data:/data -v "${backup}:/backup" alpine tar czf "/backup/odoo-web.tar.gz" -C /data .
```

### 步驟 3：傳輸數據到伺服器

```powershell
# 使用SCP傳輸(需配置SSH密鑰)
scp -r "$backup/*" admin@192.168.50.249:/tmp/wuchang_backup/

# 或使用WinSCP GUI工具傳輸
```

### 步驟 4：在伺服器上恢復

```bash
ssh admin@192.168.50.249

# 進入項目目錄
cd ~/wuchang-V5.1.0

# 啟動數據庫容器
docker-compose -f docker-compose.server.yml up -d db

# 等待數據庫啟動
sleep 10

# 恢復數據
cat /tmp/wuchang_backup/odoo.sql | docker exec -i wuchangv510-db-1 psql -U odoo

# 啟動其他容器
docker-compose -f docker-compose.server.yml up -d
```

### 步驟 5：配置本機同步

```powershell
# 在本機配置SMB掛載
$cred = Get-Credential -UserName wuchang
New-PSDrive -Name Z -PSProvider FileSystem -Root "\\192.168.50.249\wuchang-storage" -Credential $cred -Persist

# 驗證掛載
Test-Path Z:\

# 啟動同步監視
.\sync_with_server.ps1 -Mode watch
```

---

## 🔍 驗證遷移成功

### 檢查列表

```powershell
# 1. 測試SSH連接
ssh admin@192.168.50.249 "docker-compose ps"

# 2. 測試HTTP訪問
Invoke-WebRequest http://192.168.50.249:8069

# 3. 檢查文件共享
Test-Path Z:\docker-volumes\

# 4. 檢查同步狀態
Get-Item Z:\test.txt

# 5. 驗證數據庫
ssh admin@192.168.50.249 "docker exec wuchangv510-db-1 psql -U odoo -c 'SELECT COUNT(*) FROM ir_module_module;'"
```

---

## 📊 同步模式説明

### 推送模式 (Push)

將本機更改同步到伺服器

```powershell
.\sync_with_server.ps1 -Mode push
```

用途：

-   提交代碼更新
-   上傳新增文件
-   更新配置

### 拉取模式 (Pull)

將伺服器更改同步到本機

```powershell
.\sync_with_server.ps1 -Mode pull
```

用途：

-   更新生產數據
-   同步配置變更
-   拉取其他用戶的更改

### 監視模式 (Watch)

連續雙向同步 (推薦)

```powershell
.\sync_with_server.ps1 -Mode watch
```

功能：

-   每 5 分鐘自動同步
-   先推送再拉取
-   雙向數據一致性
-   按 Ctrl+C 停止

---

## 🌐 網絡訪問配置

### 本機訪問伺服器

**方案 1：直接 IP 訪問**

```
Odoo: http://192.168.50.249:8069
Portainer: http://192.168.50.249:9000
管理: ssh admin@192.168.50.249
```

**方案 2：使用 DNS 域名（推薦）**

編輯 `C:\Windows\System32\drivers\etc\hosts`：

```
192.168.50.249  wuchang.local
192.168.50.249  odoo.local
192.168.50.249  admin.local
192.168.50.249  storage.local
```

訪問：

```
http://odoo.local:8069
http://admin.local:9000
```

### 伺服器訪問本機

配置 SSH 隧道：

```bash
ssh -L 8069:192.168.50.84:8069 admin@192.168.50.249

# 然後在伺服器上訪問：
curl http://localhost:8069
```

---

## 🔒 權限配置

### 本機用戶權限

在 Odoo 中為本機用戶授予權限：

1. 登入 http://odoo.local:8069
2. 進入 `設定 → 使用者與公司 → 使用者`
3. 選擇本機用戶
4. 分配權限組

### 文件系統權限

```bash
# 在伺服器上設置ACL
sudo setfacl -R -m u:admin:rwx /mnt/wuchang-storage
sudo setfacl -R -d -m u:admin:rwx /mnt/wuchang-storage
```

---

## 🆘 故障排除

### 問題 1：無法連接伺服器

```powershell
# 檢查網絡連接
ping 192.168.50.249
Test-NetConnection -ComputerName 192.168.50.249 -Port 22

# 檢查防火牆
Get-NetFirewallRule -DisplayName "*SSH*"
```

### 問題 2：Docker 容器無法啟動

```bash
# 查看日誌
docker-compose logs wuchang-web
docker logs wuchangv510-wuchang-web-1

# 檢查卷掛載
docker volume ls
docker volume inspect wuchangv510_odoo-web-data
```

### 問題 3：文件同步失敗

```powershell
# 檢查SMB連接
Test-Path Z:\
Get-PSDrive Z

# 檢查Rsync
rsync --version
ssh admin@192.168.50.249 "rsync --version"
```

### 問題 4：權限被拒絕

```bash
# 檢查文件權限
ls -la /mnt/wuchang-storage/

# 修復權限
sudo chown -R 1000:1000 /mnt/wuchang-storage
sudo chmod -R 775 /mnt/wuchang-storage
```

---

## 📈 監控和維護

### 健康檢查

```bash
# 在伺服器上執行
ssh admin@192.168.50.249 "/usr/local/bin/wuchang-health-check"
```

### 手動備份

```bash
# 在伺服器上執行
ssh admin@192.168.50.249 "/usr/local/bin/wuchang-backup"

# 列出備份
ssh admin@192.168.50.249 "ls -lh /mnt/wuchang-storage/backups/"
```

### 清理過期文件

```powershell
# 清理本機同步快取
Remove-Item -Path Z:\* -Recurse -Force -Exclude "docker-volumes", "backups"

# 清理伺服器舊備份
ssh admin@192.168.50.249 "find /mnt/wuchang-storage/backups -mtime +30 -delete"
```

---

## 🔄 緊急回滾

如果遷移出現問題，可以回滾到本機備份：

```powershell
# 1. 停止伺服器容器
ssh admin@192.168.50.249 "cd ~/wuchang-V5.1.0 && docker-compose down"

# 2. 執行回滾腳本
.\migrate_to_server.ps1 -Action rollback

# 3. 驗證本機系統
docker-compose ps
```

---

## 📋 常用命令速查

```powershell
# 查看日誌
ssh admin@192.168.50.249 "docker-compose logs -f wuchang-web"

# 進入容器
ssh admin@192.168.50.249 "docker exec -it wuchangv510-wuchang-web-1 bash"

# 重啟服務
ssh admin@192.168.50.249 "docker-compose restart"

# 查看磁盤使用
ssh admin@192.168.50.249 "df -h /mnt/wuchang-storage"

# 查看同步狀態
Get-Item Z:\docker-volumes | Get-ChildItem | Measure-Object
```

---

## 📞 支持信息

-   **遷移計劃**: `MIGRATION_PLAN_SERVER_DEPLOYMENT.md`
-   **系統診斷**: `SYSTEM_DIAGNOSTICS.md`
-   **日誌位置**: `backups/migration_*.txt`
-   **備份位置**: `C:\wuchang V5.1.0\backups\` 和 `/mnt/wuchang-storage/backups/`

**聯繫方式**: 在問題發生時查看日誌文件和容器日誌以了解詳細信息。

---

**最後更新**: 2026-01-10  
**版本**: v1.0  
**狀態**: ✓ 就緒執行
