param(
  [int]$Framerate = 25,
  [string]$OutDir = "C:/wuchang V5.1.0/logs"
)

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
  Write-Host "未找到 ffmpeg，請先安裝並加入 PATH。" -ForegroundColor Yellow
  Write-Host "下載：https://www.gyan.dev/ffmpeg/builds/ 或使用 winget：winget install Gyan.FFmpeg"
  exit 1
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$outfile = Join-Path $OutDir "screen-$ts.mp4"

Write-Host "開始錄影（整個桌面），輸出：$outfile" -ForegroundColor Cyan
Write-Host "停止方式：在此視窗按 Ctrl+C 或關閉 ffmpeg 視窗" -ForegroundColor DarkGray

# 使用 gdigrab 擷取 Windows 桌面
ffmpeg -y -f gdigrab -framerate $Framerate -i desktop -c:v libx264 -preset veryfast -crf 23 -pix_fmt yuv420p "$outfile"
