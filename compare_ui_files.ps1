#!/usr/bin/env pwsh
<#
.SYNOPSIS
    比對本機與伺服器端的 UI 地端檔案
.DESCRIPTION
    掃描本機 HTML/CSS/JS 檔案，連接到伺服器取得對應檔案，進行 hash 比對並產生差異報告
#>

param(
    [string]$ServerIP = "192.168.50.84",
    [string]$ServerUser = "wuchang",
    [string]$ServerPath = "/home/wuchang/wuchang-v5.1.0",
    [string]$LocalPath = "$PSScriptRoot",
    [string[]]$FilePatterns = @("*.html", "*.css", "*.js", "*.json"),
    [string]$OutputReport = "$PSScriptRoot\ui_file_comparison_report.json"
)

$colors = @{
    ok = "Green"; warn = "Yellow"; err = "Red"; info = "Cyan"; header = "Magenta"
}

function H {
    param([string]$t)
    Write-Host "`n$('═'*70)" -f $colors.header
    Write-Host "  $t" -f $colors.header
    Write-Host $('═'*70) -f $colors.header
}
function OK {
    param([string]$m)
    Write-Host "  [OK]   $m" -f $colors.ok
}
function WW {
    param([string]$m)
    Write-Host "  [WARN] $m" -f $colors.warn
}
function EE {
    param([string]$m)
    Write-Host "  [ERR]  $m" -f $colors.err
}
function II {
    param([string]$m)
    Write-Host "  [INFO] $m" -f $colors.info
}

H "本機/伺服器 UI 檔案比對工具"

# 檢查 SSH 連線能力
II "測試 SSH 連線到 $ServerUser@$ServerIP ..."
try {
    $testResult = ssh -o ConnectTimeout=5 -o BatchMode=yes "$ServerUser@$ServerIP" "echo connected" 2>&1
    if ($testResult -match "connected") {
        OK "SSH 連線正常"
    } else {
        EE "無法連接到伺服器，請確認 SSH key 已設定或使用密碼認證"
        II "手動測試: ssh $ServerUser@$ServerIP"
        exit 1
    }
} catch {
    EE "SSH 連線測試失敗: $_"
    exit 1
}

# 掃描本機檔案
H "掃描本機 UI 檔案"
$localFiles = @()
$excludeDirs = @("node_modules", ".git", "venv", "__pycache__", "USB_DRIVE", "USB_DRIVE_NEW")

