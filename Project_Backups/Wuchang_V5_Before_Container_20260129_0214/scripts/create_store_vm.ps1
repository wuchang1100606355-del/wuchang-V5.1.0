# create_store_vm.ps1
# 創建店端管控 VM
# 根據 VM化架構分析與建議.md 步驟 2

$ErrorActionPreference = "Stop"

$vmName = "Wuchang-Store-Control"
$vmPath = "C:\VMs"
$vhdPath = Join-Path $vmPath "$vmName.vhdx"
$memoryStartupBytes = 4GB
$vhdSize = 100GB

Write-Host "Creating Store Control VM: $vmName" -ForegroundColor Cyan

# Check if Hyper-V module is available
if (-not (Get-Module -ListAvailable -Name Hyper-V)) {
    Write-Error "Hyper-V module is not available. Please enable Hyper-V first."
    exit 1
}

# Create VM Directory if not exists
if (-not (Test-Path $vmPath)) {
    Write-Host "Creating directory: $vmPath"
    New-Item -ItemType Directory -Path $vmPath | Out-Null
}

# Check if VM already exists
$existingVM = Get-VM -Name $vmName -ErrorAction SilentlyContinue
if ($existingVM) {
    Write-Host "VM '$vmName' already exists. Skipping creation." -ForegroundColor Yellow
} else {
    try {
        Write-Host "Creating new VM..."
        New-VM -Name $vmName `
               -MemoryStartupBytes $memoryStartupBytes `
               -Generation 2 `
               -NewVHDPath $vhdPath `
               -NewVHDSizeBytes $vhdSize

        Write-Host "VM '$vmName' created successfully." -ForegroundColor Green
        
        # Configure Network Adapter (Connect to Default Switch initially)
        # Note: New-VM usually creates a network adapter connected to nothing or default.
        # Let's ensure it's connected to Default Switch for internet access during setup if needed, 
        # or wait for the network script to attach it to the internal switch.
        # The doc says: Add-VMNetworkAdapter -VMName "Wuchang-Store-Control" -SwitchName "Default Switch"
        # But New-VM creates one by default usually. Let's check.
        
        $adapter = Get-VMNetworkAdapter -VMName $vmName
        if (-not $adapter) {
            Add-VMNetworkAdapter -VMName $vmName -SwitchName "Default Switch"
        } else {
            Connect-VMNetworkAdapter -VMNetworkAdapter $adapter -SwitchName "Default Switch"
        }
        
        # Enable Secure Boot (Standard for Gen 2)
        Set-VMFirmware -VMName $vmName -EnableSecureBoot On

        # Set Processor Count (Default is 1, maybe increase to 2 for better performance)
        Set-VMProcessor -VMName $vmName -Count 2
        
        Write-Host "VM Configuration updated (2 vCPUs, Secure Boot)." -ForegroundColor Green

    } catch {
        Write-Error "Failed to create VM: $_"
        exit 1
    }
}
