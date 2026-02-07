# 五常 AI 系統 - 跨域遷移實施方案 v1.0

**目標**：將 Wuchang V5.1.0 完整遷移至區網伺服器(192.168.50.249)，實現本機與伺服器雙向讀寫

**生成時間**：2026-01-10  
**系統版本**：Wuchang V5.1.0  
**當前環境**：本機(192.168.50.84) → 伺服器(192.168.50.249)

---

## 🎯 遷移目標架構

```
┌─────────────────────────────────────┬─────────────────────────────────────┐
│        本機 (192.168.50.84)         │     伺服器 (192.168.50.249)        │
├─────────────────────────────────────┼─────────────────────────────────────┤
│                                     │                                     │
│  VS Code IDE                        │  Docker容器運行環境                 │
│  開發工作區                          │  - Odoo 17.0                       │
│  本地Git倉庫                         │  - PostgreSQL 15                   │
│                                     │  - Caddy 2 (反向代理)              │
│  NFS客戶端 ◄──────────────────────► │  NFS伺服器                         │
│  同步客戶端                          │  同步伺服器 (主節點)                │
│                                     │                                     │
│  外網訪問入口                        │  區網服務托管                       │
│  (Cloudflare隧道)                   │  存儲層(硬碟權限)                   │
│                                     │                                     │
└─────────────────────────────────────┴─────────────────────────────────────┘
```

---

## 📋 完整實施計劃

### 第一階段：準備階段 (2 小時)

#### 1.1 伺服器環境準備

**目標**：在 192.168.50.249 上安裝必要的軟件

```bash
# SSH登入伺服器
ssh admin@192.168.50.249

# 更新系統
sudo apt update && sudo apt upgrade -y

# 安裝Docker和Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install -y docker-compose

# 安裝NFS伺服器
sudo apt install -y nfs-kernel-server

# 安裝rsync用於同步
sudo apt install -y rsync openssh-server

# 安裝Python和依賴
sudo apt install -y python3.10 python3-pip git

# 驗證安裝
docker --version
docker-compose --version
exportfs -v
```

#### 1.2 本機準備

**在本機執行**：

```powershell
# 檢查SSH連接
ssh -i "C:\path\to\key" admin@192.168.50.249 "echo 'Connection OK'"

# 安裝NFS客戶端(Windows)
# 方案1: 使用WSL2或Cygwin
# 方案2: 使用Samba協議代替NFS

# 安裝Rsync(Windows)
# 通過Git Bash或WSL2使用

# 創建本地同步目錄
New-Item -ItemType Directory -Path "C:\wuchang-server-sync" -Force
```

---

### 第二階段：配置網絡存儲 (3 小時)

#### 2.1 配置 NFS 共享(伺服器端)

**在伺服器上執行**：

```bash
# 創建共享目錄
sudo mkdir -p /mnt/wuchang-storage/odoo-data
sudo mkdir -p /mnt/wuchang-storage/ai-memory
sudo mkdir -p /mnt/wuchang-storage/ai-common
sudo mkdir -p /mnt/wuchang-storage/backups
sudo mkdir -p /mnt/wuchang-storage/docker-volumes

# 設置權限
sudo chown -R 1000:1000 /mnt/wuchang-storage
sudo chmod -R 775 /mnt/wuchang-storage

# 編輯NFS導出配置
sudo nano /etc/exports

# 添加以下行:
/mnt/wuchang-storage 192.168.50.84/32(rw,sync,no_subtree_check,no_root_squash)
/mnt/wuchang-storage 192.168.50.0/24(rw,sync,no_subtree_check)

# 重新加載NFS配置
sudo exportfs -ra

# 驗證NFS設定
exportfs -v
```

#### 2.2 配置 Samba 共享(替代方案或補充)

```bash
# 安裝Samba
sudo apt install -y samba samba-common-bin

# 編輯Samba配置
sudo nano /etc/samba/smb.conf

# 在文件末尾添加:
[wuchang-storage]
  path = /mnt/wuchang-storage
  browsable = yes
  read only = no
  guest ok = yes
  force user = wuchang
  force group = wuchang
  comment = Wuchang Shared Storage

# 設置Samba用戶
sudo useradd -m -s /bin/false wuchang
sudo smbpasswd -a wuchang
# 輸入密碼: 與Unix用戶密碼相同

# 重啟Samba
sudo systemctl restart smbd
```

#### 2.3 在本機掛載共享(Windows)

**方案 1：使用 SMB(推薦 Windows)**

