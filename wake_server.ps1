#!/usr/bin/env pwsh
<parameter name="content">#!/usr/bin/env pwsh
<#
.SYNOPSIS
    網路喚醒工具 - Wake-on-LAN
.DESCRIPTION
    發送 Magic Packet 喚醒目標伺服器
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$MAC = "00:00:00:00:00:00",
    [string]$ServerIP = "192.168.50.84",
    [string]$BroadcastIP = "192.168.50.255",
    [int]$Port = 9,
    [int]$Retries = 3,
    [int]$RetryDelay = 2
)

$colors = @{ ok = "Green"; warn = "Yellow"; err = "Red"; info = "Cyan"; header = "Magenta" }
function H($t) { Write-Host "`n$('═'*70)" -f $colors.header; Write-Host "  $t" -f $colors.header; Write-Host $('═'*70) -f $colors.header }
function OK($m) { Write-Host "  [OK]   $m" -f $colors.ok }
function WW($m) { Write-Host "  [WARN] $m" -f $colors.warn }
function EE($m) { Write-Host "  [ERR]  $m" -f $colors.err }
function II($m) { Write-Host "  [INFO] $m" -f $colors.info }

H "網路喚醒工具 - Wake-on-LAN"

# 如果沒提供 MAC，嘗試自動偵測
if ($MAC -eq "00:00:00:00:00:00") {
    II "未指定 MAC 地址，嘗試自動偵測..."
    
    try {
        # 先 ping 一下確保 ARP cache 有資料
        $null = Test-Connection -ComputerName $ServerIP -Count 1 -ErrorAction SilentlyContinue
        
        # 從 ARP cache 取得 MAC
        $arpResult = arp -a $ServerIP 2>$null | Select-String $ServerIP
        if ($arpResult) {
            $macMatch = $arpResult -match '([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'
            if ($macMatch) {
                $MAC = $matches[0].Replace('-', ':')
                OK "偵測到 MAC 地址: $MAC"
            }
        }
    } catch {
        WW "無法自動偵測 MAC 地址"
    }
    
    if ($MAC -eq "00:00:00:00:00:00") {
        EE "請提供伺服器的 MAC 地址"
        II "使用方式: pwsh -File .\wake_server.ps1 -MAC 'AA:BB:CC:DD:EE:FF'"
        II "或從 ARP: arp -a | findstr $ServerIP"
        II "或從伺服器: ip link show"
        exit 1
    }
}

# 驗證 MAC 格式
$MAC = $MAC.Replace('-', ':').ToUpper()
if ($MAC -notmatch '^([0-9A-F]{2}:){5}[0-9A-F]{2}$') {
    EE "MAC 地址格式錯誤: $MAC"
    II "正確格式: AA:BB:CC:DD:EE:FF 或 AA-BB-CC-DD-EE-FF"
    exit 1
}

II "目標伺服器: $ServerIP"
II "MAC 地址: $MAC"
II "廣播地址: $BroadcastIP"
II "UDP 埠: $Port"

# 建立 Magic Packet
function Send-WOLPacket {
    param(
        [string]$MacAddress,
        [string]$BroadcastAddress,
        [int]$UdpPort
    )
    
    try {
        # 移除分隔符並轉為 byte array
        $macBytes = $MacAddress.Replace(':', '').Replace('-', '')
        $macByteArray = [byte[]]@()
        for ($i = 0; $i -lt $macBytes.Length; $i += 2) {
            $macByteArray += [Convert]::ToByte($macBytes.Substring($i, 2), 16)
        }
        
        # 建立 Magic Packet (6 bytes of FF + 16 repetitions of MAC)
        $packet = [byte[]](,0xFF * 6)
        for ($i = 0; $i -lt 16; $i++) {
            $packet += $macByteArray
        }
        
        # 發送 UDP packet
        $udpClient = New-Object System.Net.Sockets.UdpClient
        $udpClient.Connect([System.Net.IPAddress]::Parse($BroadcastAddress), $UdpPort)
        $bytesSent = $udpClient.Send($packet, $packet.Length)
        $udpClient.Close()
        
        return $bytesSent -eq $packet.Length
    } catch {
        Write-Host "  發送失敗: $_" -f $colors.err
        return $false
    }
}

