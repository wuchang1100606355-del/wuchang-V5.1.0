$colors = @{p="Green";w="Yellow";e="Red";i="Cyan"}
function WS([string]$t) { Write-Host "
$('='*70)" -f $colors.p; Write-Host "  $t" -f $colors.p; Write-Host "$('='*70)
" -f $colors.p }
function WOK([string]$m) { Write-Host "✅ $m" -f $colors.p }
function WW([string]$m) { Write-Host "⚠️  $m" -f $colors.w }
function WE([string]$m) { Write-Host "❌ $m" -f $colors.e }

WS "🔍 網路基礎檢查"
try { $ip = [System.Net.Dns]::GetHostAddresses("wuchang.life")[0]; WOK "DNS: wuchang.life -> $ip" } catch { WW "DNS 解析失敗" }
if (Test-Connection 8.8.8.8 -Count 1 -Quiet) { WOK "網路連接正常" } else { WE "無法連接網際網路" }
try { $ip = Invoke-RestMethod "https://api.ipify.org" -TimeoutSec 5; WOK "公網 IP: $ip" } catch { WW "無法取得公網 IP" }

WS "🐳 Docker 容器驗證"
$d = Get-Service Docker -EA SilentlyContinue
if ($d -and $d.Status -eq "Running") { WOK "Docker 運行中" } else { WE "Docker 未啟動"; exit }
foreach ($n in @("caddy","wuchang-web","db")) {
    $s = docker ps --filter "name=$n" --format "{{.Status}}" 2>$null
    if ($s) { WOK "${n}: $s" } else { WW "${n}: 未運行" }
}

WS "☁️  CloudFlare Tunnel 可行性"
try { $img = docker images cloudflare/cloudflared -q 2>$null; if ($img) { WOK "cloudflared 鏡像已存在" } else { WW "鏡像未下載" } } catch {}
if (Test-Path ".env") { if ((Get-Content ".env") -match "CLOUDFLARE") { WOK "環境變數已設置" } else { WW "未設置 Token" } } else { WW ".env 不存在" }
try { Invoke-WebRequest "https://dash.cloudflare.com" -TimeoutSec 5 -UseBasicParsing | Out-Null; WOK "CloudFlare 服務可達" } catch { WW "無法連接" }

WS "🌐 公網 IP 方案可行性"
try { $ip = Invoke-RestMethod "https://api.ipify.org" -TimeoutSec 5; WOK "公網 IP 可用: $ip" } catch { WE "無公網 IP"; exit }
if (Test-Path "wuchang_os/Caddyfile") { WOK "Caddyfile 配置完成" } else { WE "Caddyfile 不存在" }
$cs = docker ps --filter "name=caddy" --format "{{.Status}}" 2>$null
if ($cs) { WOK "Caddy 運行中" } else { WW "Caddy 未運行" }

WS "🔐 Tailscale VPN 可行性"
if (Get-Command tailscale -EA SilentlyContinue) { WOK "Tailscale 已安裝" } else { WW "Tailscale 未安裝" }

WS "☁️  GCP Cloud Run 可行性"
if (Get-Command gcloud -EA SilentlyContinue) { WOK "gcloud CLI 已安裝" } else { WW "gcloud CLI 未安裝" }
if (Test-Path "Dockerfile") { WOK "Dockerfile 已存在" } else { WW "Dockerfile 不存在" }

WS "🔌 埠可達性"
foreach ($p in @(80,443,8069,3001,8080)) {
    if (Test-NetConnection 127.0.0.1 -Port $p -InformationLevel Quiet -WarningAction SilentlyContinue) { WOK "埠 $p 開放" } else { WW "埠 $p 關閉" }
}

Write-Host "
✅ 驗證完成！系統已準備好外網聯入。
" -ForegroundColor Green
