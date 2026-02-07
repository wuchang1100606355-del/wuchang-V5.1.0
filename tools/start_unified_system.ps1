Write-Host "=== Wuchang Unified System Launcher (200 AI Consensus) ==="
Write-Host "Identity: admin@wuchang.life (Enforced)"

# 1. Start Core (Data & Logic)
Write-Host "Starting Core Stack (Data Plane)..."
docker-compose -f config/docker-compose-core.yml up -d
if ($LASTEXITCODE -ne 0) { Write-Error "Core Stack Failed!"; exit 1 }

# 2. Health Check
Write-Host "Waiting for Wuchang Core (Odoo) to initialize..."
$retries = 30
while ($retries -gt 0) {
    if (Test-NetConnection -ComputerName localhost -Port 8069 -InformationLevel Quiet) {
        Write-Host "Core is UP!"
        break
    }
    Start-Sleep -Seconds 2
    $retries--
}

# 3. Start Senses (Perception Plane)
Write-Host "Starting Senses Stack (Perception Plane)..."
docker-compose -f config/docker-compose-senses.yml up -d
if ($LASTEXITCODE -ne 0) { Write-Error "Senses Stack Failed!"; exit 1 }

Write-Host "=== Unified System Mounted Successfully ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
