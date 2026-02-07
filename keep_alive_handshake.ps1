function WOK { Write-Host "[01:06:48] ✅ $args" -f Green }
function WW { Write-Host "[01:06:48] ⚠️  $args" -f Yellow }
function WS { Write-Host "[01:06:48] 💓 $args" -f Cyan }

function Test-Conn {
    param([string]$srv, [int]$port, [string]$name)
    try {
        $t = New-Object System.Net.Sockets.TcpClient
        $t.Connect($srv, $port)
        WOK "$name 握手成功"
        $t.Close()
    } catch { WW "$name 失敗" }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -f Cyan
Write-Host "  Wuchang 伺服器持續握手信號 - 保活機制" -f Cyan
Write-Host "  Ctrl+C 停止 | 每 30 秒握手一次" -f Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -f Cyan
Write-Host ""

$n = 0
while ($true) {
    $n++
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -f Cyan
    WS "握手週期 #$n 開始"
    Test-Conn localhost 8069 "Odoo"
    Test-Conn localhost 8080 "AI"
    Test-Conn localhost 3001 "Kuma"
    Test-Conn localhost 443 "CloudFlare"
    WS "握手完成，等待 30 秒... (Ctrl+C 停止)"
    Start-Sleep -Seconds 30
}
