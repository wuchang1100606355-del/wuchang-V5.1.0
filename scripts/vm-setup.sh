#! /bin/bash
# Create directories
mkdir -p /home/wuchang1100606355/app/wuchang_os/addons
mkdir -p /home/wuchang1100606355/app/config
mkdir -p /home/wuchang1100606355/app/scripts
mkdir -p /home/wuchang1100606355/app/backups
mkdir -p /home/wuchang1100606355/app/downloads
mkdir -p /home/wuchang1100606355/app/memory_store
mkdir -p /home/wuchang1100606355/scripts

# Write docker-compose.yml
cat <<'EOF' > /home/wuchang1100606355/app/docker-compose.yml
services:
  wuchang-web:
    image: odoo:15
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8069:8069"
      - "8072:8072"
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./wuchang_os/addons:/mnt/extra-addons
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    restart: always

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_USER=odoo
    volumes:
      - odoo-db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo -d postgres -h localhost"]
      interval: 5s
      timeout: 3s
      retries: 20
    restart: always

volumes:
  odoo-web-data:
  odoo-db-data:
EOF

# Write Cloud-Rebirth.sh
cat <<'EOF' > /home/wuchang1100606355/scripts/Cloud-Rebirth.sh
#!/bin/bash
BACKUP_BUCKET="wuchang-soul-backups-coffee-spark"
PROJECT_DIR="/home/wuchang1100606355/app"
cd $PROJECT_DIR
echo "--- Starting Cloud Rebirth Protocol ---"
LATEST_BACKUP=$(gsutil ls gs://$BACKUP_BUCKET/*.zip | sort | tail -n 1)
if [ -z "$LATEST_BACKUP" ]; then
    echo "Error: No backup found"
    exit 1
fi
gsutil cp $LATEST_BACKUP ./backup.zip
docker-compose up -d
echo "--- Cloud Rebirth Protocol Complete ---"
EOF

# Write Update-Dns.sh
cat <<'EOF' > /home/wuchang1100606355/scripts/Update-Dns.sh
#!/bin/bash
ZONE_NAME="wuchang-life"
RECORD_NAME="app.wuchang.life."
NEW_IP="35.221.182.184"
PROJECT_ID="coffee-spark-ai-barista-b10b5"
gcloud dns record-sets transaction start --zone=$ZONE_NAME --project=$PROJECT_ID
CURRENT_IP=$(gcloud dns record-sets list --zone=$ZONE_NAME --project=$PROJECT_ID --name=$RECORD_NAME --type=A --format="value(DATA)")
if [ ! -z "$CURRENT_IP" ]; then
    gcloud dns record-sets transaction remove --zone=$ZONE_NAME --project=$PROJECT_ID --name=$RECORD_NAME --type=A --ttl=300 "$CURRENT_IP"
fi
gcloud dns record-sets transaction add --zone=$ZONE_NAME --project=$PROJECT_ID --name=$RECORD_NAME --type=A --ttl=300 "$NEW_IP"
gcloud dns record-sets transaction execute --zone=$ZONE_NAME --project=$PROJECT_ID
EOF

# Set permissions
chmod +x /home/wuchang1100606355/scripts/*.sh
chown -R wuchang1100606355:wuchang1100606355 /home/wuchang1100606355/app
chown -R wuchang1100606355:wuchang1100606355 /home/wuchang1100606355/scripts
