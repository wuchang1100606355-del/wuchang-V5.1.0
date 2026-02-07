#!/bin/bash
# ==============================================================================
# Architecture Level Deployment: Unified Store/Workspace/Router
# Domain: logecoffee.com
# Identity: boss@logecoffee.com (Google Workspace)
# Network: Hard Binding (MAC <-> IP <-> DNS) required on Router (192.168.50.1)
# ==============================================================================

# 1. System Prep & Docker
apt-get update
apt-get install -y ca-certificates curl gnupg lsb-release
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 2. Network Integration (Tailscale)
# Ensure this node is part of the "Hard Binding" architecture
curl -fsSL https://tailscale.com/install.sh | sh
# tailscale up --authkey=tskey-auth-YOUR_KEY_HERE --accept-routes --hostname=wuchang-shop-vm

# 3. Odoo Deployment (Unified Workspace Hub)
mkdir -p /opt/wuchang-odoo
cd /opt/wuchang-odoo
cat <<EOF > docker-compose.yml
version: "3.1"
services:
  web:
    image: odoo:16.0
    restart: always
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - odoo-web-data:/var/lib/odoo
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
      # Google Workspace SMTP/Auth integration placeholders
      # - SMTP_SERVER=smtp.gmail.com
      # - SMTP_PORT=587
      # - SMTP_USER=boss@logecoffee.com
      # - SMTP_PASSWORD=poiuY926_APP_PASSWORD_HERE
  db:
    image: postgres:15
    restart: always
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_USER=odoo
    volumes:
      - odoo-db-data:/var/lib/postgresql/data

volumes:
  odoo-web-data:
  odoo-db-data:
EOF

docker compose up -d

