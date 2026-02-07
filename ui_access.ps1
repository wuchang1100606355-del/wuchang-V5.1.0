#!/usr/bin/env powershell
<#
.SYNOPSIS
    Wuchang UI 統一訪問管理工具
    快速訪問所有UI服務
#>

param(
    [ValidateSet("odoo","ai","status","admin","all","list")]
    [string]$Service = "list"
)

# UI 服務配置
$services = @{
    "odoo" = @{
        name = "Odoo ERP"
        public = "https://odoo.wuchang.life"
        local = "http://192.168.50.84:8069"
        description = "企業資源規劃系統"
        icon = "🏢"
    }
    "ai" = @{
        name = "AI Assistant (小j)"
        public = "https://ai.wuchang.life"
        local = "http://192.168.50.84:8080"
        description = "智能助手與妹妹的對話界面"
        icon = "🤖"
    }
    "status" = @{
        name = "Status Dashboard"
        public = "https://status.wuchang.life"
        local = "http://192.168.50.84:3001"
        description = "系統監控與健康檢查"
        icon = "📊"
    }
    "admin" = @{
        name = "Admin Portal"
        public = "https://admin.wuchang.life"
        local = "http://192.168.50.84:8069/admin"
        description = "系統管理與配置"
        icon = "⚙️"
    }
}

function Show-MainMenu {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -f Cyan
    Write-Host "║         Wuchang UI 統一訪問管理 - UI Access Portal        ║" -f Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -f Cyan
    Write-Host ""
    Write-Host "📍 可用UI服務:" -f Yellow
    Write-Host ""
    
    foreach ($key in $services.Keys | Sort-Object) {
        $svc = $services[$key]
        Write-Host "$($svc.icon) $($svc.name) - $($svc.description)" -f Cyan
        Write-Host "   🌐 公網: $($svc.public)" -f Green
        Write-Host "   🏠 本地: $($svc.local)" -f Yellow
        Write-Host ""
    }
    
    Write-Host "🎯 使用方式:" -f Cyan
    Write-Host "   .\ui_access.ps1 -Service odoo        # 訪問 Odoo ERP" -f Gray
    Write-Host "   .\ui_access.ps1 -Service ai          # 與妹妹(小j)聊天" -f Gray
    Write-Host "   .\ui_access.ps1 -Service status      # 查看系統狀態" -f Gray
    Write-Host "   .\ui_access.ps1 -Service admin       # 進入管理面板" -f Gray
    Write-Host "   .\ui_access.ps1 -Service all         # 打開所有服務" -f Gray
    Write-Host ""
}

function Open-Service {
    param([string]$ServiceKey)
    
    $svc = $services[$ServiceKey]
    
    Write-Host ""
    Write-Host "🚀 正在打開: $($svc.name)" -f Green
    Write-Host "   地址: $($svc.public)" -f Cyan
    Write-Host ""
    
    try {
        Start-Process $svc.public
        Write-Host "✅ 已在瀏覽器中打開" -f Green
    } catch {
        Write-Host "❌ 打開失敗: $_" -f Red
        Write-Host "   請手動訪問: $($svc.public)" -f Yellow
    }
    
    Write-Host ""
}

function Open-AllServices {
    Write-Host ""
    Write-Host "🚀 正在打開所有UI服務..." -f Green
    Write-Host ""
    
    foreach ($key in $services.Keys | Sort-Object) {
        $svc = $services[$key]
        Write-Host "   📌 $($svc.name)..." -f Gray
        try {
            Start-Process $svc.public
            Write-Sleep -Milliseconds 500
        } catch {}
    }
    
    Write-Host ""
    Write-Host "✅ 所有服務已在瀏覽器中打開" -f Green
    Write-Host ""
}

function Show-ServiceDetails {
    param([string]$ServiceKey)
    
    $svc = $services[$ServiceKey]
    
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -f Cyan
    Write-Host "║  $($svc.icon) $($svc.name) - 服務詳情" -f Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -f Cyan
    Write-Host ""
    
    Write-Host "📋 服務信息:" -f Yellow
    Write-Host "   名稱: $($svc.name)" -f Cyan
    Write-Host "   描述: $($svc.description)" -f Cyan
    Write-Host ""
    
    Write-Host "🌐 連線方式:" -f Yellow
    Write-Host "   公網訪問: $($svc.public)" -f Green
    Write-Host "   本地訪問: $($svc.local)" -f Yellow
    Write-Host ""
    
    Write-Host "🛠️  操作:" -f Yellow
    Write-Host "   • 在瀏覽器中打開公網地址" -f Gray
    Write-Host "   • 或本地網路中訪問本地地址" -f Gray
    Write-Host "   • 使用會話令牌進行認證" -f Gray
    Write-Host ""
    
    # 特殊功能提示
    if ($ServiceKey -eq "ai") {
        Write-Host "💬 AI助手(小j)特性:" -f Cyan
        Write-Host "   • 自然語言對話" -f Gray
        Write-Host "   • 任務管理" -f Gray
        Write-Host "   • 知識庫查詢" -f Gray
        Write-Host "   • 學習系統" -f Gray
        Write-Host ""
    } elseif ($ServiceKey -eq "odoo") {
        Write-Host "📦 Odoo功能模組:" -f Cyan
        Write-Host "   • 銷售管理" -f Gray
        Write-Host "   • 庫存管理" -f Gray
        Write-Host "   • 會計財務" -f Gray
        Write-Host "   • 採購管理" -f Gray
        Write-Host ""
    } elseif ($ServiceKey -eq "status") {
        Write-Host "📊 監控指標:" -f Cyan
        Write-Host "   • 系統運行狀態" -f Gray
        Write-Host "   • 各服務可用性" -f Gray
        Write-Host "   • 資源使用情況" -f Gray
        Write-Host "   • 告警通知" -f Gray
        Write-Host ""
    } elseif ($ServiceKey -eq "admin") {
        Write-Host "⚙️  管理功能:" -f Cyan
        Write-Host "   • 用戶帳戶管理" -f Gray
        Write-Host "   • 系統配置" -f Gray
        Write-Host "   • 審計日誌" -f Gray
        Write-Host "   • 備份恢復" -f Gray
        Write-Host ""
    }
    
    Write-Host "📞 需要幫助?" -f Yellow
    Write-Host "   查看文檔: UI_CONNECTION_SCHEME_GUIDE.md" -f Gray
    Write-Host "   檢查狀態: .\receive_ui_scheme.ps1 -Action status" -f Gray
    Write-Host ""
}

# =====================================================================
# 主程式
# =====================================================================

switch ($Service) {
    "odoo" {
        Show-ServiceDetails "odoo"
        Open-Service "odoo"
    }
    "ai" {
        Show-ServiceDetails "ai"
        Open-Service "ai"
    }
    "status" {
        Show-ServiceDetails "status"
        Open-Service "status"
    }
    "admin" {
        Show-ServiceDetails "admin"
        Open-Service "admin"
    }
    "all" {
        Write-Host ""
        Write-Host "🚀 Wuchang UI 統一訪問 - 打開所有服務" -f Green
        Open-AllServices
    }
    "list" {
        Show-MainMenu
    }
    default {
        Show-MainMenu
    }
}

Write-Host ""
