Start-Sleep -Seconds 30
Set-DnsClientServerAddress -InterfaceAlias 'Wi-Fi' -ServerAddresses ('192.168.50.84', '8.8.8.8')
Write-Host 'DNS settings restored to 192.168.50.84'