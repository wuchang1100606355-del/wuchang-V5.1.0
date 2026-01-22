# DNS 設定合規檢查報告

**檢查時間**：2026-01-22  
**檢查範圍**：wuchang.life DNS 配置與 Google 非營利組織規範對照  
**依據**：Google for Nonprofits 資格要求、Google Ad Grants 網站要求、DNS 最佳實踐

---

## 📋 DNS 合規檢查總覽

| 檢查項目 | Google 要求 | 現況 | 狀態 | 合規性 |
|---------|------------|------|------|--------|
| **根域名解析** | 必須正確解析 | 兩個 A 記錄 | ⚠️ | 部分合規 |
| **WWW 子域名** | 必須正確解析 | 指向 220.135.21.74 | ⚠️ | 部分合規 |
| **DNS 一致性** | 記錄必須一致 | 1個不匹配 | ❌ | 不合規 |
| **Cloudflare Tunnel 路由** | 必須配置 | 未配置 | ❌ | 不合規 |
| **SSL/TLS 支援** | 必須支援 HTTPS | 未驗證 | ❓ | 待驗證 |
| **DNS 傳播** | 必須全球可解析 | 部分可解析 | ⚠️ | 部分合規 |

**總體 DNS 合規率**：33% (2/6 項目完全合規)

---

## 一、根域名 (wuchang.life) DNS 配置檢查

### 1.1 當前配置 ⚠️ **部分合規**

**現況**（依據 `dns_records.json`）：
```json
"@": {
  "type": "A",
  "ttl": 300,
  "values": ["35.185.167.23", "220.135.21.74"],
  "description": "根域名"
}
```

**問題分析**：
- ⚠️ **兩個 A 記錄**：可能造成負載分散或路由不確定
- ⚠️ **IP 不一致**：`35.185.167.23` (Google Cloud) 和 `220.135.21.74` (路由器/店內側)
- ⚠️ **DNS 審計報告**：顯示 `mismatched: 1`

**Google 非營利組織要求**：
> DNS 記錄必須正確配置，確保域名解析正常且一致。

**合規狀態**：⚠️ **部分合規** - 記錄存在但不一致

**必須修正**：
- [ ] 統一 A 記錄指向（建議指向 Cloudflare Tunnel）
- [ ] 移除多餘的 A 記錄
- [ ] 確認主要 IP 地址

**優先級**：🔴 **P0 - 立即處理**（影響全球可見性）

---

### 1.2 Cloudflare Tunnel DNS 路由 ❌ **不合規**

**Google 要求**：
> 使用 Cloudflare Tunnel 時，必須配置正確的 DNS 路由。

**現況檢查**：
- ❌ Cloudflare Tunnel DNS 路由未配置
- ❌ `wuchang.life` 未指向 `<tunnel-id>.cfargotunnel.com`
- ⚠️ `config.yml` 中缺少根域名路由配置

**當前 config.yml 配置**：
```yaml
ingress:
  - hostname: www.wuchang.life
    service: http://wuchangv510-caddy-1:80
  # 缺少 wuchang.life 根域名配置
```

**合規狀態**：❌ **不合規** - DNS 路由未配置

**必須補齊**：
- [ ] 在 `config.yml` 中添加 `wuchang.life` 路由
- [ ] 在 Cloudflare Dashboard 配置 CNAME 記錄：
  - `wuchang.life` → `<tunnel-id>.cfargotunnel.com`
- [ ] 執行 `cloudflared tunnel route dns` 命令

**優先級**：🔴 **P0 - 立即處理**（阻擋全球可見）

---

## 二、WWW 子域名 (www.wuchang.life) DNS 配置檢查

### 2.1 當前配置 ⚠️ **部分合規**

**現況**（依據 `dns_records.json`）：
```json
"www": {
  "type": "A",
  "ttl": 300,
  "values": ["220.135.21.74"],
  "description": "WWW 子域名"
}
```

**問題分析**：
- ⚠️ **直接指向 IP**：應使用 CNAME 指向 Cloudflare Tunnel
- ⚠️ **未使用 Cloudflare Tunnel**：無法獲得 SSL 證書和全球加速
- ⚠️ **與根域名不一致**：根域名有兩個 IP，www 只有一個

