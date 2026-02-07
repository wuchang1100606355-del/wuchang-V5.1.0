Write-Host "🔥 Configuring Windows Firewall for Wuchang Services..." -ForegroundColor Cyan

$rules = @(
    @{ Name="Wuchang UI Control"; Port="8765" },
    @{ Name="Wuchang Cloud Sync"; Port="8766" }
)

foreach ($rule in $rules) {
    $name = $rule.Name
    $port = $rule.Port
    
    Write-Host "   Allowing Inbound TCP Port $port ($name)..."
    
    # Delete existing rule to avoid duplicates
    netsh advfirewall firewall delete rule name="$name" | Out-Null
    
    # Add new rule
    netsh advfirewall firewall add rule name="$name" dir=in action=allow protocol=TCP localport=$port profile=any
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Rule added successfully." -ForegroundColor Green
    } else {
        Write-Host "   ❌ Failed to add rule." -ForegroundColor Red
    }
}

Write-Host "🔥 Firewall configuration complete." -ForegroundColor Cyan
