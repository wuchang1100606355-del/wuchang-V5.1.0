# 1. 設定變數
$PROJECT_ID = "coffee-spark-ai-barista-b10b5" # Updated per Resource Topology
$ZONE = "asia-east1-b" # 建議選台灣機房 (彰化)
$VM_NAME = "odoo-server-main"
$IP_NAME = "wuchang-odoo-static-ip"
$DOMAIN = "wuchang.life"

Write-Host "正在設定專案: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# 2. 保留靜態外部 IP
Write-Host "檢查靜態 IP: $IP_NAME"
$ipExists = gcloud compute addresses list --filter="name=('$IP_NAME')" --format="get(name)"
if (-not $ipExists) {
    Write-Host "正在建立靜態 IP..."
    gcloud compute addresses create $IP_NAME --region=asia-east1
} else {
    Write-Host "IP $IP_NAME 已存在。"
}

# 3. 獲取剛剛申請的 IP
$STATIC_IP = gcloud compute addresses describe $IP_NAME --region=asia-east1 --format='get(address)'
Write-Host "您的靜態 IP 是: $STATIC_IP"

# 4. 建立 VM 實例
Write-Host "檢查 VM 實例: $VM_NAME"
$vmExists = gcloud compute instances list --filter="name=('$VM_NAME')" --format="get(name)"
if (-not $vmExists) {
    Write-Host "正在建立 VM 實例 (這可能需要幾分鐘)..."
    gcloud compute instances create $VM_NAME `
        --zone=$ZONE `
        --machine-type=e2-standard-2 `
        --image-family=ubuntu-2204-lts `
        --image-project=ubuntu-os-cloud `
        --address=$STATIC_IP `
        --tags=http-server,https-server `
        --scopes=https://www.googleapis.com/auth/cloud-platform `
        --boot-disk-size=50GB `
        --boot-disk-type=pd-ssd
    
    Write-Host "VM 建立完成。"
    Write-Host "請務必前往 DNS 管理介面將 $DOMAIN 的 A 記錄指向 $STATIC_IP"
} else {
    Write-Host "VM $VM_NAME 已存在。"
    $CURRENT_IP = gcloud compute instances describe $VM_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
    Write-Host "VM 目前的 IP 為: $CURRENT_IP"
}
