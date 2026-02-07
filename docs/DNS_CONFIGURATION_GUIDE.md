# 五常 AI 系統 DNS 配置指南

## 🌐 DNS 配置總覽

### 需要配置的域名記錄

```
主域名: wuchang.life
子域名需求：
  - ai.wuchang.life (Streamlit AI 聊天介面)
  - api.wuchang.life (FastAPI 後端)
  - odoo.wuchang.life (Odoo ERP 系統)
```

---

## 📝 Cloudflare 配置步驟

### 1. 登入 Cloudflare Dashboard

1. 前往 https://dash.cloudflare.com/
2. 選擇您的域名 `wuchang.life`

### 2. 獲取 VM IP 地址

```bash
# 在本機執行
gcloud compute instances describe vm-system-tw \
  --zone=asia-east1-b \
  --format="get(networkInterfaces[0].accessConfigs[0].natIP)"
```

假設返回的 IP 是：`35.201.XXX.XXX`

### 3. 添加 DNS 記錄

#### 記錄 1：AI 聊天介面

```
類型: A
名稱: ai
IPv4 地址: 35.201.XXX.XXX
代理狀態: 僅 DNS (灰色雲朵)
TTL: 自動
```

#### 記錄 2：API 服務

```
類型: A
名稱: api
IPv4 地址: 35.201.XXX.XXX
代理狀態: 僅 DNS (灰色雲朵)
TTL: 自動
```

#### 記錄 3：Odoo 服務

```
類型: A
名稱: odoo
IPv4 地址: 35.201.XXX.XXX
代理狀態: 僅 DNS (灰色雲朵)
TTL: 自動
```

### 4. 驗證配置

等待 1-5 分鐘後，執行：

```bash
# Windows PowerShell
Resolve-DnsName ai.wuchang.life
Resolve-DnsName api.wuchang.life
Resolve-DnsName odoo.wuchang.life

# Linux/Mac
dig ai.wuchang.life
dig api.wuchang.life
dig odoo.wuchang.life

# 或使用 nslookup
nslookup ai.wuchang.life
```

確認返回的 IP 地址是您的 VM IP。

---

## 🔧 GoDaddy 配置步驟

### 1. 登入 GoDaddy

1. 前往 https://www.godaddy.com/
2. 登入帳號
3. 進入 "My Products" → "DNS"

### 2. 添加記錄

點擊 "Add" 按鈕，添加以下記錄：

#### 記錄 1：ai

```
類型: A
主機: ai
指向: 35.201.XXX.XXX
TTL: 600 秒
```

#### 記錄 2：api

```
類型: A
主機: api
指向: 35.201.XXX.XXX
TTL: 600 秒
```

#### 記錄 3：odoo

```
類型: A
主機: odoo
指向: 35.201.XXX.XXX
TTL: 600 秒
```

### 3. 保存並等待生效

GoDaddy DNS 更新通常需要 10-30 分鐘生效。

---

## 🛡️ Google Domains 配置步驟

### 1. 登入 Google Domains

1. 前往 https://domains.google.com/
2. 選擇您的域名

### 2. 進入 DNS 設置

1. 點擊左側 "DNS"
2. 滾動到 "自訂資源記錄"

### 3. 添加記錄

#### 記錄 1：ai

```
主機名稱: ai
類型: A
TTL: 5 分鐘
數據: 35.201.XXX.XXX
```

#### 記錄 2：api

```
主機名稱: api
類型: A
TTL: 5 分鐘
數據: 35.201.XXX.XXX
```

#### 記錄 3：odoo

```
主機名稱: odoo
類型: A
TTL: 5 分鐘
數據: 35.201.XXX.XXX
```

---

## 🎯 其他 DNS 提供商通用配置

無論使用哪個 DNS 提供商，配置內容都相同：

| 記錄類型 | 主機/名稱 | 值/指向 | TTL     |
| -------- | --------- | ------- | ------- |
| A        | ai        | [VM IP] | 300-600 |
| A        | api       | [VM IP] | 300-600 |
| A        | odoo      | [VM IP] | 300-600 |

**注意事項：**

-   ⚠️ 不要啟用 CDN/代理（如 Cloudflare 的橙色雲朵），Let's Encrypt 需要直接訪問服務器
-   ✅ TTL 設置為較短值（300-600 秒）方便調試
-   ✅ 確保沒有衝突的 CNAME 記錄

---

## ✅ DNS 驗證方法

### 方法 1：使用 nslookup（所有平台）

```bash
nslookup ai.wuchang.life
nslookup api.wuchang.life
nslookup odoo.wuchang.life
```

**預期輸出：**

