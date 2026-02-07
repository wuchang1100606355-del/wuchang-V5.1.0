Param()
$root = (Get-Location).Path
$urlFile = Join-Path $root "config\jules.url.txt"
$cookieFile = Join-Path $root "config\jules.cookie.txt"
$syncScript = Join-Path $root "scripts\jules_sync.ps1"
$installTask = Join-Path $root "scripts\install_jules_sync_task.ps1"
$startupCompose = Join-Path $root "scripts\startup_compose.ps1"

if (-not (Test-Path $urlFile)) { Set-Content -Path $urlFile -Value "https://jules.google.com/task/8263971059525947125" -Encoding ASCII }
$url = (Get-Content -Path $urlFile -Raw).Trim()

powershell -NoProfile -ExecutionPolicy Bypass -File $startupCompose | Out-Null

Start-Process "http://localhost:8069/web/login"
Start-Process $url

$cookie = $env:JULES_COOKIE
if (-not $cookie -and (Test-Path $cookieFile)) { $cookie = (Get-Content -Path $cookieFile -Raw).Trim() }
if (-not $cookie) { $cookie = Read-Host "請在完成 Google 登入後，貼上該頁的 Cookie 值" }
if ($cookie) { Set-Content -Path $cookieFile -Value $cookie -Encoding ASCII }

$outPath = powershell -NoProfile -ExecutionPolicy Bypass -File $syncScript
$outFile = $outPath | Select-Object -Last 1

$authorized = $false
if (Test-Path $outFile) {
  $html = Get-Content -Path $outFile -Raw
  if ($html -and ($html -notmatch "accounts\.google\.com/v3/signin")) { $authorized = $true }
}

if ($authorized) {
  Write-Output "Jules 授權成功並已同步。輸出檔案：$outFile"
} else {
  Write-Output "Jules 尚未授權或 Cookie 無效。已保存至 $cookieFile，請確認 Cookie 後重試。當前輸出：$outFile"
}

powershell -NoProfile -ExecutionPolicy Bypass -File $installTask -IntervalMinutes 30 | Out-Null
Write-Output "已安裝排程，每 30 分鐘自動同步。"
