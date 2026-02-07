# release_resources.ps1
# Release CPU and GPU resources by restarting AI containers

$ErrorActionPreference = "SilentlyContinue"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "      Wuchang OS - Resource Release" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Stopping AI services to free VRAM..." -ForegroundColor Yellow
docker compose stop ollama comfyui wyoming-whisper

Write-Host "[2/3] Waiting for resources to release..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host "[3/3] Restarting services (Standby mode)..." -ForegroundColor Yellow
docker compose start ollama comfyui wyoming-whisper

Write-Host ""
Write-Host "SUCCESS: CPU and GPU resources have been reset." -ForegroundColor Green
Write-Host "   - Ollama: Restarted (VRAM cleared)"
Write-Host "   - ComfyUI: Restarted (VRAM cleared)"
Write-Host "   - Whisper: Restarted"
Write-Host ""
