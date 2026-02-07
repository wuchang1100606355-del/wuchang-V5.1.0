while (\True) {
    if (Test-Connection -ComputerName '8.8.8.8' -Count 1 -Quiet) {
        Write-Host 'Internet connection restored.'
        if (Test-Connection -ComputerName '192.168.50.1' -Count 1 -Quiet) {
            Write-Host 'Router (192.168.50.1) is reachable via Tailscale!'
            break
        } else {
            Write-Host 'Router not yet reachable via Tailscale. Waiting...'
        }
    } else {
        Write-Host 'Waiting for internet connection...'
    }
    Start-Sleep -Seconds 5
}