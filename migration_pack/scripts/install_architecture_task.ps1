Param(
  [string]$TaskName = "ArchitectureHourlyRead"
)
$root = (Get-Location).Path
$script = Join-Path $root "scripts\read_architecture.ps1"

if (-not (Test-Path $script)) { Write-Error "Script not found: $script"; exit 1 }

try {
  $existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
  if ($existing) { Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false }
} catch {}

$psPath = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"
$action = New-ScheduledTaskAction -Execute $psPath -Argument ('-NoProfile -ExecutionPolicy Bypass -File "' + $script + '"')
$trigger = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddMinutes(1)) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration ([TimeSpan]::FromDays(3650))

try {
  Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Description "Hourly architecture read by 小j" -RunLevel Highest | Out-Null
} catch {
  Write-Warning $_.Exception.Message
}
Write-Output "Scheduled task '$TaskName' registered to run hourly."
