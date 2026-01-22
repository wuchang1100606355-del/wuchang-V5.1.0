# DNS 設定值範本

**網域商**：Squarespace  
**網域**：wuchang.life  
**用途**：Cloudflare Tunnel DNS 路由配置

---

## ⚠️ 重要：設定前必須完成

在填入以下 DNS 設定值之前，您必須先完成 Cloudflare Tunnel 配置：

1. 執行 `cloudflared tunnel login`
2. 執行 `cloudflared tunnel create wuchang-life`
3. 取得 Tunnel ID（例如：`abc123def456789...`）

詳細步驟請參考：`cloudflared/MANUAL_SETUP_GUIDE.md`

---

## 📋 DNS 設定值（待填入）

### 根域名（wuchang.life）

**如果 Squarespace 支援根域名 CNAME**：
```
類型：CNAME
主機名稱：@
指向/目標：[待填入] <tunnel-id>.cfargotunnel.com
TTL：自動（或 300 秒）
```

**範例**（假設 Tunnel ID 是 `abc123def456789`）：
```
類型：CNAME
主機名稱：@
指向/目標：abc123def456789.cfargotunnel.com
TTL：自動
```

---

### WWW 子域名（www.wuchang.life）

```
類型：CNAME
主機名稱：www
指向/目標：[待填入] <tunnel-id>.cfargotunnel.com
TTL：自動（或 300 秒）
```

**範例**（假設 Tunnel ID 是 `abc123def456789`）：
```
類型：CNAME
主機名稱：www
指向/目標：abc123def456789.cfargotunnel.com
TTL：自動
```

---

## 🔍 如何取得 Tunnel ID

### 方法 1：從命令列

```bash
# 列出所有 Tunnel
cloudflared tunnel list

# 輸出會顯示 Tunnel ID，例如：
# ID                                   NAME            CREATED
# abc123def456789...                   wuchang-life    2026-01-22T...
```

### 方法 2：從 Cloudflare Dashboard

1. 訪問：https://one.dash.cloudflare.com/
2. 進入 **Zero Trust** → **Networks** → **Tunnels**
3. 找到您的 Tunnel（例如：`wuchang-life`）
4. 點擊 Tunnel 名稱
5. 在詳細資訊中查看 **Tunnel ID**

---

## 📝 設定步驟摘要

1. **完成 Cloudflare Tunnel 配置**
   - 參考：`cloudflared/MANUAL_SETUP_GUIDE.md`

2. **取得 Tunnel ID**
   - 從命令列或 Cloudflare Dashboard

3. **填入 DNS 設定值**
   - 將 `<tunnel-id>` 替換為實際的 Tunnel ID
   - 例如：`abc123def456789.cfargotunnel.com`

4. **在 Squarespace 設定**
   - 訪問：https://account.squarespace.com/domains/managed/wuchang.life/dns/dns-settings
   - 添加上述 CNAME 記錄

5. **驗證設定**
   - 等待 5-10 分鐘讓 DNS 傳播
   - 使用 `nslookup` 驗證
   - 測試網站可訪問性

---

## ⚠️ 注意事項

1. **Tunnel ID 格式**：通常是 32 字元的字串
2. **完整目標**：必須包含 `.cfargotunnel.com` 後綴
3. **根域名限制**：如果 Squarespace 不支援根域名 CNAME，需要將 DNS 管理轉移到 Cloudflare
4. **DNS 傳播**：設定後需要等待 5-10 分鐘才能生效

---

**建立時間**：2026-01-22  
**相關文檔**：
- `cloudflared/MANUAL_SETUP_GUIDE.md` - Cloudflare Tunnel 手動配置指南
- `SQUARESPACE_DNS_SETUP.md` - Squarespace DNS 設定完整指南
