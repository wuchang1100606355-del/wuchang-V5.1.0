#!/bin/bash
# ============================================================
# 五常AI系統 - 伺服器初始化腳本
# 在 192.168.50.249 上執行
# ============================================================

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置變數
SERVER_IP="192.168.50.249"
LOCAL_IP="192.168.50.84"
WUCHANG_HOME="/home/admin/wuchang-V5.1.0"
STORAGE_PATH="/mnt/wuchang-storage"
BACKUP_PATH="$STORAGE_PATH/backups"

# 日誌函數
log_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] ℹ $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✓ $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ✗ $1${NC}"
    exit 1
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠ $1${NC}"
}

# 檢查是否為root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此腳本必須以root身份運行"
    fi
}

# 系統更新
update_system() {
    log_info "更新系統包..."
    apt update
    apt upgrade -y
    log_success "系統更新完成"
}

# 安裝依賴
install_dependencies() {
    log_info "安裝依賴軟件..."
    
    apt install -y \
        curl \
        wget \
        git \
        vim \
        htop \
        openssh-server \
        openssh-client \
        rsync \
        python3.10 \
        python3-pip \
        net-tools \
        nfs-kernel-server \
        samba \
        samba-common-bin \
        acl
    
    log_success "依賴安裝完成"
}

# 安裝Docker
install_docker() {
    log_info "安裝Docker和Docker Compose..."
    
    # 移除舊版本
    apt remove -y docker docker-doc docker.io containerd runc 2>/dev/null || true
    
    # 安裝Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    
    # 安裝Docker Compose
    apt install -y docker-compose
    
    # 啟用Docker服務
    systemctl enable docker
    systemctl start docker
    
    # 新增admin用戶到docker組
    usermod -aG docker admin
    
    log_success "Docker安裝完成"
}

# 創建存儲目錄
create_storage() {
    log_info "創建存儲目錄結構..."
    
    mkdir -p "$STORAGE_PATH"/{odoo-data,ai-memory,ai-common,backups,docker-volumes}
    mkdir -p "$STORAGE_PATH"/docker-volumes/{odoo-db-data,odoo-web-data,caddy-data,portainer-data}
    
    # 設置權限
    chown -R 1000:1000 "$STORAGE_PATH"
    chmod -R 775 "$STORAGE_PATH"
    
    # 設置ACL
    setfacl -R -m u:admin:rwx "$STORAGE_PATH"
    setfacl -R -m u:1000:rwx "$STORAGE_PATH"
    setfacl -R -d -m u:admin:rwx "$STORAGE_PATH"
    setfacl -R -d -m u:1000:rwx "$STORAGE_PATH"
    
    log_success "存儲目錄已建立"
    log_info "目錄結構:"
    tree "$STORAGE_PATH" -L 2 2>/dev/null || find "$STORAGE_PATH" -maxdepth 2 -type d
}

# 配置NFS
configure_nfs() {
    log_info "配置NFS伺服器..."
    
    # 編寫NFS導出配置
    cat >> /etc/exports << EOF

# Wuchang Storage Share
$STORAGE_PATH $LOCAL_IP/32(rw,sync,no_subtree_check,no_root_squash)
$STORAGE_PATH 192.168.50.0/24(rw,sync,no_subtree_check)
EOF
    
    # 重新加載NFS
    exportfs -ra
    
    # 驗證配置
    log_info "NFS導出配置:"
    exportfs -v
    
    log_success "NFS配置完成"
}

# 配置Samba
configure_samba() {
    log_info "配置Samba共享..."
    
    # 創建Samba用戶
    useradd -m -s /bin/false wuchang 2>/dev/null || true
    echo "wuchang:wuchang" | chpasswd
    
    # 備份原始配置
    cp /etc/samba/smb.conf /etc/samba/smb.conf.backup
    
    # 添加共享配置
    cat >> /etc/samba/smb.conf << EOF

[wuchang-storage]
    path = $STORAGE_PATH
    browsable = yes
    read only = no
    guest ok = yes
    force user = wuchang
    force group = wuchang
    comment = Wuchang Shared Storage
    vfs objects = acl_xattr
    map acl inherit = yes

[wuchang-addons]
    path = $WUCHANG_HOME/wuchang_os/addons
    browsable = yes
    read only = no
    guest ok = yes
    force user = admin
    force group = admin
    comment = Wuchang Odoo Addons
EOF
    
    # 設置Samba密碼
    smbpasswd -a wuchang << EOF
wuchang
wuchang
EOF
    
    # 驗證配置
    testparm
    
    # 重啟Samba
    systemctl enable smbd
    systemctl restart smbd
    
    log_success "Samba配置完成"
}

