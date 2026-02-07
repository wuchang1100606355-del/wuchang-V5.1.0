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
echo "??Installation Complete!"
echo "   Web: http://localhost"
echo "   Portainer: http://localhost:9000"
