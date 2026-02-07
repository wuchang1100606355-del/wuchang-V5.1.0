Write-Host "STOPPING Bidirectional Joint Operation..." -ForegroundColor Yellow

# Function to kill process by port
function Kill-Port($port) {
    $tcp = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($tcp) {
        $pid_to_kill = $tcp.OwningProcess
        Write-Host "   Killing process $pid_to_kill on port $port..." -ForegroundColor DarkGray
        Stop-Process -Id $pid_to_kill -Force -ErrorAction SilentlyContinue
    }
}

Kill-Port 8765
Kill-Port 8766

Write-Host "STARTING Server Directed Mode..." -ForegroundColor Green

$pythonPath = "c:\wuchang V5.1.0\.venv\Scripts\python.exe"

# Start Local UI Server (Background)
$uiServer = Start-Process $pythonPath -ArgumentList "remote_ui_control/local_ui_server.py" -PassThru -NoNewWindow
Write-Host "   [OK] Local UI Server Started (PID: $($uiServer.Id))"

# Start Cloud Sync Service in Passive Mode (Background)
$syncService = Start-Process $pythonPath -ArgumentList "remote_ui_control/cloud_sync_service.py", "--passive" -PassThru -NoNewWindow
Write-Host "   [OK] Cloud Sync Service (Passive Mode) Started (PID: $($syncService.Id))"

Write-Host ""
Write-Host "SYSTEM IS NOW IN SERVER-DIRECTED OPTIMIZATION MODE" -ForegroundColor Cyan
Write-Host "Waiting for server communication..." -ForegroundColor Cyan
