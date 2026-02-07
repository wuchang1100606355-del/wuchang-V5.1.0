Write-Host "🚀 Starting Full System User Flow Verification..." -ForegroundColor Cyan

# 1. Service Status Check
Write-Host "`n📡 checking Critical Services..." -ForegroundColor Yellow

$services = @(
    @{ Name="Odoo ERP"; Port=8069 },
    @{ Name="AI Assistant"; Port=8080 },
    @{ Name="UI Control Server"; Port=8765 },
    @{ Name="Cloud Sync Service"; Port=8766 },
    @{ Name="SSH Server"; Port=22 }
)

foreach ($svc in $services) {
    $check = Test-NetConnection -ComputerName localhost -Port $svc.Port -WarningAction SilentlyContinue
    if ($check.TcpTestSucceeded) {
        Write-Host "   ✅ $($svc.Name) is Running (Port $($svc.Port))" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $($svc.Name) is DOWN (Port $($svc.Port))" -ForegroundColor Red
    }
}

# 2. File System Monitoring Check
Write-Host "`n👀 Checking File System Monitor..." -ForegroundColor Yellow
$monitor = Get-Process -Name "python" | Where-Object { $_.MainWindowTitle -match "monitor_and_handshake" -or $_.CommandLine -match "monitor_and_handshake" }
if ($monitor -or (Get-Process python | Select-String "monitor")) {
    Write-Host "   ✅ File Monitor is Active" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  File Monitor might not be running (Check manually)" -ForegroundColor Yellow
}

# 3. Server Connectivity Check
Write-Host "`n🌍 Checking Server Connectivity (192.168.50.249)..." -ForegroundColor Yellow
$ping = Test-Connection -ComputerName "192.168.50.249" -Count 1 -Quiet
if ($ping) {
    Write-Host "   ✅ Server is Reachable (Ping Success)" -ForegroundColor Green
} else {
    Write-Host "   ❌ Server is Unreachable" -ForegroundColor Red
}

# 4. SSH Access Check
Write-Host "`nUA Checking Local User 'wuchang'..." -ForegroundColor Yellow
$userCheck = Get-LocalUser -Name "wuchang" -ErrorAction SilentlyContinue
if ($userCheck) {
    Write-Host "   ✅ User 'wuchang' exists" -ForegroundColor Green
} else {
    Write-Host "   ❌ User 'wuchang' NOT FOUND" -ForegroundColor Red
}

Write-Host "`n📋 Verification Complete." -ForegroundColor Cyan
