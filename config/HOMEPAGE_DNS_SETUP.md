# 首頁 DNS 設定指南

**更新時間：** 2026-01-20  
**目的：** 為首頁（wuchang.org.tw）設定 DNS 和 Cloudflare Tunnel

---

## 📊 當前狀態

### ✅ 已確認

- ✅ **首頁檔案存在**：`index.html` (22.39 KB)
- ✅ **DNS 解析成功**：`wuchang.org.tw` → `45.76.192.186`
- ✅ **服務可訪問**：`https://wuchang.org.tw` (HTTP 200)
- ✅ **Web 伺服器運行中**：`wuchangv510-caddy-1` (端口 80/443)

### ⚠️ 需要設定

- ⚠️ **首頁域名未在 Cloudflare 配置中**
- ⚠️ **首頁域名未設定 DNS 路由**

---

## 🔧 設定步驟

### 步驟 1: 更新 Cloudflare 配置

**已更新 `cloudflared/config.yml`**，新增首頁域名配置：

```yaml
ingress:
  # 首頁（主域名）
  - hostname: wuchang.org.tw
    service: http://wuchangv510-caddy-1:80
  
  # WWW 子域名（指向首頁）
  - hostname: www.wuchang.org.tw
    service: http://wuchangv510-caddy-1:80
  
  # ... 其他服務 ...
```

**說明：**
- 首頁透過 **Caddy** 容器提供（端口 80）
- `wuchang.org.tw` 和 `www.wuchang.org.tw` 都指向首頁

---

### 步驟 2: 配置 DNS 路由

在設定 Cloudflare Tunnel 時，需要新增首頁域名的 DNS 路由：

```bash
# 使用 Docker 執行（推薦）
docker run --rm \
  -v "${USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" \
  cloudflare/cloudflared:latest tunnel route dns wuchang-tunnel wuchang.org.tw

docker run --rm \
  -v "${USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" \
  cloudflare/cloudflared:latest tunnel route dns wuchang-tunnel www.wuchang.org.tw
```

**完整 DNS 路由設定（包含首頁）：**

```bash
# 首頁
cloudflared tunnel route dns wuchang-tunnel wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel www.wuchang.org.tw

# 其他服務
cloudflared tunnel route dns wuchang-tunnel app.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel ai.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel admin.wuchang.org.tw
cloudflared tunnel route dns wuchang-tunnel monitor.wuchang.org.tw
```

---

### 步驟 3: 確認 Caddy 配置

確認 Caddy 容器可以正確提供首頁服務：

**檢查首頁檔案是否掛載到 Caddy：**

```bash
docker exec wuchangv510-caddy-1 ls -la /usr/share/caddy/
```

**或檢查 Caddy 配置：**

```bash
docker exec wuchangv510-caddy-1 cat /etc/caddy/Caddyfile
```

**確認首頁可以被訪問：**

```bash
# 本地測試
curl http://localhost:80

# 或訪問
http://localhost:80
```

---

### 步驟 4: 重啟 Cloudflare Tunnel 容器

更新配置後，需要重啟容器：

```bash
docker restart wuchangv510-cloudflared-1
```

**查看日誌確認：**

```bash
docker logs wuchangv510-cloudflared-1 --tail 20
```

應該看到首頁域名已註冊。

---

### 步驟 5: 驗證設定

**檢查 DNS 解析：**

```bash
nslookup wuchang.org.tw
nslookup www.wuchang.org.tw
```

應該解析到 Cloudflare IP（通常是 `104.x.x.x` 或 `172.x.x.x` 範圍）。

**檢查服務訪問：**

```bash
# HTTPS 訪問
curl -I https://wuchang.org.tw
curl -I https://www.wuchang.org.tw

# 或直接在瀏覽器訪問
https://wuchang.org.tw
https://www.wuchang.org.tw
```

**執行檢查腳本：**

```bash
python check_homepage_config.py
```

---

## 📋 首頁訪問地址

設定完成後，商家和居民可以通過以下地址訪問首頁：

- **主域名：** https://wuchang.org.tw
- **WWW 子域名：** https://www.wuchang.org.tw

---

## 🔍 首頁功能

根據 `index.html` 和 `HOMEPAGE_ENTRANCE_PORTAL_GUIDE.md`，首頁提供：

1. **關於我們** - 組織身份說明
2. **使命與活動** - 公益目標描述
3. **社區統計** - 數據展示
4. **系統功能入口** - 連結到各個子系統
5. **聯絡方式** - 聯絡資訊

---

## 🔗 首頁連結的其他服務

首頁提供以下系統功能的入口連結：

| 功能模組 | 連結目標 |
|---------|---------|
| 社區分析儀表板 | `/wuchang-community` |
| 社區商店 | `http://shop.wuchang.life` |
| 3D 地圖查看器 | `/map-3d-viewer` |
| 物業管理系統 | `http://odoo.wuchang.life` |
| 核心服務 | `http://core.wuchang.life` |
| 系統架構 | `/system-architecture` |

---

## ✅ 完成檢查清單

設定完成後，確認：

- [ ] Cloudflare 配置已更新（包含首頁域名）
- [ ] DNS 路由已設定（wuchang.org.tw 和 www.wuchang.org.tw）
- [ ] Caddy 容器運行正常
- [ ] 首頁檔案已掛載到 Caddy
- [ ] 容器已重啟並正常運行
- [ ] DNS 解析成功（兩個域名）
- [ ] HTTPS 服務可以訪問（兩個域名）
- [ ] 首頁內容顯示正常

---

## 📝 相關檔案

- `index.html` - 首頁檔案
- `HOMEPAGE_ENTRANCE_PORTAL_GUIDE.md` - 首頁功能指南
- `cloudflared/config.yml` - Cloudflare 配置（已更新）
- `check_homepage_config.py` - 首頁檢查腳本

---

**設定指南產生時間：** 2026-01-20  
**狀態：** 配置已更新，需要執行 DNS 路由設定
