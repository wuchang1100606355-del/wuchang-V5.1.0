<#
小J排程守護者：確保所有分身不中斷自動執行
- 定時檢查所有分身腳本是否在執行
- 發現中斷自動重啟，並記錄健康度報告
#>
$ScriptList = @(
    '小J_分身1_高可用自動監控.ps1',
    '小J_分身2_全端口外網監控.ps1',
    '小J_分身3_同業比對競爭力.ps1'
)
$CheckInterval = 60 # 每分鐘檢查一次
while ($true) {
    foreach ($script in $ScriptList) {
        $proc = Get-Process | Where-Object { $_.Path -like "*$script" }
        if (-not $proc) {
            # 未執行自動重啟
            Start-Process pwsh -ArgumentList "-File '$PSScriptRoot\$script'" -WindowStyle Hidden
            Add-Content -Path "$PSScriptRoot\健康度報告流水帳.md" -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $script 自動重啟（排程守護者）"
        }
    }
    Start-Sleep -Seconds $CheckInterval
}
