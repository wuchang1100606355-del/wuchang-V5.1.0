# www.wuchang.life 首頁優先設定指南

**更新時間：** 2026-01-20  
**優先級：** ⭐⭐⭐⭐⭐ **最高優先級**  
**首頁地址：** **http://www.wuchang.life**（必須使用此域名，一定要能訪問）

---

## 🎯 重點

**www.wuchang.life 一定要能夠訪問！**

其他服務可以暫時不設定，但 `www.wuchang.life` 必須優先設定。

---

## ✅ 當前狀態

### 已完成的配置

- ✅ **Cloudflare 配置已更新**：`www.wuchang.life` 已配置為首頁
- ✅ **配置優先級正確**：`www.wuchang.life` 在 ingress 列表的第一位
- ✅ **服務容器運行中**：`wuchangv510-caddy-1` (端口 80)
- ✅ **首頁檔案存在**：`index.html` (22.39 KB)

### 需要設定

- ⚠️ **DNS 路由未設定**：`www.wuchang.life` 需要設定 DNS 路由

---

## 🚀 立即執行（優先步驟）

### 步驟 1: 設定 DNS 路由（必須）

**使用 Docker 執行（推薦）：**

```bash
docker run --rm \
  -v "${USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" \
  cloudflare/cloudflared:latest tunnel route dns wuchang-tunnel www.wuchang.life
```

**或使用 cloudflared（如果已安裝）：**

```bash
cloudflared tunnel route dns wuchang-tunnel www.wuchang.life
```

**驗證 DNS 路由已設定：**

```bash
docker run --rm \
  -v "${USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" \
  cloudflare/cloudflared:latest tunnel route dns list
```

應該看到 `www.wuchang.life` 在列表中。

---

### 步驟 確認配置檔案正確

**確認 `cloudflared/config.yml` 配置：**

```yaml
ingress:
  # 首頁（主域名）- 必須是 www.wuchang.life（第一位）
  - hostname: www.wuchang.life
    service: http://wuchangv510-caddy-1:80
  
  # ... 其他服務 ...
```

**重要：** `www.wuchang.life` 必須在 ingress 列表的第一位，確保優先匹配。

---

### 步驟 3: 重啟 Cloudflare Tunnel 容器

```bash
docker restart wuchangv510-cloudflared-1
```

**查看日誌確認：**

```bash
docker logs wuchangv510-cloudflared-1 --tail 20
```

應該看到：
- ✅ `Registered tunnel connection`
- ✅ 沒有錯誤訊息
- ✅ `www.wuchang.life` 已註冊

---

### 步驟 4: 驗證訪問（必須確認）

**檢查 DNS 解析：**

```bash
nslookup www.wuchang.life
```

應該解析到 Cloudflare IP（通常是 `104.x.x.x` 或 `172.x.x.x` 範圍）。

**檢查服務訪問：**

```bash
# HTTP 訪問（首頁使用 HTTP）
curl -I http://www.wuchang.life

# 或直接在瀏覽器訪問
http://www.wuchang.life
```

**應該看到：**
- ✅ HTTP 200 狀態碼
- ✅ 首頁內容正常顯示

---

## 📋 完整設定命令（一次執行）

**如果還沒有設定 Cloudflare Tunnel，執行以下完整步驟：**

### 1. 登入 Cloudflare

```bash
docker run --rm -it \
  -v "${USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" \
  cloudflare/cloudflared:latest tunnel login
```

### 2. 建立隧道

```bash
docker run --rm -it \
  -v "${USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" \
  cloudflare/cloudflared:latest tunnel create wuchang-tunnel
```

**記下產生的 Tunnel ID！**

### 3. 設定 DNS 路由（優先：首頁）

```bash
# 首頁（必須，優先執行）
docker run --rm \
  -v "${USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" \
  cloudflare/cloudflared:latest tunnel route dns wuchang-tunnel www.wuchang.life

# 其他服務（可選，稍後再設定）
# docker run --rm \
#   -v "${USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" \
#   cloudflare/cloudflared:latest tunnel route dns wuchang-tunnel app.wuchang.org.tw
```

### 4. 複製憑證檔案

```bash
# 替換 <tunnel-id> 為步驟 2 記下的實際 ID
Copy-Item "${env:USERPROFILE}\.cloudflared\<tunnel-id>.json" "cloudflared\credentials.json"
```

### 5. 更新配置檔案

編輯 `cloudflared/config.yml`，將 `<tunnel-id>` 替換為實際 ID。

**確認配置：**

```yaml
tunnel: abc123-4567-8901-2345-6789abcdef12  # 實際的 Tunnel ID
credentials-file: /etc/cloudflared/credentials.json

ingress:
  # 首頁（必須是第一位）
  - hostname: www.wuchang.life
    service: http://wuchangv510-caddy-1:80
  
  # ... 其他服務 ...
```

### 6. 重啟容器

```bash
docker restart wuchangv510-cloudflared-1
```

### 7. 驗證首頁訪問

```bash
# 檢查 DNS
nslookup www.wuchang.life

# 檢查服務
curl -I http://www.wuchang.life

# 瀏覽器訪問
http://www.wuchang.life
```

---

## ✅ 首頁訪問確認

設定完成後，必須確認：

- [ ] DNS 解析成功：`nslookup www.wuchang.life` 有結果
- [ ] 服務可訪問：`http://www.wuchang.life` 顯示首頁內容
- [ ] 容器運行正常：Cloudflare Tunnel 容器正常運行
- [ ] 沒有錯誤：容器日誌沒有錯誤訊息

---

## 🔧 快速檢查腳本

執行以下腳本檢查 `www.wuchang.life` 狀態：

```bash
python setup_wuchang_life_priority.py
```

或：

```bash
python check_homepage_config.py
```

---

## ⚠️ 重要提醒

1. **www.wuchang.life 是最高優先級**
   - 其他服務可以稍後設定
   - 但 `www.wuchang.life` 必須優先完成設定

2. **首頁使用 HTTP 協議**
   - 根據要求，首頁使用 `http://`（不是 `https://`）
   - 服務指向：`http://wuchangv510-caddy-1:80`

3. **配置優先級**
   - `www.wuchang.life` 必須在 ingress 列表的第一位
   - 確保優先匹配

---

## 📋 其他服務（可選，稍後設定）

如果需要，可以稍後設定其他服務的 DNS 路由：

```bash
# 其他服務（不是優先的）
cloudflared tunnel route dns wuchang-tunnel app.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel ai.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel admin.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel monitor.wuchang.org.tw
```

**但首要任務是確保 `www.wuchang.life` 可以訪問！**

---

## 📝 相關檔案

- `cloudflared/config.yml` - Cloudflare 配置（已更新，包含 www.wuchang.life）
- `setup_wuchang_life_priority.py` - 首頁優先檢查腳本
- `check_homepage_config.py` - 首頁檢查腳本
- `HOMEPAGE_WUCHANG_LIFE_SETUP.md` - 完整設定指南

---

**設定指南產生時間：** 2026-01-20  
**優先級：** ⭐⭐⭐⭐⭐ **最高優先級**  
**首頁地址：** **http://www.wuchang.life**（必須使用此域名，一定要能訪問）
