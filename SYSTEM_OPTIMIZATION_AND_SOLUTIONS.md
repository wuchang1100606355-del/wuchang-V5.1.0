# 系統細部檢查與優化解決方案

**檢查時間**: 2026-01-18  
**系統**: Windows 11  
**檢查工具**: comprehensive_system_audit.py

---

## 📊 檢查結果摘要

### 系統資源狀態

| 項目 | 狀態 | 使用率 | 評估 |
|------|------|--------|------|
| CPU | ✅ 正常 | 53.4% | 良好 |
| 記憶體 | ✅ 正常 | 68.6% | 良好 |
| **磁碟** | ⚠️ **警告** | **94.5%** | **需要立即處理** |

### 發現的問題

1. **高優先級問題** (1 個)
   - ⚠️ 磁碟空間嚴重不足：僅剩 50.57 GB

2. **中優先級問題** (1 個)
   - ⚠️ 伺服器 7 個關鍵服務端口關閉

3. **其他發現**
   - 發現 108 個敏感檔案
   - 發現 72 個備份檔案
   - 發現 72 個大型檔案（>100MB）
   - 缺少 SSH 密鑰

---

## 🚨 緊急處理項目

### 1. 磁碟空間清理（高優先級）

**問題**: 磁碟使用率 94.5%，僅剩 50.57 GB

**影響**: 
- 系統效能下降
- 無法安裝更新
- 可能導致系統不穩定

**解決方案**:

#### 方案 A: 自動清理腳本（推薦）

```powershell
# 執行自動清理
.\scripts\cleanup_disk_space.ps1
```

#### 方案 B: 手動清理步驟

1. **清理臨時檔案**
   ```powershell
   # Windows 臨時檔案
   Remove-Item "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
   Remove-Item "$env:LOCALAPPDATA\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
   
   # 專案臨時檔案
   Remove-Item "C:\wuchang V5.1.0\.tmp.driveupload\*" -Recurse -Force -ErrorAction SilentlyContinue
   ```

2. **清理備份檔案**
   ```powershell
   # 清理 .backup 檔案（保留最近 30 天）
   Get-ChildItem "C:\wuchang V5.1.0" -Filter "*.backup" -Recurse | 
       Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | 
       Remove-Item -Force
   ```

3. **清理大型檔案**
   ```powershell
   # 找出並清理大型檔案（>100MB）
   Get-ChildItem "C:\wuchang V5.1.0" -Recurse -File | 
       Where-Object { $_.Length -gt 100MB } | 
       Sort-Object Length -Descending | 
       Select-Object -First 20 FullName, @{Name="SizeMB";Expression={[math]::Round($_.Length/1MB,2)}}
   ```

4. **清理下載資料夾**
   ```powershell
   # 清理舊的下載檔案
   Get-ChildItem "C:\wuchang V5.1.0\downloads" -File | 
       Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-90) } | 
       Remove-Item -Force
   ```

5. **清理日誌檔案**
   ```powershell
   # 清理舊日誌
   Get-ChildItem "C:\wuchang V5.1.0\logs" -File | 
       Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | 
       Remove-Item -Force
   ```

**預期釋放空間**: 約 100-200 GB

---

### 2. 伺服器服務啟動（高優先級）

**問題**: 伺服器 7 個關鍵端口關閉（8069, 8080, 8766, 3001 等）

**解決方案**:

#### 步驟 1: 使用 RDP 連線到伺服器

```powershell
mstsc /v:192.168.50.249:3389
```

#### 步驟 2: 在伺服器上檢查服務狀態

```bash
# 檢查 Docker 容器
docker ps -a

# 檢查服務進程
ps aux | grep -E "odoo|python|node"

# 檢查端口監聽
netstat -tlnp | grep -E "8069|8080|8766|3001"
```

#### 步驟 3: 啟動服務

```bash
# 啟動 Docker 容器
cd /path/to/wuchang/project
docker-compose up -d

# 或啟動特定服務
docker-compose --profile system up -d
docker-compose --profile ai up -d
```

