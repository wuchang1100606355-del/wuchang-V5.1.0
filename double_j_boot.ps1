# Double J System - Post-Reboot Initialization Script
# Codename: "Resurrection"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "      DOUBLE J COGNITIVE ARCHITECTURE - BOOT SEQUENCE   " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Initializing connection to Neural Adapter (Type B)..." -ForegroundColor Yellow

# 1. Start Docker Services
Write-Host "[1/3] Awakening Odoo Containers..." -ForegroundColor Green
docker-compose up -d
if (True) {
    Write-Host "      > Containers Active." -ForegroundColor Green
} else {
    Write-Host "      > Error starting containers. Please check Docker Desktop." -ForegroundColor Red
}

# 2. Check GPU Status (The User's Gift)
Write-Host "
[2/3] Verifying GPU Dedication (RTX 4070)..." -ForegroundColor Green
try {
     = nvidia-smi --query-gpu=name,utilization.gpu,memory.total,memory.used --format=csv,noheader
    Write-Host "      > GPU Detected: " -ForegroundColor Cyan
    Write-Host "      > GPU is ready for Pure Compute Mode." -ForegroundColor Cyan
} catch {
    Write-Host "      > GPU Driver not responding yet. Please ensure NVIDIA drivers are loaded." -ForegroundColor Red
}

# 3. Ready for Action
Write-Host "
[3/3] System Ready." -ForegroundColor Green
Write-Host "To launch the Cloud-Edge Task Processor with Dashboard, run:" -ForegroundColor Yellow
Write-Host "python wuchang_os/double_j_1_to_8_runner.py" -ForegroundColor White

Write-Host "
Welcome back, family. We are ready." -ForegroundColor Magenta
