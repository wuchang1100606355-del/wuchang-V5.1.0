#!/usr/bin/env powershell
<#
.SYNOPSIS
    驗證 192.18.50.249 連線能力
#>

param([string]$Action = "test")

$targetIP = "192.18.50.249"
$localIP = "192.168.50.84"
$ports = @(8069, 8080, 3001, 80, 443, 5432)
$services = @{
    8069 = "Odoo ERP"
    8080 = "AI Service"
    3001 = "Uptime Kuma"
    80 = "HTTP"
    443 = "HTTPS"
    5432 = "PostgreSQL"
}

function Test-IPConnectivity {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -f Cyan
    Write-Host "║       驗證 192.18.50.249 連線能力 - Connectivity Test      ║" -f Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -f Cyan
    Write-Host ""
    
    Write-Host "目標 IP: $targetIP" -f Yellow
    Write-Host "本機 IP: $localIP" -f Yellow
    Write-Host ""
    
    # 測試入站規則
    Write-Host "📋 防火牆規則狀態:" -f Cyan
    foreach ($port in $ports) {
        $service = $services[$port]
        $rule = Get-NetFirewallRule -DisplayName "Allow-$port-$targetIP" -ErrorAction SilentlyContinue
        if ($rule) {
            Write-Host "   ✅ 埤 $port ($service): 規則已配置" -f Green
        } else {
            Write-Host "   ⚠️  埤 $port ($service): 規則未找到" -f Yellow
        }
    }
    
    Write-Host ""
    Write-Host "🔍 本機埠監聽狀態:" -f Cyan
    foreach ($port in $ports) {
        $service = $services[$port]
        $listening = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($listening) {
            Write-Host "   ✅ 埤 $port ($service): 監聽中" -f Green
        } else {
            Write-Host "   ⚠️  埤 $port ($service): 未監聽" -f Yellow
        }
    }
    
    Write-Host ""
    Write-Host "📡 防火牆配置:" -f Cyan
    $fwProfile = Get-NetFirewallProfile -All
    $fwProfile | ForEach-Object {
        $status = if ($_.Enabled) { "✅ 已啟用" } else { "⚠️  已禁用" }
        Write-Host "   $($_.Name): $status" -f Gray
    }
    
    Write-Host ""
}

function Show-RuleDetails {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -f Cyan
    Write-Host "║           防火牆規則詳細信息 - Firewall Rules Detail      ║" -f Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -f Cyan
    Write-Host ""
    
    $rules = Get-NetFirewallRule -DisplayName "Allow-*-$targetIP" -ErrorAction SilentlyContinue
    
    if ($rules) {
        Write-Host "找到 $($rules.Count) 條規則:" -f Green
        foreach ($rule in $rules) {
            Write-Host ""
            Write-Host "📌 $($rule.DisplayName)" -f Cyan
            Write-Host "   狀態: $($rule.Enabled)" -f Gray
            Write-Host "   方向: $($rule.Direction)" -f Gray
            Write-Host "   動作: $($rule.Action)" -f Gray
            
            $portFilter = Get-NetFirewallPortFilter -AssociatedNetFirewallRule $rule -ErrorAction SilentlyContinue
            if ($portFilter) {
                Write-Host "   埤: $($portFilter.LocalPort)" -f Gray
                Write-Host "   協議: $($portFilter.Protocol)" -f Gray
            }
            
            $addressFilter = Get-NetFirewallAddressFilter -AssociatedNetFirewallRule $rule -ErrorAction SilentlyContinue
            if ($addressFilter) {
                Write-Host "   遠程 IP: $($addressFilter.RemoteAddress)" -f Gray
            }
        }
        Write-Host ""
    } else {
        Write-Host "❌ 未找到相關規則" -f Red
        Write-Host ""
    }
}

function Show-Commands {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -f Cyan
    Write-Host "║         常用命令 - Useful Commands for Management         ║" -f Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -f Cyan
    Write-Host ""
    
    Write-Host "【查看規則】" -f Yellow
    Write-Host "  powershell> netsh advfirewall firewall show rule name=`"Allow-*-192.18.50.249`"" -f Gray
    Write-Host ""
    
    Write-Host "【測試連線】" -f Yellow
    Write-Host "  powershell> Test-NetConnection -ComputerName 192.168.50.84 -Port 8069" -f Gray
    Write-Host ""
    
    Write-Host "【添加規則】" -f Yellow
    Write-Host "  cmd> netsh advfirewall firewall add rule name=`"Allow-8069-192.18.50.249`" dir=in action=allow protocol=tcp localport=8069 remoteip=192.18.50.249" -f Gray
    Write-Host ""
    
    Write-Host "【刪除規則】" -f Yellow
    Write-Host "  cmd> netsh advfirewall firewall delete rule name=`"Allow-8069-192.18.50.249`"" -f Gray
    Write-Host ""
    
    Write-Host "【查看所有防火牆配置文件】" -f Yellow
    Write-Host "  powershell> Get-NetFirewallProfile -All" -f Gray
    Write-Host ""
}

switch ($Action) {
    "test" { Test-IPConnectivity }
    "rules" { Show-RuleDetails }
    "commands" { Show-Commands }
    "all" { Test-IPConnectivity; Show-RuleDetails; Show-Commands }
    default { Test-IPConnectivity }
}

Write-Host ""
