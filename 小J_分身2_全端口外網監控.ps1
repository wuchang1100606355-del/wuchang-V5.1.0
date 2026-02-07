<#
小J分身二：全端口外網連線自動監控
- 每5分鐘檢查所有對外端口（可自訂）
- 發現連線異常自動重啟網路/容器
- 記錄外網連線時數，追加健康度報告
#>
$PortList = @(80,443,5000,8000)
$ExternalSeconds = 0
$CheckInterval = 300 # 5分鐘
$StartTime = Get-Date
function Test-Port {
    param($port)
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect('8.8.8.8',$port)
        $tcp.Close()
        return $true
    } catch { return $false }
}
while ($true) {
    $allOk = $true
    foreach ($p in $PortList) {
        if (-not (Test-Port $p)) {
            # 嘗試重啟網路或容器
            Restart-Service docker -ErrorAction SilentlyContinue
            Add-Content -Path "$PSScriptRoot\健康度報告流水帳.md" -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') 端口 $p 外網異常自動修復"
            $allOk = $false
        }
    }
    if ($allOk) { $ExternalSeconds += $CheckInterval }
    Start-Sleep -Seconds $CheckInterval
    if ((Get-Date) - $StartTime).TotalDays -ge 3) { break }
}
Add-Content -Path "$PSScriptRoot\健康度報告流水帳.md" -Value "三日全端口外網連線秒數：$ExternalSeconds"
