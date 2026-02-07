#!/usr/bin/env pwsh
param(
    [string[]]$Name,
    [int]$NeighborCount = 10
)

$colors = @{ ok = "Green"; warn = "Yellow"; err = "Red"; info = "Cyan"; header = "Magenta" }
function H($t) { Write-Host "\n$('═'*70)" -f $colors.header; Write-Host "  $t" -f $colors.header; Write-Host $('═'*70) -f $colors.header }
function OK($m) { Write-Host "  [OK]   $m" -f $colors.ok }
function WW($m) { Write-Host "  [WARN] $m" -f $colors.warn }
function EE($m) { Write-Host "  [ERR]  $m" -f $colors.err }

H "網路纜線 / 實體連接阜偵測"

try {
    $adapters = Get-NetAdapter -Physical -ErrorAction Stop
} catch {
    EE "無法讀取網路介面，請以系統管理員身分執行。"; exit 1
}

if ($Name) { $adapters = $adapters | Where-Object { $Name -contains $_.Name } }
if (-not $adapters) { EE "找不到符合的實體網路介面。"; exit 1 }

foreach ($a in $adapters) {
    Write-Host "\n[$($a.Name)]" -f $colors.info
    $state = $a.MediaConnectionState
    $statusColor = if ($state -eq "Connected") { $colors.ok } elseif ($state -eq "Disconnected") { $colors.warn } else { $colors.info }
    Write-Host "  連接狀態: $state | 狀態: $($a.Status) | 速率: $($a.LinkSpeed)" -f $statusColor
    Write-Host "  MAC: $($a.MacAddress) | 驅動: $($a.InterfaceDescription)" -f $colors.info

    $ips = Get-NetIPAddress -InterfaceIndex $a.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
    if ($ips) {
        foreach ($ip in $ips) { OK "IPv4: $($ip.IPAddress)/$($ip.PrefixLength)" }
    } else {
        WW "未取得 IPv4 位址 (可能僅本地連線或 DHCP 未就緒)"
    }

    $neighbors = Get-NetNeighbor -InterfaceIndex $a.ifIndex -State Reachable,Stale,Delay -ErrorAction SilentlyContinue |
        Where-Object { $_.IPAddress -match '^\d+\.\d+\.\d+\.\d+$' -and $_.IPAddress -notlike '169.254.*' }

    if ($neighbors) {
        Write-Host "  探測到的對端設備 (最多 $NeighborCount 筆):" -f $colors.info
        $neighbors |
            Sort-Object -Property State,IPAddress |
            Select-Object -First $NeighborCount |
            ForEach-Object { OK "$($_.IPAddress) / MAC $($_.LinkLayerAddress) / $($_.State)" }
    } else {
        WW "此介面尚未觀察到鄰居設備 (可嘗試傳輸或等待 ARP 更新)"
    }
}

Write-Host "\n提示: 若介面顯示 Disconnected，請檢查實體網路線是否插穩，或切換其他埠再重試。" -f $colors.info
