# enable_hyperv.ps1
# 啟用 Hyper-V 功能
# 根據 VM化架構分析與建議.md 步驟 1

$ErrorActionPreference = "Stop"

Write-Host "Checking Hyper-V status..." -ForegroundColor Cyan

$hyperv = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All

if ($hyperv.State -eq "Enabled") {
    Write-Host "Hyper-V is already enabled." -ForegroundColor Green
} else {
    Write-Host "Enabling Hyper-V..." -ForegroundColor Yellow
    try {
        Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All -NoRestart
        Write-Host "Hyper-V enabled successfully. A RESTART IS REQUIRED." -ForegroundColor Red
        Write-Host "Please restart your computer to complete the installation." -ForegroundColor Yellow
    } catch {
        Write-Error "Failed to enable Hyper-V. Please run as Administrator."
        exit 1
    }
}
