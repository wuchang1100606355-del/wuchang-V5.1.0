#!/bin/bash
# Update-Dns.sh - DNS Failover Script

ZONE_NAME="wuchang-life"
RECORD_NAME="app.wuchang.life."
NEW_IP="35.221.182.184"
PROJECT_ID="coffee-spark-ai-barista-b10b5"

echo "--- Starting DNS Failover to $NEW_IP ---"

# Create a transaction to update the record
gcloud dns record-sets transaction start --zone=$ZONE_NAME --project=$PROJECT_ID

# Get current IP (to delete it)
CURRENT_IP=$(gcloud dns record-sets list --zone=$ZONE_NAME --project=$PROJECT_ID --name=$RECORD_NAME --type=A --format="value(DATA)")

if [ ! -z "$CURRENT_IP" ]; then
    echo "Removing old record pointing to $CURRENT_IP..."
    gcloud dns record-sets transaction remove --zone=$ZONE_NAME --project=$PROJECT_ID --name=$RECORD_NAME --type=A --ttl=300 "$CURRENT_IP"
fi

echo "Adding new record pointing to $NEW_IP..."
gcloud dns record-sets transaction add --zone=$ZONE_NAME --project=$PROJECT_ID --name=$RECORD_NAME --type=A --ttl=300 "$NEW_IP"

echo "Executing transaction..."
gcloud dns record-sets transaction execute --zone=$ZONE_NAME --project=$PROJECT_ID

echo "--- DNS Failover Complete ---"
