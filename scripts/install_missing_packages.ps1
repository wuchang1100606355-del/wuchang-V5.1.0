# install_missing_packages.ps1
# 安裝缺失的 Python 套件

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "安裝缺失的 Python 套件" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 檢查 Python
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonPath) {
    Write-Host "❌ 找不到 Python，請確認 Python 已安裝並在 PATH 中" -ForegroundColor Red
    exit 1
}

Write-Host "✓ 找到 Python: $($pythonPath.Source)" -ForegroundColor Green
Write-Host ""

# 檢查並安裝套件
$packages = @("Flask", "google-auth")

foreach ($package in $packages) {
    Write-Host "檢查 $package..." -ForegroundColor Yellow
    
    # 檢查是否已安裝
    $installed = python -m pip show $package 2>$null
    if ($installed) {
        Write-Host "  ✓ $package 已安裝" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ $package 未安裝，正在安裝..." -ForegroundColor Yellow
        python -m pip install $package
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ $package 安裝成功" -ForegroundColor Green
        } else {
            Write-Host "  ❌ $package 安裝失敗" -ForegroundColor Red
        }
    }
    Write-Host ""
}

# 驗證安裝
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "安裝結果驗證" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

foreach ($package in $packages) {
    $info = python -m pip show $package 2>$null
    if ($info) {
        $version = ($info | Select-String -Pattern "Version:").ToString().Split(":")[1].Trim()
        Write-Host "✓ $package $version" -ForegroundColor Green
    } else {
        Write-Host "❌ $package 未安裝" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "安裝完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
