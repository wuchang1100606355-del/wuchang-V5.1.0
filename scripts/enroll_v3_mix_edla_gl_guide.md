# v3_mix_edla_gl 設備納管指南

**設備資訊**：
- 設備名稱: v3_mix_edla_gl
- Android 版本: 13
- IP 地址: 192.168.50.86
- 通訊埠: 41895
- 開發者模式: ✅ 已開啟
- USB/GPU/WiFi 偵錯: ✅ 已開啟

---

## 🚀 納管方式

### 方式 1: API 納管（Odoo 服務運行時）

當 VM 伺服器 (192.168.50.84) 的 Odoo 服務運行時：

```powershell
.\scripts\enroll_v3_mix_edla_gl.ps1
```

### 方式 2: Odoo UI 手動納管（推薦）

1. **登入 Odoo**
   - 訪問: `http://192.168.50.249:8069/web/login` (VM 為本地機器)
   - 使用管理員帳號登入

2. **進入設備管理**
   - 「應用程式」→「Wuchang Core」→「基礎設施」→「設備」

3. **建立新設備**
   - 點擊「建立」
   - 填寫資訊：
     - **名稱**: `v3_mix_edla_gl`
     - **IP 地址**: `192.168.50.86`
     - **設備類型**: `POS Terminal`
     - **狀態**: `Online`
     - **備註**: 
       ```
       Android 13 POS 設備
       IP: 192.168.50.86:41895
       開發者模式: 已開啟
       USB/GPU/WiFi 偵錯: 已開啟
       納管時間: 2025-01-07
       ```

4. **儲存**

### 方式 3: SQL 直接納管

在 Odoo 中執行 SQL：

1. 登入 Odoo
2. 啟用「開發者模式」
3. 「設定」→「技術」→「資料庫結構」→「執行 SQL」
4. 執行 `scripts/enroll_v3_mix_edla_gl_sql.sql` 中的 SQL 語句

---

## ✅ 納管後確認

納管成功後，在 Odoo 中應該可以看到：
- 設備名稱: v3_mix_edla_gl
- IP 地址: 192.168.50.86
- 狀態: Online
- 設備類型: POS Terminal

---

## 📋 後續步驟

1. **Google Workspace MDM 註冊**
   - 在 Google Workspace Admin Console 註冊設備
   - 設定 Kiosk 模式鎖定到 Odoo POS 應用

2. **應用程式安裝**
   - 安裝 Odoo POS 應用
   - 配置 Google Drive 同步

3. **安全策略設定**
   - 設備加密
   - 密碼策略
   - 應用程式限制
