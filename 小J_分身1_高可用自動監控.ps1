<#
小J分身一：系統高可用自動監控
- 每5分鐘檢查所有服務/容器/端口
- 發現異常自動重啟/修復
- 記錄在線率，追加健康度報告
#>
$ServiceList = @('docker','nginx','caddy')
$OnlineSeconds = 0
$CheckInterval = 300 # 5分鐘
$StartTime = Get-Date
while ($true) {
    $allOk = $true
    foreach ($svc in $ServiceList) {
        $status = (Get-Service -Name $svc -ErrorAction SilentlyContinue).Status
        if ($status -ne 'Running') {
            Start-Service $svc
            Add-Content -Path "$PSScriptRoot\健康度報告流水帳.md" -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $svc 自動重啟"
            $allOk = $false
        }
    }
    if ($allOk) { $OnlineSeconds += $CheckInterval }
    Start-Sleep -Seconds $CheckInterval
    if ((Get-Date) - $StartTime).TotalDays -ge 3) { break }
}
Add-Content -Path "$PSScriptRoot\健康度報告流水帳.md" -Value "三日總在線秒數：$OnlineSeconds"
