#!/usr/bin/env pwsh
<#
.SYNOPSIS
    五常AI系統 - 自動化遷移腳本
.DESCRIPTION
    一鍵執行系統遷移至192.168.50.249伺服器
.PARAMETER Action
    要執行的操作: prepare, backup, migrate, sync-all, test, rollback
#>

param(
    [ValidateSet('prepare', 'backup', 'migrate', 'sync-all', 'test', 'rollback')]
    [string]$Action = 'help'
)

# 配置變數
$ErrorActionPreference = "Stop"
$script:ScriptDir = Split-Path $MyInvocation.MyCommand.Path
$script:LogFile = Join-Path $ScriptDir "migration_log_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
$script:ServerIP = "192.168.50.249"
$script:ServerUser = "admin"
$script:LocalIP = "192.168.50.84"
$script:BackupDir = "$ScriptDir\backups\migration_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# 日誌函數
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    Write-Host $logMessage
    Add-Content -Path $script:LogFile -Value $logMessage
}

function Write-Success {
    param([string]$Message)
    Write-Log $Message "✓ SUCCESS"
    Write-Host $Message -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Log $Message "✗ ERROR"
    Write-Host $Message -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Log $Message "⚠ WARNING"
    Write-Host $Message -ForegroundColor Yellow
}

# 檢查SSH連接
function Test-SSHConnection {
    Write-Log "測試SSH連接至伺服器..."
    
    try {
        $output = ssh -o ConnectTimeout=5 "${script:ServerUser}@${script:ServerIP}" "echo 'SSH連接成功'" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "SSH連接正常 (${script:ServerIP})"
            return $true
        } else {
            Write-Error "SSH連接失敗: $output"
            return $false
        }
    } catch {
        Write-Error "SSH連接異常: $_"
        return $false
    }
}

# 檢查網絡連接
function Test-NetworkConnection {
    Write-Log "測試網絡連接..."
    
    $connectivity = Test-NetConnection -ComputerName $script:ServerIP -Port 22 -WarningAction SilentlyContinue
    
    if ($connectivity.TcpTestSucceeded) {
        Write-Success "網絡連接正常 ($script:ServerIP)"
        return $true
    } else {
        Write-Error "無法連接到伺服器"
        return $false
    }
}

# 準備階段
function Invoke-Prepare {
    Write-Log "========== 準備階段開始 =========="
    
    # 檢查前置條件
    Write-Log "檢查前置條件..."
    
    if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
        Write-Error "未安裝SSH客戶端"
        return $false
    }
    
    if (-not (Test-NetworkConnection)) {
        return $false
    }
    
    if (-not (Test-SSHConnection)) {
        return $false
    }
    
    # 準備備份目錄
    Write-Log "準備備份目錄..."
    New-Item -ItemType Directory -Path $script:BackupDir -Force | Out-Null
    Write-Success "備份目錄已建立: $script:BackupDir"
    
    # 在伺服器上準備環境
    Write-Log "在伺服器上執行初始化..."
    
    $initScript = @"
#!/bin/bash
set -e

echo '[步驟1] 更新系統'
sudo apt update

echo '[步驟2] 安裝必要軟件'
sudo apt install -y docker.io docker-compose nfs-kernel-server rsync openssh-server python3.10 python3-pip git

echo '[步驟3] 啟用Docker服務'
sudo systemctl enable docker
sudo systemctl start docker

echo '[步驟4] 創建存儲目錄'
sudo mkdir -p /mnt/wuchang-storage/{odoo-data,ai-memory,ai-common,backups,docker-volumes}
sudo chown -R 1000:1000 /mnt/wuchang-storage
sudo chmod -R 775 /mnt/wuchang-storage

echo '[步驟5] 驗證安裝'
docker --version
docker-compose --version
exportfs -v

echo '✓ 伺服器環境準備完成'
"@
    
    ssh "${script:ServerUser}@${script:ServerIP}" $initScript
    
    Write-Success "準備階段完成"
    return $true
}

