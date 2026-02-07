# Google Cloud 專案設定腳本
# 用途：協助設定 Google Cloud 專案和啟用抵免額度

param(
    [string]$ProjectName = "wuchang-community-os",
    [string]$ProjectDisplayName = "五常社區系統",
    [switch]$CheckBilling = $false,
    [switch]$EnableAPIs = $false
)

Write-Host "`n=== Google Cloud 專案設定 ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "專案資訊：" -ForegroundColor Yellow
Write-Host "  專案名稱: $ProjectName" -ForegroundColor White
Write-Host "  顯示名稱: $ProjectDisplayName" -ForegroundColor White
Write-Host ""

Write-Host "⚠️  注意：此腳本提供指引，實際操作需要在 Google Cloud Console 中進行" -ForegroundColor Yellow
Write-Host ""

Write-Host "=== 步驟 1: 建立或切換專案 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 訪問 Google Cloud Console:" -ForegroundColor White
Write-Host "   https://console.cloud.google.com/" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 建立新專案:" -ForegroundColor White
Write-Host "   a. 點擊頂部專案選擇器" -ForegroundColor Gray
Write-Host "   b. 點擊「新增專案」" -ForegroundColor Gray
Write-Host "   c. 專案名稱: $ProjectName" -ForegroundColor Gray
Write-Host "   d. 顯示名稱: $ProjectDisplayName" -ForegroundColor Gray
Write-Host "   e. 組織: 選擇「新北市三重區五常社區發展協會」" -ForegroundColor Gray
Write-Host "   f. 點擊「建立」" -ForegroundColor Gray
Write-Host ""

if ($CheckBilling) {
    Write-Host "=== 步驟 2: 檢查帳單和抵免額度 ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. 訪問帳單頁面:" -ForegroundColor White
    Write-Host "   https://console.cloud.google.com/billing" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. 確認帳單帳戶:" -ForegroundColor White
    Write-Host "   • 確認有帳單帳戶（即使有免費額度也需要設定）" -ForegroundColor Gray
    Write-Host "   • 如果沒有，需要建立帳單帳戶" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. 確認 $300 免費抵免額度:" -ForegroundColor White
    Write-Host "   • 在「帳單」→「預算與配額」中查看" -ForegroundColor Gray
    Write-Host "   • 確認 $300 抵免額度已啟用" -ForegroundColor Gray
    Write-Host ""
}

if ($EnableAPIs) {
    Write-Host "=== 步驟 3: 啟用必要的 API ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "訪問 API 庫:" -ForegroundColor White
    Write-Host "   https://console.cloud.google.com/apis/library" -ForegroundColor Gray
    Write-Host ""
    Write-Host "啟用以下 API:" -ForegroundColor White
    Write-Host "   ✅ Maps Embed API" -ForegroundColor Green
    Write-Host "   ✅ Geocoding API" -ForegroundColor Green
    Write-Host "   ✅ Maps JavaScript API（可選）" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "=== 關於 SBIR 專案 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "SBIR = Small Business Innovation Research（小型企業創新研究）" -ForegroundColor White
Write-Host "這是美國政府的計劃，通常用於政府合約相關的創新研究。" -ForegroundColor Gray
Write-Host ""
Write-Host "建議：" -ForegroundColor Yellow
Write-Host "  • 如果這是誤選的專案，建議建立新專案（如上）" -ForegroundColor White
Write-Host "  • 如果這個專案有其他用途，可以保留，但建議建立新專案用於五常社區系統" -ForegroundColor White
Write-Host "  • 避免混淆，建議使用明確的專案名稱" -ForegroundColor White
Write-Host ""

Write-Host "=== 資源運用規劃建議 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "優先級 1（必須）:" -ForegroundColor Yellow
Write-Host "  • Maps Embed API: 免費（無限制）" -ForegroundColor Green
Write-Host "  • Geocoding API: 免費（`$200/月）" -ForegroundColor Green
Write-Host "  • Cloud Storage: 約 `$5-10/月" -ForegroundColor White
Write-Host "  • Compute Engine: 約 `$20-50/月" -ForegroundColor White
Write-Host ""
Write-Host "預算規劃:" -ForegroundColor Yellow
Write-Host "  • 第一階段（前 3 個月）: 使用 `$300 免費額度" -ForegroundColor White
Write-Host "  • 預估使用: `$50-100/月" -ForegroundColor White
Write-Host "  • 設定預算警報: `$50, `$100, `$200" -ForegroundColor White
Write-Host ""

Write-Host "=== 下一步 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 建立新專案: $ProjectName" -ForegroundColor White
Write-Host "2. 確認帳單和抵免額度" -ForegroundColor White
Write-Host "3. 啟用必要的 API" -ForegroundColor White
Write-Host "4. 建立 API Key 並設定到 Odoo" -ForegroundColor White
Write-Host ""
Write-Host "詳細指南：" -ForegroundColor Cyan
Write-Host "  docs\GOOGLE_CLOUD_PROJECT_SETUP.md" -ForegroundColor White
