# 檢查 Google Cloud 付費項目腳本
# 用途：協助檢查和優化 Google Cloud 付費項目

param(
    [string]$ProjectId = "wuchang-community-os"
)

Write-Host "`n=== Google Cloud 付費項目檢查 ===" -ForegroundColor Cyan
Write-Host "專案: $ProjectId" -ForegroundColor White
Write-Host ""

Write-Host "⚠️  注意：此腳本提供指引，實際操作需要在 Google Cloud Console 中進行" -ForegroundColor Yellow
Write-Host ""

Write-Host "=== 步驟 1: 檢查帳單和使用量 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 訪問帳單頁面:" -ForegroundColor White
Write-Host "   https://console.cloud.google.com/billing" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 選擇帳單帳戶，查看「費用」標籤" -ForegroundColor White
Write-Host ""
Write-Host "3. 查看「依專案分組」的費用明細" -ForegroundColor White
Write-Host ""

Write-Host "=== 步驟 2: 檢查啟用的 API ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "訪問 API 庫:" -ForegroundColor White
Write-Host "   https://console.cloud.google.com/apis/dashboard?project=$ProjectId" -ForegroundColor Gray
Write-Host ""
Write-Host "檢查以下項目：" -ForegroundColor Yellow
Write-Host "  ✅ Maps Embed API（免費，保留）" -ForegroundColor Green
Write-Host "  ✅ Geocoding API（免費額度內，保留）" -ForegroundColor Green
Write-Host "  ⚠️  Vertex AI / Gemini API（檢查使用量和費用）" -ForegroundColor Yellow
Write-Host "  ⚠️  Cloud Storage（檢查使用量）" -ForegroundColor Yellow
Write-Host "  ⚠️  Compute Engine（檢查使用量）" -ForegroundColor Yellow
Write-Host "  ⚠️  Cloud SQL（檢查使用量）" -ForegroundColor Yellow
Write-Host ""

Write-Host "=== 步驟 3: 檢查資源使用情況 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "訪問資源管理:" -ForegroundColor White
Write-Host "   https://console.cloud.google.com/cloud-resource-manager?project=$ProjectId" -ForegroundColor Gray
Write-Host ""
Write-Host "檢查項目：" -ForegroundColor Yellow
Write-Host "  • VM 執行個體（Compute Engine）" -ForegroundColor White
Write-Host "  • 儲存空間（Cloud Storage）" -ForegroundColor White
Write-Host "  • 資料庫（Cloud SQL）" -ForegroundColor White
Write-Host "  • 其他資源" -ForegroundColor White
Write-Host ""

Write-Host "=== 優化建議 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 免費服務（保留）：" -ForegroundColor Green
Write-Host "   • Maps Embed API（無限制免費）" -ForegroundColor White
Write-Host "   • Geocoding API（`$200/月免費額度）" -ForegroundColor White
Write-Host ""
Write-Host "2. 可優化的服務：" -ForegroundColor Yellow
Write-Host "   • Vertex AI / Gemini API" -ForegroundColor White
Write-Host "     - 如果使用量低，考慮使用免費額度" -ForegroundColor Gray
Write-Host "     - 優化 API 呼叫頻率" -ForegroundColor Gray
Write-Host "   • Cloud Storage" -ForegroundColor White
Write-Host "     - 刪除不需要的檔案" -ForegroundColor Gray
Write-Host "     - 使用較便宜的儲存類別" -ForegroundColor Gray
Write-Host "   • Compute Engine" -ForegroundColor White
Write-Host "     - 如果不需要，可以停止或刪除 VM" -ForegroundColor Gray
Write-Host "     - 使用較小的機器類型" -ForegroundColor Gray
Write-Host "   • Cloud SQL" -ForegroundColor White
Write-Host "     - 如果不需要，可以刪除資料庫" -ForegroundColor Gray
Write-Host "     - 使用較小的資料庫實例" -ForegroundColor Gray
Write-Host ""

Write-Host "=== AI 服務優化建議 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "提升 AI 小J 服務品質或降低成本：" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 使用 Google 非營利組織免費額度：" -ForegroundColor White
Write-Host "   • Vertex AI 有免費額度（需確認）" -ForegroundColor Gray
Write-Host "   • Gemini API 有免費額度" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 優化 API 使用：" -ForegroundColor White
Write-Host "   • 使用快取減少 API 呼叫" -ForegroundColor Gray
Write-Host "   • 批次處理請求" -ForegroundColor Gray
Write-Host "   • 使用較便宜的模型（如 gemini-1.5-flash）" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 本地 AI 方案：" -ForegroundColor White
Write-Host "   • 考慮使用 Ollama（本地運行）" -ForegroundColor Gray
Write-Host "   • 減少對雲端 API 的依賴" -ForegroundColor Gray
Write-Host ""

Write-Host "=== 關閉不必要服務的步驟 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 停止 VM 執行個體（如果不需要）：" -ForegroundColor White
Write-Host "   https://console.cloud.google.com/compute/instances?project=$ProjectId" -ForegroundColor Gray
Write-Host "   • 選擇 VM → 停止 → 確認" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 刪除 Cloud Storage 儲存區（如果不需要）：" -ForegroundColor White
Write-Host "   https://console.cloud.google.com/storage/browser?project=$ProjectId" -ForegroundColor Gray
Write-Host "   • 選擇儲存區 → 刪除 → 確認" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 刪除 Cloud SQL 實例（如果不需要）：" -ForegroundColor White
Write-Host "   https://console.cloud.google.com/sql/instances?project=$ProjectId" -ForegroundColor Gray
Write-Host "   • 選擇實例 → 刪除 → 確認" -ForegroundColor Gray
Write-Host ""
Write-Host "4. 停用不需要的 API：" -ForegroundColor White
Write-Host "   https://console.cloud.google.com/apis/dashboard?project=$ProjectId" -ForegroundColor Gray
Write-Host "   • 選擇 API → 停用 → 確認" -ForegroundColor Gray
Write-Host ""

Write-Host "⚠️  警告：刪除資源前請確認：" -ForegroundColor Red
Write-Host "  • 資料已備份" -ForegroundColor Yellow
Write-Host "  • 確認不再需要該資源" -ForegroundColor Yellow
Write-Host "  • 刪除後無法恢復" -ForegroundColor Yellow
Write-Host ""

Write-Host "詳細指南：" -ForegroundColor Cyan
Write-Host "  docs\GOOGLE_CLOUD_COST_OPTIMIZATION.md" -ForegroundColor White