# 發送 Magic Packet
H "發送喚醒訊號"

$attempt = 0
$success = $false

while ($attempt -lt $Retries -and -not $success) {
    $attempt++
    Write-Host "  嘗試 $attempt/$Retries ..." -f $colors.info
    
    if (Send-WOLPacket -MacAddress $MAC -BroadcastAddress $BroadcastIP -UdpPort $Port) {
        OK "Magic Packet 已發送 (102 bytes)"
        $success = $true
    } else {
        EE "發送失敗"
        if ($attempt -lt $Retries) {
            II "等待 $RetryDelay 秒後重試..."
            Start-Sleep -Seconds $RetryDelay
        }
    }
}

if (-not $success) {
    EE "所有嘗試均失敗"
    exit 1
}

# 等待伺服器啟動
H "等待伺服器回應"
II "預計需要 30-60 秒啟動時間..."

$maxWait = 120
$waited = 0
$interval = 5
$online = $false

while ($waited -lt $maxWait) {
    Write-Host "  檢查中... ($waited/$maxWait 秒)" -NoNewline -f $colors.info
    
    $ping = Test-Connection -ComputerName $ServerIP -Count 1 -Quiet -ErrorAction SilentlyContinue
    if ($ping) {
        Write-Host " ✓" -f $colors.ok
        $online = $true
        break
    } else {
        Write-Host " ✗" -f $colors.warn
    }
    
    Start-Sleep -Seconds $interval
    $waited += $interval
}

Write-Host ""

if ($online) {
    OK "伺服器已上線！"
    II "SSH 測試: ssh wuchang@$ServerIP"
} else {
    WW "伺服器未在預期時間內回應"
    II "可能原因:"
    Write-Host "  1. BIOS/UEFI 未啟用 Wake-on-LAN" -f $colors.info
    Write-Host "  2. 網卡設定未開啟 WOL (需在作業系統設定)" -f $colors.info
    Write-Host "  3. 伺服器完全關機（非睡眠/休眠）" -f $colors.info
    Write-Host "  4. 防火牆封鎖 UDP port $Port" -f $colors.info
    Write-Host "  5. 實體線路問題" -f $colors.info
}

H "伺服器端 WOL 設定檢查"
Write-Host "  在伺服器執行以下指令確認 WOL 已啟用:" -f $colors.info
Write-Host ""
Write-Host "  # 檢查網卡 WOL 設定" -f $colors.header
Write-Host "  sudo ethtool eth0 | grep Wake-on" -f $colors.header
Write-Host "  # 應顯示: Wake-on: g (表示啟用 magic packet)" -f $colors.info
Write-Host ""
Write-Host "  # 如果顯示 Wake-on: d，需啟用:" -f $colors.header
Write-Host "  sudo ethtool -s eth0 wol g" -f $colors.header
Write-Host ""
Write-Host "  # 永久啟用 (systemd):" -f $colors.header
Write-Host "  sudo nano /etc/systemd/system/wol.service" -f $colors.header
Write-Host ""
Write-Host "  [Unit]" -f $colors.info
Write-Host "  Description=Enable Wake-on-LAN" -f $colors.info
Write-Host "  After=network.target" -f $colors.info
Write-Host ""
Write-Host "  [Service]" -f $colors.info
Write-Host "  Type=oneshot" -f $colors.info
Write-Host "  ExecStart=/usr/sbin/ethtool -s eth0 wol g" -f $colors.info
Write-Host ""
Write-Host "  [Install]" -f $colors.info
Write-Host "  WantedBy=multi-user.target" -f $colors.info
Write-Host ""
Write-Host "  sudo systemctl enable wol.service" -f $colors.header
Write-Host "  sudo systemctl start wol.service" -f $colors.header
Write-Host ""
