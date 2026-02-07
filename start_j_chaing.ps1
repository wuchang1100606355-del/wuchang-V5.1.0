$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "🚀 Starting J.CHAING Service (Twin Soul Architecture)..." -ForegroundColor Cyan
python "$ScriptDir\tools\j_chaing_service.py"
