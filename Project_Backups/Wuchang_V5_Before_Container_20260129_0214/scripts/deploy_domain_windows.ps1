# 五常 AI 系統 - Windows 網域部署腳本
# 用於從 Windows 部署到 GCP VM

param(
    [Parameter(Mandatory=$false)]
    [string]$Domain = "ai.wuchang.life",
    
    [Parameter(Mandatory=$false)]
    [string]$Email = "admin@wuchang.life",
    
    [Parameter(Mandatory=$false)]
    [string]$VMName = "vm-system-tw",
    
    [Parameter(Mandatory=$false)]
    [string]$Zone = "asia-east1-b",
    
    [Parameter(Mandatory=$false)]
    [string]$ProjectID = "coffee-spark-ai-barista-b10b5",
    
    [switch]$SkipDNSCheck
)

$ErrorActionPreference = "Stop"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " 五常 AI 系統網域部署工具" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "配置信息：" -ForegroundColor Yellow
Write-Host "  域名: $Domain" -ForegroundColor White
Write-Host "  VM: $VMName" -ForegroundColor White
Write-Host "  區域: $Zone" -ForegroundColor White
Write-Host "  項目: $ProjectID" -ForegroundColor White
Write-Host ""

# 1. 設置 GCP 項目
Write-Host "[1/6] 設置 GCP 項目..." -ForegroundColor Green
gcloud config set project $ProjectID

# 2. 獲取 VM 外部 IP
Write-Host "[2/6] 獲取 VM IP 地址..." -ForegroundColor Green
$vmIP = gcloud compute instances describe $VMName --zone=$Zone --format="get(networkInterfaces[0].accessConfigs[0].natIP)"
Write-Host "  VM IP: $vmIP" -ForegroundColor Cyan

# 3. DNS 檢查
if (-not $SkipDNSCheck) {
    Write-Host "[3/6] 檢查 DNS 配置..." -ForegroundColor Green
    Write-Host "  正在解析 $Domain..." -ForegroundColor Gray
    
    try {
        $dnsResult = Resolve-DnsName -Name $Domain -ErrorAction Stop
        $resolvedIP = $dnsResult | Where-Object {$_.Type -eq "A"} | Select-Object -First 1 -ExpandProperty IPAddress
        
        if ($resolvedIP -eq $vmIP) {
            Write-Host "  ✓ DNS 配置正確！$Domain -> $vmIP" -ForegroundColor Green
        } else {
            Write-Host "  ✗ DNS 配置錯誤！" -ForegroundColor Red
            Write-Host "    當前解析: $Domain -> $resolvedIP" -ForegroundColor Yellow
            Write-Host "    應該解析: $Domain -> $vmIP" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "請在您的 DNS 提供商處添加 A 記錄：" -ForegroundColor Yellow
            Write-Host "  類型: A" -ForegroundColor White
            Write-Host "  主機: $($Domain.Split('.')[0])" -ForegroundColor White
            Write-Host "  值: $vmIP" -ForegroundColor White
            Write-Host "  TTL: 300" -ForegroundColor White
            Write-Host ""
            $continue = Read-Host "是否繼續部署？(y/N)"
            if ($continue -ne "y" -and $continue -ne "Y") {
                Write-Host "部署已取消。" -ForegroundColor Yellow
                exit 0
            }
        }
    } catch {
        Write-Host "  ✗ 無法解析 $Domain" -ForegroundColor Red
        Write-Host "  錯誤: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "請先配置 DNS 記錄：" -ForegroundColor Yellow
        Write-Host "  類型: A" -ForegroundColor White
        Write-Host "  主機: $($Domain.Split('.')[0])" -ForegroundColor White
        Write-Host "  值: $vmIP" -ForegroundColor White
        Write-Host ""
        $continue = Read-Host "是否繼續部署？(y/N)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            Write-Host "部署已取消。" -ForegroundColor Yellow
            exit 0
        }
    }
} else {
    Write-Host "[3/6] 跳過 DNS 檢查..." -ForegroundColor Yellow
}

