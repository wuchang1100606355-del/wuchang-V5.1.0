param([string]$Action = "status")

$DeviceDir = "$PSScriptRoot\.wuchang_device"
if (-not (Test-Path $DeviceDir)) { New-Item -ItemType Directory $DeviceDir -Force | Out-Null }

function Get-DeviceID {
    $wmiId = Get-WmiObject Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID
    $macAddr = (Get-NetAdapter | Where-Object Status -eq "Up" | Select-Object -First 1).MacAddress
    return ("$wmiId$macAddr").GetHashCode().ToString().PadLeft(32, '0').Substring(0, 32)
}

function New-UniqueCode {
    param([int]$len = 32)
    $chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    $code = -join (1..$len | ForEach-Object { $chars[(Get-Random -Max $chars.Length)] })
    return $code
}

function Reg-Device {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -f Cyan
    Write-Host "║        設備UI身分釋放 - Device Identity Released          ║" -f Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -f Cyan
    Write-Host ""
    
    $deviceID = Get-DeviceID
    $ts = Get-Date -f "yyyy-MM-dd HH:mm:ss"
    $hostname = [System.Net.Dns]::GetHostName()
    
    $data = @{
        deviceID = $deviceID
        hostname = $hostname
        registeredAt = $ts
        uiStatus = "RELEASED"
        status = "ACTIVE"
    }
    
    $data | ConvertTo-Json | Out-File "$DeviceDir\identity.json" -Encoding UTF8
    
    Write-Host "✅ 設備身分已釋放:" -f Green
    Write-Host "   設備ID: $deviceID" -f Cyan
    Write-Host "   主機名: $hostname" -f Cyan
    Write-Host "   釋放時間: $ts" -f Cyan
    Write-Host "   UI狀態: RELEASED" -f Green
    Write-Host ""
}

function Gen-Token {
    if (-not (Test-Path "$DeviceDir\identity.json")) {
        Write-Host "❌ 尚未註冊設備身分" -f Red
        return
    }
    
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -f Cyan
    Write-Host "║       本機唯一碼與約定金生成 - Token Generation           ║" -f Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -f Cyan
    Write-Host ""
    
    $identity = Get-Content "$DeviceDir\identity.json" | ConvertFrom-Json
    $uniqueCode = New-UniqueCode 32
    $agreeToken = New-UniqueCode 32
    $ts = Get-Date -f "yyyy-MM-dd HH:mm:ss"
    
    $token = @{
        uniqueCode = $uniqueCode
        agreeToken = $agreeToken
        generatedAt = $ts
        expiresAt = (Get-Date).AddHours(24).ToString("yyyy-MM-dd HH:mm:ss")
        status = "ACTIVE"
    }
    
    $token | ConvertTo-Json | Out-File "$DeviceDir\token.json" -Encoding UTF8
    
    Write-Host "✅ 本機唯一碼與約定金已生成:" -f Green
    Write-Host "   本機唯一碼: $uniqueCode" -f Cyan
    Write-Host "   約定金令牌: $agreeToken" -f Green
    Write-Host "   生成時間: $ts" -f Cyan
    Write-Host "   過期時間: 2026-01-12 01:09:13" -f Yellow
    Write-Host ""
}

function Est-Channel {
    if (-not (Test-Path "$DeviceDir\token.json")) {
        Write-Host "❌ 尚未生成驗證令牌" -f Red
        return
    }
    
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -f Cyan
    Write-Host "║    驗證專用通道建立 - Verification Channel Established   ║" -f Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -f Cyan
    Write-Host ""
    
    $token = Get-Content "$DeviceDir\token.json" | ConvertFrom-Json
    $channelID = New-UniqueCode 16
    $secret = New-UniqueCode 32
    $ts = Get-Date -f "yyyy-MM-dd HH:mm:ss"
    
    $channel = @{
        channelID = $channelID
        secret = $secret
        uniqueCode = $token.uniqueCode
        agreeToken = $token.agreeToken
        createdAt = $ts
        status = "ESTABLISHED"
        endpoints = @(
            "http://localhost:8069/auth/verify"
            "http://localhost:8080/auth/verify"
            "https://wuchang.life/verify"
        )
    }
    
    $channel | ConvertTo-Json | Out-File "$DeviceDir\channel.json" -Encoding UTF8
    
    Write-Host "✅ 驗證專用通道已建立:" -f Green
    Write-Host "   通道ID: $channelID" -f Cyan
    Write-Host "   通道密鑰: $secret" -f Yellow
    Write-Host "   約定金令牌: $($token.agreeToken)" -f Green
    Write-Host "   建立時間: $ts" -f Cyan
    Write-Host "   狀態: ESTABLISHED" -f Green
    Write-Host ""
    Write-Host "📡 可用驗證端點:" -f Cyan
    $channel.endpoints | ForEach-Object { Write-Host "   → $_" -f Gray }
    Write-Host ""
}

function Show-Status {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -f Cyan
    Write-Host "║       設備身份驗證系統狀態 - System Status              ║" -f Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -f Cyan
    Write-Host ""
    
    if (Test-Path "$DeviceDir\identity.json") {
        $id = Get-Content "$DeviceDir\identity.json" | ConvertFrom-Json
        Write-Host "✅ 設備身分: REGISTERED" -f Green
        Write-Host "   設備ID: $($id.deviceID)" -f Cyan
        Write-Host "   主機: $($id.hostname)" -f Cyan
        Write-Host ""
    } else {
        Write-Host "❌ 設備身分: 未註冊" -f Red
        Write-Host ""
    }
    
    if (Test-Path "$DeviceDir\token.json") {
        $tok = Get-Content "$DeviceDir\token.json" | ConvertFrom-Json
        Write-Host "✅ 本機驗證碼: ACTIVE" -f Green
        Write-Host "   唯一碼: $($tok.uniqueCode)" -f Green
        Write-Host "   約定金: $($tok.agreeToken)" -f Green
        Write-Host "   過期: $($tok.expiresAt)" -f Yellow
        Write-Host ""
    } else {
        Write-Host "⚠️  本機驗證碼: 未生成" -f Yellow
        Write-Host ""
    }
    
    if (Test-Path "$DeviceDir\channel.json") {
        $ch = Get-Content "$DeviceDir\channel.json" | ConvertFrom-Json
        Write-Host "✅ 驗證通道: ESTABLISHED" -f Green
        Write-Host "   通道ID: $($ch.channelID)" -f Green
        Write-Host "   密鑰: $($ch.secret)" -f Yellow
        Write-Host "   狀態: $($ch.status)" -f Green
        Write-Host ""
    } else {
        Write-Host "⚠️  驗證通道: 未建立" -f Yellow
        Write-Host ""
    }
    
    if (Get-Process powershell | Where-Object { $_.CommandLine -match "keep_alive" }) {
        Write-Host "✅ 握手信號: 運行中" -f Green
    } else {
        Write-Host "⚠️  握手信號: 未運行" -f Yellow
    }
    Write-Host ""
}

switch ($Action) {
    "register" { Reg-Device }
    "token" { Gen-Token }
    "auth" { Est-Channel }
    default { Show-Status }
}
