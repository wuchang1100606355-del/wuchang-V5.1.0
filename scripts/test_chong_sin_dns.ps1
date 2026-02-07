# 重新總店 DNS 解析測試腳本
# 用途：測試私人 DNS 主機名稱是否正確解析

param(
    [string]$Domain = "chong-sin.local"
)

Write-Host "=== 重新總店 DNS 解析測試 ===" -ForegroundColor Cyan
Write-Host "測試時間: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
Write-Host ""

$testHosts = @(
    @{Name="POS 伺服器（完整）"; Host="pos-server.$Domain"; ExpectedIP="192.168.50.84"},
    @{Name="Odoo 服務（完整）"; Host="odoo.$Domain"; ExpectedIP="192.168.50.84"},
    @{Name="API 服務（完整）"; Host="api.$Domain"; ExpectedIP="192.168.50.84"},
    @{Name="POS 伺服器（簡化）"; Host="pos-server"; ExpectedIP="192.168.50.84"},
    @{Name="Odoo 服務（簡化）"; Host="odoo-server"; ExpectedIP="192.168.50.84"},
    @{Name="路由器（完整）"; Host="router.$Domain"; ExpectedIP="192.168.50.1"},
    @{Name="路由器（簡化）"; Host="router"; ExpectedIP="192.168.50.1"}
)

$results = @()
foreach ($test in $testHosts) {
    Write-Host "測試: $($test.Name) ($($test.Host))" -ForegroundColor Yellow
    try {
        $addresses = [System.Net.Dns]::GetHostAddresses($test.Host)
        $resolvedIP = $addresses[0].IPAddressToString
        Write-Host "  ✓ 解析成功: $resolvedIP" -ForegroundColor Green
        
        if ($resolvedIP -eq $test.ExpectedIP) {
            Write-Host "    ✓ IP 地址正確" -ForegroundColor Green
            $results += @{Host=$test.Host; Status="成功"; IP=$resolvedIP; Correct=$true}
        } else {
            Write-Host "    ⚠ IP 地址不符合預期（預期: $($test.ExpectedIP)）" -ForegroundColor Yellow
            $results += @{Host=$test.Host; Status="警告"; IP=$resolvedIP; Correct=$false}
        }
        
        # 測試連線（僅對伺服器 IP）
        if ($test.ExpectedIP -eq "192.168.50.84") {
            try {
                $connection = Test-NetConnection -ComputerName $resolvedIP -Port 8069 -WarningAction SilentlyContinue -InformationLevel Quiet -ErrorAction Stop
                if ($connection) {
                    Write-Host "    ✓ 服務連線正常 (Port 8069)" -ForegroundColor Green
                } else {
                    Write-Host "    ⚠ 服務連線失敗 (Port 8069) - 服務可能未啟動" -ForegroundColor Yellow
                }
            } catch {
                Write-Host "    ⚠ 無法測試服務連線" -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host "  ❌ 解析失敗: $($_.Exception.Message)" -ForegroundColor Red
        $results += @{Host=$test.Host; Status="失敗"; IP="N/A"; Correct=$false}
    }
    Write-Host ""
}

# 顯示測試摘要
Write-Host "=== 測試摘要 ===" -ForegroundColor Cyan
$successCount = ($results | Where-Object { $_.Correct -eq $true }).Count
$totalCount = $results.Count

Write-Host "總測試數: $totalCount" -ForegroundColor White
Write-Host "成功: $successCount" -ForegroundColor Green
Write-Host "失敗: $($totalCount - $successCount)" -ForegroundColor $(if (($totalCount - $successCount) -gt 0) { "Red" } else { "Green" })

if ($successCount -eq $totalCount) {
    Write-Host "`n✓ 所有 DNS 解析測試通過！" -ForegroundColor Green
} else {
    Write-Host "`n⚠ 部分測試失敗，請檢查設定" -ForegroundColor Yellow
    Write-Host "`n建議：" -ForegroundColor Yellow
    Write-Host "  1. 確認 Hosts 檔案設定正確" -ForegroundColor White
    Write-Host "  2. 執行: .\scripts\setup_chong_sin_private_dns.ps1" -ForegroundColor White
    Write-Host "  3. 檢查路由器 DNS 設定（如果支援）" -ForegroundColor White
}

Write-Host "`n=== 測試完成 ===" -ForegroundColor Green
