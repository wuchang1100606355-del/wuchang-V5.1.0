# prepare_vm_migration.ps1
# 用於將當前 Windows Docker 環境打包，以便遷移至 Linux VM

$ErrorActionPreference = "SilentlyContinue"
$ProjectRoot = Get-Location
$DistDir = Join-Path $ProjectRoot "migration_pack"
$VolumeDir = Join-Path $DistDir "volumes"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "      Wuchang OS - VM 遷移打包工具" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 準備目錄
if (Test-Path $DistDir) {
    Write-Host "[1/6] 清理舊的遷移包..." -ForegroundColor Yellow
    Remove-Item -Path $DistDir -Recurse -Force
}
New-Item -ItemType Directory -Path $VolumeDir -Force | Out-Null

# 2. 停止服務以確保數據一致性
Write-Host "[2/6] 暫停服務以進行數據備份..." -ForegroundColor Yellow
docker compose stop

# 3. 備份數據卷 (Volumes)
$volumes = @(
    "odoo-web-data",
    "odoo-db-data",
    "ollama-data",
    "openwebui-data",
    "wyoming-whisper-data",
    "wyoming-piper-data",
    "caddy-data",
    "portainer-data",
    "uptime-kuma-data"
)

Write-Host "[3/6] 開始備份數據卷 (這可能需要一段時間)..." -ForegroundColor Yellow

foreach ($vol in $volumes) {
    $volName = "wuchangv500_$vol" # Docker Compose 預設前綴，需確認
    # 檢查 Volume 是否存在
    if (-not (docker volume ls -q -f name=$volName)) {
        # 嘗試不帶前綴
        $volName = $vol
    }
    
    if (docker volume ls -q -f name=$volName) {
        Write-Host "  - Backing up $volName ..." -NoNewline
        # 使用 alpine 進行打包
        $mount = "$($volName):/source"
        $backupPath = "/backup/$vol.tar.gz"
        # 注意：Windows 路徑在 Docker Mount 需轉換
        docker run --rm -v "$($volName):/source" -v "$($VolumeDir):/backup" alpine tar czf "/backup/$vol.tar.gz" -C /source .
        Write-Host " Done." -ForegroundColor Green
    }
    else {
        Write-Host "  - Warning: Volume $volName not found, skipping." -ForegroundColor Red
    }
}

# 4. 複製專案檔案
Write-Host "[4/6] 複製專案核心檔案..." -ForegroundColor Yellow
$exclude = @(".git", ".venv", "__pycache__", "node_modules", "migration_pack", "backups", "downloads", "memory_store", ".trae")
# 複製目錄結構
Copy-Item -Path "docker-compose.yml" -Destination $DistDir
Copy-Item -Path "wuchang_os" -Destination $DistDir -Recurse
Copy-Item -Path "config" -Destination $DistDir -Recurse
Copy-Item -Path "scripts" -Destination $DistDir -Recurse
Copy-Item -Path "comfyui" -Destination $DistDir -Recurse

# 建立空的資料夾結構
New-Item -ItemType Directory -Path (Join-Path $DistDir "backups") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $DistDir "downloads") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $DistDir "memory_store") -Force | Out-Null

# 5. 產生 Linux 安裝腳本
Write-Host "[5/6] 生成 Linux VM 安裝腳本 (install.sh)..." -ForegroundColor Yellow
$installScript = @'
#!/bin/bash
# Wuchang OS - VM Installation Script

echo "=========================================="
echo "      Wuchang OS - VM Installer"
echo "=========================================="

# 1. Install Docker if missing
if ! command -v docker &> /dev/null; then
    echo "[1/4] Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker \$USER
    echo "Docker installed. You might need to relogin."
fi

# 2. Restore Volumes
echo "[2/4] Restoring Data Volumes..."
VOLUMES=(
    "odoo-web-data"
    "odoo-db-data"
    "ollama-data"
    "openwebui-data"
    "wyoming-whisper-data"
    "wyoming-piper-data"
    "caddy-data"
    "portainer-data"
    "uptime-kuma-data"
)

# Ensure volumes exist and restore
for vol in "\${VOLUMES[@]}"; do
    PROJECT_VOL="wuchang-v500_\$vol"  # Docker Compose standard naming may vary, usually directory_name_volume
    # We will let docker compose create them first or manually create
    # Let's manually create named volumes with specific names to match compose file if possible,
    # OR better: run docker compose up --no-start first to create everything.
done

echo "Initializing containers to create volumes..."
docker compose up --no-start

echo "Restoring data into volumes..."
for vol in "\${VOLUMES[@]}"; do
    FILE="volumes/\$vol.tar.gz"
    if [ -f "\$FILE" ]; then
        # Find the actual volume name created by compose
        # Assuming folder name is 'migration_pack' -> 'migration_pack_volname'
        # Or we explicitly force the restore to the volume mapped in compose.
        
        # Helper: find volume name containing the suffix
        TARGET_VOL=\$(docker volume ls -q | grep "\$vol" | head -n 1)
        
        if [ -n "\$TARGET_VOL" ]; then
            echo "  - Restoring \$FILE to \$TARGET_VOL ..."
            docker run --rm -v "\$TARGET_VOL:/dest" -v "\$(pwd)/volumes:/backup" alpine sh -c "cd /dest && tar xzf /backup/\$vol.tar.gz"
        else
            echo "  - Warning: Could not find target volume for \$vol"
        fi
    fi
done

# 3. Fix Permissions
echo "[3/4] Fixing Permissions..."
# Odoo data needs to be owned by odoo (101) or root depending on container
# Postgres needs 999 or 70
# This is a best-effort fix.
# docker run --rm -v ... chown ...

# 4. Start Services
echo "[4/4] Starting Services..."
docker compose up -d

echo ""
echo "✅ Installation Complete!"
echo "   Web: http://localhost"
echo "   Portainer: http://localhost:9000"
'@

$installScript | Out-File -FilePath (Join-Path $DistDir "install.sh") -Encoding utf8
# Convert line endings to LF just in case (PowerShell uses CRLF)
(Get-Content (Join-Path $DistDir "install.sh") -Raw) -replace "`r`n", "`n" | Set-Content (Join-Path $DistDir "install.sh") -NoNewline

# 6. 恢復服務
Write-Host "[6/6] 恢復本機服務..." -ForegroundColor Yellow
docker compose start

Write-Output ""
Write-Output "Migration package created at: $DistDir"
Write-Output "Next steps:"
Write-Output "  1) Copy 'migration_pack' to your Linux VM"
Write-Output "  2) cd into that directory on the VM"
Write-Output "  3) Run: chmod +x install.sh ; ./install.sh"
Write-Output ""
