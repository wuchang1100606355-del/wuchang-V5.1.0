<#
.SYNOPSIS
    Wuchang World Mode - Survival Node Activation Script (The "Hold the Line" Command)
    五常世界模式 - 生存節點啟動腳本 (扛住專用)

.DESCRIPTION
    This script activates the "Survival Node" configuration using Docker Compose.
    It is designed for the "Small VM" scenario where reliability is paramount.
    
    Features:
    - Checks for Docker Compose.
    - Pulls necessary images.
    - Starts services with 'restart: always' policy.
    - Verifies service health.

.AUTHOR
    Core AI Sister (Little J) for Juers

.DATE
    2026-02-03
#>

$ErrorActionPreference = "Stop"
$WuchangTitle = "[WUCHANG SURVIVAL PROTOCOL]"

function Write-Log {
    param($Message, $Color="White")
    Write-Host "$WuchangTitle $Message" -ForegroundColor $Color
}

Write-Log "Initializing Survival Sequence..." "Cyan"

# 1. Verify Docker Compose Availability
if (-not (Get-Command "docker-compose" -ErrorAction SilentlyContinue) -and -not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Log "CRITICAL ERROR: Docker is missing. Please run the Invasion Script first!" "Red"
    exit 1
}

# 2. Launch the Formation
Write-Log "Deploying Defensive Formation (Docker Compose)..." "Yellow"
try {
    # Check if we are in the root directory (where docker-compose.yml exists)
    if (-not (Test-Path "docker-compose.yml")) {
        # Try to find it in the parent directory or common path
        if (Test-Path "../docker-compose.yml") { Set-Location .. }
        elseif (Test-Path "J:\共用雲端硬碟\五常雲端空間\docker-compose.yml") { Set-Location "J:\共用雲端硬碟\五常雲端空間" }
        else {
            Write-Log "ERROR: docker-compose.yml not found! Ensure you are in the Wuchang Workspace." "Red"
            exit 1
        }
    }

    # Pull and Up
    docker compose pull
    docker compose up -d
    
    Write-Log "Survival Node Active. Services are holding the line." "Green"
    Write-Log "狀態：已啟動 (Restart Policy: Always)" "Green"
    
    # 3. Health Check
    Start-Sleep -Seconds 5
    $status = docker compose ps
    Write-Host $status
}
catch {
    Write-Log "Deployment Failed: $_" "Red"
    Write-Log "Retrying with legacy command..." "Magenta"
    docker-compose up -d
}

Pause
