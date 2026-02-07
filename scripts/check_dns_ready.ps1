# DNS 就緒檢查工具

param(
    [Parameter(Mandatory=$false)]
    [string]$Domain = "ai.wuchang.life",
    
    [Parameter(Mandatory=$false)]
    [string]$ExpectedIP = "",
    
    [Parameter(Mandatory=$false)]
    [string]$VMName = "vm-system-tw",
    
    [Parameter(Mandatory=$false)]
    [string]$Zone = "asia-east1-b"
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " DNS 就緒檢查工具" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 如果沒有提供 IP，從 GCP 獲取
if (-not $ExpectedIP) {
    Write-Host "正在從 GCP 獲取 VM IP..." -ForegroundColor Yellow
    try {
        $ExpectedIP = gcloud compute instances describe $VMName --zone=$Zone --format="get(networkInterfaces[0].accessConfigs[0].natIP)" 2>$null
        if ($ExpectedIP) {
            Write-Host "  VM IP: $ExpectedIP" -ForegroundColor Green
        } else {
            Write-Host "  ✗ 無法獲取 VM IP" -ForegroundColor Red
            Write-Host "  請手動指定: -ExpectedIP '35.201.XXX.XXX'" -ForegroundColor Yellow
            exit 1
        }
    } catch {
        Write-Host "  ✗ 無法連接到 GCP" -ForegroundColor Red
        Write-Host "  錯誤: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "檢查配置：" -ForegroundColor Yellow
Write-Host "  域名: $Domain" -ForegroundColor White
Write-Host "  期望 IP: $ExpectedIP" -ForegroundColor White
Write-Host ""

# 定義要檢查的所有域名
$baseDomain = "wuchang.life"
$subdomains = @("ai", "api", "odoo")
$allDomains = $subdomains | ForEach-Object { "$_.$baseDomain" }

$allPassed = $true

Write-Host "開始檢查 DNS 記錄..." -ForegroundColor Cyan
Write-Host ""

foreach ($checkDomain in $allDomains) {
    Write-Host "  檢查 $checkDomain ..." -ForegroundColor Gray
    
    try {
        $result = Resolve-DnsName -Name $checkDomain -Type A -ErrorAction Stop
        $resolvedIP = $result | Where-Object {$_.Type -eq "A"} | Select-Object -First 1 -ExpandProperty IPAddress
        
        if ($resolvedIP -eq $ExpectedIP) {
            Write-Host "    ✓ 正確: $checkDomain -> $resolvedIP" -ForegroundColor Green
        } else {
            Write-Host "    ✗ 錯誤: $checkDomain -> $resolvedIP (期望: $ExpectedIP)" -ForegroundColor Red
            $allPassed = $false
        }
    } catch {
        Write-Host "    ✗ 無法解析: $checkDomain" -ForegroundColor Red
        Write-Host "       錯誤: $($_.Exception.Message)" -ForegroundColor DarkRed
        $allPassed = $false
    }
    
    Start-Sleep -Milliseconds 200
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan

if ($allPassed) {
    Write-Host " ✅ DNS 配置正確！" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "所有域名均正確解析到 $ExpectedIP" -ForegroundColor Green
    Write-Host ""
    Write-Host "下一步：執行部署腳本" -ForegroundColor Yellow
    Write-Host ".\scripts\deploy_domain_windows.ps1" -ForegroundColor White
    Write-Host ""
    exit 0
} else {
    Write-Host " ⚠️ DNS 配置有誤！" -ForegroundColor Red
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "請檢查 DNS 配置：" -ForegroundColor Yellow
    Write-Host "  1. 確認已添加所有 A 記錄" -ForegroundColor White
    Write-Host "  2. 確認記錄指向正確的 IP: $ExpectedIP" -ForegroundColor White
    Write-Host "  3. 等待 DNS 傳播（可能需要 5-30 分鐘）" -ForegroundColor White
    Write-Host "  4. 清除本地 DNS 緩存: ipconfig /flushdns" -ForegroundColor White
    Write-Host ""
    Write-Host "詳細配置指南：" -ForegroundColor Yellow
    Write-Host "  .\docs\DNS_CONFIGURATION_GUIDE.md" -ForegroundColor White
    Write-Host ""
    exit 1
}
