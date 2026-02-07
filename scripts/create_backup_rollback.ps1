# 系統備份與回滾點創建腳本
# 合規: 符合 Google 非營利組織合規要求

param (
    [string]$BackupName = "",
    [switch]$FullBackup = $false
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "backups"
$rollbackDir = "$backupDir/rollback_points"

# 生成備份名稱
if ([string]::IsNullOrEmpty($BackupName)) {
    $BackupName = "backup_$timestamp"
} else {
    $BackupName = "${BackupName}_$timestamp"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  系統備份與回滾點創建" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "備份名稱: $BackupName" -ForegroundColor Yellow
Write-Host "時間戳: $timestamp" -ForegroundColor Yellow
Write-Host ""

# 創建備份目錄
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
New-Item -ItemType Directory -Force -Path $rollbackDir | Out-Null
New-Item -ItemType Directory -Force -Path "$rollbackDir/$BackupName" | Out-Null

$backupPath = "$rollbackDir/$BackupName"
$metadataFile = "$backupPath/metadata.json"

Write-Host "[1/5] 備份數據庫..." -ForegroundColor Yellow

try {
    # 查找數據庫容器
    $dbContainer = docker ps -q -f ancestor=postgres:15 | Select-Object -First 1
    
    if (-not $dbContainer) {
        Write-Host "  ❌ 未找到數據庫容器" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "  找到數據庫容器: $dbContainer" -ForegroundColor Cyan
    
    # 備份所有數據庫
    $databases = @("admin", "postgres", "odoo")
    $dbBackupDir = "$backupPath/database"
    New-Item -ItemType Directory -Force -Path $dbBackupDir | Out-Null
    
    foreach ($db in $databases) {
        Write-Host "  備份數據庫: $db" -ForegroundColor Gray
        $dbBackupFile = "$dbBackupDir/${db}_$timestamp.sql"
        
        docker exec $dbContainer pg_dump -U odoo -F c -f "/tmp/${db}_backup.dump" $db 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            docker cp "${dbContainer}:/tmp/${db}_backup.dump" $dbBackupFile
            docker exec $dbContainer rm -f "/tmp/${db}_backup.dump"
            Write-Host "    ✅ $db 備份完成" -ForegroundColor Green
        } else {
            Write-Host "    ⚠️  $db 備份跳過（可能不存在）" -ForegroundColor Yellow
        }
    }
    
    Write-Host "  ✅ 數據庫備份完成" -ForegroundColor Green
    
} catch {
    Write-Host "  ❌ 數據庫備份失敗: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

Write-Host "[2/5] 備份配置文件..." -ForegroundColor Yellow

try {
    $configBackupDir = "$backupPath/config"
    New-Item -ItemType Directory -Force -Path $configBackupDir | Out-Null
    
    # 備份關鍵配置文件
    $configFiles = @(
        "docker-compose.yml",
        "docker-compose-ai.yml",
        "config/odoo.conf",
        "config/official_ai_identity.json"
    )
    
    foreach ($file in $configFiles) {
        if (Test-Path $file) {
            $destFile = "$configBackupDir/$(Split-Path -Leaf $file)"
            Copy-Item -Path $file -Destination $destFile -Force
            Write-Host "  ✅ 已備份: $file" -ForegroundColor Green
        }
    }
    
    Write-Host "  ✅ 配置文件備份完成" -ForegroundColor Green
    
} catch {
    Write-Host "  ❌ 配置文件備份失敗: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

Write-Host "[3/5] 備份系統參數..." -ForegroundColor Yellow

try {
    $paramsBackupFile = "$backupPath/system_parameters.sql"
    
    # 導出系統參數
    $sql = "COPY (SELECT key, value FROM ir_config_parameter ORDER BY key) TO STDOUT WITH CSV HEADER;"
    docker exec $dbContainer psql -U odoo -d admin -c "$sql" > $paramsBackupFile 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ 系統參數備份完成" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  系統參數備份跳過" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "  ⚠️  系統參數備份失敗: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""

Write-Host "[4/5] 創建備份元數據..." -ForegroundColor Yellow

try {
    $metadata = @{
        backup_name = $BackupName
        timestamp = $timestamp
        date = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        backup_type = if ($FullBackup) { "full" } else { "standard" }
        databases = @("admin", "postgres", "odoo")
        config_files = $configFiles
        created_by = $env:USERNAME
        system_info = @{
            hostname = $env:COMPUTERNAME
            os = (Get-CimInstance Win32_OperatingSystem).Caption
        }
        compliance = @{
            google_nonprofit = $true
            purpose = "system_backup_rollback_point"
        }
    }
    
    $metadata | ConvertTo-Json -Depth 10 | Out-File -FilePath $metadataFile -Encoding UTF8
    Write-Host "  ✅ 元數據創建完成" -ForegroundColor Green
    
} catch {
    Write-Host "  ❌ 元數據創建失敗: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

Write-Host "[5/5] 創建回滾點記錄..." -ForegroundColor Yellow

try {
    $rollbackIndexFile = "$rollbackDir/rollback_index.json"
    
    # 讀取現有索引
    $rollbackIndex = @()
    if (Test-Path $rollbackIndexFile) {
        $rollbackIndex = Get-Content $rollbackIndexFile | ConvertFrom-Json
    }
    
    # 添加新回滾點
    $rollbackPoint = @{
        name = $BackupName
        timestamp = $timestamp
        date = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        path = $backupPath
        metadata_file = $metadataFile
        type = if ($FullBackup) { "full" } else { "standard" }
    }
    
    $rollbackIndex = @($rollbackPoint) + $rollbackIndex
    $rollbackIndex | ConvertTo-Json -Depth 10 | Out-File -FilePath $rollbackIndexFile -Encoding UTF8
    
    Write-Host "  ✅ 回滾點記錄創建完成" -ForegroundColor Green
    
} catch {
    Write-Host "  ❌ 回滾點記錄創建失敗: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ 備份與回滾點創建完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "備份位置: $backupPath" -ForegroundColor Cyan
Write-Host "回滾點名稱: $BackupName" -ForegroundColor Cyan
Write-Host ""
Write-Host "備份內容:" -ForegroundColor Yellow
Write-Host "  - 數據庫備份 (PostgreSQL)" -ForegroundColor White
Write-Host "  - 配置文件" -ForegroundColor White
Write-Host "  - 系統參數" -ForegroundColor White
Write-Host "  - 元數據和回滾點記錄" -ForegroundColor White
Write-Host ""
Write-Host "查看回滾點列表:" -ForegroundColor Yellow
Write-Host "  Get-Content backups/rollback_points/rollback_index.json | ConvertFrom-Json" -ForegroundColor Gray
Write-Host ""
