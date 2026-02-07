# 檢查系統地端檔案夾容量
# 用途：找出佔用空間最大的檔案和資料夾

param(
    [string]$Path = ".",
    [int]$TopFolders = 20,
    [int]$TopFiles = 20
)

Write-Host "`n=== 系統地端檔案夾容量檢查 ===" -ForegroundColor Cyan
Write-Host "檢查路徑: $((Resolve-Path $Path).Path)" -ForegroundColor White
Write-Host ""

# 總容量
$totalSize = (Get-ChildItem -Path $Path -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
Write-Host "總容量: $([math]::Round($totalSize/1GB, 2)) GB ($([math]::Round($totalSize/1MB, 2)) MB)" -ForegroundColor Green
Write-Host ""

# 檢查主要資料夾
Write-Host "=== 主要資料夾容量（前 $TopFolders 名） ===" -ForegroundColor Yellow
$folders = Get-ChildItem -Path $Path -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    try {
        $size = (Get-ChildItem $_.FullName -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        [PSCustomObject]@{
            Folder = $_.Name
            SizeGB = [math]::Round($size/1GB, 2)
            SizeMB = [math]::Round($size/1MB, 2)
            Path = $_.FullName
        }
    } catch {
        Write-Warning "無法計算 $($_.Name) 的大小: $_"
        $null
    }
} | Where-Object { $_ -ne $null } | Sort-Object SizeGB -Descending | Select-Object -First $TopFolders

$folders | Format-Table Folder, SizeGB, SizeMB -AutoSize

# 檢查大檔案
Write-Host "`n=== 大檔案（前 $TopFiles 名，> 100MB） ===" -ForegroundColor Yellow
$largeFiles = Get-ChildItem -Path $Path -File -Recurse -ErrorAction SilentlyContinue | 
    Where-Object { $_.Length -gt 100MB } | 
    Sort-Object Length -Descending | 
    Select-Object -First $TopFiles | 
    ForEach-Object {
        [PSCustomObject]@{
            Name = $_.Name
            SizeGB = [math]::Round($_.Length/1GB, 2)
            SizeMB = [math]::Round($_.Length/1MB, 2)
            Path = $_.FullName
        }
    }

if ($largeFiles) {
    $largeFiles | Format-Table Name, SizeGB, SizeMB -AutoSize
} else {
    Write-Host "沒有找到大於 100MB 的檔案" -ForegroundColor Gray
}

# 檢查常見的大檔案夾類型
Write-Host "`n=== 常見大檔案夾類型檢查 ===" -ForegroundColor Yellow
$commonFolders = @(
    @{Name="node_modules"; Pattern="node_modules"},
    @{Name=".git"; Pattern="\.git"},
    @{Name="__pycache__"; Pattern="__pycache__"},
    @{Name="Python 虛擬環境"; Pattern="(venv|env|\.venv)"},
    @{Name="wuchang_os"; Pattern="wuchang_os"},
    @{Name="migration_pack"; Pattern="migration_pack"},
    @{Name="vm_deploy"; Pattern="vm_deploy"},
    @{Name="workshop_deploy"; Pattern="workshop_deploy"}
)

foreach ($folderType in $commonFolders) {
    $matches = Get-ChildItem -Path $Path -Recurse -Directory -ErrorAction SilentlyContinue | 
        Where-Object { $_.Name -match $folderType.Pattern }
    
    if ($matches) {
        $totalSize = 0
        foreach ($match in $matches) {
            try {
                $size = (Get-ChildItem $match.FullName -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
                $totalSize += $size
            } catch {
                # 忽略錯誤
            }
        }
        
        if ($totalSize -gt 0) {
            $color = if ($totalSize -gt 1GB) { 'Red' } elseif ($totalSize -gt 100MB) { 'Yellow' } else { 'White' }
            Write-Host "$($folderType.Name): $([math]::Round($totalSize/1GB, 2)) GB ($([math]::Round($totalSize/1MB, 2)) MB) - 找到 $($matches.Count) 個" -ForegroundColor $color
        }
    }
}

# 檢查日誌檔案
Write-Host "`n=== 日誌檔案檢查（> 10MB） ===" -ForegroundColor Yellow
$logFiles = Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue | 
    Where-Object { $_.Extension -match "\.(log|txt)" -and $_.Length -gt 10MB } | 
    Sort-Object Length -Descending | 
    Select-Object -First 10

if ($logFiles) {
    $logFiles | ForEach-Object {
        Write-Host "$($_.Name): $([math]::Round($_.Length/1MB, 2)) MB - $($_.FullName)" -ForegroundColor Yellow
    }
} else {
    Write-Host "沒有找到大於 10MB 的日誌檔案" -ForegroundColor Gray
}

Write-Host "`n=== 檢查完成 ===" -ForegroundColor Green
Write-Host "`n建議：" -ForegroundColor Cyan
Write-Host "  1. 檢查 node_modules、.git、__pycache__ 等快取資料夾" -ForegroundColor White
Write-Host "  2. 清理不需要的日誌檔案" -ForegroundColor White
Write-Host "  3. 檢查是否有重複的備份或遷移資料夾" -ForegroundColor White
Write-Host "  4. 考慮使用 .gitignore 排除不需要的檔案" -ForegroundColor White
