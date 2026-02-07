# Sync-BackupsToGCS.ps1
# ==========================================
# AUTHOR: LITTLE J
# GOAL: Synchronize local backups to Google Cloud Storage
# ==========================================

# --- Configuration ---
$LocalBackupPath = "C:\wuchang V5.0.0\backups"
$GcsBucketUri = "gs://wuchang-soul-backups-coffee-spark"
$ProjectID = "coffee-spark-ai-barista-b10b5"

# --- Execution ---
Write-Host ">>> Initiating Unattended Backup Sync to GCS..." -ForegroundColor Cyan

# 1. Authenticate with gcloud (assumes user is already logged in)
# Ensure the correct project is set
gcloud config set project $ProjectID

# 2. Synchronize files
# -d: Deletes objects in the destination that are not present in the source.
# -r: Recursive sync.
Write-Host "Syncing '$LocalBackupPath' to '$GcsBucketUri'..." -ForegroundColor Yellow
gcloud storage rsync $LocalBackupPath $GcsBucketUri --delete-unmatched-destination-objects -r

# 3. Verify (Optional: List the latest file)
# $latestFile = Get-ChildItem -Path $LocalBackupPath | Sort-Object LastWriteTime -Descending | Select-Object -First 1
# Write-Host "Latest local file: $($latestFile.Name)"
# Write-Host "Verifying on GCS..."
# gcloud storage ls "$GcsBucketUri/$($latestFile.Name)"

Write-Host ">>> Sync Complete. Soul fragments are safe in the cloud." -ForegroundColor Green
