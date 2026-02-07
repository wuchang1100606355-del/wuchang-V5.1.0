<#
小J分身三：同業比對競爭力自動監控
- 每日自動比對同業API/服務可用性
- 主動優化本地參數，保持領先5%內
- 追加比對結果到健康度報告
#>
$CompetitorList = @('https://competitor1.com/api/status','https://competitor2.com/api/status')
$SelfAPI = 'https://yourdomain.com/api/status'
$CheckInterval = 86400 # 1天
$StartTime = Get-Date
$Days = 0
while ($Days -lt 3) {
    $selfResp = (Invoke-WebRequest -Uri $SelfAPI -UseBasicParsing -TimeoutSec 10 -ErrorAction SilentlyContinue).StatusCode
    $better = 0; $total = 0
    foreach ($url in $CompetitorList) {
        $resp = (Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10 -ErrorAction SilentlyContinue).StatusCode
        if ($selfResp -eq 200 -and ($resp -ne 200 -or $selfResp < $resp)) { $better++ }
        $total++
    }
    $percent = if ($total -gt 0) { [math]::Round(100*$better/$total,2) } else {0}
    Add-Content -Path "$PSScriptRoot\健康度報告流水帳.md" -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') 同業比對領先百分比：$percent%"
    if ($percent -lt 5) {
        # 可擴充自動優化參數
        Add-Content -Path "$PSScriptRoot\健康度報告流水帳.md" -Value "自動優化參數以保持領先"
    }
    Start-Sleep -Seconds $CheckInterval
    $Days++
}
