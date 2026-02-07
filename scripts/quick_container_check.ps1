# Quick Container Check Script
# UTF-8 encoding

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "UI Container Quick Check" -ForegroundColor Cyan

# Check Docker
try {
    docker --version | Out-Null
    Write-Host "[OK] Docker is running" -ForegroundColor Green
} catch {
    Write-Host "[X] Docker is not running" -ForegroundColor Red
    exit 1
}

# Check containers
Write-Host "`nContainer Status:" -ForegroundColor Yellow
docker ps --format "table {{.Names}}`t{{.Status}}`t{{.Ports}}" 2>&1

# Check ports
Write-Host "`nPort Status:" -ForegroundColor Yellow
$ports = @(8069, 8080, 3001, 8888)
foreach ($port in $ports) {
    $conn = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($conn) {
        Write-Host "  Port $port : In Use" -ForegroundColor Green
    } else {
        Write-Host "  Port $port : Not Used" -ForegroundColor Yellow
    }
}

# Quick connection test
Write-Host "`nQuick Connection Test:" -ForegroundColor Yellow
try {
    $r = Invoke-WebRequest -Uri "http://localhost:8069" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "  Odoo (8069): OK" -ForegroundColor Green
} catch {
    Write-Host "  Odoo (8069): No Response" -ForegroundColor Red
}

try {
    $r = Invoke-WebRequest -Uri "http://localhost:8888/api/supervisor/status" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "  AI Supervisor (8888): OK" -ForegroundColor Green
} catch {
    Write-Host "  AI Supervisor (8888): No Response" -ForegroundColor Red
}
