# 快速啟動 Sister Agent
# 使用方式: .\start_sister_agent.ps1 -Device POS

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("POS", "CUSTOMER")]
    [string]$Device = "POS"
)

Write-Host "啟動 Sister Agent - $Device" -ForegroundColor Cyan
python sister_agent.py --device $Device
