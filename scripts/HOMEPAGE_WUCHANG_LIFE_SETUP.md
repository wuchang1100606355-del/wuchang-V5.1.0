# 首頁 DNS 設定指南 - www.wuchang.life

**更新時間：** 2026-01-20  
**首頁地址：** **http://www.wuchang.life** （必須使用此域名）

---

## 📊 當前狀態

### ✅ 已確認

- ✅ **首頁檔案存在**：`index.html` (22.39 KB)
- ✅ **Web 伺服器運行中**：`wuchangv510-caddy-1` (端口 80/443)
- ✅ **Cloudflare 配置已更新**：包含 `www.wuchang.life`

### ⚠️ 需要設定

- ⚠️ **DNS 路由未設定**：`www.wuchang.life` 需要設定 DNS 路由

---

## 🔧 設定步驟

### 步驟 1: 配置 DNS 路由

**設定 Cloudflare Tunnel DNS 路由（使用 Docker）：**

```bash
# 首頁域名（必須）
docker run --rm \
  -v "${USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" \
  cloudflare/cloudflared:latest tunnel route dns wuchang-tunnel www.wuchang.life
```

**或使用 cloudflared（如果已安裝）：**

```bash
cloudflared tunnel route dns wuchang-tunnel www.wuchang.life
```

---

### 步驟 2: 確認 Cloudflare 配置

**確認 `cloudflared/config.yml` 配置正確：**

```yaml
ingress:
  # 首頁（主域名）- 必須是 www.wuchang.life
  - hostname: www.wuchang.life
    service: http://wuchangv510-caddy-1:80
  
  # ... 其他服務 ...
```

---

### 步驟 3: 重啟 Cloudflare Tunnel 容器

```bash
docker restart wuchangv510-cloudflared-1
```

**查看日誌確認：**

```bash
docker logs wuchangv510-cloudflared-1 --tail 20
```

應該看到 `www.wuchang.life` 已註冊。

---

### 步驟 4: 驗證設定

**檢查 DNS 解析：**

```bash
nslookup www.wuchang.life
```

應該解析到 Cloudflare IP（通常是 `104.x.x.x` 或 `172.x.x.x` 範圍）。

**檢查服務訪問：**

```bash
# HTTP 訪問（首頁使用 HTTP）
curl -I http://www.wuchang.life

# HTTPS 訪問（如果支援）
curl -I https://www.wuchang.life

# 或直接在瀏覽器訪問
http://www.wuchang.life
```

**執行檢查腳本：**

```bash
python check_homepage_config.py
```

---

## 📋 完整 DNS 路由設定

**所有需要設定的域名（包含首頁）：**

```bash
# 首頁（必須）
cloudflared tunnel route dns wuchang-tunnel www.wuchang.life

# 其他服務
cloudflared tunnel route dns wuchang-tunnel app.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel ai.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel admin.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel monitor.wuchang.org.tw
```

**使用 Docker 執行：**

```bash
# 首頁
docker run --rm \
  -v "${USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" \
  cloudflare/cloudflared:latest tunnel route dns wuchang-tunnel www.wuchang.life

# 其他服務
docker run --rm \
  -v "${USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" \
  cloudflare/cloudflared:latest tunnel route dns wuchang-tunnel app.wuchang.org.tw

docker run --rm \
  -v "${USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" \
  cloudflare/cloudflared:latest tunnel route dns wuchang-tunnel ai.wuchang.org.tw

docker run --rm \
  -v "${USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" \
  cloudflare/cloudflared:latest tunnel route dns wuchang-tunnel admin.wuchang.org.tw

docker run --rm \
  -v "${USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" \
  cloudflare/cloudflared:latest tunnel route dns wuchang-tunnel monitor.wuchang.org.tw
```

---

## ✅ 首頁訪問地址

設定完成後，商家和居民可以通過以下地址訪問首頁：

- **首頁：** http://www.wuchang.life ✅
- **或 HTTPS：** https://www.wuchang.life（如果 Caddy 配置 SSL）

---

## 📋 完整服務地址列表

設定完成後，所有服務地址：

| 服務 | 地址 | 說明 |
|-----|------|------|
| **首頁** | http://www.wuchang.life | 主頁面（必須使用此域名） |
| Odoo ERP 系統 | https://app.wuchang.org.tw | 主要業務系統 |
| AI 介面 | https://ai.wuchang.org.tw | AI 智能助手 |
| 容器管理 | https://admin.wuchang.org.tw | 系統管理 |
| 系統監控 | https://monitor.wuchang.org.tw | 服務狀態監控 |

---

## ⚠️ 重要提醒

1. **首頁域名必須是 `www.wuchang.life`**
   - 不能使用 `wuchang.org.tw`
   - 不能使用 `wuchang.life`（沒有 www）
   - 必須是 `www.wuchang.life`

2. **首頁使用 HTTP 協議**
   - 根據要求，首頁使用 `http://`（不是 `https://`）
   - 如需 HTTPS，需要在 Caddy 配置 SSL

3. **確保 Caddy 配置正確**
   - 確認 Caddy 容器可以正確提供首頁服務
   - 確認首頁檔案已掛載到容器中

---

## 🔧 確認 Caddy 配置

**檢查 Caddy 容器是否運行：**

```bash
docker ps | Select-String caddy
```

**檢查首頁檔案是否可訪問：**

```bash
# 本地測試
curl http://localhost:80
```

**檢查 Caddy 配置：**

```bash
docker exec wuchangv510-caddy-1 cat /etc/caddy/Caddyfile
```

應該看到 `www.wuchang.life` 的配置。

---

## ✅ 完成檢查清單

設定完成後，確認：

- [ ] Cloudflare 配置已更新（包含 `www.wuchang.life`）
- [ ] DNS 路由已設定（`www.wuchang.life`）
- [ ] Caddy 容器運行正常
- [ ] 首頁檔案已掛載到 Caddy
- [ ] 容器已重啟並正常運行
- [ ] DNS 解析成功（`www.wuchang.life`）
- [ ] HTTP 服務可以訪問（`http://www.wuchang.life`）
- [ ] 首頁內容顯示正常

---

## 📝 相關檔案

- `index.html` - 首頁檔案
- `cloudflared/config.yml` - Cloudflare 配置（已更新）
- `check_homepage_config.py` - 首頁檢查腳本
- `HOMEPAGE_ENTRANCE_PORTAL_GUIDE.md` - 首頁功能指南

---

**設定指南產生時間：** 2026-01-20  
**首頁地址：** **http://www.wuchang.life**（必須使用此域名）
