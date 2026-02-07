Write-Host '=== Wuchang Router Status Audit (Target: 192.168.50.1) ===' -ForegroundColor Cyan

$RouterIP = '192.168.50.1'

# 1. Basic Connectivity
Write-Host '
[1] ICMP Ping Test' -ForegroundColor Yellow
if (Test-Connection -ComputerName $RouterIP -Count 1 -Quiet) {
    Write-Host "Ping $RouterIP : SUCCESS" -ForegroundColor Green
} else {
    Write-Host "Ping $RouterIP : FAILED" -ForegroundColor Red
    exit
}

# 2. ARP Entry (MAC Address)
Write-Host '
[2] ARP / MAC Address Info' -ForegroundColor Yellow
$arp = arp -a $RouterIP
if ($arp) {
    $arp | Select-String $RouterIP | ForEach-Object { Write-Host $_.ToString().Trim() }
} else {
    Write-Host 'No ARP entry found.' -ForegroundColor Red
}

# 3. Service Port Scan
Write-Host '
[3] Service Port Scan' -ForegroundColor Yellow
$ports = @(80, 443, 8080, 8443, 22, 23, 53)
foreach ($port in $ports) {
    $tnc = Test-NetConnection -ComputerName $RouterIP -Port $port -WarningAction SilentlyContinue
    if ($tnc.TcpTestSucceeded) {
        Write-Host "Port $port : OPEN" -ForegroundColor Green
    } else {
        # Write-Host "Port $port : CLOSED" -ForegroundColor Gray
    }
}

# 4. Web Interface Check
Write-Host '
[4] Web Interface Check' -ForegroundColor Yellow

# Check HTTP (80)
try {
    $uri = "http://$RouterIP"
    $response = Invoke-WebRequest -Uri $uri -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
    if ($response) {
        $title = 'Unknown'
        if ($response.Content -match '<title>(.*?)</title>') {
            $title = $matches[1]
        }
        Write-Host "HTTP (80) Title: $title" -ForegroundColor Green
        Write-Host "HTTP (80) Status: $($response.StatusCode)" -ForegroundColor Green
    }
} catch {
    Write-Host "HTTP (80) Request Failed: $($_.Exception.Message)" -ForegroundColor Gray
}

# Check HTTPS (8443) - Common for ASUS/Routers
try {
    $uri = "https://$RouterIP:8443"
    $response = Invoke-WebRequest -Uri $uri -UseBasicParsing -TimeoutSec 3 -SkipCertificateCheck -ErrorAction SilentlyContinue
    if ($response) {
        $title = 'Unknown'
        if ($response.Content -match '<title>(.*?)</title>') {
            $title = $matches[1]
        }
        Write-Host "HTTPS (8443) Title: $title" -ForegroundColor Green
        Write-Host "HTTPS (8443) Status: $($response.StatusCode)" -ForegroundColor Green
    }
} catch {
    Write-Host "HTTPS (8443) Request Failed: $($_.Exception.Message)" -ForegroundColor Gray
}

# 5. DNS Resolution Check
Write-Host '
[5] DNS Resolver Test' -ForegroundColor Yellow
try {
    $dns = Resolve-DnsName -Name 'google.com' -Server $RouterIP -ErrorAction Stop
    if ($dns) {
        Write-Host "DNS Resolution (google.com): SUCCESS" -ForegroundColor Green 
    }
} catch {
    Write-Host "DNS Resolution: FAILED" -ForegroundColor Red
}

Write-Host '
=== Audit Complete ===' -ForegroundColor Cyan