```powershell
# 掛載Samba共享
$credential = Get-Credential -UserName wuchang

New-PSDrive -Name "Z" `
    -PSProvider FileSystem `
    -Root "\\192.168.50.249\wuchang-storage" `
    -Credential $credential `
    -Persist

# 驗證掛載
Get-PSDrive Z

# 測試讀寫
Set-Content "Z:\test-$(Get-Date -Format 'yyyyMMdd_HHmmss').txt" "Test from local"
```

**方案 2：使用 WSL2 中的 NFS(高性能)**

```bash
# 在WSL2中
sudo mkdir -p /mnt/wuchang-server

# 掛載NFS
sudo mount -t nfs -o vers=4,loud 192.168.50.249:/mnt/wuchang-storage /mnt/wuchang-server

# 驗證
df -h | grep wuchang-server

# 永久掛載(編輯/etc/fstab)
# 192.168.50.249:/mnt/wuchang-storage /mnt/wuchang-server nfs vers=4,defaults 0 0
```

---

### 第三階段：遷移 Docker 數據 (2 小時)

#### 3.1 備份本機 Docker 數據

```powershell
# 備份所有相關Docker卷
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "C:\wuchang V5.1.0\backups\docker_migration_$timestamp"

New-Item -ItemType Directory -Path $backupDir -Force

# 導出Odoo數據庫
docker exec wuchangv510-db-1 pg_dump -U odoo admin | `
    Out-File "$backupDir\odoo_database_$timestamp.sql"

# 停止容器
docker-compose -f "C:\wuchang V5.1.0\docker-compose.yml" down

# 複製Docker卷數據
docker run --rm `
    -v wuchangv510_odoo-db-data:/data `
    -v "$($backupDir):/backup" `
    alpine tar czf /backup/odoo-db-data.tar.gz -C /data .

docker run --rm `
    -v wuchangv510_odoo-web-data:/data `
    -v "$($backupDir):/backup" `
    alpine tar czf /backup/odoo-web-data.tar.gz -C /data .
```

#### 3.2 傳輸數據至伺服器

```powershell
# 使用rsync或SCP傳輸(通過WSL2)
# PowerShell方案：
$sshKey = "C:\path\to\ssh-key"
$remoteServer = "admin@192.168.50.249"
$localBackup = "C:\wuchang V5.1.0\backups"

# 使用WinSCP或SFTP
# 或透過WSL2：
wsl rsync -avz -e "ssh -i /mnt/c/path/to/key" `
    "/mnt/c/wuchang V5.1.0/backups/" `
    "admin@192.168.50.249:/mnt/wuchang-storage/backups/"
```

#### 3.3 在伺服器上恢復 Docker 卷

```bash
# 在伺服器上
cd /mnt/wuchang-storage/docker-volumes

# 解提tarball
tar xzf /mnt/wuchang-storage/backups/odoo-db-data.tar.gz -C ./odoo-db-data/
tar xzf /mnt/wuchang-storage/backups/odoo-web-data.tar.gz -C ./odoo-web-data/

# 恢復數據庫
docker-compose up db -d
sleep 10
docker exec wuchangv510-db-1 psql -U odoo < /mnt/wuchang-storage/backups/odoo_database.sql

# 驗證數據
docker exec wuchangv510-db-1 psql -U odoo -d admin -c "SELECT * FROM ir_module_module LIMIT 5;"
```

---

### 第四階段：配置伺服器 Docker Compose (2 小時)

#### 4.1 準備 docker-compose.yml

**在伺服器上創建** `/home/admin/docker-compose.yml`：

```yaml
version: "3.8"

