# 店內伺服器認證憑證配置報告

**執行時間：** 2026-01-20  
**憑證來源：** Downloads\cert_key.tar  
**憑證用途：** 路由器識別本機為伺服器的認證憑證

---

## ✅ 憑證檔案狀態

### 憑證位置
```
cloudflared/
├── cert_key.tar (原始壓縮檔, 6144 bytes)
├── cert.pem (憑證檔案, 1956 bytes)
└── key.pem (私鑰檔案, 1679 bytes)
```

### 憑證資訊
- **憑證檔案：** cert.pem
- **私鑰檔案：** key.pem
- **建立時間：** 2026/1/19 上午 09:41:47

---

## 🔧 路由器配置說明

### 用途
這些憑證用於讓路由器識別本機（店內伺服器）的身份，建立安全的伺服器認證連線。

### 配置方式

#### 1. 系統層級配置
憑證可以配置在以下位置：

**Caddy Web Server（HTTPS 服務）**
```yaml
# docker-compose.unified.yml
caddy:
  volumes:
    - ./cloudflared/cert.pem:/etc/caddy/cert.pem:ro
    - ./cloudflared/key.pem:/etc/caddy/key.pem:ro
```

**Caddyfile 配置**
```
https://your-domain.com {
    tls /etc/caddy/cert.pem /etc/caddy/key.pem
    reverse_proxy localhost:8069
}
```

#### 2. 路由器層級配置
路由器可能需要：
- 上傳憑證到路由器管理介面
- 設定路由器的伺服器認證規則
- 配置路由器信任本機伺服器憑證

#### 3. 系統服務配置
如果需要系統服務使用這些憑證：
```bash
# 複製到系統憑證目錄
sudo cp cert.pem /etc/ssl/certs/server-cert.pem
sudo cp key.pem /etc/ssl/private/server-key.pem
sudo chmod 600 /etc/ssl/private/server-key.pem
```

---

## 🔐 安全注意事項

### 私鑰保護
1. **權限設定**
   - 私鑰應限制為只有授權用戶可讀取
   - 建議使用 600 權限（僅所有者可讀寫）

2. **儲存安全**
   - 不要將私鑰上傳到公開儲存庫
   - 定期備份憑證檔案
   - 確保憑證檔案在安全的儲存位置

3. **憑證有效期**
   - 檢查憑證到期時間
   - 在到期前更新憑證

---

## 📋 後續步驟

### 1. 確認路由器配置需求
- 檢查路由器是否需要上傳憑證
- 確認路由器的伺服器認證設定方式

### 2. 配置 Web 伺服器（如需要）
- 如果使用 HTTPS，配置 Caddy 使用這些憑證
- 確認域名與憑證的匹配

### 3. 測試連接
- 確認路由器可以識別伺服器
- 測試 HTTPS 連線（如果配置）

---

## 💡 建議

1. **憑證備份**
   - 保留原始 `cert_key.tar` 檔案
   - 考慮備份到安全位置

2. **憑證管理**
   - 記錄憑證的用途和配置位置
   - 建立憑證更新流程

3. **文件記錄**
   - 記錄路由器的配置方式
   - 記錄憑證使用的服務

---

**狀態：** ✅ 憑證檔案已準備就緒  
**下一步：** 確認路由器配置方式並配置使用憑證
