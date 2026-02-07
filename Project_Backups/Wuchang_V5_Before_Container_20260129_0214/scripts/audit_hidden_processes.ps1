Write-Host '=== Wuchang Hidden & Suspicious Process Audit ===' -ForegroundColor Cyan

# 1. Get All Processes with detailed info
Write-Host 'Gathering process information...' -ForegroundColor Yellow
$processes = Get-CimInstance Win32_Process
$perfData = Get-Process -ErrorAction SilentlyContinue

# 2. Check for High Resource Usage (Top 5 CPU)
Write-Host "`n[1] Top 5 CPU Consumers" -ForegroundColor Yellow
$perfData | Sort-Object CPU -Descending | Select-Object -First 5 Name, Id, @{Name='CPU(s)';Expression={[math]::Round($_.CPU, 2)}}, Path

# 3. Check for Suspicious Paths (Temp, AppData)
Write-Host "`n[2] Processes Running from Suspicious Paths (Temp/AppData)" -ForegroundColor Yellow
$suspicious = $processes | Where-Object { 
    $_.ExecutablePath -match 'AppData' -or 
    $_.ExecutablePath -match 'Temp' 
} | Select-Object Name, ProcessId, ExecutablePath

if ($suspicious) {
    $suspicious | Format-Table -AutoSize
} else {
    Write-Host 'None found.' -ForegroundColor Green
}

# 4. Check for Hidden Windows (No Title but Interactive User Process)
# Note: Many system processes have no window. We focus on non-system users.
Write-Host "`n[3] Processes with Empty Command Lines (Potential Hiding)" -ForegroundColor Yellow
$emptyCmd = $processes | Where-Object { [string]::IsNullOrWhiteSpace($_.CommandLine) -and $_.Name -ne 'System Idle Process' -and $_.Name -ne 'System' }
if ($emptyCmd) {
    $emptyCmd | Select-Object Name, ProcessId | Format-Table -AutoSize
} else {
    Write-Host 'None found.' -ForegroundColor Green
}

# 5. Network Listeners (Non-Standard)
Write-Host "`n[4] Active Network Listeners (Process Mapping)" -ForegroundColor Yellow
$connections = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue
foreach ($conn in $connections) {
    $proc = $processes | Where-Object { $_.ProcessId -eq $conn.OwningProcess }
    $pName = if ($proc) { $proc.Name } else { "Unknown($($conn.OwningProcess))" }
    
    # Filter out common standard ports to reduce noise if needed, or show all for full audit
    Write-Host "Port $($conn.LocalPort) : $pName"
}

Write-Host "`n=== Audit Complete ===" -ForegroundColor Cyan
