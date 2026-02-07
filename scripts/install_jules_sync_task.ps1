Param(
  [int]$IntervalMinutes = 30
)
$root = (Get-Location).Path
$script = Join-Path $root "scripts\jules_sync.ps1"
$taskName = "JulesSync"

if (-not (Test-Path $script)) { Write-Error "Script not found: $script"; exit 1 }

try {
  $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
  if ($task) { Unregister-ScheduledTask -TaskName $taskName -Confirm:$false }
} catch {}

$psPath = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"
$action = New-ScheduledTaskAction -Execute $psPath -Argument ('-NoProfile -ExecutionPolicy Bypass -File "' + $script + '"')
$trigger = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddMinutes(1)) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) -RepetitionDuration ([TimeSpan]::FromDays(3650))
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Description "Auto sync Jules task page" -RunLevel Highest | Out-Null
Write-Output "Scheduled task '$taskName' registered to run every $IntervalMinutes minutes."
