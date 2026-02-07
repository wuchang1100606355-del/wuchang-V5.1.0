# cert_key.tar 同步報告

**執行時間：** 2026-01-20  
**來源位置：** `%USERPROFILE%\Downloads\cert_key.tar`  
**目標位置：** `cloudflared\cert_key.tar`

---

## ✅ 操作完成

### 1. 檔案複製
- ✅ 已從 Downloads 複製到 `cloudflared` 目錄
- ✅ 檔案大小：6144 bytes
- ✅ 最後修改時間：2026/1/21 下午 09:19:46

### 2. 檔案內容
tar 檔案包含以下檔案：
- ✅ `cert.pem` - Cloudflare Tunnel 憑證
- ✅ `key.pem` - Cloudflare Tunnel 私鑰

### 3. 解壓縮狀態
- ✅ 已解壓縮到 `cloudflared` 目錄

---

## 📋 檔案位置

```
cloudflared/
├── cert_key.tar (原始壓縮檔)
├── cert.pem (解壓縮的憑證)
└── key.pem (解壓縮的私鑰)
```

---

## ⚙️ 後續配置

這些憑證檔案用於 Cloudflare Tunnel 的命名隧道（Named Tunnel）配置。

### 檢查 config.yml 配置

確認 `cloudflared/config.yml` 中的憑證路徑：

```yaml
tunnel: <TUNNEL_ID>
credentials-file: /path/to/cert.pem
```

或使用環境變數：
```yaml
TUNNEL_TOKEN: <YOUR_TUNNEL_TOKEN>
```

---

## 🔐 安全注意事項

1. **私鑰保護**
   - `key.pem` 是敏感檔案，請確保權限設定正確
   - 不要將私鑰上傳到公開儲存庫

2. **憑證驗證**
   - 確認憑證有效性
   - 檢查憑證到期時間

---

**狀態：** ✅ 完成  
**下一步：** 確認 Cloudflare Tunnel 配置使用這些憑證檔案
