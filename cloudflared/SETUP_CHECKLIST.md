# Cloudflare Tunnel 配置檢查清單

## ✅ 配置步驟檢查

### 步驟 1：獲取憑證
- [ ] 訪問 Cloudflare Dashboard
- [ ] 進入 Zero Trust → Networks → Tunnels
- [ ] 建立或選擇 Tunnel
- [ ] 下載或記錄憑證資訊

### 步驟 2：建立 credentials.json
- [ ] 複製 `credentials.json.template` 為 `credentials.json`
- [ ] 填入 `AccountTag`
- [ ] 填入 `TunnelSecret`
- [ ] 填入 `TunnelID`
- [ ] 確認 `TunnelName` 正確

### 步驟 3：更新 config.yml
- [ ] 複製 `config.yml.template` 為 `config.yml`
- [ ] 將 `<YOUR_TUNNEL_ID>` 替換為實際 Tunnel ID
- [ ] 確認所有 hostname 正確
- [ ] 確認所有 service 路徑正確

### 步驟 4：配置 DNS 路由
- [ ] 在 Cloudflare Dashboard 配置 CNAME 記錄
- [ ] `www.wuchang.life` → `<tunnel-id>.cfargotunnel.com`
- [ ] `wuchang.life` → `<tunnel-id>.cfargotunnel.com`
- [ ] 確認 Proxy 狀態為開啟（橙色雲朵）

### 步驟 5：複製檔案到容器
- [ ] 複製 `credentials.json` 到容器
- [ ] 複製 `config.yml` 到容器
- [ ] 確認檔案權限正確

### 步驟 6：重啟容器
- [ ] 重啟 `wuchangv510-cloudflared-1` 容器
- [ ] 檢查容器日誌
- [ ] 確認連接成功

### 步驟 7：驗證
- [ ] 測試 `https://www.wuchang.life` 可訪問
- [ ] 測試 `https://wuchang.life` 可訪問
- [ ] 檢查 SSL 證書有效性
- [ ] 確認無錯誤訊息

---

## 📋 需要填寫的資訊

### 從 Cloudflare Dashboard 取得：

1. **AccountTag (Account ID)**
   - 位置：Dashboard 右側面板
   - 格式：32 字元字串

2. **TunnelID**
   - 位置：Zero Trust → Networks → Tunnels
   - 格式：32 字元字串

3. **TunnelSecret**
   - 位置：下載的憑證檔案或建立 Tunnel 時顯示
   - 格式：Base64 編碼字串

---

## 🔍 驗證命令

```bash
# 檢查容器狀態
docker ps | grep cloudflared

# 檢查日誌
docker logs wuchangv510-cloudflared-1

# 測試訪問
curl -I https://www.wuchang.life
curl -I https://wuchang.life

# 檢查 DNS
nslookup www.wuchang.life
nslookup wuchang.life
```

---

## ⚠️ 注意事項

1. **憑證檔案安全**：`credentials.json` 包含敏感資訊，不要提交到版本控制
2. **Tunnel ID**：確保 `config.yml` 和 `credentials.json` 中的 Tunnel ID 一致
3. **DNS 傳播**：DNS 變更可能需要 5-10 分鐘才能生效
4. **容器路徑**：Docker 容器內路徑為 `/etc/cloudflared/`

---

**建立日期**：2026-01-22
