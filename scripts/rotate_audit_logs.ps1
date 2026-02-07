param(
  [string]$ServerUrl = "http://localhost:8080",
  [string]$OutRoot = "C:/wuchang V5.1.0/logs/audit/daily",
  [int]$RetentionDays = 365
)

$today = Get-Date -Format "yyyy-MM-dd"
$outDir = Join-Path $OutRoot $today
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

function Save-Json($obj, $path) { ($obj | ConvertTo-Json -Depth 10) | Out-File -FilePath $path -Encoding UTF8 }
function Save-Url($url, $path) { try { Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $path -TimeoutSec 30 } catch { } }

# 匯出事件 CSV/JSONL 與伺服器快照
$eventsCsv = Join-Path $outDir ("events-" + $today + ".csv")
$eventsJsonl = Join-Path $outDir ("events-" + $today + ".jsonl")
Save-Url ("$ServerUrl/events/export.csv") $eventsCsv
if (Test-Path "C:/wuchang V5.1.0/events.log.jsonl") { Copy-Item "C:/wuchang V5.1.0/events.log.jsonl" $eventsJsonl -Force }

try { $devices = Invoke-RestMethod -Method Get -Uri "$ServerUrl/devices"; Save-Json $devices (Join-Path $outDir ("devices-" + $today + ".json")) } catch {}
try { $skills = Invoke-RestMethod -Method Get -Uri "$ServerUrl/skills"; Save-Json $skills (Join-Path $outDir ("skills-" + $today + ".json")) } catch {}

# 生成每日摘要 SUMMARY.md（事件類型統計）
$summary = @()
if (Test-Path $eventsCsv) {
  try {
    $rows = Import-Csv $eventsCsv
    $groups = $rows | Group-Object -Property type | Sort-Object Count -Descending
    $summary += "# 每日摘要 ($today)"
    $summary += "\n事件類型統計："
    foreach ($g in $groups) { $summary += "- $($g.Name): $($g.Count)" }
  } catch {}
}
if (-not $summary) { $summary = "# 每日摘要 ($today)\n(無事件或匯出失敗)" }
$summary -join "`n" | Out-File -FilePath (Join-Path $outDir 'SUMMARY.md') -Encoding UTF8

# 保留策略：刪除超過 RetentionDays 的資料夾
try {
  Get-ChildItem $OutRoot -Directory | Where-Object { $_.Name -match "^\d{4}-\d{2}-\d{2}$" } | ForEach-Object {
    $d = Get-Date $_.Name
    if ((Get-Date) - $d -gt ([TimeSpan]::FromDays($RetentionDays))) { Remove-Item $_.FullName -Recurse -Force }
  }
} catch {}

Write-Host "[Daily] 已產出：$outDir" -ForegroundColor Green
