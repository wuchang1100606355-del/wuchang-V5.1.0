# 自動接收 UI 筆電指令檔案腳本
# 無需互動，自動偵測並同步

param(
    [string]$RemoteIP = "",
    [string]$RemotePath = "",
    [switch]$DryRun = $true,
    [ValidateSet("newer", "larger")]
    [string]$Strategy = "newer"
)

Write-Host "=== 自動接收 UI 筆電指令檔案 ===" -ForegroundColor Cyan

# 1. 偵測或使用指定的 IP
if ($RemoteIP) {
    $foundIP = $RemoteIP
    Write-Host "`n[1] 使用指定的 IP: $foundIP" -ForegroundColor Green
} else {
    Write-Host "`n[1] 自動偵測 UI 筆電..." -ForegroundColor Yellow
    
    # 常見的 UI 筆電 IP 地址
    $uiLaptopIPs = @("192.168.50.84", "192.168.50.88", "192.168.50.80")
    
    $foundIP = $null
    foreach ($ip in $uiLaptopIPs) {
        Write-Host "  檢查 $ip..." -ForegroundColor Gray
        try {
            $result = Test-Connection -ComputerName $ip -Count 1 -Quiet -ErrorAction SilentlyContinue
            if ($result) {
                Write-Host "  ✓ 找到在線設備: $ip" -ForegroundColor Green
                $foundIP = $ip
                break
            }
        } catch {
            continue
        }
    }
    
    if (-not $foundIP) {
        Write-Host "  ❌ 未找到在線的 UI 筆電設備" -ForegroundColor Red
        exit 1
    }
}

# 2. 檢查或使用指定的共享路徑
if ($RemotePath) {
    $sharePath = $RemotePath
    Write-Host "`n[2] 使用指定的共享路徑: $sharePath" -ForegroundColor Green
} else {
    Write-Host "`n[2] 檢查網絡共享..." -ForegroundColor Yellow
    $shareNames = @("wuchang", "C$", "Users", "share")
    $sharePath = $null
    
    foreach ($share in $shareNames) {
        $testPath = "\\$foundIP\$share"
        if (Test-Path $testPath -ErrorAction SilentlyContinue) {
            if ($share -eq "wuchang") {
                $sharePath = $testPath
            } elseif ($share -eq "C$" -or $share -eq "Users") {
                $wuchangPath = Join-Path $testPath "wuchang"
                if (Test-Path $wuchangPath -ErrorAction SilentlyContinue) {
                    $sharePath = $wuchangPath
                }
            } else {
                $sharePath = $testPath
            }
            
            if ($sharePath) {
                Write-Host "  ✓ 找到共享路徑: $sharePath" -ForegroundColor Green
                break
            }
        }
    }
    
    if (-not $sharePath) {
        Write-Host "  ❌ 未找到共享路徑" -ForegroundColor Red
        exit 1
    }
}

# 3. 執行同步
Write-Host "`n[3] 執行同步..." -ForegroundColor Yellow
Write-Host "  遠端路徑: $sharePath" -ForegroundColor Cyan
Write-Host "  本地路徑: $(Get-Location)" -ForegroundColor Cyan
Write-Host "  策略: $Strategy" -ForegroundColor Cyan
Write-Host "  模式: $(if ($DryRun) { '預覽 (Dry-Run)' } else { '實際同步' })" -ForegroundColor Cyan

$dryRunFlag = if ($DryRun) { "--dry-run" } else { "" }
$cmd = "python scripts/sync_with_ui_laptop.py --remote-path `"$sharePath`" --sync-strategy $Strategy $dryRunFlag"

Write-Host "`n  執行命令: $cmd" -ForegroundColor Gray

$output = & python scripts/sync_with_ui_laptop.py --remote-path $sharePath --sync-strategy $Strategy $(if ($DryRun) { "--dry-run" }) 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n  ✓ 執行完成！" -ForegroundColor Green
    Write-Host $output
} else {
    Write-Host "`n  ❌ 執行失敗" -ForegroundColor Red
    Write-Host $output
    exit 1
}

Write-Host "`n=== 完成 ===" -ForegroundColor Cyan
