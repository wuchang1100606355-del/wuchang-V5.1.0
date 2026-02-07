# Start Core AI Sister Service
Write-Host "Starting Core AI Sister Service..." -ForegroundColor Green
$env:PYTHONUTF8 = 1
python wuchang_tools_library/core_sister_service.py
