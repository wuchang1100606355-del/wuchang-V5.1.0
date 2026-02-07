# Wuchang OS V5.1.0 - 服務端口連結

**更新時間**: 2026-01-07

---

## 🌐 核心服務

### 1. Odoo 主系統
- **名稱**: wuchang-web
- **本地連結**: http://localhost:8069
- **描述**: Odoo ERP 主系統，包含所有 Wuchang 模組

### 2. 數據庫 (PostgreSQL)
- **名稱**: db
- **端口**: 5432 (內部)
- **描述**: PostgreSQL 數據庫服務（僅內部訪問）

---

## 🤖 AI 服務

### 3. Ollama (本地 LLM)
- **名稱**: ollama
- **本地連結**: http://localhost:11434
- **API 文檔**: http://localhost:11434/api/tags
- **描述**: 本地大語言模型服務，小j 的主要 AI 引擎

### 4. Open WebUI (AI 界面)
- **名稱**: open-webui
- **本地連結**: http://localhost:8080
- **描述**: Ollama 的 Web 管理界面

---

## 🌍 網絡服務

### 5. Caddy (反向代理)
- **名稱**: caddy
- **HTTP**: http://localhost:80
- **HTTPS**: https://localhost:443
- **描述**: 反向代理和 SSL 終止

### 6. Caddy UI (管理界面)
- **名稱**: caddy-ui
- **本地連結**: http://localhost:8081
- **HTTPS**: https://localhost:8444
- **描述**: Caddy 管理界面

### 7. Cloudflare Tunnel
- **名稱**: cloudflared
- **描述**: Cloudflare 隧道服務（無本地端口）

---

## 🛠️ 管理工具

### 8. Portainer (容器管理)
- **名稱**: portainer
- **本地連結**: http://localhost:9000
- **描述**: Docker 容器可視化管理界面

### 9. Uptime Kuma (監控)
- **名稱**: uptime-kuma
- **本地連結**: http://localhost:3001
- **描述**: 服務監控和狀態檢查工具

---

## 📋 快速訪問列表

```
核心服務:
  - Odoo:        http://localhost:8069
  - Ollama:      http://localhost:11434
  - Open WebUI:  http://localhost:8080

管理工具:
  - Portainer:   http://localhost:9000
  - Uptime Kuma: http://localhost:3001
  - Caddy UI:    http://localhost:8081

網絡服務:
  - Caddy HTTP:  http://localhost:80
  - Caddy HTTPS: https://localhost:443
```

---

## 🔗 常用 API 端點

### Ollama API
- **模型列表**: http://localhost:11434/api/tags
- **生成請求**: http://localhost:11434/api/generate
- **聊天請求**: http://localhost:11434/api/chat

### Odoo API
- **健康檢查**: http://localhost:8069/web/health
- **Web 界面**: http://localhost:8069/web

---

## 💡 使用提示

1. **首次訪問 Odoo**: 需要創建數據庫或登入現有數據庫
2. **Ollama 測試**: 訪問 http://localhost:11434/api/tags 查看可用模型
3. **容器管理**: 使用 Portainer 可視化管理所有容器
4. **服務監控**: Uptime Kuma 會自動監控所有服務狀態

---

**注意**: 所有連結均為本地訪問（localhost）。如需外部訪問，請配置相應的網絡設置。