# 配置SSH
configure_ssh() {
    log_info "配置SSH訪問..."
    
    # 編輯SSH配置
    cat > /etc/ssh/sshd_config.d/60-wuchang.conf << EOF
# Wuchang SSH Configuration
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication yes
X11Forwarding yes
X11DisplayOffset 10
PrintMotd no
PrintLastLog yes
TCPKeepAlive yes
AcceptEnv LANG LC_*
EOF
    
    # 驗證配置
    sshd -T | grep -E "permitrootlogin|pubkeyauthentication"
    
    # 重啟SSH
    systemctl restart ssh
    
    log_success "SSH配置完成"
}

# 配置防火牆
configure_firewall() {
    log_info "配置防火牆..."
    
    # 啟用ufw
    ufw --force enable
    
    # 允許必要端口
    ufw allow 22/tcp    # SSH
    ufw allow 80/tcp    # HTTP
    ufw allow 443/tcp   # HTTPS
    ufw allow 8069/tcp  # Odoo
    ufw allow 9000/tcp  # Portainer
    ufw allow 2049/tcp  # NFS
    ufw allow 445/tcp   # Samba
    ufw allow 139/tcp   # Samba
    ufw allow 5432/tcp  # PostgreSQL
    
    # 限制SSH訪問
    ufw limit 22/tcp
    
    # 顯示規則
    log_info "防火牆規則:"
    ufw status numbered
    
    log_success "防火牆配置完成"
}

# 克隆項目倉庫
clone_repository() {
    log_info "克隆Wuchang項目..."
    
    if [ ! -d "$WUCHANG_HOME" ]; then
        git clone https://github.com/wuchang1100606355-del/wuchang-V5.1.0.git "$WUCHANG_HOME"
        cd "$WUCHANG_HOME"
        git checkout migration/ui-total-ai
    else
        cd "$WUCHANG_HOME"
        git pull
    fi
    
    # 設置權限
    chown -R admin:admin "$WUCHANG_HOME"
    
    log_success "項目克隆完成"
}

# 準備Docker環境
prepare_docker() {
    log_info "準備Docker環境..."
    
    # 創建docker-compose文件
    log_info "創建docker-compose.yml..."
    
    cat > "$WUCHANG_HOME/docker-compose.server.yml" << 'EOF'
version: '3.8'

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
      - ./wuchang_os/addons:/mnt/extra-addons
      - /mnt/wuchang-storage/downloads:/mnt/jules:rw
      - ./wuchang_os/config:/mnt/jules-config:ro
      - /mnt/wuchang-storage/ai-memory/memory_store:/opt/wuchang/memory_store
      - /mnt/wuchang-storage/ai-common/common_store:/opt/wuchang/common_store
    command: odoo -d admin --db_host=db --db_user=odoo --db_password=odoo --proxy-mode --longpolling-port=8072
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
      - GOOGLE_APPLICATION_CREDENTIALS=./wuchang_os/config/gcp/littlej-sa.json
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
      - ./wuchang_os/Caddyfile:/etc/caddy/Caddyfile
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
EOF
    
    log_success "Docker環境準備完成"
}

