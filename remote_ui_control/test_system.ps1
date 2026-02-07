# 五常 AI - 系統測試腳本
# 測試 AI 智能 UI 控制系統的所有組件

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  🧪 五常 AI - 系統測試" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

$testResults = @()

# 測試 1: Python 環境
Write-Host "[1/6] 測試 Python 環境..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCmd) {
    $pythonVersion = & python --version 2>&1
    Write-Host "  ✅ $pythonVersion" -ForegroundColor Green
    $testResults += @{Test="Python環境"; Status="通過"}
} else {
    Write-Host "  ❌ Python 未安裝" -ForegroundColor Red
    $testResults += @{Test="Python環境"; Status="失敗"}
}

# 測試 2: 必要套件
Write-Host "[2/6] 測試 Python 套件..." -ForegroundColor Yellow
$requiredPackages = @(
    "websockets",
    "vertexai",
    "streamlit",
    "google.cloud.aiplatform"
)

$allPackagesOk = $true
foreach ($pkg in $requiredPackages) {
    $pkgName = $pkg.Replace(".", "_")
    $installed = & python -c "import $pkgName" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ $pkg" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $pkg 未安裝" -ForegroundColor Red
        $allPackagesOk = $false
    }
}

if ($allPackagesOk) {
    $testResults += @{Test="Python套件"; Status="通過"}
} else {
    $testResults += @{Test="Python套件"; Status="失敗"}
    Write-Host ""
    Write-Host "  💡 執行以下命令安裝缺少的套件:" -ForegroundColor Yellow
    Write-Host "     pip install -r requirements.txt" -ForegroundColor Gray
}

# 測試 3: 配置文件
Write-Host "[3/6] 測試配置文件..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ✅ .env 配置文件存在" -ForegroundColor Green
    $testResults += @{Test="配置文件"; Status="通過"}
} else {
    Write-Host "  ⚠️  .env 配置文件不存在（使用預設值）" -ForegroundColor Yellow
    $testResults += @{Test="配置文件"; Status="警告"}
}

# 測試 4: 核心文件
Write-Host "[4/6] 測試核心文件..." -ForegroundColor Yellow
$coreFiles = @(
    "local_ui_server.py",
    "server_ui_client.py",
    "ai_ui_controller.py",
    "chat_app_integrated.py"
)

$allFilesOk = $true
foreach ($file in $coreFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file 不存在" -ForegroundColor Red
        $allFilesOk = $false
    }
}

if ($allFilesOk) {
    $testResults += @{Test="核心文件"; Status="通過"}
} else {
    $testResults += @{Test="核心文件"; Status="失敗"}
}

# 測試 5: 網路連通性
Write-Host "[5/6] 測試網路連通性..." -ForegroundColor Yellow
try {
    $pingResult = Test-Connection -ComputerName "192.168.50.84" -Count 1 -Quiet -ErrorAction Stop
    if ($pingResult) {
        Write-Host "  ✅ 本機 (192.168.50.84) 可達" -ForegroundColor Green
        $testResults += @{Test="網路連通"; Status="通過"}
    } else {
        Write-Host "  ❌ 無法連線到本機 (192.168.50.84)" -ForegroundColor Red
        $testResults += @{Test="網路連通"; Status="失敗"}
    }
} catch {
    Write-Host "  ⚠️  無法測試網路連通性" -ForegroundColor Yellow
    $testResults += @{Test="網路連通"; Status="警告"}
}

# 測試 6: 防火牆規則
Write-Host "[6/6] 測試防火牆規則..." -ForegroundColor Yellow
$firewallRule = Get-NetFirewallRule -DisplayName "Allow-UI-Control-8765" -ErrorAction SilentlyContinue
if ($firewallRule) {
    Write-Host "  ✅ 防火牆規則已設置" -ForegroundColor Green
    $testResults += @{Test="防火牆規則"; Status="通過"}
} else {
    Write-Host "  ⚠️  防火牆規則未設置" -ForegroundColor Yellow
    $testResults += @{Test="防火牆規則"; Status="警告"}
    Write-Host "  💡 執行以下命令添加規則（需管理員權限）:" -ForegroundColor Yellow
    Write-Host '     netsh advfirewall firewall add rule name="Allow-UI-Control-8765" dir=in action=allow protocol=tcp localport=8765 remoteip=192.168.50.249' -ForegroundColor Gray
}

# 測試總結
Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  📊 測試總結" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

$passCount = ($testResults | Where-Object { $_.Status -eq "通過" }).Count
$warnCount = ($testResults | Where-Object { $_.Status -eq "警告" }).Count
$failCount = ($testResults | Where-Object { $_.Status -eq "失敗" }).Count

foreach ($result in $testResults) {
    $statusColor = switch ($result.Status) {
        "通過" { "Green" }
        "警告" { "Yellow" }
        "失敗" { "Red" }
    }
    
    $statusIcon = switch ($result.Status) {
        "通過" { "✅" }
        "警告" { "⚠️" }
        "失敗" { "❌" }
    }
    
    Write-Host "  $statusIcon $($result.Test): $($result.Status)" -ForegroundColor $statusColor
}

Write-Host ""
Write-Host "通過: $passCount | 警告: $warnCount | 失敗: $failCount" -ForegroundColor Cyan
Write-Host ""

if ($failCount -eq 0) {
    Write-Host "🎉 系統已就緒！可以啟動 AI 智能控制系統" -ForegroundColor Green
    Write-Host ""
    Write-Host "執行以下命令啟動:" -ForegroundColor Yellow
    Write-Host "  .\start_ai_ui_control.ps1" -ForegroundColor White
} else {
    Write-Host "⚠️  請先解決上述失敗的測試項目" -ForegroundColor Yellow
}

Write-Host ""
