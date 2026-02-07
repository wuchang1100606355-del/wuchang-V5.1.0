# 五常 AI 系統網域部署指南

## 📋 部署前準備

### 1. DNS 配置

在您的域名提供商（如 Cloudflare、GoDaddy 等）添加以下 DNS 記錄：

```
類型: A
主機: ai (或您想要的子域名)
值: [您的 VM IP 地址]
TTL: 300 (或自動)

類型: A
主機: api
值: [您的 VM IP 地址]
TTL: 300

類型: A
主機: odoo
值: [您的 VM IP 地址]
TTL: 300
```

### 2. 獲取 VM IP 地址

```bash
gcloud compute instances describe vm-system-tw \
  --zone=asia-east1-b \
  --format="get(networkInterfaces[0].accessConfigs[0].natIP)"
```

### 3. 確認所需軟件

-   gcloud CLI (已安裝)
-   PowerShell 5.1+ (Windows)
-   或 Bash (Linux/Mac)

---

## 🚀 快速部署

### 方式一：Windows PowerShell（推薦）

```powershell
# 進入項目目錄
cd "c:\wuchang V5.1.0"

# 執行部署
.\scripts\deploy_domain_windows.ps1 `
  -Domain "ai.wuchang.life" `
  -Email "admin@wuchang.life" `
  -VMName "vm-system-tw" `
  -Zone "asia-east1-b" `
  -ProjectID "coffee-spark-ai-barista-b10b5"
```

### 方式二：直接在 VM 上執行

1. SSH 連接到 VM：

```bash
gcloud compute ssh vm-system-tw --zone=asia-east1-b
```

2. 上傳並執行腳本：

```bash
# 設置環境變量
export DOMAIN_NAME="wuchang.life"
export SUBDOMAIN="ai"
export ADMIN_EMAIL="admin@wuchang.life"

# 下載並執行
chmod +x deploy_domain_full.sh
sudo ./deploy_domain_full.sh
```

---

## 📦 部署內容

### 安裝的組件

-   ✅ Nginx (反向代理服務器)
-   ✅ Certbot (Let's Encrypt SSL 證書)
-   ✅ Systemd 服務（Streamlit + FastAPI）
-   ✅ UFW 防火牆規則
-   ✅ 自動 SSL 證書續期

### 配置的服務

#### 1. Streamlit AI 聊天介面

-   **域名**: https://ai.wuchang.life
-   **端口**: 8501 (內部)
-   **服務**: wuchang-streamlit.service
-   **目錄**: ~/app/vm_deploy/

#### 2. FastAPI 後端 API

-   **域名**: https://api.wuchang.life
-   **端口**: 8000 (內部)
-   **服務**: wuchang-api.service
-   **目錄**: ~/app/vm_deploy/fastapi/

#### 3. Odoo ERP 系統

-   **域名**: https://odoo.wuchang.life
-   **端口**: 8069 (內部)
-   **服務**: Docker Compose
-   **目錄**: ~/app/wuchang_os/

---

## 🔧 管理命令

### 服務管理

```bash
# 查看服務狀態
sudo systemctl status wuchang-streamlit
sudo systemctl status wuchang-api

# 重啟服務
sudo systemctl restart wuchang-streamlit
sudo systemctl restart wuchang-api

# 查看日誌
sudo journalctl -u wuchang-streamlit -f
sudo journalctl -u wuchang-api -f

# 停止服務
sudo systemctl stop wuchang-streamlit
sudo systemctl stop wuchang-api

# 啟動服務
sudo systemctl start wuchang-streamlit
sudo systemctl start wuchang-api
```

### Nginx 管理

```bash
# 測試配置
sudo nginx -t

# 重載配置
sudo systemctl reload nginx

# 重啟 Nginx
sudo systemctl restart nginx

# 查看錯誤日誌
sudo tail -f /var/log/nginx/error.log

# 查看訪問日誌
sudo tail -f /var/log/nginx/access.log
```

### SSL 證書管理

```bash
# 手動續期所有證書
sudo certbot renew

# 測試續期（不實際執行）
sudo certbot renew --dry-run

# 查看證書信息
sudo certbot certificates

# 為新域名添加證書
sudo certbot --nginx -d new.wuchang.life

# 刪除證書
sudo certbot delete --cert-name ai.wuchang.life
```

---

## 🔍 故障排除

### 1. 無法訪問網站

**檢查項目：**

```bash
# 1. 檢查 DNS 解析
nslookup ai.wuchang.life

# 2. 檢查服務狀態
sudo systemctl status wuchang-streamlit
sudo systemctl status nginx

# 3. 檢查端口監聽
sudo netstat -tlnp | grep -E '8501|80|443'

# 4. 測試本地連接
curl http://localhost:8501
```

**常見解決方案：**

```bash
# 重啟所有服務
sudo systemctl restart wuchang-streamlit
sudo systemctl restart nginx

