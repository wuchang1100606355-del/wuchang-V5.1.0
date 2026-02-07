# 五常 AI 系統網域部署 - 快速開始

## 🚀 三步驟完成部署

### 步驟 1：配置 DNS（5 分鐘）

1. **獲取 VM IP 地址**

    ```powershell
    gcloud compute instances describe vm-system-tw `
      --zone=asia-east1-b `
      --format="get(networkInterfaces[0].accessConfigs[0].natIP)"
    ```

    假設返回：`35.201.XXX.XXX`

2. **在您的 DNS 提供商添加記錄**

    ```
    類型: A,  主機: ai,   值: 35.201.XXX.XXX
    類型: A,  主機: api,  值: 35.201.XXX.XXX
    類型: A,  主機: odoo, 值: 35.201.XXX.XXX
    ```

3. **等待 DNS 生效**（5-15 分鐘）

---

### 步驟 2：驗證 DNS（1 分鐘）

```powershell
cd "c:\wuchang V5.1.0"
.\scripts\check_dns_ready.ps1
```

**預期輸出：**

```
✓ 正確: ai.wuchang.life -> 35.201.XXX.XXX
✓ 正確: api.wuchang.life -> 35.201.XXX.XXX
✓ 正確: odoo.wuchang.life -> 35.201.XXX.XXX
✅ DNS 配置正確！
```

---

### 步驟 3：執行部署（10-15 分鐘）

```powershell
cd "c:\wuchang V5.1.0"

.\scripts\deploy_domain_windows.ps1 `
  -Domain "ai.wuchang.life" `
  -Email "admin@wuchang.life" `
  -VMName "vm-system-tw" `
  -Zone "asia-east1-b" `
  -ProjectID "coffee-spark-ai-barista-b10b5"
```

**部署過程：**

1. ✅ 設置 GCP 項目
2. ✅ 獲取 VM IP
3. ✅ 驗證 DNS 配置
4. ✅ 上傳部署腳本到 VM
5. ✅ 在 VM 上執行：
    - 安裝 Nginx
    - 安裝 Certbot
    - 配置反向代理
    - 獲取 SSL 證書
    - 設置 systemd 服務
    - 啟動所有服務
6. ✅ 驗證部署結果

**完成後：**

```
✅ 部署完成！

訪問地址：
  主要服務: https://ai.wuchang.life
  API 服務: https://api.wuchang.life
  Odoo 服務: https://odoo.wuchang.life
```

---

## 📋 完整命令流程

```powershell
# 1. 進入項目目錄
cd "c:\wuchang V5.1.0"

# 2. 檢查 DNS（可選但推薦）
.\scripts\check_dns_ready.ps1

# 3. 執行部署
.\scripts\deploy_domain_windows.ps1

# 4. 打開瀏覽器訪問
Start-Process "https://ai.wuchang.life"
```

---

## 🔧 部署選項

### 基本部署（使用默認值）

```powershell
.\scripts\deploy_domain_windows.ps1
```

### 自定義域名

```powershell
.\scripts\deploy_domain_windows.ps1 -Domain "chat.wuchang.life"
```

### 跳過 DNS 檢查（不推薦）

```powershell
.\scripts\deploy_domain_windows.ps1 -SkipDNSCheck
```

### 部署到不同的 VM

```powershell
.\scripts\deploy_domain_windows.ps1 `
  -VMName "vm-prod-server" `
  -Zone "us-central1-a"
```

---

## ✅ 驗證部署

### 1. 檢查 HTTPS 訪問

```powershell
# 打開瀏覽器測試
Start-Process "https://ai.wuchang.life"
```

### 2. 檢查 SSL 證書

```powershell
# SSH 到 VM
gcloud compute ssh vm-system-tw --zone=asia-east1-b

# 查看證書
sudo certbot certificates
```

### 3. 檢查服務狀態

```bash
# 在 VM 上執行
sudo systemctl status wuchang-streamlit
sudo systemctl status wuchang-api
sudo systemctl status nginx
```

### 4. 查看日誌

```bash
# Streamlit 日誌
sudo journalctl -u wuchang-streamlit -f

# API 日誌
sudo journalctl -u wuchang-api -f

# Nginx 錯誤日誌
sudo tail -f /var/log/nginx/error.log
```

---

## 🚨 常見問題

### Q1: DNS 檢查失敗？

**A:**

```powershell
# 清除 DNS 緩存
ipconfig /flushdns

# 等待 5-10 分鐘後重試
.\scripts\check_dns_ready.ps1
```

### Q2: SSL 證書獲取失敗？

**A:**

1. 確認 DNS 指向正確
2. 確認沒有啟用 CDN 代理（Cloudflare 橙色雲朵）
3. 檢查防火牆規則

```bash
# 在 VM 上執行
sudo ufw status
sudo ufw allow 'Nginx Full'
```

### Q3: 服務無法啟動？

**A:**

```bash
# 查看詳細錯誤
sudo journalctl -u wuchang-streamlit -n 50

# 手動啟動測試
cd ~/app/vm_deploy
streamlit run chat_app_enhanced.py
```

### Q4: 502 Bad Gateway 錯誤？

**A:**

```bash
# 檢查後端服務
sudo systemctl status wuchang-streamlit

# 重啟服務
sudo systemctl restart wuchang-streamlit

# 檢查端口
sudo netstat -tlnp | grep 8501
```

---

## 📚 相關文檔

-   **完整部署指南**: `docs/DOMAIN_DEPLOYMENT_GUIDE.md`
-   **DNS 配置詳解**: `docs/DNS_CONFIGURATION_GUIDE.md`
-   **系統優化報告**: `SYSTEM_OPTIMIZATION_REPORT.md`

---

## 💡 提示

### 部署前檢查清單

-   [ ] 已安裝 gcloud CLI
-   [ ] 已認證 GCP 帳號
-   [ ] DNS 記錄已配置
-   [ ] VM 正在運行
-   [ ] 防火牆規則允許 HTTP/HTTPS

### 時間預估

-   DNS 配置：5 分鐘
-   DNS 傳播：5-30 分鐘
-   部署執行：10-15 分鐘
-   **總計：20-50 分鐘**

### 成本預估

-   Let's Encrypt SSL：免費
-   Nginx：免費
-   GCP VM：按現有計費
-   域名：按註冊商收費

---

## 🎯 下一步

部署完成後，您可以：

1. **配置 AI 學習系統**

    ```bash
    ssh vm-system-tw
    cd ~/app
    python initialize_learning_system.py
    ```

2. **運行測試**

    ```bash
    python test_learning_system.py
    ```

3. **監控服務**

    ```bash
    sudo systemctl status wuchang-*
    ```

4. **查看成長報告**
    - 訪問 https://ai.wuchang.life
    - 點擊側邊欄 "生成成長報告"

---

## 🆘 獲取幫助

### 自動診斷

```powershell
# Windows
.\scripts\diagnose_deployment.ps1

# 或 SSH 到 VM
gcloud compute ssh vm-system-tw --zone=asia-east1-b
sudo ~/check_system_health.sh
```

### 手動檢查

```bash
# 服務狀態
sudo systemctl status wuchang-streamlit --no-pager

# 最近錯誤
sudo journalctl -u wuchang-streamlit -n 50 --no-pager

# Nginx 配置測試
sudo nginx -t

# 端口監聽
sudo netstat -tlnp | grep -E '80|443|8501'
```

---

**祝部署順利！** 🎉

有任何問題，請查看詳細文檔或檢查系統日誌。
