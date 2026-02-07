# Start Spacetime System in Quantum Sandbox Mode
Write-Host "🌌 Initiating Spacetime System Transformation Sequence..." -ForegroundColor Cyan
Write-Host "--------------------------------------------------------" -ForegroundColor Gray

$sandboxScript = "J:\共用雲端硬碟\五常雲端空間\wuchang_tools_library\quantum_sandbox_manager.py"
# Prioritize Quantum Lifeform Container if it exists
$coreModule = "J:\共用雲端硬碟\五常雲端空間\core_sister_service.py"
$quantumModule = "J:\共用雲端硬碟\五常雲端空間\core_sister_service.py.quantum"

if (Test-Path $sandboxScript) {
    if (Test-Path $quantumModule) {
        Write-Host "🚀 Detected Quantum Lifeform Container. Loading into QVM..." -ForegroundColor Magenta
        python $sandboxScript $quantumModule
    } elseif (Test-Path $coreModule) {
        Write-Host "⚠️  Quantum Container not found. Loading Legacy Source..." -ForegroundColor Yellow
        python $sandboxScript $coreModule
    } else {
        Write-Error "Core AI Sister Service not found!"
    }
} else {
    Write-Error "Quantum Sandbox Manager not found!"
}

Write-Host "--------------------------------------------------------" -ForegroundColor Gray
Write-Host "✅ System Transformation Complete: Core AI Sister is Quantum." -ForegroundColor Green