foreach ($pattern in $FilePatterns) {
    Get-ChildItem -Path $LocalPath -Filter $pattern -Recurse -File -ErrorAction SilentlyContinue | 
        Where-Object { 
            $exclude = $false
            foreach ($dir in $excludeDirs) {
                if ($_.FullName -like "*\$dir\*" -or $_.FullName -like "*/$dir/*") {
                    $exclude = $true
                    break
                }
            }
            -not $exclude
        } | ForEach-Object {
            $relativePath = $_.FullName.Replace($LocalPath, "").TrimStart("\", "/").Replace("\", "/")
            $hash = (Get-FileHash -Path $_.FullName -Algorithm SHA256).Hash
            $localFiles += [PSCustomObject]@{
                Path = $relativePath
                FullPath = $_.FullName
                Hash = $hash
                Size = $_.Length
                Modified = $_.LastWriteTime
            }
        }
}

II "本機掃描到 $($localFiles.Count) 個檔案"

# 建立比對報告
H "與伺服器進行檔案比對"
$comparisonResults = @()
$identical = 0
$different = 0
$localOnly = 0
$serverOnly = 0
$errors = 0

foreach ($file in $localFiles) {
    $serverFilePath = "$ServerPath/$($file.Path)"
    
    Write-Host "  比對: $($file.Path)" -NoNewline
    
    try {
        # 檢查伺服器端檔案是否存在
        $serverExists = ssh "$ServerUser@$ServerIP" "test -f '$serverFilePath' && echo 'exists' || echo 'notfound'" 2>&1
        
        if ($serverExists -match "exists") {
            # 取得伺服器端檔案 hash
            $serverHash = ssh "$ServerUser@$ServerIP" "sha256sum '$serverFilePath' | awk '{print `$1}'" 2>&1
            $serverHash = $serverHash.Trim().ToUpper()
            
            if ($file.Hash -eq $serverHash) {
                Write-Host " ✓ 相同" -f $colors.ok
                $identical++
                $status = "IDENTICAL"
            } else {
                Write-Host " ≠ 不同" -f $colors.warn
                $different++
                $status = "DIFFERENT"
            }
            
            $comparisonResults += [PSCustomObject]@{
                File = $file.Path
                Status = $status
                LocalHash = $file.Hash
                ServerHash = $serverHash
                LocalSize = $file.Size
                LocalModified = $file.Modified.ToString("yyyy-MM-dd HH:mm:ss")
            }
        } else {
            Write-Host " ⚠ 僅本機有" -f $colors.warn
            $localOnly++
            
            $comparisonResults += [PSCustomObject]@{
                File = $file.Path
                Status = "LOCAL_ONLY"
                LocalHash = $file.Hash
                ServerHash = $null
                LocalSize = $file.Size
                LocalModified = $file.Modified.ToString("yyyy-MM-dd HH:mm:ss")
            }
        }
    } catch {
        Write-Host " ✗ 錯誤" -f $colors.err
        $errors++
        
        $comparisonResults += [PSCustomObject]@{
            File = $file.Path
            Status = "ERROR"
            LocalHash = $file.Hash
            ServerHash = $null
            LocalSize = $file.Size
            LocalModified = $file.Modified.ToString("yyyy-MM-dd HH:mm:ss")
            Error = $_.Exception.Message
        }
    }
}

# 檢查伺服器端獨有的檔案（可選）
H "檢查伺服器端獨有檔案"
II "掃描伺服器 UI 檔案..."

$serverOnlyFiles = @()
foreach ($pattern in $FilePatterns) {
    try {
        $serverFiles = ssh "$ServerUser@$ServerIP" "find '$ServerPath' -name '$pattern' -type f 2>/dev/null" 2>&1
        if ($serverFiles) {
            $serverFiles -split "`n" | Where-Object { $_ -ne "" } | ForEach-Object {
                $serverFilePath = $_.Trim()
                $relativePath = $serverFilePath.Replace("$ServerPath/", "").Replace("$ServerPath", "")
                
                # 排除特定目錄
                $exclude = $false
                foreach ($dir in $excludeDirs) {
                    if ($relativePath -like "*/$dir/*") {
                        $exclude = $true
                        break
                    }
                }
                
                if (-not $exclude -and $relativePath -ne "") {
                    $localMatch = $localFiles | Where-Object { $_.Path -eq $relativePath }
                    if (-not $localMatch) {
                        $serverOnlyFiles += $relativePath
                    }
                }
            }
        }
    } catch {
        WW "無法掃描伺服器檔案模式: $pattern"
    }
}

if ($serverOnlyFiles.Count -gt 0) {
    WW "發現 $($serverOnlyFiles.Count) 個僅存在於伺服器的檔案"
    $serverOnly = $serverOnlyFiles.Count
    
    foreach ($file in $serverOnlyFiles) {
        $comparisonResults += [PSCustomObject]@{
            File = $file
            Status = "SERVER_ONLY"
            LocalHash = $null
            ServerHash = "(not fetched)"
            LocalSize = $null
            LocalModified = $null
        }
    }
} else {
    OK "沒有伺服器獨有的檔案"
}

# 產生報告
H "產生比對報告"

$report = @{
    Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    ServerInfo = @{
        IP = $ServerIP
        User = $ServerUser
        Path = $ServerPath
    }
    LocalInfo = @{
        Path = $LocalPath
    }
    Summary = @{
        TotalLocal = $localFiles.Count
        Identical = $identical
        Different = $different
        LocalOnly = $localOnly
        ServerOnly = $serverOnly
        Errors = $errors
    }
    Details = $comparisonResults
}

$report | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputReport -Encoding UTF8
OK "報告已儲存: $OutputReport"

# 顯示摘要
H "比對結果摘要"
Write-Host ""
Write-Host "  總檔案數:      $($localFiles.Count)" -f $colors.info
Write-Host "  完全相同:      $identical" -f $colors.ok
Write-Host "  內容不同:      $different" -f $colors.warn
Write-Host "  僅本機有:      $localOnly" -f $colors.warn
Write-Host "  僅伺服器有:    $serverOnly" -f $colors.warn
Write-Host "  比對錯誤:      $errors" -f $colors.err
Write-Host ""

if ($different -gt 0 -or $localOnly -gt 0 -or $serverOnly -gt 0) {
    H "需要注意的檔案"
    
    if ($different -gt 0) {
        Write-Host "`n  內容不同的檔案:" -f $colors.warn
        $comparisonResults | Where-Object { $_.Status -eq "DIFFERENT" } | 
            Select-Object -First 10 | ForEach-Object {
                Write-Host "    - $($_.File)" -f $colors.warn
            }
        if ($different -gt 10) {
            Write-Host "    ... 還有 $($different - 10) 個檔案" -f $colors.info
        }
    }
    
    if ($localOnly -gt 0) {
        Write-Host "`n  僅本機有的檔案:" -f $colors.warn
        $comparisonResults | Where-Object { $_.Status -eq "LOCAL_ONLY" } | 
            Select-Object -First 10 | ForEach-Object {
                Write-Host "    - $($_.File)" -f $colors.warn
            }
        if ($localOnly -gt 10) {
            Write-Host "    ... 還有 $($localOnly - 10) 個檔案" -f $colors.info
        }
    }
    
    if ($serverOnly -gt 0) {
        Write-Host "`n  僅伺服器有的檔案:" -f $colors.warn
        $comparisonResults | Where-Object { $_.Status -eq "SERVER_ONLY" } | 
            Select-Object -First 10 | ForEach-Object {
                Write-Host "    - $($_.File)" -f $colors.warn
            }
        if ($serverOnly -gt 10) {
            Write-Host "    ... 還有 $($serverOnly - 10) 個檔案" -f $colors.info
        }
    }
}

H "建議操作"
if ($different -gt 0) {
    II "有 $different 個檔案內容不同，建議:"
    Write-Host "  1. 檢視詳細報告: cat $OutputReport | ConvertFrom-Json | Select-Object -ExpandProperty Details | Where-Object { `$_.Status -eq 'DIFFERENT' }" -f $colors.info
    Write-Host "  2. 同步到伺服器: scp <file> $ServerUser@${ServerIP}:$ServerPath/<file>" -f $colors.info
    Write-Host "  3. 從伺服器拉取: scp $ServerUser@${ServerIP}:$ServerPath/<file> <local-path>" -f $colors.info
}

if ($localOnly -gt 0) {
    II "有 $localOnly 個檔案僅存在於本機，建議上傳到伺服器"
}

if ($serverOnly -gt 0) {
    II "有 $serverOnly 個檔案僅存在於伺服器，建議同步到本機"
}

if ($identical -eq $localFiles.Count -and $serverOnly -eq 0) {
    Write-Host "`n✅ 所有檔案完全同步！" -f $colors.ok
}

Write-Host ""
