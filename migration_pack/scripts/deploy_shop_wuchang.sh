#!/bin/bash
# 重新店 (Shop Wuchang) - 雲端部署腳本
# 此腳本用於在雲端 VM 內部執行，完成 Docker 與 Odoo 的安裝。

echo "=========================================="
echo "      Wuchang Shop - Cloud Installer      "
echo "      (Powered by Little J & Vertex AI)   "
echo "=========================================="

# 1. 基礎環境檢查與 Docker 安裝
if ! command -v docker &> /dev/null; then
    echo "[1/4] 正在安裝 Docker 引擎..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker \
    echo "Docker 安裝完成。請登出後重新登入，或手動執行 'newgrp docker' 以套用權限。"
    echo "注意：如果您現在登出，請重新連線並再次執行此腳本。"
else
    echo "[1/4] Docker 已安裝，跳過。"
fi

# 2. 準備目錄結構
echo "[2/4] 建立專案目錄結構..."
PROJECT_ROOT=~/wuchang_shop
mkdir -p \/odoo-data
mkdir -p \/postgres-data
mkdir -p \/config
mkdir -p \/addons

# 3. 部署 Odoo Docker Compose 設定
echo "[3/4] 產生 docker-compose.yml..."
cat <<EOF > \/docker-compose.yml
version: '3.8'
services:
  web:
    image: odoo:17
    container_name: shop-wuchang-web
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - ./odoo-data:/var/lib/odoo
      - ./config:/etc/odoo
      - ./addons:/mnt/extra-addons
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=shop_wuchang_secret_pass
    restart: always

  db:
    image: postgres:15
    container_name: shop-wuchang-db
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=shop_wuchang_secret_pass
      - POSTGRES_USER=odoo
    volumes:
      - ./postgres-data:/var/lib/postgresql/data
    restart: always

  # Caddy 作為反向代理 (自動 HTTPS)
  caddy:
    image: caddy:latest
    container_name: shop-wuchang-caddy
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./caddy_data:/data
      - ./caddy_config:/config
    command: caddy reverse-proxy --from shop.wuchang.life --to web:8069
EOF

# 4. 寫入 AI 設定檔 (若有)
if [ -f "shop_ai_config.xml" ]; then
    echo "[4/4] 偵測到 AI 設定檔，正在部署..."
    cp shop_ai_config.xml \/addons/
    # 這裡假設 addons 資料夾內會有 wuchang_core 模組，稍後需要將源碼同步過來
else
    echo "[4/4] 未偵測到 shop_ai_config.xml，跳過 AI 設定。"
fi

echo "=========================================="
echo "部署準備完成！"
echo "下一步："
echo "1. 將您的 Odoo 模組 (wuchang_os/addons) 上傳到 \/addons"
echo "2. 進入目錄: cd \"
echo "3. 啟動服務: docker compose up -d"
echo "=========================================="
