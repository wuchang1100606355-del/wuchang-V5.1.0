$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$userDataDir = "C:\wuchang_browser_profile"
$url = "http://192.168.50.1"

# Create profile directory if it does not exist
if (-not (Test-Path $userDataDir)) {
    New-Item -ItemType Directory -Path $userDataDir | Out-Null
}

Write-Host "Launching Shared Chrome Browser..."
Start-Process -FilePath $chromePath -ArgumentList "--remote-debugging-port=9222", "--user-data-dir=$userDataDir", "--no-first-run", "--no-default-browser-check", "$url", "--enable-features=V3DualWANControl"