```
Server:  [DNS 服務器]
Address:  [DNS 服務器 IP]

Non-authoritative answer:
Name:    ai.wuchang.life
Address:  35.201.XXX.XXX
```

### 方法 2：使用 dig（Linux/Mac）

```bash
dig ai.wuchang.life +short
dig api.wuchang.life +short
dig odoo.wuchang.life +short
```

**預期輸出：**

```
35.201.XXX.XXX
```

### 方法 3：使用 PowerShell（Windows）

```powershell
Resolve-DnsName ai.wuchang.life | Select-Object Name, IPAddress
```

### 方法 4：在線 DNS 檢查工具

-   https://dnschecker.org/
-   https://www.whatsmydns.net/
-   https://mxtoolbox.com/SuperTool.aspx

輸入您的域名，確認全球 DNS 服務器都返回正確的 IP。

---

## 🔄 DNS 傳播時間

### 預估時間

-   **Cloudflare**: 1-5 分鐘
-   **GoDaddy**: 10-30 分鐘
-   **Google Domains**: 5-15 分鐘
-   **其他提供商**: 最多 48 小時（通常在 1 小時內）

### 加速傳播技巧

1. 設置較短的 TTL（300-600 秒）
2. 清除本地 DNS 緩存：

    ```bash
    # Windows
    ipconfig /flushdns

    # Mac
    sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder

    # Linux
    sudo systemd-resolve --flush-caches
    ```

---

## 🚨 常見問題排除

### 問題 1：DNS 解析到錯誤 IP

**檢查步驟：**

1. 確認 DNS 記錄配置正確
2. 等待 TTL 時間過期
3. 清除本地 DNS 緩存
4. 檢查是否有衝突的記錄（如舊的 A 記錄或 CNAME）

### 問題 2：某些地區無法解析

**可能原因：**

-   DNS 傳播未完成
-   ISP DNS 緩存

**解決方法：**

-   等待更長時間
-   使用 Google DNS (8.8.8.8) 或 Cloudflare DNS (1.1.1.1)

### 問題 3：SSL 證書無法獲取

**檢查項目：**

1. DNS 必須指向正確的服務器
2. 不能使用 CDN 代理（Cloudflare 橙色雲朵需要關閉）
3. 防火牆必須允許 80 和 443 端口
4. 確保域名可以從公網訪問

---

## 📋 DNS 配置檢查清單

在執行部署腳本前，確認：

-   [ ] DNS 記錄已添加（ai, api, odoo）
-   [ ] 所有記錄類型為 A
-   [ ] 所有記錄指向相同的 VM IP
-   [ ] 未啟用 CDN/代理（如適用）
-   [ ] TTL 設置為合理值（300-600）
-   [ ] 使用 nslookup/dig 驗證解析成功
-   [ ] 等待至少 5-10 分鐘確保傳播
-   [ ] 從不同網絡/設備測試訪問

---

## 🔐 GCP 防火牆配置

### 確保允許 HTTP/HTTPS 流量

```bash
# 檢查現有規則
gcloud compute firewall-rules list

# 如需創建新規則
gcloud compute firewall-rules create allow-http \
  --allow tcp:80 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow HTTP"

gcloud compute firewall-rules create allow-https \
  --allow tcp:443 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow HTTPS"
```

---

## 🎓 進階配置

### 添加通配符子域名（可選）

```
類型: A
名稱: *
IPv4 地址: 35.201.XXX.XXX
```

這將使所有子域名（如 test.wuchang.life）指向同一服務器。

### 添加 IPv6 支持（如果 VM 有 IPv6）

```
類型: AAAA
名稱: ai
IPv6 地址: [VM IPv6 地址]
```

### 設置 CAA 記錄（增強安全性）

```
類型: CAA
名稱: @
值: 0 issue "letsencrypt.org"
```

這限制只有 Let's Encrypt 可以為您的域名簽發證書。

---

## 📞 獲取幫助

### DNS 檢查命令總結

```bash
# 快速檢查腳本（Windows PowerShell）
$domains = @("ai.wuchang.life", "api.wuchang.life", "odoo.wuchang.life")
foreach ($domain in $domains) {
    Write-Host "檢查 $domain ..." -ForegroundColor Yellow
    $result = Resolve-DnsName $domain -ErrorAction SilentlyContinue
    if ($result) {
        Write-Host "  ✓ $domain -> $($result.IPAddress)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $domain 無法解析" -ForegroundColor Red
    }
}
```

### 部署前快速驗證

```powershell
# 執行此腳本確認 DNS 就緒
.\scripts\check_dns_ready.ps1 -Domain "ai.wuchang.life"
```

---

**最後更新**: 2026 年 1 月 10 日  
**版本**: 5.1.0  
**作者**: 小 j AI 系統團隊
