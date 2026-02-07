param(
  [string]$ServerUrl = "http://localhost:8080",
  [string]$MerchantName = "Demo Cafe"
)

Write-Host "[Sim] 啟動新商家模擬: $MerchantName，伺服器: $ServerUrl"

$venvPy = "C:/wuchang V5.1.0/.venv/Scripts/python.exe"
$activate = "C:/wuchang V5.1.0/.venv/Scripts/Activate.ps1"
$agent = "C:/wuchang V5.1.0/sister_agent.py"

if (-not (Test-Path $venvPy)) {
  Write-Error "找不到虛擬環境 Python：$venvPy"
  exit 1
}

# 啟動 POS 與 CUSTOMER 代理（各自開新視窗）
Start-Process powershell -ArgumentList @("-NoExit","-Command","& '$activate'; python '$agent' --device POS --vm-url $ServerUrl --hostname DemoPOS1") | Out-Null
Start-Process powershell -ArgumentList @("-NoExit","-Command","& '$activate'; python '$agent' --device CUSTOMER --vm-url $ServerUrl --hostname DemoCustomer1") | Out-Null

Start-Sleep -Seconds 6

# 推送同步 UI 指令（不夾帶 URL，讓代理使用伺服器配置）
$syncPos = @{ device_type = "POS"; command = @{ type = "SYNC_UI" } } | ConvertTo-Json -Compress
Invoke-RestMethod -Method Post -Uri "$ServerUrl/commands/push" -Body $syncPos -ContentType "application/json" | Out-Null

$syncCust = @{ device_type = "CUSTOMER"; command = @{ type = "SYNC_UI" } } | ConvertTo-Json -Compress
Invoke-RestMethod -Method Post -Uri "$ServerUrl/commands/push" -Body $syncCust -ContentType "application/json" | Out-Null

Start-Sleep -Seconds 2

# 顯示目前註冊裝置清單
Write-Host "[Sim] 已推送 SYNC_UI，列出當前裝置："
$devices = Invoke-RestMethod -Method Get -Uri "$ServerUrl/devices"
$devices | ConvertTo-Json -Depth 5

Write-Host "[Sim] 如需測試重新整理，將推送 RELOAD 到 POS 與 CUSTOMER"
$reloadPos = @{ device_type = "POS"; command = @{ type = "RELOAD" } } | ConvertTo-Json -Compress
Invoke-RestMethod -Method Post -Uri "$ServerUrl/commands/push" -Body $reloadPos -ContentType "application/json" | Out-Null

$reloadCus = @{ device_type = "CUSTOMER"; command = @{ type = "RELOAD" } } | ConvertTo-Json -Compress
Invoke-RestMethod -Method Post -Uri "$ServerUrl/commands/push" -Body $reloadCus -ContentType "application/json" | Out-Null

Write-Host "[Sim] 模擬完成。POS/客顯應已切到指定 UI 並重載。"
