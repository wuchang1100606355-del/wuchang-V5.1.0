Write-Host "Enabling Router Relay Manually..."

# 1. Enable IP Forwarding
Write-Host "Enabling IP Forwarding..."
cmd /c "netsh int ipv4 set global forwarding=enabled"

# 2. Add Static Route
Write-Host "Adding Static Route..."
cmd /c "route add 92.18.50.249 mask 255.255.255.255 192.168.50.1"

# 3. Configure Firewall
Write-Host "Configuring Firewall..."
netsh advfirewall firewall set rule name="File and Printer Sharing (Echo Request - ICMPv4-In)" dir=in action=allow

# 4. Configure NAT/PortProxy
Write-Host "Configuring NAT/PortProxy..."
$ports = @(8069, 8080, 3001, 80, 443, 5432)
foreach ($port in $ports) {
    Write-Host "  Proxying port $port..."
    netsh interface portproxy add v4tov4 listenport=$port listenaddress=0.0.0.0 connectport=$port connectaddress=192.168.50.84
}

Write-Host "Relay Enabled."
