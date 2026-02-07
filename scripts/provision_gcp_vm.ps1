Param(
  [string]$PROJECT_ID = "coffee-spark-ai-barista-b10b5",
  [string]$ZONE = "us-central1-a",
  [ValidateSet('system','ui')][string]$ROLE = 'system'
)

$DOMAIN = "wuchang.life"
if ($ROLE -eq 'system') {
  $VM_NAME = "vm-system-us"
  $IP_NAME = "ip-system-us"
  $MACHINE = "e2-standard-4"
  $BOOT_SIZE = "200GB"
}
else {
  $VM_NAME = "vm-ui-ai-hub"
  $IP_NAME = "ip-ui-ai-hub"
  $MACHINE = "e2-standard-8"
  $BOOT_SIZE = "150GB"
}
$RANDOM_ID = Get-Random
$TEMP_ZIP = "$env:TEMP\wuchang_project_$RANDOM_ID.zip"

Write-Host "正在設定專案: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# 2. 保留靜態外部 IP
Write-Host "檢查靜態 IP: $IP_NAME"
$ipCheck = gcloud compute addresses list --filter="name=$IP_NAME AND region:us-central1" --format="value(name)"
if (-not $ipCheck) {
    Write-Host "正在建立靜態 IP..."
    gcloud compute addresses create $IP_NAME --region=us-central1
} else {
    Write-Host "IP $IP_NAME 已存在。"
}

# 3. 獲取剛剛申請的 IP
$STATIC_IP = gcloud compute addresses describe $IP_NAME --region=us-central1 --format='value(address)'
Write-Host "您的靜態 IP 是: $STATIC_IP"

# 4. 建立 VM 實例
Write-Host "檢查 VM 實例: $VM_NAME"
$vmCheck = gcloud compute instances list --filter="name=$VM_NAME AND zone:$ZONE" --format="value(name)"
if (-not $vmCheck) {
    Write-Host "正在建立 VM 實例 (這可能需要幾分鐘)..."
    gcloud compute instances create $VM_NAME `
        --zone=$ZONE `
        --machine-type=$MACHINE `
        --image-family=ubuntu-2204-lts `
        --image-project=ubuntu-os-cloud `
        --address=$STATIC_IP `
        --tags=http-server,https-server `
        --scopes=https://www.googleapis.com/auth/cloud-platform `
        --boot-disk-size=$BOOT_SIZE `
        --boot-disk-type=pd-ssd `
        --metadata=startup-script='#!/bin/bash
apt-get update -y
apt-get install -y ca-certificates curl gnupg lsb-release nfs-common
curl -fsSL https://get.docker.com | sh
systemctl enable docker
mkdir -p /opt/wuchang
'
    
    Write-Host "VM 建立完成。"
    Write-Host "請務必前往 DNS 管理介面將 $DOMAIN 的 A 記錄指向 $STATIC_IP"
    Write-Host "VM 規格: $MACHINE, Disk: $BOOT_SIZE, Role: $ROLE"
} else {
    Write-Host "VM $VM_NAME 已存在。"
    $CURRENT_IP = gcloud compute instances describe $VM_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
    Write-Host "VM 目前的 IP 為: $CURRENT_IP"
}

if ($ROLE -eq 'ui') {
  Write-Host "正在打包並上傳專案..."
  $zip = $TEMP_ZIP
  Compress-Archive -Path 'C:\wuchang V5.1.0\*' -DestinationPath $zip -Force
  gcloud compute scp $zip "$VM_NAME`:~/wuchang_project.zip" --zone=$ZONE
  Write-Host "正在解壓與啟動 UI 服務..."
  gcloud compute ssh $VM_NAME --zone=$ZONE --command "mkdir -p ~/app && mv ~/wuchang_project.zip ~/app/ && cd ~/app && unzip -o wuchang_project.zip && docker compose --profile ui up -d"
  gcloud compute ssh $VM_NAME --zone=$ZONE --command "cd ~/app && docker compose --profile ui exec -T ollama ollama pull llama3.2"
  Write-Host "UI 服務已啟動。請檢查健康狀態與 DNS 指向。"
}

if ($ROLE -eq 'system') {
  Write-Host "正在打包並上傳專案..."
  $zip = $TEMP_ZIP
  Compress-Archive -Path 'C:\wuchang V5.1.0\*' -DestinationPath $zip -Force
  gcloud compute scp $zip "$VM_NAME`:~/wuchang_project.zip" --zone=$ZONE
  Write-Host "正在解壓與啟動 System 服務..."
  gcloud compute ssh $VM_NAME --zone=$ZONE --command "mkdir -p ~/app && mv ~/wuchang_project.zip ~/app/ && cd ~/app && unzip -o wuchang_project.zip && docker compose --profile system up -d"
  Write-Host "System 服務已啟動。請檢查健康狀態與隧道路由。"
}
