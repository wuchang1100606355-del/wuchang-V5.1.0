Write-Host "=== Wuchang Local Environment Audit ===" -ForegroundColor Cyan

Write-Host "`n[1] System Resources" -ForegroundColor Yellow
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, @{Name='RAM_Total_GB';Expression={[math]::Round($_.TotalVisibleMemorySize/1MB, 2)}}, @{Name='RAM_Free_GB';Expression={[math]::Round($_.FreePhysicalMemory/1MB, 2)}}
Get-PSDrive C | Select-Object @{Name='Disk_C_Free_GB';Expression={[math]::Round($_.Free/1GB, 2)}}, @{Name='Disk_C_Total_GB';Expression={[math]::Round($_.Used/1GB + $_.Free/1GB, 2)}}

Write-Host "`n[2] Network Status" -ForegroundColor Yellow
ipconfig /all | Select-String 'IPv4 Address', 'Default Gateway', 'DNS Servers', 'Description' -Context 0,2
Write-Host "Testing Internet (8.8.8.8)..." -NoNewline
try { $null = Test-Connection 8.8.8.8 -Count 1 -ErrorAction Stop; Write-Host " OK" -ForegroundColor Green } catch { Write-Host " FAIL" -ForegroundColor Red }
Write-Host "Testing Router (192.168.50.1)..." -NoNewline
try { $null = Test-Connection 192.168.50.1 -Count 1 -ErrorAction Stop; Write-Host " OK" -ForegroundColor Green } catch { Write-Host " FAIL" -ForegroundColor Red }

Write-Host "`n[3] Tailscale Status" -ForegroundColor Yellow
tailscale status

Write-Host "`n[4] Docker Services" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host "`n[5] Critical Ports Check" -ForegroundColor Yellow
$ports = @{8069='Odoo'; 5432='PostgreSQL'; 80='Caddy HTTP'; 443='Caddy HTTPS'; 11434='Ollama'}
foreach ($port in $ports.Keys) {
    $p = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($p) { Write-Host "$($ports[$port]) ($port): LISTENING" -ForegroundColor Green }
    else { Write-Host "$($ports[$port]) ($port): NOT LISTENING" -ForegroundColor Red }
}

Write-Host "`n=== Audit Complete ===" -ForegroundColor Cyan
