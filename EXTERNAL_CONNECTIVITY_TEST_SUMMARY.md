# 外網連線可行性測試摘要

**測試日期**: 2026-01-18  
**測試工具**: `scripts/test_external_connectivity.ps1`

---

## 📊 測試結果

### ✅ 已通過的項目

根據系統當前狀態：

1. **Docker 容器運行狀態**
   - ✅ Caddy 容器運行中 (端口 80, 443)
   - ✅ Odoo 容器運行中 (端口 8069)
   - ✅ Cloudflared 容器運行中 (Tunnel 服務)

2. **本地端口監聽**
   - ✅ 端口 80 (HTTP) - Caddy 監聽
   - ✅ 端口 443 (HTTPS) - Caddy 監聽
   - ✅ 端口 8069 (Odoo) - Odoo 監聽
   - ✅ 端口 8080 (AI 服務) - Open WebUI 監聽

3. **服務可訪問性**
   - ✅ 本地訪問正常
   - ✅ 內網訪問正常

---

## 🔍 需要驗證的項目

### 1. Cloudflare Tunnel 連接狀態

**檢查方法**:
```powershell
docker logs <cloudflared-container-name> --tail 20
```

**預期結果**:
- 日誌中應顯示 "connected" 或 "registered"
- 無錯誤訊息

**如果未連接**:
1. 檢查環境變數 `CLOUDFLARE_TUNNEL_TOKEN`
2. 驗證 Token 是否有效
3. 檢查網絡連接

---

### 2. DNS 解析

**測試命令**:
```powershell
Resolve-DnsName -Name "wuchang.life" -Type A
```

**預期結果**:
- 應解析到 Cloudflare IP 地址
- 或解析到 Tunnel 地址

**如果解析失敗**:
1. 檢查 Cloudflare DNS 設置
2. 確認 CNAME 記錄指向正確的 Tunnel
3. 等待 DNS 傳播（TTL 時間）

---

### 3. HTTPS 外網訪問

**測試命令**:
```powershell
Invoke-WebRequest -Uri "https://wuchang.life/health" -UseBasicParsing
```

**預期結果**:
- 返回 HTTP 200 狀態碼
- SSL 證書有效
- 響應時間 < 3 秒

**如果無法訪問**:
1. 檢查 Cloudflare Tunnel 是否連接
2. 驗證 Caddy 配置
3. 檢查防火牆規則

---

## 🚀 執行完整測試

### 方法 1: 使用測試腳本（推薦）

```powershell
# 完整測試
powershell -ExecutionPolicy Bypass -File scripts\test_external_connectivity.ps1 -Detailed

# 快速測試
powershell -ExecutionPolicy Bypass -File scripts\test_external_connectivity_simple.ps1

# 包含最高權限 UI 測試
powershell -ExecutionPolicy Bypass -File scripts\test_external_connectivity.ps1 -TestSupremeUI
```

### 方法 2: 手動測試

```powershell
# 1. 檢查容器
docker ps --filter "name=cloudflared"
docker ps --filter "name=caddy"

# 2. 檢查端口
Test-NetConnection -ComputerName localhost -Port 80
Test-NetConnection -ComputerName localhost -Port 443

# 3. DNS 解析
Resolve-DnsName -Name "wuchang.life" -Type A

# 4. HTTPS 連接
Invoke-WebRequest -Uri "https://wuchang.life/health" -UseBasicParsing

# 5. 公網 IP
Invoke-WebRequest -Uri "https://api.ipify.org" -UseBasicParsing
```

---

## 📋 測試檢查清單

- [ ] Cloudflare Tunnel 容器運行中
- [ ] Tunnel 連接狀態正常
- [ ] Caddy 容器運行中
- [ ] 本地端口 80, 443 監聽中
- [ ] DNS 解析正常
- [ ] HTTPS 外網訪問成功
- [ ] 最高權限 UI 可訪問（可選）

---

## 🔧 故障排除

### Cloudflare Tunnel 未連接

**解決步驟**:
1. 檢查環境變數:
   ```powershell
   Get-Content .env | Select-String "CLOUDFLARE"
   ```

2. 查看容器日誌:
   ```powershell
   docker logs <cloudflared-container-name>
   ```

3. 重啟容器:
   ```powershell
   docker-compose restart cloudflared-named
   ```

### DNS 解析失敗

**解決步驟**:
1. 登入 Cloudflare Dashboard
2. 檢查 DNS 記錄配置
3. 確認 CNAME 指向正確的 Tunnel 地址

### HTTPS 無法訪問

**解決步驟**:
1. 檢查 Caddy 配置:
   ```powershell
   Get-Content wuchang_os\Caddyfile
   ```

2. 查看 Caddy 日誌:
   ```powershell
   docker logs <caddy-container-name>
   ```

3. 重啟 Caddy:
   ```powershell
   docker-compose restart caddy
   ```

---

## 📝 測試報告

執行測試後會生成詳細報告，包含：
- 各項測試的詳細結果
- 錯誤訊息（如有）
- 建議的修復步驟

報告文件位置: `external_connectivity_test_YYYYMMDD_HHMMSS.txt`

---

## 🎯 下一步

1. **執行測試**: 使用提供的測試腳本
2. **查看結果**: 檢查測試報告
3. **修復問題**: 根據報告中的建議修復
4. **重新測試**: 確認問題已解決

---

## 📞 支援

如有問題，請：
1. 查看測試報告中的詳細錯誤
2. 檢查容器日誌
3. 參考故障排除指南
4. 聯繫系統管理員
