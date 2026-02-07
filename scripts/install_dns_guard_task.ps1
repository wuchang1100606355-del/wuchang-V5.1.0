Param(
  [string]$DailyTime = "03:00",
  [int]$HealIntervalMinutes = 15,
  [string]$DailyTaskName = "DNSDailyCheck",
  [string]$HealTaskName = "DNSHealMonitor"
)
$root = (Get-Location).Path
$autoLog = Join-Path $root "automation.log"
try { Add-Content -LiteralPath $autoLog -Value ("[" + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + "] install_dns_guard_task start") } catch {}
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
  $self = $MyInvocation.MyCommand.Definition
  $psPathElev = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"
  $args = ('-NoProfile -ExecutionPolicy Bypass -File "' + $self + '" -DailyTime ' + '"' + $DailyTime + '"' + ' -HealIntervalMinutes ' + $HealIntervalMinutes + ' -DailyTaskName ' + '"' + $DailyTaskName + '"' + ' -HealTaskName ' + '"' + $HealTaskName + '"')
  try { Start-Process -FilePath $psPathElev -ArgumentList $args -Verb RunAs | Out-Null } catch {}
  try {
    $csv = Join-Path $root "logs\work_log.csv"
    if (-not (Test-Path $csv)) { Set-Content -LiteralPath $csv -Value "date,time,actor,task,result,details" -Encoding UTF8 }
    Add-Content -LiteralPath $csv -Value ("{0},{1},{2},{3},{4},{5}" -f (Get-Date -Format "yyyy-MM-dd"), (Get-Date -Format "HH:mm:ss"), "xiao-j", "install_dns_guard_task", "ELEVATE", "requested_admin")
  } catch {}
  Write-Output "Elevation requested. Please accept the UAC prompt."
  exit 0
}
$script = Join-Path $root "scripts\dns_guard.ps1"
if (-not (Test-Path $script)) { Write-Error "Script not found: $script"; exit 1 }

try {
  $t1 = Get-ScheduledTask -TaskName $DailyTaskName -ErrorAction SilentlyContinue
  if ($t1) { Unregister-ScheduledTask -TaskName $DailyTaskName -Confirm:$false }
} catch {}
try {
  $t2 = Get-ScheduledTask -TaskName $HealTaskName -ErrorAction SilentlyContinue
  if ($t2) { Unregister-ScheduledTask -TaskName $HealTaskName -Confirm:$false }
} catch {}

$psPath = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"
$actionDaily = New-ScheduledTaskAction -Execute $psPath -Argument ('-NoProfile -ExecutionPolicy Bypass -File "' + $script + '" -Action check')
$actionHeal = New-ScheduledTaskAction -Execute $psPath -Argument ('-NoProfile -ExecutionPolicy Bypass -File "' + $script + '" -Action heal')

# Parse time
try {
  $tParts = $DailyTime -split ":"
  $hour = [int]$tParts[0]
  $minute = [int]$tParts[1]
  $at = (Get-Date).Date.AddHours($hour).AddMinutes($minute)
} catch {
  $at = (Get-Date).Date.AddHours(3)
}

$triggerDaily = New-ScheduledTaskTrigger -Daily -At $at
$triggerHeal = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddMinutes(1)) -RepetitionInterval (New-TimeSpan -Minutes $HealIntervalMinutes) -RepetitionDuration ([TimeSpan]::FromDays(3650))

Register-ScheduledTask -TaskName $DailyTaskName -Action $actionDaily -Trigger $triggerDaily -Description "Daily DNS check by 小j" -RunLevel Highest | Out-Null
Register-ScheduledTask -TaskName $HealTaskName -Action $actionHeal -Trigger $triggerHeal -Description "DNS heal monitor by 小j" -RunLevel Highest | Out-Null

Write-Output ("Scheduled tasks registered: " + $DailyTaskName + ", " + $HealTaskName)
try { Add-Content -LiteralPath $autoLog -Value ("[" + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + "] install_dns_guard_task done") } catch {}