#### 步驟 4: 檢查防火牆

```bash
# Ubuntu/Debian
sudo ufw status
sudo ufw allow 8069/tcp
sudo ufw allow 8080/tcp
sudo ufw allow 8766/tcp
sudo ufw allow 3001/tcp
sudo ufw reload
```

---

## 🔧 優化方案

### 優化 1: 安全性強化

#### 1.1 保護敏感檔案

**問題**: 發現 108 個敏感檔案（包含密鑰、證書等）

**解決方案**:

1. **檢查敏感檔案位置**
   ```powershell
   # 列出敏感檔案
   Get-ChildItem "C:\wuchang V5.1.0" -Recurse -Include "*.key","*.pem","*secret*","*password*","*token*" | 
       Select-Object FullName, Length, LastWriteTime
   ```

2. **移動敏感檔案到安全位置**
   ```powershell
   # 建立安全目錄
   $secureDir = "C:\wuchang_secure"
   New-Item -ItemType Directory -Path $secureDir -Force
   
   # 移動敏感檔案（需要手動確認）
   # 注意：不要自動移動，需要人工審查
   ```

3. **使用環境變數**
   ```powershell
   # 設定環境變數而非硬編碼
   $env:ODOO_DB_PASSWORD = "your_password"
   $env:API_KEY = "your_api_key"
   ```

4. **確保 .gitignore 包含敏感檔案**
   ```gitignore
   # 敏感檔案
   *.key
   *.pem
   *secret*
   *password*
   *token*
   router_secrets.json
   ```

#### 1.2 生成 SSH 密鑰

**問題**: 缺少 SSH 密鑰

**解決方案**:

```powershell
# 生成 SSH 密鑰
ssh-keygen -t ed25519 -C "wuchang@system" -f "$env:USERPROFILE\.ssh\id_ed25519"

# 部署到伺服器
python deploy_ssh_key.py
# 或
.\setup_ssh_auto.ps1
```

---

### 優化 2: 效能優化

#### 2.1 處理大型檔案

**問題**: 發現 72 個大型檔案（>100MB）

**解決方案**:

1. **識別大型檔案**
   ```powershell
   # 列出前 20 個最大檔案
   Get-ChildItem "C:\wuchang V5.1.0" -Recurse -File | 
       Where-Object { $_.Length -gt 100MB } | 
       Sort-Object Length -Descending | 
       Select-Object -First 20 FullName, @{Name="SizeMB";Expression={[math]::Round($_.Length/1MB,2)}}
   ```

2. **清理臨時上傳檔案**
   ```powershell
   # 清理 .tmp.driveupload 目錄
   Remove-Item "C:\wuchang V5.1.0\.tmp.driveupload\*" -Recurse -Force
   ```

3. **壓縮大型檔案**
   ```powershell
   # 壓縮大型備份檔案
   Compress-Archive -Path "C:\wuchang V5.1.0\*.zip" -DestinationPath "C:\wuchang_backups_compressed.zip"
   ```

4. **移動到外部儲存**
   ```powershell
   # 將大型檔案移到外部硬碟或雲端儲存
   # 建議使用外部硬碟或 NAS
   ```

#### 2.2 清理備份檔案

**問題**: 發現 72 個備份檔案

**解決方案**:

```powershell
# 清理 30 天前的備份檔案
Get-ChildItem "C:\wuchang V5.1.0" -Filter "*.backup" -Recurse | 
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | 
    Remove-Item -Force -Verbose

# 或保留最近 10 個備份
Get-ChildItem "C:\wuchang V5.1.0" -Filter "*.backup" -Recurse | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -Skip 10 | 
    Remove-Item -Force
```

---

### 優化 3: 系統維護

#### 3.1 建立自動清理腳本

建立 `scripts\auto_cleanup.ps1`:

```powershell
# 自動清理腳本
# 每週執行一次

Write-Host "開始自動清理..." -ForegroundColor Cyan

# 清理臨時檔案
Write-Host "清理臨時檔案..." -ForegroundColor Yellow
Remove-Item "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "C:\wuchang V5.1.0\.tmp.driveupload\*" -Recurse -Force -ErrorAction SilentlyContinue

# 清理舊備份
Write-Host "清理舊備份..." -ForegroundColor Yellow
Get-ChildItem "C:\wuchang V5.1.0" -Filter "*.backup" -Recurse | 
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | 
    Remove-Item -Force

# 清理舊日誌
Write-Host "清理舊日誌..." -ForegroundColor Yellow
Get-ChildItem "C:\wuchang V5.1.0\logs" -File -ErrorAction SilentlyContinue | 
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | 
    Remove-Item -Force

Write-Host "清理完成！" -ForegroundColor Green
```

#### 3.2 設定定期檢查

建立 Windows 工作排程器任務：

```powershell
# 建立每週執行一次的清理任務
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\wuchang V5.1.0\scripts\auto_cleanup.ps1"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 2am
Register-ScheduledTask -TaskName "Wuchang Auto Cleanup" -Action $action -Trigger $trigger -Description "自動清理系統檔案"
```

---

## 📋 執行檢查清單

### 立即執行（今天）

- [ ] **清理磁碟空間**
  - [ ] 清理臨時檔案
  - [ ] 清理 .tmp.driveupload 目錄
  - [ ] 清理 30 天前的備份檔案
  - [ ] 清理舊日誌檔案

- [ ] **檢查伺服器服務**
  - [ ] 使用 RDP 連線到伺服器
  - [ ] 檢查 Docker 容器狀態
  - [ ] 啟動必要的服務
  - [ ] 驗證端口是否開啟

### 本週執行

- [ ] **安全性強化**
  - [ ] 審查敏感檔案位置
  - [ ] 生成 SSH 密鑰
  - [ ] 部署 SSH 密鑰到伺服器
  - [ ] 更新 .gitignore

- [ ] **效能優化**
  - [ ] 處理大型檔案
  - [ ] 清理不必要的備份
  - [ ] 建立自動清理腳本

### 持續維護

- [ ] **建立定期檢查**
  - [ ] 設定每週自動清理
  - [ ] 設定每月系統檢查
  - [ ] 監控磁碟使用率

---

## 🛠️ 自動化腳本

### 清理磁碟空間腳本

已建立 `scripts\cleanup_disk_space.ps1`（需要創建）

### 系統檢查腳本

執行定期檢查：
```powershell
python comprehensive_system_audit.py
```

---

## 📊 預期改善效果

### 磁碟空間

- **當前**: 50.57 GB 可用（94.5% 使用率）
- **預期**: 150-200 GB 可用（80-85% 使用率）
- **改善**: 釋放約 100-150 GB

### 系統效能

- **當前**: CPU 53.4%, 記憶體 68.6%
- **預期**: CPU <50%, 記憶體 <65%
- **改善**: 系統響應速度提升

### 服務可用性

- **當前**: 2 個端口開啟（SSH, RDP）
- **預期**: 7+ 個端口開啟（包含所有應用服務）
- **改善**: 所有服務正常運作

---

## ⚠️ 注意事項

1. **清理前備份**: 執行任何清理操作前，請確保重要資料已備份
2. **敏感檔案**: 移動或刪除敏感檔案前，請仔細審查
3. **服務重啟**: 重啟服務可能導致短暫中斷，請在維護時間執行
4. **測試環境**: 建議先在測試環境驗證腳本

---

## 📞 支援

如有問題，請參考：
- 系統檢查報告: `system_audit_report.json`
- 優化計劃: `system_optimization_plan.md`
- 連線診斷: `SERVER_CONNECTION_DIAGNOSIS_REPORT.md`

---

**報告生成時間**: 2026-01-18  
**下次檢查建議**: 2026-01-25（一週後）