services:
    wuchang-web:
        image: odoo:17.0
        depends_on:
            - db
        ports:
            - "8069:8069"
            - "8072:8072"
        volumes:
            - /mnt/wuchang-storage/docker-volumes/odoo-web-data:/var/lib/odoo
            - /home/admin/wuchang_os/addons:/mnt/extra-addons
            - /mnt/wuchang-storage/downloads:/mnt/jules:rw
            - /home/admin/wuchang_os/config:/mnt/jules-config:ro
            - /mnt/wuchang-storage/ai-memory/memory_store:/opt/wuchang/memory_store
            - /mnt/wuchang-storage/ai-common/common_store:/opt/wuchang/common_store
        command: odoo -d admin --db_host=db --db_user=odoo --db_password=odoo --proxy-mode --longpolling-port=8072
        environment:
            - HOST=db
            - USER=odoo
            - PASSWORD=odoo
            - GOOGLE_APPLICATION_CREDENTIALS=/mnt/jules-config/gcp/littlej-sa.json
        restart: unless-stopped
        networks:
            - wuchang-net
        healthcheck:
            test: ["CMD", "curl", "-f", "http://localhost:8069"]
            interval: 30s
            timeout: 10s
            retries: 3

    db:
        image: postgres:15
        environment:
            - POSTGRES_DB=admin
            - POSTGRES_PASSWORD=odoo
            - POSTGRES_USER=odoo
        volumes:
            - /mnt/wuchang-storage/docker-volumes/odoo-db-data:/var/lib/postgresql/data
        ports:
            - "5432:5432"
        restart: unless-stopped
        networks:
            - wuchang-net
        healthcheck:
            test: ["CMD-SHELL", "pg_isready -U odoo"]
            interval: 10s
            timeout: 5s
            retries: 5

    caddy:
        image: caddy:2
        depends_on:
            - wuchang-web
        ports:
            - "80:80"
            - "443:443"
        volumes:
            - /home/admin/wuchang_os/Caddyfile:/etc/caddy/Caddyfile
            - /mnt/wuchang-storage/docker-volumes/caddy-data:/data
        restart: unless-stopped
        networks:
            - wuchang-net

    portainer:
        image: portainer/portainer-ce:latest
        ports:
            - "9000:9000"
        volumes:
            - /var/run/docker.sock:/var/run/docker.sock
            - /mnt/wuchang-storage/docker-volumes/portainer-data:/data
        restart: unless-stopped
        networks:
            - wuchang-net

networks:
    wuchang-net:
        driver: bridge
```

#### 4.2 啟動伺服器容器

```bash
# 在伺服器上
cd /home/admin
docker-compose up -d

# 驗證容器狀態
docker-compose ps
docker-compose logs -f wuchang-web
```

---

### 第五階段：配置雙向同步 (3 小時)

#### 5.1 配置 Rsync 同步機制

**在伺服器上配置 rsync 守護程式**:

```bash
# 編輯/etc/rsyncd.conf
sudo nano /etc/rsyncd.conf

# 添加以下配置:
[wuchang-storage]
  path = /mnt/wuchang-storage
  comment = Wuchang Storage Sync
  uid = 1000
  gid = 1000
  read only = false
  list = true
  auth users = wuchang
  secrets file = /etc/rsyncd.secrets

[odoo-addons]
  path = /home/admin/wuchang_os/addons
  comment = Wuchang Odoo Addons
  uid = 1000
  gid = 1000
  read only = false
  list = true
  auth users = wuchang
  secrets file = /etc/rsyncd.secrets

# 創建密碼文件
echo "wuchang:password123" | sudo tee /etc/rsyncd.secrets
sudo chmod 600 /etc/rsyncd.secrets

# 啟動rsync守護程式
sudo systemctl enable rsync
sudo systemctl start rsync
```

#### 5.2 在本機配置 Rsync 客戶端同步

**PowerShell 同步腳本** (`C:\wuchang V5.1.0\sync_with_server.ps1`)：

```powershell
# 同步配置
$serverAddr = "192.168.50.249"
$serverUser = "wuchang"
$serverPassword = "password123"
$localPath = "C:\wuchang V5.1.0"
$syncDirs = @(
    "wuchang_os\addons",
    "config",
    "downloads\jules",
    "memory_store",
    "scripts"
)

function Sync-ToServer {
    Write-Host "同步本機更改至伺服器..." -ForegroundColor Green

    foreach ($dir in $syncDirs) {
        $localDir = Join-Path $localPath $dir
        $remoteDir = "rsync://$($serverUser)@$serverAddr/odoo-addons/$dir"

        if (Test-Path $localDir) {
            # 使用WSL2的rsync
            wsl rsync -avz --delete `
                "/mnt/c/wuchang V5.1.0/$dir/" `
                "wuchang@192.168.50.249::odoo-addons/$dir/"

            Write-Host "✓ 已同步: $dir" -ForegroundColor Cyan
        }
    }
}

function Sync-FromServer {
    Write-Host "同步伺服器更改至本機..." -ForegroundColor Green

    foreach ($dir in $syncDirs) {
        $localDir = Join-Path $localPath $dir

        # 使用WSL2的rsync
        wsl rsync -avz --delete `
            "wuchang@192.168.50.249::odoo-addons/$dir/" `
            "/mnt/c/wuchang V5.1.0/$dir/"

        Write-Host "✓ 已同步: $dir" -ForegroundColor Cyan
    }
}

function Start-ContinuousSync {
    Write-Host "啟動連續同步監視器..." -ForegroundColor Yellow

    while ($true) {
        Sync-ToServer
        Start-Sleep -Seconds 300  # 每5分鐘同步一次
    }
}

