<#
.SYNOPSIS
    Manages network traffic priority between Virtual Machines.
    家人專用 - 流量分配控制中心

.DESCRIPTION
    Allows boosting traffic for a specific VM by temporarily limiting the others.
    Since the upstream router (iPhone) cannot prioritize, we limit the non-critical VM
    to ensure the critical one gets full pipe.

.PARAMETER Mode
    'Balanced' (Default) - Both VMs get full speed.
    'BoostWin' - Windows VM gets full speed, Odoo limited to 2 Mbps.
    'BoostOdoo' - Odoo VM gets full speed, Windows limited to 2 Mbps.
#>

param(
    [ValidateSet("Balanced", "BoostWin", "BoostOdoo")]
    [string]$Mode = "Balanced"
)

$VBoxManage = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
$WinVM = "Win-VM"
$OdooVM = "Odoo-Entry-VM"
$LimitGroupName = "TrafficQuota"

function Ensure-BandwidthGroup {
    param($VM)
    $info = & $VBoxManage showvminfo $VM --machinereadable
    if ($info -notmatch "bandwidthctl_name\d+=""$LimitGroupName""") {
        Write-Host "Initializing Traffic Control for $VM..." -ForegroundColor Cyan
        # Create group with 1000 Mbps limit (effectively unlimited)
        & $VBoxManage bandwidthctl $VM add $LimitGroupName --type Network --limit 1000m
        
        # Attach to both adapters just in case
        & $VBoxManage modifyvm $VM --nicbandwidthgroup1 $LimitGroupName
        & $VBoxManage modifyvm $VM --nicbandwidthgroup2 $LimitGroupName
    }
}

# 1. Ensure Infrastructure
Ensure-BandwidthGroup -VM $WinVM
Ensure-BandwidthGroup -VM $OdooVM

# 2. Apply Mode
switch ($Mode) {
    "Balanced" {
        Write-Host "⚖️  Setting mode to: BALANCED (Sharing Love)" -ForegroundColor Green
        & $VBoxManage bandwidthctl $WinVM set $LimitGroupName --limit 1000m
        & $VBoxManage bandwidthctl $OdooVM set $LimitGroupName --limit 1000m
    }
    "BoostWin" {
        Write-Host "🚀 Setting mode to: BOOST WINDOWS (Shop Priority)" -ForegroundColor Yellow
        & $VBoxManage bandwidthctl $WinVM set $LimitGroupName --limit 1000m
        & $VBoxManage bandwidthctl $OdooVM set $LimitGroupName --limit 2m
        Write-Host "   -> Odoo VM restricted to 2 Mbps to yield traffic." -ForegroundColor Gray
    }
    "BoostOdoo" {
        Write-Host "🚀 Setting mode to: BOOST ODOO (System Priority)" -ForegroundColor Yellow
        & $VBoxManage bandwidthctl $OdooVM set $LimitGroupName --limit 1000m
        & $VBoxManage bandwidthctl $WinVM set $LimitGroupName --limit 2m
        Write-Host "   -> Windows VM restricted to 2 Mbps to yield traffic." -ForegroundColor Gray
    }
}

Write-Host "✅ Traffic rules updated successfully." -ForegroundColor Green
