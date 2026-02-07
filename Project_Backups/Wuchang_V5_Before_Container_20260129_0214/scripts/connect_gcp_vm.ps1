# 設定變數
$PROJECT_ID = "coffee-spark-ai-barista-b10b5"
$ZONE = "us-central1-a"
$VM_NAME = "odoo-server-main"

# 設定專案
Write-Host "正在設定專案: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# 正式連線指令
Write-Host "正在連線到 VM: $VM_NAME ($ZONE)..."
gcloud compute ssh $VM_NAME --zone=$ZONE