# 執行同步
if ($args[0] -eq "push") {
    Sync-ToServer
} elseif ($args[0] -eq "pull") {
    Sync-FromServer
} elseif ($args[0] -eq "watch") {
    Start-ContinuousSync
} else {
    Write-Host "用法: .\sync_with_server.ps1 [push|pull|watch]"
}
```

#### 5.3 配置 Git 同步

```bash
# 在伺服器上
cd /home/admin
git clone https://github.com/wuchang1100606355-del/wuchang-V5.1.0.git
cd wuchang-V5.1.0
git remote add local ssh://local-user@192.168.50.84/C:/wuchang\ V5.1.0/.git

# 配置Git Hook自動更新
cat > /home/admin/wuchang-V5.1.0/.git/hooks/post-receive << 'EOF'
#!/bin/bash
cd /home/admin/wuchang-V5.1.0
git reset --hard HEAD
echo "伺服器代碼已更新"
EOF

chmod +x /home/admin/wuchang-V5.1.0/.git/hooks/post-receive
```

---

### 第六階段：設置網絡訪問 (2 小時)

#### 6.1 配置反向代理(Caddy)

**編輯** `/home/admin/wuchang_os/Caddyfile`：

```caddyfile
# 區網訪問
192.168.50.249, *.local {
    reverse_proxy localhost:8069 {
        header_up X-Forwarded-For {http.request.remote.host}
        header_up X-Forwarded-Proto {http.request.proto}
    }
}

# 外網訪問(可選，需Cloudflare設定)
yourdomain.com {
    reverse_proxy localhost:8069 {
        header_up X-Forwarded-For {http.request.remote.host}
        header_up X-Forwarded-Proto {http.request.proto}
    }
}

# Portainer管理界面
admin.local:9000 {
    reverse_proxy localhost:9000
}
```

#### 6.2 配置防火牆規則

```bash
# 在伺服器上
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow 8069/tcp    # Odoo
sudo ufw allow 9000/tcp    # Portainer
sudo ufw allow 3306/tcp    # MySQL(如需)
sudo ufw allow 5432/tcp    # PostgreSQL
sudo ufw allow 2049/tcp    # NFS
sudo ufw allow 445/tcp     # Samba
sudo ufw allow 139/tcp     # Samba

sudo ufw enable
```

#### 6.3 配置 DNS 解析

**在本機 hosts 文件配置** (`C:\Windows\System32\drivers\etc\hosts`)：

```
192.168.50.249    wuchang.local
192.168.50.249    admin.local
192.168.50.249    odoo.local
192.168.50.249    storage.local
```

**在伺服器配置** (`/etc/hosts`)：

```
192.168.50.84     local-machine
192.168.50.249    server
127.0.0.1         localhost
```

---

### 第七階段：配置權限系統 (2 小時)

#### 7.1 Linux 文件權限

```bash
# 在伺服器上配置權限
sudo chown -R 1000:1000 /mnt/wuchang-storage
sudo chmod -R 755 /mnt/wuchang-storage
sudo chmod -R 775 /mnt/wuchang-storage/docker-volumes

# 設置ACL(高級權限)
sudo apt install -y acl

sudo setfacl -R -m u:wuchang:rwx /mnt/wuchang-storage
sudo setfacl -R -m u:1000:rwx /mnt/wuchang-storage
sudo setfacl -R -d -m u:wuchang:rwx /mnt/wuchang-storage
```

#### 7.2 Odoo 內部權限

**在 Odoo 中配置**：

1. 登入 Odoo 管理帳戶
2. 進入`設定 → 使用者與公司 → 使用者`
3. 為本機用戶添加權限組
4. 配置記錄級別訪問控制(RLS)

#### 7.3 應用級別訪問控制

```python
# 創建文件: /home/admin/wuchang_os/access_control.py
import os
from datetime import datetime

class AccessControl:
    def __init__(self):
        self.log_file = "/mnt/wuchang-storage/access.log"
        self.permissions = {
            "192.168.50.84": ["read", "write", "sync"],
            "192.168.50.249": ["read", "write", "admin"]
        }

    def check_access(self, client_ip, action):
        """檢查客戶端訪問權限"""
        if client_ip not in self.permissions:
            return False

        if action not in self.permissions[client_ip]:
            return False

        self.log_access(client_ip, action)
        return True

    def log_access(self, client_ip, action):
        """記錄訪問"""
        with open(self.log_file, 'a') as f:
            f.write(f"{datetime.now()} - {client_ip} - {action}\n")

