# Windows 雲端資料夾自動同步腳本（適用於五常 AI 共用機制）
# 請以系統管理員權限執行
# 將本機 ai_data 與雲端資料夾自動雙向同步

$localPath = "$PSScriptRoot\ai_data"
$cloudPath = "J:\共用雲端硬碟\五常雲端空間\ai_data"

# 檢查本機 ai_data 是否存在，若無則建立
if (!(Test-Path $localPath)) {
    New-Item -ItemType Directory -Path $localPath | Out-Null
}

# 使用 robocopy 進行雙向同步
# 1. 雲端 → 本機
robocopy $cloudPath $localPath /MIR /Z /R:2 /W:2 /XD ".git" ".venv" /XF ".DS_Store"
# 2. 本機 → 雲端
robocopy $localPath $cloudPath /MIR /Z /R:2 /W:2 /XD ".git" ".venv" /XF ".DS_Store"

Write-Host "ai_data 雲端同步完成！" -ForegroundColor Green