# 4. 上傳部署腳本
Write-Host "[4/6] 上傳部署腳本到 VM..." -ForegroundColor Green
$deployScript = "$PSScriptRoot\deploy_domain_full.sh"

if (-not (Test-Path $deployScript)) {
    Write-Host "  ✗ 找不到部署腳本: $deployScript" -ForegroundColor Red
    exit 1
}

gcloud compute scp $deployScript ${VMName}:~/deploy_domain.sh --zone=$Zone
Write-Host "  ✓ 腳本已上傳" -ForegroundColor Green

# 5. 設置環境變數並執行部署
Write-Host "[5/6] 在 VM 上執行部署..." -ForegroundColor Green
Write-Host "  這可能需要幾分鐘時間..." -ForegroundColor Gray

$envVars = @"
export DOMAIN_NAME='wuchang.life'
export SUBDOMAIN='$($Domain.Split('.')[0])'
export ADMIN_EMAIL='$Email'
export VM_NAME='$VMName'
export GCP_ZONE='$Zone'
"@

$remoteCommands = @"
$envVars
chmod +x ~/deploy_domain.sh
sudo ~/deploy_domain.sh
"@

Write-Host "執行命令：" -ForegroundColor Gray
Write-Host $remoteCommands -ForegroundColor DarkGray
Write-Host ""

try {
    gcloud compute ssh $VMName --zone=$Zone --command="$remoteCommands"
    Write-Host "  ✓ 部署腳本執行完成" -ForegroundColor Green
} catch {
    Write-Host "  ✗ 部署失敗" -ForegroundColor Red
    Write-Host "  錯誤: $_" -ForegroundColor Red
    exit 1
}

# 6. 驗證部署
Write-Host "[6/6] 驗證部署..." -ForegroundColor Green
Start-Sleep -Seconds 5

Write-Host "  檢查 Nginx 狀態..." -ForegroundColor Gray
$nginxStatus = gcloud compute ssh $VMName --zone=$Zone --command="sudo systemctl is-active nginx" 2>$null
if ($nginxStatus -eq "active") {
    Write-Host "  ✓ Nginx 運行中" -ForegroundColor Green
} else {
    Write-Host "  ✗ Nginx 未運行" -ForegroundColor Red
}

Write-Host "  檢查 Streamlit 服務..." -ForegroundColor Gray
$streamlitStatus = gcloud compute ssh $VMName --zone=$Zone --command="sudo systemctl is-active wuchang-streamlit" 2>$null
if ($streamlitStatus -eq "active") {
    Write-Host "  ✓ Streamlit 運行中" -ForegroundColor Green
} else {
    Write-Host "  ✗ Streamlit 未運行" -ForegroundColor Red
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " 部署完成！" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "訪問地址：" -ForegroundColor Yellow
Write-Host "  主要服務: https://$Domain" -ForegroundColor White
Write-Host "  API 服務: https://api.wuchang.life" -ForegroundColor White
Write-Host "  Odoo 服務: https://odoo.wuchang.life" -ForegroundColor White
Write-Host ""
Write-Host "管理命令：" -ForegroundColor Yellow
Write-Host "  SSH 連接: gcloud compute ssh $VMName --zone=$Zone" -ForegroundColor White
Write-Host "  查看日誌: gcloud compute ssh $VMName --zone=$Zone --command='sudo journalctl -u wuchang-streamlit -f'" -ForegroundColor White
Write-Host "  重啟服務: gcloud compute ssh $VMName --zone=$Zone --command='sudo systemctl restart wuchang-streamlit'" -ForegroundColor White
Write-Host ""
Write-Host "SSL 證書：" -ForegroundColor Yellow
Write-Host "  證書會在 60 天後自動續期" -ForegroundColor White
Write-Host "  手動續期: gcloud compute ssh $VMName --zone=$Zone --command='sudo certbot renew'" -ForegroundColor White
Write-Host ""

# 打開瀏覽器
$openBrowser = Read-Host "是否在瀏覽器中打開？(Y/n)"
if ($openBrowser -ne "n" -and $openBrowser -ne "N") {
    Start-Process "https://$Domain"
}

Write-Host "部署成功完成！🎉" -ForegroundColor Green