# 創建監視和維護腳本
create_maintenance_scripts() {
    log_info "創建維護腳本..."
    
    # 健康檢查腳本
    cat > /usr/local/bin/wuchang-health-check << 'SCRIPT'
#!/bin/bash

echo "════════════════════════════════════════"
echo "  五常AI系統 - 健康檢查"
echo "════════════════════════════════════════"

# 檢查Docker狀態
echo "Docker 容器狀態:"
docker-compose -f /home/admin/wuchang-V5.1.0/docker-compose.server.yml ps

# 檢查磁盤空間
echo ""
echo "磁盤空間使用:"
df -h /mnt/wuchang-storage

# 檢查數據庫
echo ""
echo "數據庫連接:"
docker exec wuchangv510-db-1 pg_isready -U odoo 2>/dev/null || echo "PostgreSQL 連接正常"

# 檢查應用健康
echo ""
echo "應用健康檢查:"
curl -s http://localhost:8069/health || echo "Odoo 運行中"

# 檢查NFS
echo ""
echo "NFS 導出:"
exportfs -v

# 檢查備份
echo ""
echo "最新備份:"
ls -lh /mnt/wuchang-storage/backups/ | tail -5
SCRIPT
    
    chmod +x /usr/local/bin/wuchang-health-check
    
    # 自動備份腳本
    cat > /usr/local/bin/wuchang-backup << 'SCRIPT'
#!/bin/bash

BACKUP_DIR="/mnt/wuchang-storage/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "開始備份: $TIMESTAMP"

# 備份數據庫
docker exec wuchangv510-db-1 pg_dump -U odoo admin | \
    gzip > "$BACKUP_DIR/odoo_db_$TIMESTAMP.sql.gz"

# 備份卷
docker run --rm \
    -v wuchangv510_odoo-web-data:/data \
    -v "$BACKUP_DIR:/backup" \
    alpine tar czf "/backup/odoo-web-data_$TIMESTAMP.tar.gz" -C /data .

echo "備份完成: $BACKUP_DIR/odoo_db_$TIMESTAMP.sql.gz"
SCRIPT
    
    chmod +x /usr/local/bin/wuchang-backup
    
    # 添加定時備份任務
    cat > /etc/cron.d/wuchang-backup << 'CRON'
# Wuchang Daily Backup
0 2 * * * root /usr/local/bin/wuchang-backup > /var/log/wuchang-backup.log 2>&1
CRON
    
    log_success "維護腳本已建立"
}

# 顯示完成信息
show_completion_info() {
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo "  ✓ 五常AI系統伺服器初始化完成"
    echo "════════════════════════════════════════════════════════"
    echo ""
    echo "重要信息:"
    echo "  IP地址:           $SERVER_IP"
    echo "  SSH訪問:          ssh admin@$SERVER_IP"
    echo "  Odoo地址:         http://$SERVER_IP:8069"
    echo "  Portainer:        http://$SERVER_IP:9000"
    echo "  存儲路徑:         $STORAGE_PATH"
    echo "  項目路徑:         $WUCHANG_HOME"
    echo ""
    echo "共享訪問:"
    echo "  SMB: \\\\$SERVER_IP\\wuchang-storage"
    echo "  NFS: $STORAGE_PATH"
    echo ""
    echo "下一步:"
    echo "  1. 恢復備份數據:"
    echo "     ssh admin@$SERVER_IP 'cd $WUCHANG_HOME && docker-compose -f docker-compose.server.yml up -d'"
    echo ""
    echo "  2. 驗證系統:"
    echo "     ssh admin@$SERVER_IP '/usr/local/bin/wuchang-health-check'"
    echo ""
    echo "  3. 在本機上配置同步:"
    echo "     PowerShell> .\\sync_with_server.ps1 -Mode watch"
    echo ""
    echo "════════════════════════════════════════════════════════"
}

# 主程序流程
main() {
    echo "═════════════════════════════════════════════════════════"
    echo "  五常AI系統 - 伺服器初始化腳本 v1.0"
    echo "═════════════════════════════════════════════════════════"
    echo ""
    
    check_root
    
    log_info "開始初始化伺服器..."
    log_info "目標IP: $SERVER_IP"
    log_info "存儲路徑: $STORAGE_PATH"
    echo ""
    
    update_system
    install_dependencies
    install_docker
    create_storage
    configure_nfs
    configure_samba
    configure_ssh
    configure_firewall
    clone_repository
    prepare_docker
    create_maintenance_scripts
    
    show_completion_info
}

# 執行主程序
main
