$sourcePath = "C:\wuchang V5.0.0"
$destinationPath = "C:\wuchang V5.0.0\wuchang_v5_deploy.zip"
$excludeList = @(
    "pgdata",
    "backups",
    "logs",
    "node_modules",
    ".git",
    "memory_store",
    "downloads",
    "jules_session_*"
)

if (Test-Path $destinationPath) { Remove-Item $destinationPath }

Write-Host "正在打包系統內容，排除大型資料夾..."
$files = Get-ChildItem -Path $sourcePath -Exclude $excludeList -Recurse
Compress-Archive -Path $files.FullName -DestinationPath $destinationPath -Force
Write-Host "打包完成：$destinationPath"