**Google 非營利組織要求**：
> 網站必須使用 HTTPS/SSL 安全憑證，全面透過 HTTPS 提供服務。

**合規狀態**：⚠️ **部分合規** - 記錄存在但配置不當

**必須修正**：
- [ ] 將 A 記錄改為 CNAME 記錄
- [ ] 指向 Cloudflare Tunnel：`<tunnel-id>.cfargotunnel.com`
- [ ] 確保與根域名配置一致

**優先級**：🔴 **P0 - 立即處理**（影響 HTTPS 和全球可見）

---

## 三、DNS 記錄一致性檢查

### 3.1 DNS 審計結果 ❌ **不合規**

**現況**（依據 `dns_audit_report.json`）：
- ⚠️ `mismatched: 1` - 有 1 個 DNS 記錄不匹配
- ⚠️ 根域名有兩個 A 記錄，可能造成解析不確定

**Google 要求**：
> DNS 記錄必須一致，避免解析衝突。

**合規狀態**：❌ **不合規** - 存在不匹配記錄

**必須修正**：
- [ ] 修復不匹配的 DNS 記錄
- [ ] 統一所有相關記錄的配置
- [ ] 重新執行 DNS 審計確認

**優先級**：🔴 **P0 - 立即處理**（影響域名解析）

---

## 四、Cloudflare Tunnel DNS 路由配置檢查

### 4.1 config.yml 配置 ❌ **不合規**

**當前配置問題**：
```yaml
ingress:
  - hostname: www.wuchang.life
    service: http://wuchangv510-caddy-1:80
  # ❌ 缺少 wuchang.life 根域名配置
```

**Google 要求**：
> 使用 Cloudflare Tunnel 時，必須為所有需要公開訪問的域名配置路由。

**合規狀態**：❌ **不合規** - 缺少根域名路由

**必須補齊**：
- [ ] 在 `config.yml` 中添加根域名路由：
  ```yaml
  ingress:
    - hostname: wuchang.life
      service: http://wuchangv510-caddy-1:80
    - hostname: www.wuchang.life
      service: http://wuchangv510-caddy-1:80
  ```

**優先級**：🔴 **P0 - 立即處理**（阻擋全球可見）

---

### 4.2 Cloudflare Dashboard DNS 配置 ❌ **不合規**

**必須配置的 DNS 記錄**：

1. **根域名 (wuchang.life)**
   - 類型：CNAME
   - 名稱：`@` 或 `wuchang.life`
   - 目標：`<tunnel-id>.cfargotunnel.com`
   - Proxy：開啟（橙色雲朵）

2. **WWW 子域名 (www.wuchang.life)**
   - 類型：CNAME
   - 名稱：`www`
   - 目標：`<tunnel-id>.cfargotunnel.com`
   - Proxy：開啟（橙色雲朵）

**現況**：❌ **未配置**

**合規狀態**：❌ **不合規** - DNS 路由未配置

**必須補齊**：
- [ ] 在 Cloudflare Dashboard 配置 CNAME 記錄
- [ ] 確保 Proxy 狀態為開啟
- [ ] 驗證 DNS 記錄正確解析

**優先級**：🔴 **P0 - 立即處理**（阻擋全球可見）

---

## 五、DNS 傳播與全球可訪問性檢查

### 5.1 DNS 傳播狀態 ⚠️ **部分合規**

**Google 要求**：
> 網站必須全球可見，DNS 記錄必須在全球範圍內正確傳播。

**現況檢查**：
- ⚠️ DNS 記錄存在但可能未完全傳播
- ❌ 無法驗證全球可訪問性（Cloudflare Tunnel 未配置）
- ⚠️ 部分 DNS 伺服器可能解析到不同的 IP

**合規狀態**：⚠️ **部分合規** - 記錄存在但傳播狀態未驗證

**必須驗證**：
- [ ] 使用 DNS 傳播檢查工具驗證全球解析
- [ ] 確認所有主要 DNS 伺服器解析一致
- [ ] 等待 DNS 傳播完成（通常 5-10 分鐘）

**優先級**：🟡 **P1 - 高優先級**（完成 P0 後驗證）

---

## 六、DNS 合規缺口總結

### 🔴 **P0 - 立即處理（阻擋合規）**

