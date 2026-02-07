Param(
  [string]$Root = (Get-Location).Path,
  [string]$TaskName = "WuchangReadingReminder",
  [string]$Time1 = "09:00",
  [string]$Time2 = "21:00"
)
$ErrorActionPreference = "Stop"
$act = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$($Root)\scripts\context_archive_and_index.ps1`""
function MakeTrigger($t) {
  try {
    $dt = [datetime]::ParseExact($t, "HH:mm", $null)
    return New-ScheduledTaskTrigger -Daily -At $dt.TimeOfDay
  } catch {
    return New-ScheduledTaskTrigger -Daily -At  (Get-Date).Date.AddHours(9).TimeOfDay
  }
}
$tr1 = MakeTrigger $Time1
$tr2 = MakeTrigger $Time2
try {
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
} catch {}
$task = New-ScheduledTask -Action $act -Trigger @($tr1,$tr2)
Register-ScheduledTask -TaskName $TaskName -InputObject $task | Out-Null
Write-Output ("reading_reminder_installed: " + $TaskName)
