Param(
  [string]$Root = (Get-Location).Path
)
$ErrorActionPreference = "Stop"
$ts = Get-Date -Format "yyyyMMddHHmmss"
$out = Join-Path $Root ("logs\network_snapshot_" + $ts + ".txt")

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("[Adapters]") | Out-Null
try {
  $adapters = Get-NetAdapter | Select-Object Name, InterfaceDescription, Status, LinkSpeed, MacAddress
  $lines.Add(($adapters | Format-Table -AutoSize | Out-String)) | Out-Null
} catch {
  $lines.Add("Get-NetAdapter failed: " + $_.Exception.Message) | Out-Null
}

$lines.Add("") | Out-Null
$lines.Add("[IPAddresses]") | Out-Null
try {
  $ips = Get-NetIPAddress | Select-Object InterfaceAlias, IPAddress, PrefixLength, AddressFamily, Type
  $lines.Add(($ips | Format-Table -AutoSize | Out-String)) | Out-Null
} catch {
  $lines.Add("Get-NetIPAddress failed: " + $_.Exception.Message) | Out-Null
}

$lines.Add("") | Out-Null
$lines.Add("[ipconfig /all]") | Out-Null
try {
  $ipc = ipconfig /all | Out-String
  $lines.Add($ipc) | Out-Null
} catch {
  $lines.Add("ipconfig failed: " + $_.Exception.Message) | Out-Null
}

$lines.Add("") | Out-Null
$lines.Add("[route print]") | Out-Null
try {
  $rt = route print | Out-String
  $lines.Add($rt) | Out-Null
} catch {
  $lines.Add("route print failed: " + $_.Exception.Message) | Out-Null
}

 $gwIp = $null
 try {
   $def = Get-NetRoute -DestinationPrefix "0.0.0.0/0" | Sort-Object -Property RouteMetric | Select-Object -First 1
   if ($def) { $gwIp = $def.NextHop }
 } catch {}
 $lines.Add("") | Out-Null
 $lines.Add("[Gateway]") | Out-Null
 $lines.Add(("Gateway=" + ($gwIp ? $gwIp : ""))) | Out-Null
 $gwMac = ""
 if ($gwIp) {
   try {
     $arpRaw = arp -a | Out-String
     $lines.Add($arpRaw) | Out-Null
     $m = [Regex]::Match($arpRaw, [Regex]::Escape($gwIp) + "\s+([0-9a-f\-:]{17})", [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
     if ($m.Success) { $gwMac = $m.Groups[1].Value }
   } catch {}
 }
 $brand = ""
 $model = ""
 $server = ""
 $title = ""
 if ($gwIp) {
   try {
     $resp = Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 ("http://" + $gwIp)
     if ($resp.Headers.ContainsKey("Server")) { $server = "" + $resp.Headers["Server"] }
     $html = "" + $resp.Content
     $t = [Regex]::Match($html, "<title>(.*?)</title>", [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
     if ($t.Success) { $title = $t.Groups[1].Value }
     if ($html -match "ASUS" -or $server -match "asus" -or $title -match "ASUS") { $brand = "ASUS" }
     if ($brand -eq "ASUS") {
       $mm = [Regex]::Match($html, "(RT-[A-Z]+\-?\d+|GT-AX\d+|RT-AX\d+|TUF-AX\d+|ZenWiFi\s*[A-Z0-9\-]+)", [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
       if ($mm.Success) { $model = $mm.Groups[1].Value }
     }
   } catch {}
 }
 try {
   $disc = @{ ts = (Get-Date -Format "yyyy-MM-dd HH:mm:ss"); gateway = ($gwIp ? $gwIp : ""); mac = $gwMac; brand = $brand; model = $model; http_server = $server; title = $title }
   $jsonPath = Join-Path $Root "logs/router_discovery.json"
   $dir = Split-Path -Parent $jsonPath
   if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
   ($disc | ConvertTo-Json -Depth 6) | Set-Content -LiteralPath $jsonPath -Encoding UTF8
   $lines.Add("") | Out-Null
   $lines.Add("[RouterDiscovery]") | Out-Null
   $lines.Add(("Brand=" + $brand + "; Model=" + $model + "; Server=" + $server + "; Title=" + $title)) | Out-Null
 } catch {}

Set-Content -LiteralPath $out -Value ($lines -join "`r`n") -Encoding UTF8
Write-Output $out
