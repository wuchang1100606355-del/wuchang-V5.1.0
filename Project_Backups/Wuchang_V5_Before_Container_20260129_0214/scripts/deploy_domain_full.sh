#!/bin/bash
# 五常 AI 系統 - GCP VM 完整網域部署腳本
# 包含 Nginx、SSL 證書、域名配置

set -e

echo "======================================"
echo " 五常 AI 系統網域部署工具"
echo "======================================"

# 配置變量
DOMAIN_NAME="${DOMAIN_NAME:-wuchang.life}"
SUBDOMAIN="${SUBDOMAIN:-ai}"
FULL_DOMAIN="${SUBDOMAIN}.${DOMAIN_NAME}"
EMAIL="${ADMIN_EMAIL:-admin@wuchang.life}"
PROJECT_ID="${GCP_PROJECT_ID:-coffee-spark-ai-barista-b10b5}"
VM_NAME="${VM_NAME:-vm-system-tw}"
ZONE="${GCP_ZONE:-asia-east1-b}"

echo "配置信息："
echo "  域名: $FULL_DOMAIN"
echo "  郵箱: $EMAIL"
echo "  VM: $VM_NAME"
echo "  區域: $ZONE"
echo ""

# 檢查是否在 GCP VM 上運行
if [ ! -f /etc/google_compute_engine ]; then
    echo "警告：似乎不在 GCP VM 上運行"
    read -p "是否繼續? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 1. 更新系統
echo "[1/7] 更新系統套件..."
sudo apt-get update
sudo apt-get upgrade -y

# 2. 安裝 Nginx
echo "[2/7] 安裝 Nginx..."
sudo apt-get install -y nginx

# 3. 安裝 Certbot (Let's Encrypt)
echo "[3/7] 安裝 Certbot..."
sudo apt-get install -y certbot python3-certbot-nginx

# 4. 配置 Nginx
echo "[4/7] 配置 Nginx..."

# 創建 Streamlit 應用配置
sudo tee /etc/nginx/sites-available/wuchang-streamlit > /dev/null <<EOF
server {
    listen 80;
    server_name $FULL_DOMAIN;
    
    # Redirect HTTP to HTTPS (will be configured after SSL setup)
    # return 301 https://\$server_name\$request_uri;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }
    
    # WebSocket support for Streamlit
    location /_stcore/stream {
        proxy_pass http://localhost:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

# 創建 FastAPI 應用配置
sudo tee /etc/nginx/sites-available/wuchang-api > /dev/null <<EOF
server {
    listen 80;
    server_name api.$DOMAIN_NAME;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 創建 Odoo 應用配置
sudo tee /etc/nginx/sites-available/wuchang-odoo > /dev/null <<EOF
server {
    listen 80;
    server_name odoo.$DOMAIN_NAME;
    
    location / {
        proxy_pass http://localhost:8069;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
        client_max_body_size 100M;
    }
    
    location /longpolling {
        proxy_pass http://localhost:8072;
    }
}
EOF

# 啟用站點
sudo ln -sf /etc/nginx/sites-available/wuchang-streamlit /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/wuchang-api /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/wuchang-odoo /etc/nginx/sites-enabled/

# 移除默認配置
sudo rm -f /etc/nginx/sites-enabled/default

# 測試 Nginx 配置
echo "測試 Nginx 配置..."
sudo nginx -t

# 重啟 Nginx
echo "重啟 Nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

# 5. 設置防火牆
echo "[5/7] 配置防火牆..."
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw --force enable

# 6. 獲取 SSL 證書
echo "[6/7] 獲取 SSL 證書..."
echo "注意：請確保 DNS 記錄已正確指向此 VM 的 IP"
read -p "DNS 記錄是否已配置？(y/N) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 為 Streamlit 獲取證書
    sudo certbot --nginx -d $FULL_DOMAIN --non-interactive --agree-tos -m $EMAIL
    
    # 為 API 獲取證書
    sudo certbot --nginx -d api.$DOMAIN_NAME --non-interactive --agree-tos -m $EMAIL
    
    # 為 Odoo 獲取證書
    sudo certbot --nginx -d odoo.$DOMAIN_NAME --non-interactive --agree-tos -m $EMAIL
    
    echo "SSL 證書獲取成功！"
    
    # 設置自動續期
    sudo systemctl enable certbot.timer
    sudo systemctl start certbot.timer
else
    echo "跳過 SSL 配置。稍後可運行：sudo certbot --nginx -d $FULL_DOMAIN"
fi

# 7. 啟動應用服務
echo "[7/7] 啟動應用服務..."

# 創建 systemd 服務文件 - Streamlit
sudo tee /etc/systemd/system/wuchang-streamlit.service > /dev/null <<EOF
[Unit]
Description=Wuchang AI Streamlit Application
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/app/vm_deploy
Environment="PATH=/home/$USER/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/local/bin/streamlit run chat_app_enhanced.py --server.port=8501 --server.address=localhost
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 創建 systemd 服務文件 - FastAPI
sudo tee /etc/systemd/system/wuchang-api.service > /dev/null <<EOF
[Unit]
Description=Wuchang AI FastAPI Application
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/app/vm_deploy/fastapi
Environment="PATH=/home/$USER/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Service]
WantedBy=multi-user.target
EOF

# 重載 systemd 並啟動服務
sudo systemctl daemon-reload
sudo systemctl enable wuchang-streamlit
sudo systemctl start wuchang-streamlit
sudo systemctl enable wuchang-api
sudo systemctl start wuchang-api

# 檢查服務狀態
echo ""
echo "======================================"
echo " 部署完成！"
echo "======================================"
echo ""
echo "服務狀態："
sudo systemctl status wuchang-streamlit --no-pager | head -n 5
sudo systemctl status wuchang-api --no-pager | head -n 5
echo ""
echo "訪問地址："
echo "  Streamlit: https://$FULL_DOMAIN"
echo "  API: https://api.$DOMAIN_NAME"
echo "  Odoo: https://odoo.$DOMAIN_NAME"
echo ""
echo "查看日誌："
echo "  Streamlit: sudo journalctl -u wuchang-streamlit -f"
echo "  API: sudo journalctl -u wuchang-api -f"
echo "  Nginx: sudo tail -f /var/log/nginx/error.log"
echo ""
echo "管理命令："
echo "  重啟服務: sudo systemctl restart wuchang-streamlit"
echo "  查看狀態: sudo systemctl status wuchang-streamlit"
echo "  測試 Nginx: sudo nginx -t"
echo "  重載 Nginx: sudo systemctl reload nginx"
echo ""
echo "證書續期："
echo "  手動續期: sudo certbot renew"
echo "  測試續期: sudo certbot renew --dry-run"
echo ""
