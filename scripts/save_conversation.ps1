param(
  [string]$Text,
  [string]$FromFile,
  [string]$OutDir = "C:/wuchang V5.1.0/logs/audit/conversations"
)

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$ts = Get-Date -Format "yyyy-MM-dd-HHmmss"
$outPath = Join-Path $OutDir ("conversation-" + $ts + ".txt")

if ($FromFile -and (Test-Path $FromFile)) {
  Copy-Item $FromFile $outPath -Force
} elseif ($Text) {
  $Text | Out-File -FilePath $outPath -Encoding UTF8
} else {
  Write-Host "請以 -Text 或 -FromFile 提供內容" -ForegroundColor Yellow
  exit 1
}

Write-Host "[Conversation] 已保存：$outPath" -ForegroundColor Green