# 備份階段
function Invoke-Backup {
    Write-Log "========== 備份階段開始 =========="
    
    # 停止本機容器
    Write-Log "停止本機Docker容器..."
    & docker-compose -f "$ScriptDir\docker-compose.yml" down
    Write-Success "容器已停止"
    
    # 備份Docker卷
    Write-Log "備份Docker數據卷..."
    
    $volumes = @(
        @{ name = "wuchangv510_odoo-db-data"; file = "odoo-db-data.tar.gz" },
        @{ name = "wuchangv510_odoo-web-data"; file = "odoo-web-data.tar.gz" },
        @{ name = "wuchangv510_caddy-data"; file = "caddy-data.tar.gz" }
    )
    
    foreach ($vol in $volumes) {
        Write-Log "備份卷: $($vol.name)..."
        
        & docker run --rm `
            -v "$($vol.name):/data" `
            -v "$($script:BackupDir):/backup" `
            alpine tar czf "/backup/$($vol.file)" -C /data .
        
        Write-Success "已備份: $($vol.file)"
    }
    
    # 備份數據庫
    Write-Log "備份Odoo數據庫..."
    & docker-compose -f "$ScriptDir\docker-compose.yml" up db -d
    Start-Sleep -Seconds 5
    
    & docker exec wuchangv510-db-1 pg_dump -U odoo admin | `
        Out-File "$script:BackupDir\odoo_database.sql"
    
    Write-Success "數據庫備份完成"
    
    # 備份文件
    Write-Log "備份項目文件..."
    $dirs = @("wuchang_os", "config", "downloads", "scripts", "memory_store")
    
    foreach ($dir in $dirs) {
        if (Test-Path "$ScriptDir\$dir") {
            Write-Log "備份: $dir..."
            Compress-Archive -Path "$ScriptDir\$dir" `
                -DestinationPath "$script:BackupDir\$dir.zip" -Force
            Write-Success "已備份: $dir"
        }
    }
    
    Write-Success "備份階段完成"
    return $true
}

# 遷移階段
function Invoke-Migrate {
    Write-Log "========== 遷移階段開始 =========="
    
    if (-not (Test-Path $script:BackupDir)) {
        Write-Error "未找到備份目錄，請先執行備份"
        return $false
    }
    
    # 傳輸備份至伺服器
    Write-Log "傳輸備份文件至伺服器..."
    
    try {
        scp -r "$script:BackupDir\*" "${script:ServerUser}@${script:ServerIP}:/tmp/wuchang_backup/"
        Write-Success "備份文件已傳輸"
    } catch {
        Write-Error "文件傳輸失敗: $_"
        return $false
    }
    
    # 在伺服器上恢復
    Write-Log "在伺服器上執行恢復..."
    
    $restoreScript = @"
#!/bin/bash
set -e

echo '[步驟1] 提取備份文件'
cd /mnt/wuchang-storage

tar xzf /tmp/wuchang_backup/odoo-db-data.tar.gz -C docker-volumes/
tar xzf /tmp/wuchang_backup/odoo-web-data.tar.gz -C docker-volumes/
tar xzf /tmp/wuchang_backup/caddy-data.tar.gz -C docker-volumes/

echo '[步驟2] 恢復數據庫'
cd /home/admin
docker-compose up -d db
sleep 10

psql -h 127.0.0.1 -U odoo -d admin < /tmp/wuchang_backup/odoo_database.sql

echo '[步驟3] 恢復項目文件'
cd /home/admin
unzip -o /tmp/wuchang_backup/wuchang_os.zip
unzip -o /tmp/wuchang_backup/config.zip
unzip -o /tmp/wuchang_backup/scripts.zip

echo '[步驟4] 啟動全部容器'
docker-compose up -d

echo '✓ 伺服器遷移完成'
"@
    
    ssh "${script:ServerUser}@${script:ServerIP}" $restoreScript
    
    Write-Success "遷移階段完成"
    return $true
}

# 同步階段
function Invoke-SyncAll {
    Write-Log "========== 同步階段開始 =========="
    
    # 配置SMB掛載
    Write-Log "配置Samba共享掛載..."
    
    $credential = Get-Credential -UserName wuchang
    
    try {
        New-PSDrive -Name "Z" `
            -PSProvider FileSystem `
            -Root "\\$script:ServerIP\wuchang-storage" `
            -Credential $credential `
            -Persist -Force | Out-Null
        
        Write-Success "Samba共享已掛載: Z:\"
    } catch {
        Write-Error "掛載失敗: $_"
        return $false
    }
    
    # 測試讀寫
    Write-Log "測試讀寫權限..."
    
    try {
        $testFile = "Z:\test_$(Get-Random).txt"
        Set-Content -Path $testFile -Value "本機測試 $(Get-Date)"
        $content = Get-Content -Path $testFile
        Remove-Item -Path $testFile -Force
        Write-Success "讀寫測試通過"
    } catch {
        Write-Error "讀寫測試失敗: $_"
        return $false
    }
    
    Write-Success "同步階段完成"
    return $true
}

# 測試階段
function Invoke-Test {
    Write-Log "========== 測試階段開始 =========="
    
    # 測試HTTP訪問
    Write-Log "測試HTTP訪問..."
    
    try {
        $response = Invoke-WebRequest -Uri "http://$script:ServerIP:8069" -TimeoutSec 10 -SkipHttpErrorCheck
        if ($response.StatusCode -eq 200) {
            Write-Success "Odoo HTTP訪問正常"
        } else {
            Write-Warning "HTTP狀態: $($response.StatusCode)"
        }
    } catch {
        Write-Error "HTTP訪問失敗: $_"
    }
    
    # 測試SSH連接
    Write-Log "測試SSH連接..."
    $sshTest = ssh "${script:ServerUser}@${script:ServerIP}" "docker-compose ps" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "SSH連接正常"
        Write-Host $sshTest
    } else {
        Write-Error "SSH連接異常"
    }
    
    # 驗證文件共享
    Write-Log "驗證文件共享..."
    if (Test-Path "Z:\") {
        $items = Get-ChildItem "Z:\" -ErrorAction SilentlyContinue | Measure-Object
        Write-Success "文件共享可訪問 ($($items.Count) 個項目)"
    } else {
        Write-Error "文件共享不可訪問"
    }
    
    Write-Success "測試階段完成"
    return $true
}

# 回滾階段
function Invoke-Rollback {
    Write-Log "========== 回滾階段開始 =========="
    
    Write-Warning "這將回滾到備份狀態"
    
    if (-not (Test-Path $script:BackupDir)) {
        Write-Error "未找到備份文件"
        return $false
    }
    
    # 停止伺服器容器
    Write-Log "停止伺服器容器..."
    ssh "${script:ServerUser}@${script:ServerIP}" "cd /home/admin && docker-compose down" 2>&1
    
    # 恢復本機備份
    Write-Log "恢復本機備份..."
    
    $volumes = @(
        @{ name = "wuchangv510_odoo-db-data"; file = "odoo-db-data.tar.gz" },
        @{ name = "wuchangv510_odoo-web-data"; file = "odoo-web-data.tar.gz" }
    )
    
    foreach ($vol in $volumes) {
        Write-Log "恢復卷: $($vol.name)..."
        
        & docker run --rm `
            -v "$($vol.name):/data" `
            -v "$($script:BackupDir):/backup" `
            alpine sh -c "rm -rf /data/* && tar xzf /backup/$($vol.file) -C /data"
    }
    
    # 恢復數據庫
    Write-Log "恢復數據庫..."
    & docker-compose -f "$ScriptDir\docker-compose.yml" up db -d
    Start-Sleep -Seconds 5
    
    & docker exec wuchangv510-db-1 psql -U odoo < "$script:BackupDir\odoo_database.sql"
    
    # 啟動本機容器
    Write-Log "啟動本機容器..."
    & docker-compose -f "$ScriptDir\docker-compose.yml" up -d
    
    Write-Success "回滾完成"
    return $true
}

# 主函數
function Show-Help {
    Write-Host @"
五常AI系統 - 自動化遷移腳本

用法: .\migrate_to_server.ps1 -Action <操作>

可用操作:
    prepare   - 準備伺服器環境
    backup    - 備份本機數據
    migrate   - 執行完整遷移
    sync-all  - 配置同步機制
    test      - 測試遷移結果
    rollback  - 回滾到備份狀態

完整流程:
    1. .\migrate_to_server.ps1 -Action prepare
    2. .\migrate_to_server.ps1 -Action backup
    3. .\migrate_to_server.ps1 -Action migrate
    4. .\migrate_to_server.ps1 -Action sync-all
    5. .\migrate_to_server.ps1 -Action test

備份位置: $script:BackupDir
日誌文件: $script:LogFile
"@
}

# 執行主流程
Write-Log "========== 五常AI系統遷移腳本開始 =========="
Write-Log "目標伺服器: $script:ServerIP"
Write-Log "操作: $Action"

switch ($Action) {
    "prepare" { Invoke-Prepare }
    "backup" { Invoke-Backup }
    "migrate" { Invoke-Migrate }
    "sync-all" { Invoke-SyncAll }
    "test" { Invoke-Test }
    "rollback" { Invoke-Rollback }
    default { Show-Help }
}

Write-Log "========== 腳本執行完成 =========="
Write-Host "`n日誌文件: $script:LogFile`n" -ForegroundColor Cyan
