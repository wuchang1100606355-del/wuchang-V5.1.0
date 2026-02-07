# 新增 Google Cloud 專案管理員腳本
# 用途：協助新增 wuchang11006355@gmail.com 為專案管理員

param(
    [string]$ProjectId = "wuchang-community-os",
    [string]$AdminEmail = "wuchang11006355@gmail.com",
    [string]$Role = "roles/editor"
)

Write-Host "`n=== 新增 Google Cloud 專案管理員 ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "專案資訊：" -ForegroundColor Yellow
Write-Host "  專案 ID: $ProjectId" -ForegroundColor White
Write-Host "  管理員電子郵件: $AdminEmail" -ForegroundColor White
Write-Host "  角色: $Role" -ForegroundColor White
Write-Host ""

Write-Host "⚠️  注意：此操作需要在 Google Cloud Console 中進行" -ForegroundColor Yellow
Write-Host ""

Write-Host "=== 步驟 1: 訪問 IAM 與管理 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 訪問 IAM 頁面:" -ForegroundColor White
Write-Host "   https://console.cloud.google.com/iam-admin/iam?project=$ProjectId" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 確認已選擇正確專案: $ProjectId" -ForegroundColor White
Write-Host ""

Write-Host "=== 步驟 2: 新增成員 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 點擊「授予存取權」按鈕（右上角）" -ForegroundColor White
Write-Host ""
Write-Host "2. 在「新增成員」欄位輸入:" -ForegroundColor White
Write-Host "   $AdminEmail" -ForegroundColor Gray
Write-Host ""

Write-Host "=== 步驟 3: 選擇角色 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "建議角色：" -ForegroundColor Yellow
Write-Host "  • 專案編輯者 (Project Editor) - roles/editor" -ForegroundColor Green
Write-Host "    權限: 可以管理專案資源，不能刪除專案" -ForegroundColor Gray
Write-Host ""
Write-Host "其他選項：" -ForegroundColor Yellow
Write-Host "  • 擁有者 (Owner) - roles/owner" -ForegroundColor White
Write-Host "    權限: 完整權限（不建議，除非必要）" -ForegroundColor Gray
Write-Host "  • 檢視者 (Viewer) - roles/viewer" -ForegroundColor White
Write-Host "    權限: 只能查看（權限不足）" -ForegroundColor Gray
Write-Host ""

Write-Host "=== 步驟 4: 儲存設定 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 選擇角色: $Role" -ForegroundColor White
Write-Host "2. 點擊「儲存」" -ForegroundColor White
Write-Host "3. 確認新管理員已出現在成員列表中" -ForegroundColor White
Write-Host ""

Write-Host "=== 使用 gcloud CLI（如果已安裝） ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "如果已安裝 gcloud CLI，可以使用以下命令：" -ForegroundColor White
Write-Host ""
Write-Host "  gcloud projects add-iam-policy-binding $ProjectId `\" -ForegroundColor Gray
Write-Host "      --member='user:$AdminEmail' `\" -ForegroundColor Gray
Write-Host "      --role='$Role'" -ForegroundColor Gray
Write-Host ""

Write-Host "=== 驗證設定 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 確認成員列表中有 $AdminEmail" -ForegroundColor White
Write-Host "2. 確認角色設定正確" -ForegroundColor White
Write-Host "3. 可以請新管理員登入確認權限" -ForegroundColor White
Write-Host ""

Write-Host "=== 安全建議 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 確認新管理員已啟用雙因素驗證 (2FA)" -ForegroundColor Yellow
Write-Host "2. 定期審查 IAM 權限" -ForegroundColor Yellow
Write-Host "3. 移除不需要的權限" -ForegroundColor Yellow
Write-Host ""

Write-Host "=== 完成 ===" -ForegroundColor Green
Write-Host ""
Write-Host "新管理員 $AdminEmail 已新增為專案編輯者" -ForegroundColor White
Write-Host "詳細設定文件：" -ForegroundColor Cyan
Write-Host "  docs\GOOGLE_CLOUD_PROJECT_CONFIG.md" -ForegroundColor White
