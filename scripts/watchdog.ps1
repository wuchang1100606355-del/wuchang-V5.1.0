Param(
  [switch]$ScreenWatch,
  [switch]$NoRed,
  [switch]$NoRecording,
  [int]$Minutes = 10,
  [int]$IntervalSec = 5
)
$root = "C:\wuchang V5.0.0"
function Ensure-Dir($p) {
  $dir = Split-Path -Parent $p
  if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
}
if ($ScreenWatch) {
  try {
    Add-Type -AssemblyName System.Drawing | Out-Null
    Add-Type -AssemblyName System.Windows.Forms | Out-Null
  } catch {}
  $bounds = [System.Windows.Forms.SystemInformation]::VirtualScreen
  $stamp = Get-Date -Format "yyyyMMddHHmmss"
  $outDir = Join-Path $root ("downloads\screen_watch\" + $stamp)
  New-Item -ItemType Directory -Path $outDir -Force | Out-Null
  $endAt = (Get-Date).AddMinutes($Minutes)
  $idx = 0
  $found = $false
  $foundFile = ""
  while ((Get-Date) -lt $endAt) {
    $bmp = New-Object System.Drawing.Bitmap ($bounds.Width), ($bounds.Height)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($bounds.Left, $bounds.Top, 0, 0, $bmp.Size)
    $file = Join-Path $outDir ("shot_{0:D4}.png" -f $idx)
    if (-not $NoRed) {
      $step = 6
      $red = 0
      $tot = 0
      $minX = [int]$bmp.Width
      $minY = [int]$bmp.Height
      $maxX = 0
      $maxY = 0
      for ($y = 0; $y -lt $bmp.Height; $y += $step) {
        for ($x = 0; $x -lt $bmp.Width; $x += $step) {
          $c = $bmp.GetPixel($x, $y)
          if ($c.R -gt 200 -and $c.G -lt 60 -and $c.B -lt 60) {
            $red++
            if ($x -lt $minX) { $minX = $x }
            if ($y -lt $minY) { $minY = $y }
            if ($x -gt $maxX) { $maxX = $x }
            if ($y -gt $maxY) { $maxY = $y }
          }
          $tot++
        }
      }
      $ratio = if ($tot -gt 0) { [double]$red / [double]$tot } else { 0.0 }
      if ($ratio -gt 0.08 -and $maxX -gt $minX -and $maxY -gt $minY) {
        $w = [int]([Math]::Min($bmp.Width - $minX, ($maxX - $minX + $step)))
        $h = [int]([Math]::Min($bmp.Height - $minY, ($maxY - $minY + $step)))
        try {
          $rect = New-Object System.Drawing.Rectangle($minX, $minY, $w, $h)
          $crop = $bmp.Clone($rect, $bmp.PixelFormat)
          $cropFile = Join-Path $outDir ("shot_{0:D4}_region.png" -f $idx)
          $crop.Save($cropFile, [System.Drawing.Imaging.ImageFormat]::Png)
          $crop.Dispose()
          $meta = @{ ts = (Get-Date -Format "yyyy-MM-dd HH:mm:ss"); file = $file; crop = $cropFile; x = $minX; y = $minY; width = $w; height = $h; ratio = [math]::Round($ratio, 4) }
          ($meta | ConvertTo-Json) | Set-Content -LiteralPath (Join-Path $outDir "region.json") -Encoding UTF8
        } catch {}
        $bmp.Save($file, [System.Drawing.Imaging.ImageFormat]::Png)
        $g.Dispose()
        $bmp.Dispose()
        $found = $true
        $foundFile = $file
        break
      }
      else {
        $bmp.Save($file, [System.Drawing.Imaging.ImageFormat]::Png)
        $g.Dispose()
        $bmp.Dispose()
      }
    }
    else {
      $bmp.Save($file, [System.Drawing.Imaging.ImageFormat]::Png)
      $g.Dispose()
      $bmp.Dispose()
    }
    $idx++
    Start-Sleep -Seconds $IntervalSec
  }
  $workLogCsv = Join-Path $root "logs\work_log.csv"
  Ensure-Dir $workLogCsv
  if (-not (Test-Path $workLogCsv)) {
    Set-Content -LiteralPath $workLogCsv -Value "date,time,actor,task,result,details" -Encoding UTF8
  }
  $res = if ($found) { "FOUND" } else { "NOT FOUND" }
  $det = if ($found) {
    $region = Join-Path $outDir "region.json"
    if (Test-Path $region) {
      try { $j = Get-Content -LiteralPath $region -Raw | ConvertFrom-Json; $det = ("file=" + $foundFile + "; region=" + $j.x + "," + $j.y + "," + $j.width + "," + $j.height + "; ratio=" + $j.ratio) } catch { $det = ("file=" + $foundFile) }
    }
    else { ("file=" + $foundFile) }
  }
  else { ("shots=" + $idx + "; dir=" + $outDir) }
  Add-Content -LiteralPath $workLogCsv -Value ("{0},{1},{2},{3},{4},{5}" -f (Get-Date -Format "yyyy-MM-dd"), (Get-Date -Format "HH:mm:ss"), "xiao-j", "screen_watch", $res, $det)
  Write-Output ("ScreenWatch: " + $res + " " + $det)
  exit 0
}
else {
  $webName = "wuchangv500-wuchang-web-1"
  $ok = $false
  try {
    $rows = docker ps --format "{{.Names}}`t{{.Status}}"
    $line = ($rows | Where-Object { $_ -like "$webName*" } | Select-Object -First 1)
    if ($line) {
      $parts = $line -split "`t"
      if ($parts.Length -ge 2) {
        $st = $parts[1]
        if ($st -like "Up*") { $ok = $true }
      }
    }
  } catch {}
  if (-not $ok) {
    Push-Location $root
    try { docker compose up -d | Out-Null } catch {}
    Pop-Location
  }
  try {
    $resp = Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 http://localhost:8069/web
    if ($resp.StatusCode -lt 200 -or $resp.StatusCode -ge 400) { $ok = $false }
  } catch { $ok = $false }
  if (-not $ok) {
    Push-Location $root
    try { docker compose up -d | Out-Null } catch {}
    Pop-Location
  }
}
