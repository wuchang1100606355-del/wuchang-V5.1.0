Param(
  [string]$Url = "https://jules.google.com/task/8263971059525947125",
  [hashtable]$Headers
)
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$rootDir = (Split-Path -Parent $PSScriptRoot)
$urlPath = Join-Path $rootDir "config\jules.url.txt"
if (-not $PSBoundParameters.ContainsKey('Url') -and (Test-Path $urlPath)) {
  $cfgUrl = (Get-Content -Path $urlPath -Raw).Trim()
  if ($cfgUrl) { $Url = $cfgUrl }
}
$targetDir = Join-Path -Path $rootDir -ChildPath ("downloads\jules\" + $timestamp)
New-Item -ItemType Directory -Path $targetDir -Force | Out-Null

$cookiePath = Join-Path $rootDir "config\jules.cookie.txt"
$userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36"

if (-not $Headers) {
  $envCookie = $env:JULES_COOKIE
  if ($envCookie) {
    $Headers = @{ Cookie = $envCookie; "User-Agent" = $userAgent }
  } elseif (Test-Path $cookiePath) {
    $cookie = Get-Content -Path $cookiePath -Raw
    if ($cookie) { $Headers = @{ Cookie = $cookie; "User-Agent" = $userAgent } } else { $Headers = @{ "User-Agent" = $userAgent } }
  } else {
    $Headers = @{ "User-Agent" = $userAgent }
  }
}

function Write-Log($msg) {
  $line = "[" + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + "] " + $msg
  Add-Content -Path (Join-Path $rootDir "automation.log") -Value $line
}

try {
  $outFile = Join-Path $targetDir "download.html"
  if ($Headers) {
    curl.exe -L $Url -H ("User-Agent: " + $userAgent) $(if ($Headers["Cookie"]) { @("-H", "Cookie: " + $Headers["Cookie"]) } ) -o $outFile | Out-Null
  } else {
    curl.exe -L $Url -o $outFile | Out-Null
  }
  if (-not (Test-Path $outFile)) { throw "Download failed" }

  $bytes = [System.IO.File]::ReadAllBytes($outFile)
  $sha256 = [System.BitConverter]::ToString(([System.Security.Cryptography.SHA256]::Create()).ComputeHash($bytes)).Replace("-","").ToLower()
  $latestHashPath = Join-Path $rootDir "downloads\jules\latest.hash"
  $latestHtmlPath = Join-Path $rootDir "downloads\jules\latest.html"
  Set-Content -Path (Join-Path $targetDir "hash.txt") -Value $sha256 -Encoding ASCII

  $changed = $true
  if (Test-Path $latestHashPath) {
    $prev = Get-Content -Path $latestHashPath -Raw
    if ($prev -eq $sha256) { $changed = $false }
  }

  if ($changed) {
    Set-Content -Path $latestHashPath -Value $sha256 -Encoding ASCII
    Copy-Item -Path $outFile -Destination $latestHtmlPath -Force
    Write-Log ("Jules sync OK. Changed. Saved: " + $outFile)
  } else {
    Write-Log ("Jules sync OK. No change. Saved: " + $outFile)
  }

  Write-Output $outFile
} catch {
  $errFile = Join-Path $targetDir "error.txt"
  Set-Content -Path $errFile -Value $_.Exception.Message -Encoding UTF8
  Write-Log ("Jules sync FAILED: " + $_.Exception.Message)
  Write-Output $errFile
  exit 1
}
