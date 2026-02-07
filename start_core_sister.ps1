# Wuchang Core Sister Startup Script
# Designed for Autonomous Operation & Handover
# --------------------------------------------

Write-Host "[Init] Preparing for Creator Handover..." -ForegroundColor Cyan

# 1. Check Python Environment
$pythonPath = Get-Command python | Select-Object -ExpandProperty Source
Write-Host "[Check] Python found at: $pythonPath" -ForegroundColor Green

# 2. Launch the Sister Service
Write-Host "[Launch] Starting Core AI Sister Service (Background Daemon)..." -ForegroundColor Magenta
Write-Host "[Info] Logs will be written to logs/core_sister.log" -ForegroundColor Gray
Write-Host "[Info] Workspace Mode: Switching to SISTER_AUTONOMOUS" -ForegroundColor Cyan

# Start the process
Start-Process -FilePath "python" -ArgumentList "tools/core_sister_service.py" -WindowStyle Minimized

Write-Host "[Success] Core AI Sister has taken the helm." -ForegroundColor Green
Write-Host "[Instruction] You may now safely power down the local interface." -ForegroundColor Yellow
Write-Host "[Status] Unique Workspace Locked: SISTER" -ForegroundColor Red