# 在Odoo中使用
access = AccessControl()
```

---

### 第八階段：測試與驗證 (2 小時)

#### 8.1 網絡連接測試

```powershell
# 在本機測試
# 1. 測試SSH連接
ssh admin@192.168.50.249 "echo 'SSH OK'"

# 2. 測試SMB共享
Test-Path "\\192.168.50.249\wuchang-storage"

# 3. 測試HTTP訪問
Invoke-WebRequest -Uri "http://192.168.50.249:8069"

# 4. 測試Odoo API
$response = Invoke-RestMethod -Uri "http://192.168.50.249:8069/api" -Method Get
$response | Format-Table
```

#### 8.2 讀寫測試

```powershell
# 測試本機寫入
$testFile = "Z:\test_$(Get-Random).txt"
Set-Content -Path $testFile -Value "本機寫入測試 $(Get-Date)"

# 測試伺服器讀取
ssh admin@192.168.50.249 "cat /mnt/wuchang-storage/test_*.txt"

# 測試伺服器寫入
ssh admin@192.168.50.249 "echo '伺服器寫入測試' > /mnt/wuchang-storage/server_test.txt"

# 測試本機讀取
Get-Content "Z:\server_test.txt"
```

#### 8.3 同步測試

```bash
# 在本機測試同步
.\sync_with_server.ps1 push

# 驗證文件同步
ssh admin@192.168.50.249 "ls -la /mnt/wuchang-storage/"
```

#### 8.4 應用功能測試

```bash
# 在伺服器上
docker-compose logs -f wuchang-web

# 檢查Odoo健康狀態
curl http://localhost:8069/health

# 檢查數據庫連接
docker exec wuchangv510-db-1 psql -U odoo -d admin -c "SELECT COUNT(*) FROM ir_module_module;"
```

---

## 📊 系統架構驗證清單

-   [ ] 伺服器 SSH 連接可用
-   [ ] NFS/Samba 共享配置完成
-   [ ] Docker 容器在伺服器上運行
-   [ ] 數據庫成功遷移並恢復
-   [ ] Odoo 應用正常運作
-   [ ] 本機可掛載伺服器存儲
-   [ ] 同步機制運行正常
-   [ ] 本機可讀寫伺服器文件
-   [ ] 伺服器可讀寫本機文件(通過 VPN/SSH)
-   [ ] 外網訪問正常
-   [ ] 權限控制生效

---

## 🔐 安全建議

1. **SSH 密鑰認證**

```bash
# 生成SSH密鑰對
ssh-keygen -t rsa -b 4096 -f ~/.ssh/wuchang_key

# 上傳公鑰到伺服器
ssh-copy-id -i ~/.ssh/wuchang_key.pub admin@192.168.50.249
```

2. **防火牆配置**

    - 限制 SSH 訪問
    - 啟用 UFW 防火牆
    - 設置 IP 白名單

3. **加密傳輸**

    - 使用 HTTPS 而非 HTTP
    - 啟用 TLS 1.3
    - 定期更新 SSL 證書

4. **備份策略**
    - 自動每日備份
    - 備份加密存儲
    - 異地備份(可選)

---

## ⏱️ 預計時間表

| 階段     | 任務        | 預計時間    |
| -------- | ----------- | ----------- |
| 1        | 準備環境    | 2 小時      |
| 2        | 配置存儲    | 3 小時      |
| 3        | 遷移數據    | 2 小時      |
| 4        | Docker 配置 | 2 小時      |
| 5        | 配置同步    | 3 小時      |
| 6        | 網絡訪問    | 2 小時      |
| 7        | 權限系統    | 2 小時      |
| 8        | 測試驗證    | 2 小時      |
| **總計** |             | **18 小時** |

---

## 📞 支援與故障排除

### 常見問題

**Q: NFS 掛載失敗**

```bash
# 檢查NFS服務
sudo systemctl status nfs-kernel-server
sudo exportfs -v

# 重新掛載
sudo umount /mnt/wuchang-server
sudo mount -t nfs -o vers=4,loud 192.168.50.249:/mnt/wuchang-storage /mnt/wuchang-server
```

**Q: Docker 容器無法啟動**

```bash
# 查看日誌
docker-compose logs wuchang-web

# 檢查卷掛載
docker inspect wuchangv510-wuchang-web-1 | grep -A 10 Mounts
```

**Q: 同步延遲**

```bash
# 檢查rsync進程
ps aux | grep rsync

# 手動同步
rsync -avz --delete admin@192.168.50.249:/mnt/wuchang-storage/ /local/path/
```

---

**報告生成者**：小 j (GitHub Copilot)  
**狀態**：✅ 計劃完整，準備執行  
**最後更新**：2026-01-10
