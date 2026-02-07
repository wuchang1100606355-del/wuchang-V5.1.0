# setup_vm_network.ps1
# 配置虛擬網絡
# 根據 VM化架構分析與建議.md 步驟 3

$ErrorActionPreference = "Stop"

$switchName = "Wuchang-Internal"
$vmName = "Wuchang-Store-Control"
$ipAddress = "192.168.100.1"
$prefixLength = 24
$interfaceAlias = "vEthernet ($switchName)"

Write-Host "Configuring VM Network..." -ForegroundColor Cyan

# 1. Create Internal Switch
$switch = Get-VMSwitch -Name $switchName -ErrorAction SilentlyContinue
if ($switch) {
    Write-Host "Switch '$switchName' already exists." -ForegroundColor Yellow
} else {
    Write-Host "Creating Internal Switch: $switchName"
    New-VMSwitch -Name $switchName -SwitchType Internal
}

# 2. Configure Host IP Address for the Internal Switch
# The adapter is usually named "vEthernet (SwitchName)"
Write-Host "Configuring IP Address for Host Adapter: $interfaceAlias"

# Check if interface exists (it might take a moment after switch creation)
Start-Sleep -Seconds 3

if (Get-NetAdapter -Name $interfaceAlias -ErrorAction SilentlyContinue) {
    # Check if IP is already assigned
    $existingIP = Get-NetIPAddress -InterfaceAlias $interfaceAlias -AddressFamily IPv4 -ErrorAction SilentlyContinue
    if ($existingIP) {
        if ($existingIP.IPAddress -eq $ipAddress) {
            Write-Host "IP $ipAddress is already assigned to $interfaceAlias." -ForegroundColor Green
        } else {
            Write-Host "Warning: $interfaceAlias has IP $($existingIP.IPAddress). Please check configuration manually." -ForegroundColor Yellow
        }
    } else {
        Write-Host "Assigning IP $ipAddress to $interfaceAlias"
        New-NetIPAddress -IPAddress $ipAddress -PrefixLength $prefixLength -InterfaceAlias $interfaceAlias
    }
} else {
    Write-Error "Network Adapter '$interfaceAlias' not found. Please check Switch creation."
    # List available adapters for debugging
    Get-NetAdapter | Select-Object Name, InterfaceDescription | Format-Table
    exit 1
}

# 3. Connect VM to this Switch
# Note: The doc implies connecting the VM to this switch.
# The previous script connected it to "Default Switch".
# Usually for "Store Control", we might want it isolated (Internal) OR NAT.
# If "Internal", it has no internet unless we setup NAT.
# The doc says "Configuring Virtual Network" and sets IP 192.168.100.1 on Host.
# This implies a private network between Host and VM.
# Let's add a SECOND adapter for this internal network, or replace the Default Switch?
# The doc says: "Add-VMNetworkAdapter ... -SwitchName 'Default Switch'" in Step 2.
# Then Step 3 creates "Wuchang-Internal".
# It doesn't explicitly say to connect the VM to "Wuchang-Internal", but it implies it for "Network Configuration".
# I will ADD a second adapter connected to "Wuchang-Internal" to the VM, 
# so it has Internet (via Default Switch) AND Private Link (via Wuchang-Internal).

Write-Host "Connecting VM '$vmName' to '$switchName'..."
$internalAdapterName = "Network Adapter Internal"
$vmAdapter = Get-VMNetworkAdapter -VMName $vmName | Where-Object { $_.SwitchName -eq $switchName }

if (-not $vmAdapter) {
    Add-VMNetworkAdapter -VMName $vmName -SwitchName $switchName -Name $internalAdapterName
    Write-Host "Added Internal Network Adapter to VM." -ForegroundColor Green
} else {
    Write-Host "VM is already connected to '$switchName'." -ForegroundColor Yellow
}

Write-Host "Network Configuration Complete." -ForegroundColor Green
