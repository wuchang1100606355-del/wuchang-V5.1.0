# 五常 AI - Cloudflare 自動配置腳本

param(
    [Parameter(Mandatory=$true)]
    [string]$ApiToken,
    
    [Parameter(Mandatory=$true)]
    [string]$ZoneId,
    
    [string]$Domain = "wuchang.life",
    [string]$PublicIP = ""
)

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  ☁️  Cloudflare 自動配置" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# 取得公網 IP
if (-not $PublicIP) {
    Write-Host "📡 偵測公網 IP..." -ForegroundColor Yellow
    try {
        $PublicIP = (Invoke-WebRequest -Uri "https://api.ipify.org" -UseBasicParsing).Content
        Write-Host "   ✅ $PublicIP" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ 無法取得公網 IP" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Cloudflare API 標頭
$headers = @{
    "Authorization" = "Bearer $ApiToken"
    "Content-Type" = "application/json"
}

$baseUrl = "https://api.cloudflare.com/client/v4"

# ============================================
# 1. 列出現有 DNS 記錄
# ============================================

Write-Host "1️⃣  檢查現有 DNS 記錄..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/zones/$ZoneId/dns_records" -Headers $headers -Method GET
    $existingRecords = $response.result
    Write-Host "   ✅ 找到 $($existingRecords.Count) 筆記錄" -ForegroundColor Green
} catch {
    Write-Host "   ❌ 無法取得 DNS 記錄: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================
# 2. 建立或更新 A 記錄
# ============================================

Write-Host "2️⃣  設定 A 記錄..." -ForegroundColor Yellow

$aRecord = $existingRecords | Where-Object {$_.type -eq "A" -and $_.name -eq $Domain}

$aRecordData = @{
    type = "A"
    name = "@"
    content = $PublicIP
    ttl = 1
    proxied = $true
} | ConvertTo-Json

if ($aRecord) {
    # 更新
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/zones/$ZoneId/dns_records/$($aRecord.id)" -Headers $headers -Method PUT -Body $aRecordData
        Write-Host "   ✅ 已更新 A 記錄: $Domain → $PublicIP" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ 更新失敗: $_" -ForegroundColor Red
    }
} else {
    # 建立
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/zones/$ZoneId/dns_records" -Headers $headers -Method POST -Body $aRecordData
        Write-Host "   ✅ 已建立 A 記錄: $Domain → $PublicIP" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ 建立失敗: $_" -ForegroundColor Red
    }
}

Write-Host ""

# ============================================
# 3. 建立 CNAME 記錄
# ============================================

Write-Host "3️⃣  設定 CNAME 記錄..." -ForegroundColor Yellow

$subdomains = @("sync", "api", "www")

foreach ($subdomain in $subdomains) {
    $fullName = "$subdomain.$Domain"
    $cnameRecord = $existingRecords | Where-Object {$_.type -eq "CNAME" -and $_.name -eq $fullName}
    
    $cnameData = @{
        type = "CNAME"
        name = $subdomain
        content = $Domain
        ttl = 1
        proxied = $true
    } | ConvertTo-Json
    
    if ($cnameRecord) {
        # 更新
        try {
            $response = Invoke-RestMethod -Uri "$baseUrl/zones/$ZoneId/dns_records/$($cnameRecord.id)" -Headers $headers -Method PUT -Body $cnameData
            Write-Host "   ✅ 已更新: $fullName" -ForegroundColor Green
        } catch {
            Write-Host "   ❌ 更新失敗: $fullName" -ForegroundColor Red
        }
    } else {
        # 建立
        try {
            $response = Invoke-RestMethod -Uri "$baseUrl/zones/$ZoneId/dns_records" -Headers $headers -Method POST -Body $cnameData
            Write-Host "   ✅ 已建立: $fullName" -ForegroundColor Green
        } catch {
            Write-Host "   ❌ 建立失敗: $fullName" -ForegroundColor Red
        }
    }
}

Write-Host ""

# ============================================
# 4. 設定 SSL 模式
# ============================================

Write-Host "4️⃣  設定 SSL 模式..." -ForegroundColor Yellow

$sslData = @{
    value = "strict"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/zones/$ZoneId/settings/ssl" -Headers $headers -Method PATCH -Body $sslData
    Write-Host "   ✅ SSL 模式: 完整(嚴格)" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  無法設定 SSL 模式（可能需要手動設定）" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# 5. 啟用安全功能
# ============================================

Write-Host "5️⃣  啟用安全功能..." -ForegroundColor Yellow

# Always Use HTTPS
$httpsData = @{ value = "on" } | ConvertTo-Json
try {
    Invoke-RestMethod -Uri "$baseUrl/zones/$ZoneId/settings/always_use_https" -Headers $headers -Method PATCH -Body $httpsData | Out-Null
    Write-Host "   ✅ Always Use HTTPS" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  無法啟用 Always Use HTTPS" -ForegroundColor Yellow
}

# Automatic HTTPS Rewrites
$rewriteData = @{ value = "on" } | ConvertTo-Json
try {
    Invoke-RestMethod -Uri "$baseUrl/zones/$ZoneId/settings/automatic_https_rewrites" -Headers $headers -Method PATCH -Body $rewriteData | Out-Null
    Write-Host "   ✅ Automatic HTTPS Rewrites" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  無法啟用 Automatic HTTPS Rewrites" -ForegroundColor Yellow
}

# Minimum TLS Version
$tlsData = @{ value = "1.2" } | ConvertTo-Json
try {
    Invoke-RestMethod -Uri "$baseUrl/zones/$ZoneId/settings/min_tls_version" -Headers $headers -Method PATCH -Body $tlsData | Out-Null
    Write-Host "   ✅ Minimum TLS Version: 1.2" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  無法設定 TLS 版本" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# 6. 建立防火牆規則（範例）
# ============================================

Write-Host "6️⃣  防火牆規則..." -ForegroundColor Yellow
Write-Host "   ⚠️  防火牆規則需透過 Dashboard 手動設定" -ForegroundColor Yellow
Write-Host "   建議規則:" -ForegroundColor Gray
Write-Host "   - 封鎖已知機器人 (cf.threat_score gt 10)" -ForegroundColor Gray
Write-Host "   - 速率限制 API (rate(5m) gt 100)" -ForegroundColor Gray

Write-Host ""

# ============================================
# 完成
# ============================================

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  ✅ Cloudflare 配置完成" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "DNS 記錄:" -ForegroundColor Yellow
Write-Host "  $Domain → $PublicIP" -ForegroundColor Green
Write-Host "  sync.$Domain → $Domain (CNAME)" -ForegroundColor Green
Write-Host "  api.$Domain → $Domain (CNAME)" -ForegroundColor Green
Write-Host "  www.$Domain → $Domain (CNAME)" -ForegroundColor Green
Write-Host ""
Write-Host "SSL: 完整(嚴格)" -ForegroundColor Green
Write-Host ""
Write-Host "請等待 DNS 傳播（通常 1-5 分鐘）" -ForegroundColor Yellow
Write-Host "然後執行測試腳本驗證:" -ForegroundColor Yellow
Write-Host "  .\test_external_access.ps1" -ForegroundColor Gray
Write-Host ""
