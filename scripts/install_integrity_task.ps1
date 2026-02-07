Param(
  [string]$Time = "02:00",
  [string]$TaskName = "IntegrityDailyCheck"
)
$root = (Get-Location).Path
$script = Join-Path $root "scripts\verify_integrity.ps1"

if (-not (Test-Path $script)) { Write-Error "Script not found: $script"; exit 1 }

try {
  $existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
  if ($existing) { Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false }
} catch {}

$psPath = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"
$action = New-ScheduledTaskAction -Execute $psPath -Argument ('-NoProfile -ExecutionPolicy Bypass -File "' + $script + '"')

# Parse time
try {
  $tParts = $Time -split "[:]"
  $hour = [int]$tParts[0]
  $minute = [int]$tParts[1]
  $at = (Get-Date).Date.AddHours($hour).AddMinutes($minute)
} catch {
  $at = (Get-Date).Date.AddHours(2)
}

$trigger = New-ScheduledTaskTrigger -Daily -At $at
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Description "Daily integrity check by 小j" -RunLevel Highest | Out-Null
Write-Output "Scheduled task '$TaskName' registered to run daily at $Time."
