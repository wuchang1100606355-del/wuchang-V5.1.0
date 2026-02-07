# 容器掛載統計報告

## 📊 總覽

- **總共定義的容器數**: 9 個
- **當前運行的容器數**: 8 個
- **地端檔案夾掛載的容器數**: 3 個
- **總掛載點數**: 7 個地端檔案夾掛載

---

## 📦 容器列表

### 定義的容器（9 個）

1. **wuchang-web** - Odoo 應用服務
2. **db** - PostgreSQL 資料庫
3. **caddy** - 反向代理服務
4. **caddy-ui** - UI 反向代理服務
5. **cloudflared** - Cloudflare 隧道（匿名）
6. **cloudflared-named** - Cloudflare 命名隧道
7. **uptime-kuma** - 服務監控
8. **portainer** - 容器管理 UI
9. **ollama** - 本地 LLM 服務

### 當前運行的容器（8 個）

✅ **wuchang-web** - 運行中  
✅ **db** - 運行中  
✅ **caddy** - 運行中  
✅ **caddy-ui** - 運行中  
✅ **cloudflared** - 運行中  
❌ **cloudflared-named** - 未運行（需要 CLOUDFLARE_TUNNEL_TOKEN）  
✅ **uptime-kuma** - 運行中（健康）  
✅ **portainer** - 運行中  
✅ **ollama** - 運行中  

---

## 📁 地端檔案夾掛載詳情

### 1. wuchang-web 容器（5 個掛載點）

| 地端路徑 | 容器路徑 | 類型 | 說明 |
|---------|---------|------|------|
| `./wuchang_os/addons` | `/mnt/extra-addons` | bind | Odoo 自定義模組 |
| `./downloads/jules` | `/mnt/jules` | bind | Jules 下載目錄（讀寫） |
| `./config` | `/mnt/jules-config` | bind | 配置檔案（只讀） |
| `${AI_MEMORY_PATH}/memory_store` | `/opt/wuchang/memory_store` | bind | AI 記憶體存儲 |
| `${AI_COMMON_PATH}/common_store` | `/opt/wuchang/common_store` | bind | AI 共用存儲 |

### 2. caddy 容器（1 個掛載點）

| 地端路徑 | 容器路徑 | 類型 | 說明 |
|---------|---------|------|------|
| `./wuchang_os/Caddyfile` | `/etc/caddy/Caddyfile` | bind | Caddy 配置文件 |

### 3. caddy-ui 容器（1 個掛載點）

| 地端路徑 | 容器路徑 | 類型 | 說明 |
|---------|---------|------|------|
| `./wuchang_os/Caddyfile` | `/etc/caddy/Caddyfile` | bind | Caddy 配置文件 |

---

## 💾 Docker Volumes（非地端檔案夾）

以下為 Docker 管理的 volumes，不直接掛載地端檔案夾：

- `odoo-web-data` - Odoo Web 數據
- `odoo-db-data` - PostgreSQL 數據
- `caddy-data` - Caddy 數據
- `uptime-kuma-data` - Uptime Kuma 數據
- `portainer-data` - Portainer 數據
- `ollama-data` - Ollama 模型數據

---

## 📈 統計摘要

### 掛載類型分布

- **地端檔案夾掛載 (bind mount)**: 7 個
- **Docker Volumes**: 6 個
- **總掛載點**: 13 個

### 容器掛載分布

- **wuchang-web**: 5 個地端檔案夾 + 1 個 volume
- **caddy**: 1 個地端檔案夾 + 1 個 volume
- **caddy-ui**: 1 個地端檔案夾 + 1 個 volume
- **其他容器**: 僅使用 Docker volumes

---

## 🔍 詳細掛載路徑

### wuchang-web 容器完整掛載

```
地端 -> 容器
─────────────────────────────────────────
C:\wuchang V5.1.0\wuchang_os\addons 
  -> /mnt/extra-addons

C:\wuchang V5.1.0\downloads\jules 
  -> /mnt/jules (rw)

C:\wuchang V5.1.0\config 
  -> /mnt/jules-config (ro)

${AI_MEMORY_PATH}\memory_store 
  -> /opt/wuchang/memory_store

${AI_COMMON_PATH}\common_store 
  -> /opt/wuchang/common_store

odoo-web-data (volume)
  -> /var/lib/odoo
```

### Caddy 容器掛載

```
地端 -> 容器
─────────────────────────────────────────
C:\wuchang V5.1.0\wuchang_os\Caddyfile 
  -> /etc/caddy/Caddyfile

caddy-data (volume)
  -> /data
```

---

## ✅ 合規聲明

符合 Google 非營利組織合規要求

---

## 📝 最後更新

- **報告時間**: 2026-01-07 21:57
- **檢查方式**: docker-compose + docker inspect
