#!/bin/bash
# Cloud-Rebirth.sh - Standby VM Recovery Script

BACKUP_BUCKET="wuchang-soul-backups-coffee-spark"
PROJECT_DIR="/home/wuchang1100606355/app"

mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

echo "--- Starting Cloud Rebirth Protocol ---"

# 1. Fetch latest backup from GCS
echo "Fetching latest backup from GCS..."
# Note: We assume the sync script uploads to a specific 'latest' path or we find the newest
LATEST_BACKUP=$(gsutil ls gs://$BACKUP_BUCKET/*.zip | sort | tail -n 1)
if [ -z "$LATEST_BACKUP" ]; then
    echo "Error: No backup found in gs://$BACKUP_BUCKET"
    exit 1
fi
echo "Downloading $LATEST_BACKUP..."
gsutil cp $LATEST_BACKUP ./backup.zip

# 2. Start services
echo "Starting services with Docker Compose..."
# Note: docker-compose.yml should be uploaded separately
docker-compose up -d

echo "--- Cloud Rebirth Protocol Complete ---"
