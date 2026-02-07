$ErrorActionPreference = "Stop"

function Test-FileSafety {
    param($Path, $Description)
    if (-not (Test-Path $Path)) {
        Write-Error "[SAFETY FAIL] Missing $Description at $Path"
    }
    $content = Get-Content $Path -Raw
    if ([string]::IsNullOrWhiteSpace($content)) {
        Write-Error "[SAFETY FAIL] $Description is empty"
    }
    Write-Host "[SAFETY PASS] $Description verified." -ForegroundColor Green
}

function Test-DirSafety {
    param($Path, $Description)
    if (-not (Test-Path $Path)) {
        Write-Error "[SAFETY FAIL] Missing directory $Description at $Path"
    }
    $items = Get-ChildItem $Path
    if ($items.Count -eq 0) {
         Write-Warning "[SAFETY WARNING] Directory $Description is empty"
    } else {
         Write-Host "[SAFETY PASS] $Description verified ($($items.Count) items)." -ForegroundColor Green
    }
}

Write-Host "=== 1. Pre-Mount Safety Checks (容器掛載前安全檢查) ==="
try {
    Test-FileSafety "config/odoo/odoo.conf" "Odoo Config"
    Test-FileSafety "config/cloudflared/config.yml" "Cloudflare Tunnel Config"
    Test-FileSafety "config/cloudflared/credentials.json" "Tunnel Credentials"
    Test-DirSafety "wuchang_os/addons" "Wuchang Addons"

    # Check Docker Daemon
    docker info > $null
    if ($LASTEXITCODE -ne 0) { throw "Docker Daemon is not running!" }
    Write-Host "[SAFETY PASS] Docker Daemon is running." -ForegroundColor Green

} catch {
    Write-Error "Safety Check Failed: $_"
    exit 1
}

Write-Host "`n=== 2. Creating Named Volumes ==="
docker volume create wuchang-odoo-config
docker volume create wuchang-cloudflared-config
docker volume create wuchang-odoo-addons

Write-Host "`n=== 3. Syncing Configs (J: Drive -> Docker Volumes) ==="

function Sync-FileToVolume {
    param($Volume, $Source, $DestName)
    Write-Host "Syncing file $Source to $Volume..."
    $id = docker run -d -v ${Volume}:/target alpine tail -f /dev/null
    try {
        docker cp $Source "${id}:/target/${DestName}"
    } finally {
        docker rm -f $id > $null
    }
}

function Sync-DirToVolume {
    param($Volume, $Source)
    Write-Host "Syncing directory $Source to $Volume (This may take a moment)..."
    $id = docker run -d -v ${Volume}:/target alpine tail -f /dev/null
    try {
        # Clean target first to ensure sync is exact? 
        # For now, just overwrite. Docker cp handles recursive copy.
        # We copy content of Source to /target/
        # Powershell syntax for source might need to be specific.
        # If we do docker cp ./wuchang_os/addons/. id:/target/ it should work.
        docker cp "${Source}/." "${id}:/target/"
    } finally {
        docker rm -f $id > $null
    }
}

Sync-FileToVolume "wuchang-odoo-config" "./config/odoo/odoo.conf" "odoo.conf"
Sync-FileToVolume "wuchang-cloudflared-config" "./config/cloudflared/config.yml" "config.yml"
Sync-FileToVolume "wuchang-cloudflared-config" "./config/cloudflared/credentials.json" "credentials.json"
Sync-DirToVolume "wuchang-odoo-addons" "./wuchang_os/addons"

Write-Host "`n=== Sync Complete & Verified ==="
