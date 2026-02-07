# 五常 AI - 本機端 UI 控制服務啟動腳本
# 在本機 (192.168.50.84) 執行

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  🎮 五常 AI - 本機端 UI 控制服務" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# 檢查 Python
Write-Host "檢查 Python 環境..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "❌ 找不到 Python！請先安裝 Python 3.8+" -ForegroundColor Red
    exit 1
}

$pythonVersion = & python --version 2>&1
Write-Host "✅ $pythonVersion" -ForegroundColor Green
Write-Host ""

# 檢查依賴
Write-Host "檢查依賴套件..." -ForegroundColor Yellow
$packagesOk = $true
$requiredPackages = @("websockets", "pyautogui")

foreach ($pkg in $requiredPackages) {
    $installed = & python -c "import $pkg" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 缺少套件: $pkg" -ForegroundColor Red
        $packagesOk = $false
    } else {
        Write-Host "✅ $pkg 已安裝" -ForegroundColor Green
    }
}

if (-not $packagesOk) {
    Write-Host ""
    Write-Host "正在安裝缺少的套件..." -ForegroundColor Yellow
    & python -m pip install -r requirements.txt
    Write-Host ""
}

# 檢查 .env 文件
Write-Host "檢查配置文件..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  找不到 .env 文件，使用預設配置" -ForegroundColor Yellow
    Write-Host "建議複製 .env.example 為 .env 並修改密鑰" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env 配置已找到" -ForegroundColor Green
}
Write-Host ""

# 檢查防火牆規則
Write-Host "檢查防火牆規則..." -ForegroundColor Yellow
$firewallRule = Get-NetFirewallRule -DisplayName "Allow-UI-Control-8765" -ErrorAction SilentlyContinue

if (-not $firewallRule) {
    Write-Host "⚠️  未找到防火牆規則，嘗試添加..." -ForegroundColor Yellow
    try {
        netsh advfirewall firewall add rule name="Allow-UI-Control-8765" dir=in action=allow protocol=tcp localport=8765 remoteip=192.168.50.249 | Out-Null
        Write-Host "✅ 防火牆規則已添加" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  添加防火牆規則需要管理員權限" -ForegroundColor Yellow
        Write-Host "   請以管理員身份執行此腳本，或手動添加規則" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ 防火牆規則已存在" -ForegroundColor Green
}
Write-Host ""

# 顯示網路資訊
Write-Host "網路資訊:" -ForegroundColor Cyan
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*"})[0].IPAddress
Write-Host "  本機 IP: $ipAddress" -ForegroundColor White
Write-Host "  監聽端口: 8765" -ForegroundColor White
Write-Host "  允許來自: 192.168.50.249" -ForegroundColor White
Write-Host ""

# 啟動服務
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  🚀 正在啟動服務..." -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "按 Ctrl+C 停止服務" -ForegroundColor Yellow
Write-Host ""

try {
    & python local_ui_server.py
} catch {
    Write-Host ""
    Write-Host "❌ 服務啟動失敗: $_" -ForegroundColor Red
    exit 1
}
