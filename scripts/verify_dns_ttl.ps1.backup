# 驗證 DNS TTL 設定
# 檢查當前 DNS 記錄的 TTL 值是否符合預期（5400 秒）

param(
    [Parameter(Mandatory=$false)]
    [string]$Domain = "wuchang.life",
    
    [Parameter(Mandatory=$false)]
    [int]$ExpectedTTL = 5400
)

Write-Host "=== DNS TTL 設定驗證 ===" -ForegroundColor Cyan
Write-Host "`n檢查網域: $Domain" -ForegroundColor Yellow
Write-Host "預期 TTL: $ExpectedTTL 秒（$([math]::Round($ExpectedTTL/60, 1)) 分鐘）" -ForegroundColor Yellow
Write-Host ""

# 檢查 DNS 記錄
try {
    Write-Host "[1] 查詢 DNS A 記錄..." -ForegroundColor Cyan
    $dnsResult = Resolve-DnsName -Name $Domain -Type A -ErrorAction Stop
    
    if ($dnsResult) {
        Write-Host "  ✓ DNS 記錄查詢成功" -ForegroundColor Green
        Write-Host "  IP 地址: $($dnsResult[0].IPAddress)" -ForegroundColor White
        
        # 注意：PowerShell 的 Resolve-DnsName 不直接返回 TTL
        # 需要使用 nslookup 或其他工具
        Write-Host "`n[2] 使用 nslookup 查詢 TTL..." -ForegroundColor Cyan
        $nslookupResult = nslookup -type=A $Domain 2>&1
        
        if ($nslookupResult -match "TTL") {
            Write-Host "  ✓ 找到 TTL 資訊" -ForegroundColor Green
            $nslookupResult | Select-String "TTL" | ForEach-Object {
                Write-Host "    $_" -ForegroundColor White
            }
        } else {
            Write-Host "  ⚠ 無法從 nslookup 獲取 TTL（可能需要使用 dig 或其他工具）" -ForegroundColor Yellow
        }
        
        Write-Host "`n[3] 建議使用 Google Cloud DNS 查詢實際 TTL..." -ForegroundColor Cyan
        Write-Host "  命令: gcloud dns record-sets list --zone=wuchang-life --project=coffee-spark-ai-barista-b10b5 --name=$Domain. --type=A" -ForegroundColor Gray
        Write-Host "  或使用線上工具查詢 DNS TTL" -ForegroundColor Gray
        
    } else {
        Write-Host "  ❌ DNS 記錄查詢失敗" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ DNS 查詢錯誤: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== 驗證完成 ===" -ForegroundColor Green
Write-Host "`n注意：" -ForegroundColor Yellow
Write-Host "  - PowerShell 的 Resolve-DnsName 不直接返回 TTL 值" -ForegroundColor Gray
Write-Host "  - 建議使用 Google Cloud DNS 命令或線上 DNS 查詢工具" -ForegroundColor Gray
Write-Host "  - 當前設定應為 TTL = 5400 秒（90 分鐘）" -ForegroundColor Gray
