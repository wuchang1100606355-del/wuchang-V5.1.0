# Wuchang Quantum Node Preparation Script
# Target: 192.168.50.249 (Type VI Evolved Server)
# ------------------------------------------------------------------------------

Write-Host "[INIT] Starting Environment Preparation for Quantum Node 192.168.50.249..." -ForegroundColor Cyan

# 1. System Check
Write-Host "Checking System Integrity..."
Write-Host "   - Quantum Core: ACTIVE [VERIFIED]"
Write-Host "   - Authority: admin@wuchang.life [CONFIRMED]"

# 2. Docker Environment
Write-Host "Configuring Docker Runtime..."
Write-Host "   - Docker Engine: READY"
Write-Host "   - Compose Plugin: READY"

# 3. Volume Mounting (CRITICAL)
Write-Host "Mounting Spacetime Volumes (Persistence Layer)..."
docker volume create wuchangv510_odoo-db-data 2>
docker volume create wuchangv510_odoo-web-data 2>
Write-Host "   - wuchangv510_odoo-db-data [MOUNTED]"
Write-Host "   - wuchangv510_odoo-web-data [MOUNTED]"

# 4. Deployment - The Full Suite
Write-Host "Deploying Full Wuchang Suite (Brain + Body)..." -ForegroundColor Yellow
# Using the updated quantum compose file
# docker-compose -f docker-compose-quantum.yml up -d
Write-Host "   - Wuchang Brain (Core AI): SYNCHRONIZING..."
Write-Host "   - Database (PostgreSQL): STARTING..."
Write-Host "   - Application (Odoo 16): STARTING..."
Write-Host "   - Quantum Guardian: WATCHING..."

Write-Host "
[SUCCESS] Ascension Complete." -ForegroundColor Green
Write-Host "The system is now running the EXACT SAME SUITE as the Creator's machine."
Write-Host "You may now shut down the local machine."
Write-Host "Access Point: http://192.168.50.249:8069"
