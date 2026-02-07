#!/usr/bin/env pwsh
<#
.SYNOPSIS
    自動清理磁碟空間腳本
.DESCRIPTION
    清理臨時檔案、備份檔案、日誌檔案等以釋放磁碟空間
.PARAMETER DryRun
    僅顯示將要清理的檔案，不實際刪除
#>

param(
    [switch]$DryRun = $false
)

$BasePath = "C:\wuchang V5.1.0"
$TotalFreed = 0

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Get-FolderSize {
    param([string]$Path)
    if (Test-Path $Path) {
        $size = (Get-ChildItem $Path -Recurse -File -ErrorAction SilentlyContinue | 
                 Measure-Object -Property Length -Sum).Sum
        return [math]::Round($size / 1GB, 2)
    }
    return 0
}

function Remove-OldFiles {
    param(
        [string]$Path,
        [int]$DaysOld = 30,
        [string]$Filter = "*",
        [string]$Description = "檔案"
    )
    
    if (-not (Test-Path $Path)) {
        Write-Warning "$Description 路徑不存在: $Path"
        return 0
    }
    
    Write-Info "清理 $Description (超過 $DaysOld 天)..."
    
    $cutoffDate = (Get-Date).AddDays(-$DaysOld)
    $files = Get-ChildItem $Path -Filter $Filter -Recurse -File -ErrorAction SilentlyContinue | 
             Where-Object { $_.LastWriteTime -lt $cutoffDate }
    
    $totalSize = ($files | Measure-Object -Property Length -Sum).Sum
    $sizeGB = [math]::Round($totalSize / 1GB, 2)
    $count = $files.Count
    
    if ($count -gt 0) {
        if ($DryRun) {
            Write-Host "  [DRY RUN] 將刪除 $count 個檔案，釋放 $sizeGB GB" -ForegroundColor Yellow
            $files | Select-Object -First 10 FullName, @{Name="SizeMB";Expression={[math]::Round($_.Length/1MB,2)}}, LastWriteTime | Format-Table
        } else {
            $files | Remove-Item -Force -ErrorAction SilentlyContinue
            Write-Success "已刪除 $count 個檔案，釋放 $sizeGB GB"
        }
        return $sizeGB
    } else {
        Write-Success "沒有需要清理的 $Description"
        return 0
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  磁碟空間清理工具" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

if ($DryRun) {
    Write-Warning "DRY RUN 模式：僅顯示將要清理的檔案，不會實際刪除"
    Write-Host ""
}

# 1. 清理 Windows 臨時檔案
Write-Host "`n[1] 清理 Windows 臨時檔案" -ForegroundColor Yellow
$tempPaths = @(
    "$env:TEMP",
    "$env:LOCALAPPDATA\Temp"
)

foreach ($tempPath in $tempPaths) {
    if (Test-Path $tempPath) {
        $sizeBefore = Get-FolderSize $tempPath
        Write-Info "清理: $tempPath (當前大小: $sizeBefore GB)"
        
        if ($DryRun) {
            $files = Get-ChildItem $tempPath -Recurse -File -ErrorAction SilentlyContinue
            $totalSize = ($files | Measure-Object -Property Length -Sum).Sum
            $sizeGB = [math]::Round($totalSize / 1GB, 2)
            Write-Host "  [DRY RUN] 將釋放約 $sizeGB GB" -ForegroundColor Yellow
            $TotalFreed += $sizeGB
        } else {
            try {
                Get-ChildItem $tempPath -Recurse -File -ErrorAction SilentlyContinue | 
                    Remove-Item -Force -ErrorAction SilentlyContinue
                $sizeAfter = Get-FolderSize $tempPath
                $freed = $sizeBefore - $sizeAfter
                Write-Success "釋放 $freed GB"
                $TotalFreed += $freed
            } catch {
                Write-Warning "清理失敗: $_"
            }
        }
    }
}

# 2. 清理專案臨時檔案
Write-Host "`n[2] 清理專案臨時檔案" -ForegroundColor Yellow
$projectTempPaths = @(
    "$BasePath\.tmp.driveupload",
    "$BasePath\temp",
    "$BasePath\.cache"
)

foreach ($tempPath in $projectTempPaths) {
    $freed = Remove-OldFiles -Path $tempPath -DaysOld 7 -Description "臨時檔案"
    $TotalFreed += $freed
}

# 3. 清理備份檔案
Write-Host "`n[3] 清理舊備份檔案" -ForegroundColor Yellow
$freed = Remove-OldFiles -Path $BasePath -DaysOld 30 -Filter "*.backup" -Description "備份檔案"
$TotalFreed += $freed

# 4. 清理日誌檔案
Write-Host "`n[4] 清理舊日誌檔案" -ForegroundColor Yellow
$logPaths = @(
    "$BasePath\logs",
    "$BasePath\*.log"
)

foreach ($logPath in $logPaths) {
    if ($logPath -like "*.log") {
        # 單個檔案模式
        $freed = Remove-OldFiles -Path $BasePath -DaysOld 30 -Filter "*.log" -Description "日誌檔案"
    } else {
        # 目錄模式
        $freed = Remove-OldFiles -Path $logPath -DaysOld 30 -Filter "*.log" -Description "日誌檔案"
    }
    $TotalFreed += $freed
}

# 5. 清理下載資料夾
Write-Host "`n[5] 清理下載資料夾" -ForegroundColor Yellow
$freed = Remove-OldFiles -Path "$BasePath\downloads" -DaysOld 90 -Description "下載檔案"
$TotalFreed += $freed

# 6. 清理大型臨時檔案
Write-Host "`n[6] 檢查大型檔案" -ForegroundColor Yellow
$largeFiles = Get-ChildItem $BasePath -Recurse -File -ErrorAction SilentlyContinue | 
              Where-Object { $_.Length -gt 100MB -and $_.FullName -like "*tmp*" } |
              Sort-Object Length -Descending |
              Select-Object -First 20

if ($largeFiles) {
    $totalSize = ($largeFiles | Measure-Object -Property Length -Sum).Sum
    $sizeGB = [math]::Round($totalSize / 1GB, 2)
    Write-Info "發現 $($largeFiles.Count) 個大型臨時檔案，總計 $sizeGB GB"
    
    if ($DryRun) {
        Write-Host "  [DRY RUN] 將釋放約 $sizeGB GB" -ForegroundColor Yellow
        $largeFiles | Select-Object -First 10 FullName, @{Name="SizeMB";Expression={[math]::Round($_.Length/1MB,2)}} | Format-Table
        $TotalFreed += $sizeGB
    } else {
        $confirm = Read-Host "是否刪除這些大型臨時檔案? (y/N)"
        if ($confirm -eq "y" -or $confirm -eq "Y") {
            $largeFiles | Remove-Item -Force -ErrorAction SilentlyContinue
            Write-Success "已刪除大型臨時檔案，釋放 $sizeGB GB"
            $TotalFreed += $sizeGB
        }
    }
}

# 總結
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  清理完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`n總計釋放空間: $([math]::Round($TotalFreed, 2)) GB" -ForegroundColor Green

if ($DryRun) {
    Write-Host "`n[INFO] 這是 DRY RUN 模式，沒有實際刪除檔案" -ForegroundColor Yellow
    Write-Host "執行時不帶 -DryRun 參數以實際清理" -ForegroundColor Yellow
}

Write-Host ""
