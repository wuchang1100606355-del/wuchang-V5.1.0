# Set static IP for Wi-Fi interface
$InterfaceAlias = "Wi-Fi"
$IPAddress = "192.168.50.84"
$PrefixLength = 24
$Gateway = "192.168.50.1"
$DNSServers = ("192.168.50.1", "8.8.8.8")

Write-Host "Configuring $InterfaceAlias..." -ForegroundColor Yellow

# Check if interface exists
if (-not (Get-NetAdapter -Name $InterfaceAlias -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Interface '$InterfaceAlias' not found." -ForegroundColor Red
    exit 1
}

Write-Host "Setting IP address to $IPAddress..."
try {
    # Attempt to set Static IP directly. If it fails, we try disabling DHCP first.
    New-NetIPAddress -InterfaceAlias $InterfaceAlias -IPAddress $IPAddress -PrefixLength $PrefixLength -DefaultGateway $Gateway -AddressFamily IPv4 -ErrorAction Stop
} catch {
    Write-Host "New-NetIPAddress failed. Trying to update existing configuration..." -ForegroundColor Yellow
    try {
        # If IP exists (DHCP or Static), we might need to remove it or disable DHCP first.
        # Safest bet is to disable DHCP (which usually clears dynamic IP) then set static.
        Set-NetIPInterface -InterfaceAlias $InterfaceAlias -Dhcp Disabled -ErrorAction SilentlyContinue
        
        # Remove existing IPs to be clean (ignoring errors if none exist)
        Remove-NetIPAddress -InterfaceAlias $InterfaceAlias -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue
        
        # Apply new IP
        New-NetIPAddress -InterfaceAlias $InterfaceAlias -IPAddress $IPAddress -PrefixLength $PrefixLength -DefaultGateway $Gateway -AddressFamily IPv4 -ErrorAction Stop
    } catch {
        Write-Host "Failed to set static IP: $_" -ForegroundColor Red
        exit 1
    }
}

# Set DNS
Write-Host "Setting DNS servers..."
Set-DnsClientServerAddress -InterfaceAlias $InterfaceAlias -ServerAddresses $DNSServers

# Verify
$NewConfig = Get-NetIPConfiguration -InterfaceAlias $InterfaceAlias
Write-Host "Configuration Updated:" -ForegroundColor Green
Write-Host "IP: $($NewConfig.IPv4Address.IPAddress)"
Write-Host "Gateway: $($NewConfig.IPv4DefaultGateway.NextHop)"
Write-Host "DNS: $($NewConfig.Dnsserver.ServerAddresses -join ', ')"