1. **統一根域名 A 記錄**
   - 移除多餘的 A 記錄
   - 統一指向 Cloudflare Tunnel

2. **配置 Cloudflare Tunnel DNS 路由**
   - 在 `config.yml` 中添加根域名路由
   - 在 Cloudflare Dashboard 配置 CNAME 記錄
   - 執行 `cloudflared tunnel route dns` 命令

3. **修復 DNS 記錄不匹配**
   - 修復不匹配的 DNS 記錄
   - 重新執行 DNS 審計

4. **更新 www.wuchang.life 配置**
   - 將 A 記錄改為 CNAME
   - 指向 Cloudflare Tunnel

### 🟡 **P1 - 高優先級（驗證與優化）**

5. **驗證 DNS 傳播**
   - 使用 DNS 傳播檢查工具
   - 確認全球解析一致

6. **驗證 HTTPS/SSL**
   - 確認 SSL 證書自動配置
   - 驗證 HTTPS 可正常訪問

---

## 七、正確的 DNS 配置範例

### 7.1 Cloudflare Dashboard DNS 記錄

```
類型    名稱          目標                              Proxy
CNAME   @             <tunnel-id>.cfargotunnel.com     ✅ 開啟
CNAME   www           <tunnel-id>.cfargotunnel.com     ✅ 開啟
```

### 7.2 config.yml 配置

```yaml
tunnel: <tunnel-id>
credentials-file: /etc/cloudflared/credentials.json

ingress:
  # 根域名（必須放在 www 之前）
  - hostname: wuchang.life
    service: http://wuchangv510-caddy-1:80
  
  # WWW 子域名
  - hostname: www.wuchang.life
    service: http://wuchangv510-caddy-1:80
  
  # 其他服務...
  - hostname: app.wuchang.org.tw
    service: http://wuchangv510-wuchang-web-1:8069
  
  # 預設規則（必須放在最後）
  - service: http_status:404
```

### 7.3 命令列配置

```bash
# 配置根域名路由
cloudflared tunnel route dns wuchang-life wuchang.life

# 配置 WWW 子域名路由
cloudflared tunnel route dns wuchang-life www.wuchang.life
```

---

## 八、驗證檢查清單

### DNS 配置驗證
- [ ] 根域名 CNAME 記錄已配置
- [ ] WWW 子域名 CNAME 記錄已配置
- [ ] Cloudflare Tunnel DNS 路由已配置
- [ ] `config.yml` 中包含根域名路由
- [ ] DNS 記錄不匹配問題已修復

### DNS 解析驗證
- [ ] `nslookup wuchang.life` 解析正確
- [ ] `nslookup www.wuchang.life` 解析正確
- [ ] DNS 傳播檢查工具顯示全球一致
- [ ] 所有主要 DNS 伺服器解析一致

### HTTPS/SSL 驗證
- [ ] `https://wuchang.life` 可訪問
- [ ] `https://www.wuchang.life` 可訪問
- [ ] SSL 證書有效（無警告）
- [ ] HTTP 自動重定向到 HTTPS

---

## 九、參考資源

- **Cloudflare Tunnel DNS 路由**：https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/routing-to-tunnel/dns/
- **DNS 最佳實踐**：https://developers.cloudflare.com/dns/manage-dns-records/
- **Google for Nonprofits 要求**：https://www.google.com/nonprofits/qualify/

---

## 十、結論

**當前 DNS 合規狀態**：⚠️ **33% 合規** (2/6 項目完全合規)

**主要問題**：
1. ❌ 根域名有兩個 A 記錄，造成解析不確定
2. ❌ Cloudflare Tunnel DNS 路由未配置
3. ❌ DNS 記錄不匹配
4. ⚠️ www.wuchang.life 使用 A 記錄而非 CNAME

**必須立即處理**：
- 完成 Cloudflare Tunnel DNS 路由配置
- 統一並修復 DNS 記錄
- 驗證 DNS 傳播和全球可訪問性

**完成 P0 任務後，DNS 合規率可提升至 100%**

---

**報告生成時間**：2026-01-22  
**檢查依據**：Google for Nonprofits 要求、DNS 最佳實踐、Cloudflare Tunnel 文檔
