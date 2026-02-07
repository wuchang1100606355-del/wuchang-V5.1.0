# enable_nonprofit_credits_for_admin.ps1
# 為 admin@wuchang.life 開啟非營利抵免申請流程

$ADMIN_EMAIL = "admin@wuchang.life"
$PROJECT_ID = "my-j-483304"
$ORG_NAME = "五常非營利組織"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Google Cloud 非營利抵免開通" -ForegroundColor Cyan
Write-Host "帳號: $ADMIN_EMAIL" -ForegroundColor Yellow
Write-Host "專案 ID: $PROJECT_ID" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "步驟 1: 檢查必要資訊..." -ForegroundColor Green
Write-Host "  組織: $ORG_NAME" -ForegroundColor White
Write-Host "  管理員帳號: $ADMIN_EMAIL" -ForegroundColor White
Write-Host "  Google Cloud 專案: $PROJECT_ID" -ForegroundColor White
Write-Host ""

Write-Host "步驟 2: 開啟申請頁面..." -ForegroundColor Green
Write-Host ""

# Google for Nonprofits
$nonprofitsUrl = "https://www.google.com/nonprofits"
Write-Host "  [1] Google for Nonprofits 驗證" -ForegroundColor Yellow
Write-Host "      網址: $nonprofitsUrl" -ForegroundColor Cyan
Start-Process $nonprofitsUrl

Start-Sleep -Seconds 2

# Google Cloud 非營利抵免申請
$creditsUrl = "https://cloud.google.com/apply-for-nonprofit-credits"
Write-Host "  [2] Google Cloud 非營利抵免申請" -ForegroundColor Yellow
Write-Host "      網址: $creditsUrl" -ForegroundColor Cyan
Start-Process $creditsUrl

Start-Sleep -Seconds 2

# Google Cloud Console 帳單設定
$billingUrl = "https://console.cloud.google.com/billing?project=$PROJECT_ID"
Write-Host "  [3] Google Cloud Console 帳單設定" -ForegroundColor Yellow
Write-Host "      網址: $billingUrl" -ForegroundColor Cyan
Start-Process $billingUrl

Start-Sleep -Seconds 2

# Google Admin Console
$adminUrl = "https://admin.google.com"
Write-Host "  [4] Google Workspace 管理控制台" -ForegroundColor Yellow
Write-Host "      網址: $adminUrl" -ForegroundColor Cyan
Write-Host "      帳號: $ADMIN_EMAIL" -ForegroundColor White
Start-Process $adminUrl

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "申請流程說明" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 確認 Google for Nonprofits 驗證狀態" -ForegroundColor White
Write-Host "   • 使用 $ADMIN_EMAIL 登入" -ForegroundColor Gray
Write-Host "   • 確認組織已通過驗證" -ForegroundColor Gray
Write-Host "   • 準備驗證文件（如需要）" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 申請 Google Cloud 非營利抵免額" -ForegroundColor White
Write-Host "   • 填寫申請表單" -ForegroundColor Gray
Write-Host "   • 組織名稱: $ORG_NAME" -ForegroundColor Gray
Write-Host "   • 專案 ID: $PROJECT_ID" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 連結帳單帳戶" -ForegroundColor White
Write-Host "   • 在 Google Cloud Console 設定帳單" -ForegroundColor Gray
Write-Host "   • 申請抵免額" -ForegroundColor Gray
Write-Host ""
Write-Host "4. 等待審核（7-14 個工作天）" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "已開啟所有必要的頁面" -ForegroundColor Green
Write-Host "請使用 $ADMIN_EMAIL 登入並完成申請流程" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