# 檢查防火牆
sudo ufw status
sudo ufw allow 'Nginx Full'
```

### 2. SSL 證書錯誤

**檢查證書狀態：**

```bash
sudo certbot certificates
```

**重新獲取證書：**

```bash
# 刪除舊證書
sudo certbot delete --cert-name ai.wuchang.life

# 重新獲取
sudo certbot --nginx -d ai.wuchang.life
```

### 3. 服務無法啟動

**查看詳細錯誤：**

```bash
sudo journalctl -u wuchang-streamlit -n 100 --no-pager
sudo journalctl -u wuchang-api -n 100 --no-pager
```

**常見問題：**

-   **端口被占用**：`sudo lsof -i :8501`
-   **權限問題**：`sudo chown -R $USER:$USER ~/app`
-   **依賴缺失**：`pip install -r requirements.txt`

### 4. Nginx 配置錯誤

**測試配置：**

```bash
sudo nginx -t
```

**查看配置文件：**

```bash
cat /etc/nginx/sites-available/wuchang-streamlit
```

**編輯配置：**

```bash
sudo nano /etc/nginx/sites-available/wuchang-streamlit
sudo nginx -t  # 測試
sudo systemctl reload nginx  # 重載
```

---

## 📊 監控和性能

### 實時監控

```bash
# CPU 和記憶體使用
htop

# 磁盤使用
df -h

# 網絡連接
sudo netstat -an | grep ESTABLISHED | wc -l

# Nginx 連接數
ps aux | grep nginx | wc -l
```

### 日誌分析

```bash
# 最近的錯誤
sudo journalctl -p err -n 50

# Streamlit 訪問量
sudo journalctl -u wuchang-streamlit | grep "GET" | wc -l

# Nginx 訪問統計
sudo awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10
```

---

## 🔒 安全建議

### 1. 定期更新

```bash
# 系統更新
sudo apt update && sudo apt upgrade -y

# Python 依賴更新
pip list --outdated
pip install --upgrade [package]
```

### 2. 防火牆規則

```bash
# 查看當前規則
sudo ufw status numbered

# 只允許必要端口
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 3. SSL 配置加強

```bash
# 編輯 Nginx SSL 配置
sudo nano /etc/nginx/sites-available/wuchang-streamlit

# 添加以下內容到 server 塊：
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers HIGH:!aNULL:!MD5;
```

### 4. 備份配置

```bash
# 備份 Nginx 配置
sudo cp -r /etc/nginx /backup/nginx-$(date +%Y%m%d)

# 備份 systemd 服務
sudo cp /etc/systemd/system/wuchang-*.service /backup/

# 備份應用數據
tar -czf ~/backup/app-$(date +%Y%m%d).tar.gz ~/app
```

---

## 📈 性能優化

### Nginx 優化

```nginx
# /etc/nginx/nginx.conf
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
client_max_body_size 100M;
```

### Streamlit 優化

```bash
# ~/.streamlit/config.toml
[server]
maxUploadSize = 100
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

---

## 🆘 緊急恢復

### 快速回滾

```bash
# 停止服務
sudo systemctl stop wuchang-streamlit wuchang-api

# 恢復配置
sudo cp /backup/nginx-backup/* /etc/nginx/

# 重啟
sudo systemctl restart nginx
sudo systemctl start wuchang-streamlit wuchang-api
```

### 完全重新部署

```bash
# 移除所有配置
sudo rm /etc/nginx/sites-enabled/wuchang-*
sudo rm /etc/systemd/system/wuchang-*.service

# 重新執行部署腳本
sudo ./deploy_domain_full.sh
```

---

## 📞 獲取幫助

### 查看系統狀態

```bash
# 運行健康檢查
curl https://ai.wuchang.life/_stcore/health

# 查看所有服務狀態
sudo systemctl status wuchang-* --no-pager
```

### 收集診斷信息

```bash
# 生成診斷報告
sudo journalctl -u wuchang-streamlit -n 200 > streamlit.log
sudo journalctl -u wuchang-api -n 200 > api.log
sudo nginx -T > nginx_config.txt
sudo certbot certificates > ssl_status.txt
```

---

## ✅ 部署檢查清單

-   [ ] DNS 記錄已配置並生效
-   [ ] VM 防火牆規則已設置
-   [ ] GCP 防火牆規則允許 HTTP/HTTPS
-   [ ] 部署腳本執行成功
-   [ ] Nginx 配置測試通過
-   [ ] SSL 證書獲取成功
-   [ ] Streamlit 服務運行中
-   [ ] FastAPI 服務運行中
-   [ ] 可以通過 HTTPS 訪問網站
-   [ ] WebSocket 連接正常
-   [ ] 自動續期 Cron 任務已設置

---

**最後更新**: 2026 年 1 月 10 日  
**版本**: 5.1.0  
**作者**: 小 j AI 系統團隊
