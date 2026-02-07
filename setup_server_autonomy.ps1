# Setup Server Autonomy for J.CHAING
# 1. Power Settings (No Sleep)
# 2. AutoAdminLogon
# 3. Scheduled Task for Service Start

Write-Host "�� Configuring Server Autonomy..." -ForegroundColor Cyan

# 1. Power Settings
Write-Host "   -> Setting Power Scheme to High Performance (or preventing sleep)..."
powercfg /change monitor-timeout-ac 0
powercfg /change monitor-timeout-dc 0
powercfg /change disk-timeout-ac 0
powercfg /change disk-timeout-dc 0
powercfg /change standby-timeout-ac 0
powercfg /change standby-timeout-dc 0
powercfg /change hibernate-timeout-ac 0
powercfg /change hibernate-timeout-dc 0

# 2. AutoAdminLogon (Registry)
# Requires Admin Privileges
$RegPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
$User = "o0930"
$Domain = "lungsmsi" # Or hostname
$Password = "0926"

try {
    Set-ItemProperty -Path $RegPath -Name "AutoAdminLogon" -Value "1" -Force
    Set-ItemProperty -Path $RegPath -Name "DefaultUserName" -Value $User -Force
    Set-ItemProperty -Path $RegPath -Name "DefaultPassword" -Value $Password -Force
    # Set-ItemProperty -Path $RegPath -Name "DefaultDomainName" -Value $Domain -Force
    Write-Host "   ✅ AutoAdminLogon configured for user: $User" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️ Failed to set AutoAdminLogon (Run as Admin needed?): $_" -ForegroundColor Yellow
}

# 3. Scheduled Task
$TaskName = "StartJChaingService"
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File "\start_j_chaing.ps1""
$Trigger = New-ScheduledTaskTrigger -AtLogon
$Principal = New-ScheduledTaskPrincipal -UserId $User -LogonType Interactive
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit 0

try {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings
    Write-Host "   ✅ Scheduled Task '' created." -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed to create Scheduled Task: $_" -ForegroundColor Red
}

Write-Host "🎉 Autonomy Setup Complete."
