# 接收 UI 筆電指令檔案腳本
# 自動從 UI 筆電同步檔案到本地

Write-Host "=== 接收 UI 筆電指令檔案 ===" -ForegroundColor Cyan

# 1. 偵測 UI 筆電
Write-Host "`n[1] 偵測 UI 筆電設備..." -ForegroundColor Yellow

# 常見的 UI 筆電 IP 地址
$uiLaptopIPs = @(
    "192.168.50.84",  # LUNGsMSI
    "192.168.50.88",  # 另一個可能的 UI 設備
    "192.168.50.80"
)

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
    Write-Host "  ⚠ 未找到在線的 UI 筆電設備" -ForegroundColor Yellow
    Write-Host "`n請手動指定 IP 地址：" -ForegroundColor Yellow
    $manualIP = Read-Host "  請輸入 UI 筆電 IP 地址"
    if ($manualIP) {
        $foundIP = $manualIP
    } else {
        Write-Host "  ❌ 未指定 IP 地址，退出" -ForegroundColor Red
        exit 1
    }
}

# 2. 檢查網絡共享
Write-Host "`n[2] 檢查網絡共享..." -ForegroundColor Yellow
$shareNames = @("wuchang", "C$", "Users", "share")
$remotePath = $null

foreach ($share in $shareNames) {
    $testPath = "\\$foundIP\$share"
    Write-Host "  檢查 $testPath..." -ForegroundColor Gray
    if (Test-Path $testPath -ErrorAction SilentlyContinue) {
        if ($share -eq "wuchang") {
            $remotePath = $testPath
        } elseif ($share -eq "C$" -or $share -eq "Users") {
            # 尋找 wuchang 目錄
            $wuchangPath = Join-Path $testPath "wuchang"
            if (Test-Path $wuchangPath -ErrorAction SilentlyContinue) {
                $remotePath = $wuchangPath
            }
        } else {
            $remotePath = $testPath
        }
        
        if ($remotePath) {
            Write-Host "  ✓ 找到共享路徑: $remotePath" -ForegroundColor Green
            break
        }
    }
}

if (-not $remotePath) {
    Write-Host "  ⚠ 未找到共享路徑" -ForegroundColor Yellow
    Write-Host "`n請手動指定共享路徑：" -ForegroundColor Yellow
    $manualPath = Read-Host "  請輸入共享路徑 (例如: \\192.168.50.84\wuchang)"
    if ($manualPath) {
        $remotePath = $manualPath
    } else {
        Write-Host "  ❌ 未指定共享路徑，退出" -ForegroundColor Red
        exit 1
    }
}

# 3. 執行同步（預覽模式）
Write-Host "`n[3] 執行同步（預覽模式）..." -ForegroundColor Yellow
Write-Host "  遠端路徑: $remotePath" -ForegroundColor Cyan
Write-Host "  本地路徑: $(Get-Location)" -ForegroundColor Cyan

$pythonCmd = "python scripts/sync_with_ui_laptop.py --remote-path `"$remotePath`" --sync-strategy newer --dry-run"
Write-Host "`n  執行命令: $pythonCmd" -ForegroundColor Gray

$preview = & python scripts/sync_with_ui_laptop.py --remote-path $remotePath --sync-strategy newer --dry-run 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n  ✓ 預覽完成" -ForegroundColor Green
    Write-Host $preview
} else {
    Write-Host "`n  ⚠ 預覽執行時發生錯誤" -ForegroundColor Yellow
    Write-Host $preview
}

# 4. 確認是否執行實際同步
Write-Host "`n[4] 確認執行同步..." -ForegroundColor Yellow
$confirm = Read-Host "  是否執行實際同步？ (Y/N)"
if ($confirm -eq 'Y' -or $confirm -eq 'y') {
    Write-Host "`n  正在執行同步..." -ForegroundColor Yellow
    $sync = & python scripts/sync_with_ui_laptop.py --remote-path $remotePath --sync-strategy newer 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n  ✓ 同步完成！" -ForegroundColor Green
        Write-Host $sync
    } else {
        Write-Host "`n  ❌ 同步失敗" -ForegroundColor Red
        Write-Host $sync
    }
} else {
    Write-Host "`n  已取消同步" -ForegroundColor Gray
}

Write-Host "`n=== 完成 ===" -ForegroundColor Cyan
