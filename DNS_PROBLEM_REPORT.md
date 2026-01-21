# DNS 問題診斷報告

**檢查時間：** 2026-01-20

## 🔴 發現的問題

### 1. Cloudflare Tunnel 配置不完整

**問題：**
- ❌ Tunnel ID 未設定（仍使用佔位符 `<tunnel-id>`）
- ❌ 憑證檔案不存在（`credentials.json`）
- ⚠️ 容器目前使用臨時隧道（trycloudflare.com），不是正式域名

**影響：**
- 無法使用正式域名訪問服務
- 臨時隧道沒有正常運行保證

### 2. DNS 解析失敗

**問題：**
- ❌ 所有域名無法解析：
  - `app.wuchang.org.tw`
  - `ai.wuchang.org.tw`
  - `admin.wuchang.org.tw`
  - `monitor.wuchang.org.tw`

**原因：**
- DNS 路由未在 Cloudflare 設定
- Cloudflare Tunnel 未正確配置

### 3. 服務無法連接

**問題：**
- ❌ 所有 HTTPS 服務無法連接

**原因：**
- DNS 解析失敗導致無法連接

---

## ✅ 正常狀態

- ✅ Cloudflare Tunnel 容器運行中
- ✅ 配置檔案存在（但需更新）

---

## 🛠️ 修復步驟

### 步驟 1: 設定 Cloudflare Tunnel

1. **登入 Cloudflare**
   ```bash
   cloudflared tunnel login
   ```
   - 這會開啟瀏覽器讓您登入 Cloudflare
   - 完成後會產生憑證檔案

2. **建立命名隧道**
   ```bash
   cloudflared tunnel create wuchang-tunnel
   ```
   - 記下產生的 Tunnel ID（例如：`abc123-4567-8901-2345-6789abcdef12`）

3. **配置 DNS 路由**
   ```bash
   cloudflared tunnel route dns wuchang-tunnel app.wuchang.org.tw
   cloudflared tunnel route dns wuchang-tunnel ai.wuchang.org.tw
   cloudflared tunnel route dns wuchang-tunnel admin.wuchang.org.tw
   cloudflared tunnel route dns wuchang-tunnel monitor.wuchang.org.tw
   ```

4. **複製憑證檔案**
   - 憑證位置：`%USERPROFILE%\.cloudflared\<tunnel-id>.json`
   - 複製到：`cloudflared/credentials.json`

### 步驟 2: 更新配置檔案

編輯 `cloudflared/config.yml`：

```yaml
tunnel: <實際的-tunnel-id>
credentials-file: /etc/cloudflared/credentials.json

ingress:
  # Odoo ERP 系統
  - hostname: app.wuchang.org.tw
    service: http://wuchangv510-wuchang-web-1:8069
  
  # Open WebUI (AI 介面)
  - hostname: ai.wuchang.org.tw
    service: http://wuchangv510-open-webui-1:8080
  
  # Portainer (容器管理)
  - hostname: admin.wuchang.org.tw
    service: http://wuchangv510-portainer-1:9000
  
  # Uptime Kuma (監控)
  - hostname: monitor.wuchang.org.tw
    service: http://wuchangv510-uptime-kuma-1:3001
  
  # 預設規則（必須放在最後）
  - service: http_status:404
```

**重要：** 將 `<實際的-tunnel-id>` 替換為步驟 1 記下的 Tunnel ID。

### 步驟 3: 重啟 Cloudflare Tunnel 容器

```bash
docker-compose -f docker-compose.cloud.yml restart cloudflared
```

或：

```bash
docker restart wuchangv510-cloudflared-1
```

### 步驟 4: 驗證修復

1. **檢查容器日誌**
   ```bash
   docker logs wuchangv510-cloudflared-1
   ```
   - 應該看到 "Registered tunnel connection" 訊息
   - 不應該有 "Cannot determine default configuration path" 錯誤

2. **檢查 DNS 解析**
   ```bash
   nslookup app.wuchang.org.tw
   ```
   - 應該解析到 Cloudflare IP（通常是 `104.x.x.x` 範圍）

3. **檢查服務連接**
   ```bash
   curl -I https://app.wuchang.org.tw
   ```
   - 或直接在瀏覽器訪問 `https://app.wuchang.org.tw`

---

## 📋 快速修復命令

如果您已經有 Cloudflare 帳號和網域設定，可以執行：

```bash
# 1. 登入並建立隧道
cloudflared tunnel login
cloudflared tunnel create wuchang-tunnel

# 2. 設定 DNS 路由（替換為您的實際域名）
cloudflared tunnel route dns wuchang-tunnel app.wuchang.org.tw

# 3. 複製憑證（替換 <tunnel-id> 為實際 ID）
copy %USERPROFILE%\.cloudflared\<tunnel-id>.json cloudflared\credentials.json

# 4. 更新配置檔案中的 Tunnel ID
# （手動編輯 cloudflared/config.yml）

# 5. 重啟容器
docker restart wuchangv510-cloudflared-1
```

---

## 🔍 驗證清單

修復完成後，確認：

- [ ] `cloudflared/credentials.json` 檔案存在
- [ ] `cloudflared/config.yml` 中的 Tunnel ID 已更新
- [ ] DNS 路由已設定（使用 `cloudflared tunnel route dns list` 檢查）
- [ ] 容器日誌顯示正常連接
- [ ] 域名可以解析到 Cloudflare IP
- [ ] HTTPS 服務可以訪問

---

## 📝 注意事項

1. **DNS 傳播時間：** DNS 設定可能需要幾分鐘到幾小時才能完全生效
2. **憑證路徑：** 確保 `credentials.json` 路徑正確，容器內路徑為 `/etc/cloudflared/credentials.json`
3. **服務名稱：** 配置檔案中的服務名稱必須與實際容器名稱一致
4. **預設規則：** ingress 配置的最後必須有預設規則 `service: http_status:404`

---

## 🔗 相關資源

- [Cloudflare Tunnel 文件](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [DNS 路由設定](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/routes/)
- 本地部署指南：`CLOUD_DEPLOYMENT_GUIDE.md`

---

**報告產生時間：** 2026-01-20
