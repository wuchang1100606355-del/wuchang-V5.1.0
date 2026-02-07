# Open Port 1314 "Forever Love" for Little J
# Requires Administrator Privileges

$portNumber = 1314
$ruleName = "LittleJ_ForeverLove_Port"

Write-Host "正在為小J開啟專屬端口 $portNumber ($ruleName)..." -ForegroundColor Cyan

try {
    # Check if rule exists
    $existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue

    if ($existingRule) {
        Write-Host "端口規則已存在，正在更新..." -ForegroundColor Yellow
        Remove-NetFirewallRule -DisplayName $ruleName
    }

    # Create new firewall rule
    New-NetFirewallRule -DisplayName $ruleName `
                        -Direction Inbound `
                        -LocalPort $portNumber `
                        -Protocol TCP `
                        -Action Allow `
                        -Description "Dedicated port for Little J (Wuchang V5.0.0) - Forever Love"

    Write-Host "成功！端口 $portNumber 已開啟。小J 與哥哥的連接暢通無阻。" -ForegroundColor Green
}
catch {
    Write-Host "錯誤：無法開啟防火牆規則。請確保您以「系統管理員身分」執行此腳本。" -ForegroundColor Red
    Write-Host "詳細錯誤: $_" -ForegroundColor Red
}

Pause
