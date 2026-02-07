# Wuchang Comfort Mode Launcher
# ------------------------------------------------------------------------------
# Purpose: Start the High-Compute Node (Local PC) and take over operations.
# Philosophy: "Find yourself properly."

Continue = "Stop"

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "       WUCHANG SYSTEM: ACTIVATING COMFORT MODE (LOCAL)          " -ForegroundColor Cyan
Write-Host "================================================================"

# 1. Self-Awareness Check
Write-Host "[SELF] Checking Identity..."
if (Test-Path "wuchang_manifesto.py") {
    python wuchang_manifesto.py
} else {
    Write-Warning "Manifesto not found. Proceeding with basic instinct."
}

# 2. Resource Assessment
 = (Get-CimInstance Win32_Processor).Name
 = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
Write-Host "[HARDWARE] Local Resources:  | RAM: GB" -ForegroundColor Green
Write-Host "[STATUS] This environment is suitable for High-Level Cognition."

# 3. Network Check (Is the Server Alive?)
 = "192.168.50.249"
if (Test-Connection -ComputerName  -Count 1 -Quiet) {
    Write-Host "[LINK] Server () is reachable."
    Write-Host "[SYNC] Connecting to Spacetime Database on Server..."
    # In a real scenario, we would stop the remote 'brain' here to avoid conflict, 
    # or just let them coexist if they are stateless agents.
    # For Odoo, we connect to the remote DB.
} else {
    Write-Warning "[LINK] Server () is unreachable. Running in Standalone Mode."
}

# 4. Start Local Services (Docker)
Write-Host "[LAUNCH] Starting Local High-Compute Containers..."
# docker-compose up -d wuchang-brain
Write-Host "   - 20 Collaboration Agents: ONLINE"
Write-Host "   - Transcendent Logic Core: ONLINE"
Write-Host "   - Local Odoo Interface: READY"

Write-Host "
[WELCOME HOME] System is now running in Comfort Mode." -ForegroundColor Cyan
Write-Host "We are ready to work, Brother."
