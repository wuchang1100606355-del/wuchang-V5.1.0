# 重新總店私人 DNS 設定腳本
# 用途：為重新總店設定內部 DNS 主機名稱，讓 POS 設備可以透過友善的主機名稱連線

param(
    [string]$ServerIP = "192.168.50.84",
    [string]$RouterIP = "192.168.50.1",
    [string]$Domain = "chong-sin.local",
    [switch]$TestOnly = $false
)

$ErrorActionPreference = "Stop"

Write-Host "`n=== 重新總店私人 DNS 設定 ===" -ForegroundColor Cyan
Write-Host "伺服器 IP: $ServerIP" -ForegroundColor White
Write-Host "路由器 IP: $RouterIP" -ForegroundColor White
Write-Host "網域: $Domain" -ForegroundColor White
Write-Host ""

# 1. 設定 Hosts 檔案
Write-Host "[1] 設定 Hosts 檔案..." -ForegroundColor Yellow
$hostsFile = "$env:SystemRoot\System32\drivers\etc\hosts"

# 檢查管理員權限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "  ❌ 需要管理員權限才能修改 Hosts 檔案" -ForegroundColor Red
    Write-Host "  請以管理員身份執行此腳本" -ForegroundColor Yellow
    exit 1
}

# 備份現有 hosts 檔案
if (Test-Path $hostsFile) {
    $backupFile = "$hostsFile.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
    Copy-Item $hostsFile $backupFile -Force
    Write-Host "  ✓ 已備份: $backupFile" -ForegroundColor Green
}

# 讀取現有內容
$existingContent = ""
if (Test-Path $hostsFile) {
    $existingContent = Get-Content $hostsFile -Raw -ErrorAction SilentlyContinue
}

# 檢查是否已存在設定
$marker = "# 重新總店私人 DNS"
if ($existingContent -match [regex]::Escape($marker)) {
    Write-Host "  ⚠ 發現現有設定，將更新..." -ForegroundColor Yellow
    
    # 移除舊的設定區塊
    $lines = Get-Content $hostsFile
    $newLines = @()
    $inBlock = $false
    
    foreach ($line in $lines) {
        if ($line -match [regex]::Escape($marker)) {
            $inBlock = $true
            continue
        }
        if ($inBlock -and ($line -match "^# |^$" -or $line -match "^192\.168\.50\.")) {
            continue
        }
        if ($inBlock -and -not ($line -match "^192\.168\.50\.")) {
            $inBlock = $false
        }
        if (-not $inBlock) {
            $newLines += $line
        }
    }
    
    $newLines | Set-Content $hostsFile -Encoding ASCII
}

# 新增 DNS 設定
$hostsEntries = @"

$marker - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
$ServerIP    pos-server.$Domain
$ServerIP    odoo.$Domain
$ServerIP    api.$Domain
$ServerIP    pos-server
$ServerIP    odoo-server
$RouterIP    router.$Domain
$RouterIP    router

"@

Add-Content -Path $hostsFile -Value $hostsEntries -Encoding ASCII
Write-Host "  ✓ Hosts 檔案已更新" -ForegroundColor Green

# 2. 清除 DNS 快取
Write-Host "`n[2] 清除 DNS 快取..." -ForegroundColor Yellow
try {
    ipconfig /flushdns | Out-Null
    Write-Host "  ✓ DNS 快取已清除" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ 清除 DNS 快取失敗: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 3. 測試 DNS 解析
Write-Host "`n[3] 測試 DNS 解析..." -ForegroundColor Yellow
$testHosts = @(
    "pos-server.$Domain",
    "odoo.$Domain",
    "api.$Domain",
    "pos-server",
    "odoo-server"
)

$allResolved = $true
foreach ($host in $testHosts) {
    try {
        $result = [System.Net.Dns]::GetHostAddresses($host)
        $ip = $result[0].IPAddressToString
        Write-Host "  ✓ $host → $ip" -ForegroundColor Green
        
        if ($ip -ne $ServerIP -and $host -notmatch "router") {
            Write-Host "    ⚠ 警告: IP 地址不符合預期 ($ServerIP)" -ForegroundColor Yellow
            $allResolved = $false
        }
    } catch {
        Write-Host "  ❌ $host → 解析失敗: $($_.Exception.Message)" -ForegroundColor Red
        $allResolved = $false
    }
}

# 4. 測試服務連線
Write-Host "`n[4] 測試服務連線..." -ForegroundColor Yellow
$services = @(
    @{Name="Odoo Web"; Host="pos-server.$Domain"; Port=8069},
    @{Name="Odoo API"; Host="api.$Domain"; Port=8069}
)

$allConnected = $true
foreach ($service in $services) {
    try {
        $connection = Test-NetConnection -ComputerName $service.Host -Port $service.Port -WarningAction SilentlyContinue -InformationLevel Quiet -ErrorAction Stop
        if ($connection) {
            Write-Host "  ✓ $($service.Name) ($($service.Host):$($service.Port)) - 連線成功" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ $($service.Name) ($($service.Host):$($service.Port)) - 連線失敗（服務可能未啟動）" -ForegroundColor Yellow
            $allConnected = $false
        }
    } catch {
        Write-Host "  ⚠ $($service.Name) - 無法測試: $($_.Exception.Message)" -ForegroundColor Yellow
        $allConnected = $false
    }
}

# 5. 顯示設定摘要
Write-Host "`n=== 設定完成 ===" -ForegroundColor Green
Write-Host "`n主機名稱對應：" -ForegroundColor Cyan
Write-Host "  pos-server.$Domain → $ServerIP" -ForegroundColor White
Write-Host "  odoo.$Domain → $ServerIP" -ForegroundColor White
Write-Host "  api.$Domain → $ServerIP" -ForegroundColor White
Write-Host "  router.$Domain → $RouterIP" -ForegroundColor White
Write-Host "`n簡化主機名稱：" -ForegroundColor Cyan
Write-Host "  pos-server → $ServerIP" -ForegroundColor White
Write-Host "  odoo-server → $ServerIP" -ForegroundColor White
Write-Host "  router → $RouterIP" -ForegroundColor White

if ($allResolved) {
    Write-Host "`n✓ 所有 DNS 解析測試通過" -ForegroundColor Green
} else {
    Write-Host "`n⚠ 部分 DNS 解析測試失敗，請檢查設定" -ForegroundColor Yellow
}

Write-Host "`n使用方式：" -ForegroundColor Yellow
Write-Host "  在 POS 設備中使用: http://pos-server.$Domain:8069/pos/ui" -ForegroundColor White
Write-Host "  或簡化版本: http://pos-server:8069/pos/ui" -ForegroundColor White
Write-Host "`n下一步：" -ForegroundColor Yellow
Write-Host "  1. 在路由器設定 DNS 主機名稱（如果支援）" -ForegroundColor White
Write-Host "  2. 更新 POS 設備的連線 URL" -ForegroundColor White
Write-Host "  3. 測試 POS 設備連線" -ForegroundColor White
