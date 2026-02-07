# UI 心跳服務 (PowerShell)
# 用途：UI 設備定時發送心跳到 VM 伺服器

param(
    [string]$VMIP = "192.168.50.84",
    [string]$DeviceIP = $null,
    [string]$DeviceName = $null,
    [int]$Interval = 30
)

# 獲取本機 IP
if (-not $DeviceIP) {
    $DeviceIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike "127.*"} | Select-Object -First 1).IPAddress
    if (-not $DeviceIP) {
        $DeviceIP = "127.0.0.1"
    }
}

# 獲取主機名稱
if (-not $DeviceName) {
    $DeviceName = $env:COMPUTERNAME
}

$HeartbeatURL = "http://${VMIP}:8069/wuchang/ui/heartbeat"

Write-Host "`n=== UI 心跳服務啟動 ===" -ForegroundColor Cyan
Write-Host "VM 伺服器: $VMIP" -ForegroundColor White
Write-Host "UI 設備 IP: $DeviceIP" -ForegroundColor White
Write-Host "UI 設備名稱: $DeviceName" -ForegroundColor White
Write-Host "心跳間隔: $Interval 秒" -ForegroundColor White
Write-Host ""

$consecutiveFailures = 0
$maxFailures = 5

while ($true) {
    try {
        $body = @{
            device_ip = $DeviceIP
            device_name = $DeviceName
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri $HeartbeatURL -Method POST -Body $body -ContentType "application/json" -TimeoutSec 5 -ErrorAction Stop
        
        $isProxying = $response.is_proxying
        $statusMsg = if ($isProxying) { "代理中" } else { "正常" }
        
        Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ✓ 心跳已發送 - 狀態: $statusMsg" -ForegroundColor Green
        
        if ($isProxying) {
            Write-Host "  ⚠ 伺服器正在代理 UI 工作，請檢查 UI 設備連線狀態" -ForegroundColor Yellow
        }
        
        $consecutiveFailures = 0
    } catch {
        $consecutiveFailures++
        Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ✗ 心跳發送失敗: $($_.Exception.Message)" -ForegroundColor Red
        
        if ($consecutiveFailures -ge $maxFailures) {
            Write-Host ""
            Write-Host "⚠ 連續 $consecutiveFailures 次心跳失敗" -ForegroundColor Yellow
            Write-Host "  請檢查 VM 伺服器狀態和網路連線" -ForegroundColor Yellow
            Write-Host ""
            $consecutiveFailures = 0
        }
    }
    
    Start-Sleep -Seconds $Interval
}
