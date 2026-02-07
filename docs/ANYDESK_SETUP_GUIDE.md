# POS 設備 AnyDesk 設定指南

**文件日期**: 2025-01-07  
**系統版本**: Wuchang OS V5.1.0  
**設備**: v3_mix_edla_gl (主要 POS)

---

## 📋 AnyDesk 資訊

### v3_mix_edla_gl (主要 POS)
- **AnyDesk ID**: `748464958`
- **設定狀態**: 未完成
- **IP 地址**: 192.168.50.86

---

## 🚀 設定步驟

### Step 1: 在 v3_mix_edla_gl 設備上安裝 AnyDesk

1. **下載 AnyDesk**
   - 訪問: https://anydesk.com/zh/downloads/android
   - 下載 Android 版本
   - 安裝到設備

2. **開啟 AnyDesk**
   - 啟動 AnyDesk 應用程式
   - 確認 AnyDesk ID 為 `748464958`

### Step 2: 設定 AnyDesk

1. **設定無人值守訪問**
   - 進入 AnyDesk 設定
   - 啟用「無人值守訪問」
   - 設定訪問密碼（建議使用強密碼）

2. **設定安全選項**
   - 啟用「僅接受已知的連接」
   - 設定「允許的設備列表」（可選）

3. **測試連線**
   - 從其他設備使用 AnyDesk ID `748464958` 連線
   - 確認可以成功連線

### Step 3: 更新設備記錄

#### 方式 1: 使用 PowerShell 腳本

```powershell
# 更新 AnyDesk ID（設定狀態：未完成）
.\scripts\configure_anydesk_pos.ps1 -AnyDeskID "748464958"

# 設定完成後，標記為已完成
.\scripts\configure_anydesk_pos.ps1 -AnyDeskID "748464958" -Configured
```

#### 方式 2: 使用 Python 腳本

```bash
# 更新 AnyDesk ID（設定狀態：未完成）
python scripts\configure_anydesk_pos.py --anydesk-id "748464958"

# 設定完成後，標記為已完成
python scripts\configure_anydesk_pos.py --anydesk-id "748464958" --configured
```

#### 方式 3: 透過 Odoo UI

1. 訪問: http://192.168.50.249:8069/web/login
2. 進入「基礎設施」→「設備」
3. 找到「v3_mix_edla_gl」
4. 編輯設備：
   - **AnyDesk ID**: `748464958`
   - **AnyDesk 密碼**: （填入設定的密碼）
   - **AnyDesk 已設定**: 勾選（設定完成後）

---

## ✅ 設定完成確認

設定完成後，應確認：

- [ ] AnyDesk 已安裝在 v3_mix_edla_gl 設備上
- [ ] AnyDesk ID 為 `748464958`
- [ ] 無人值守訪問已啟用
- [ ] 可以從其他設備成功連線
- [ ] Odoo 設備記錄中已更新 AnyDesk 資訊
- [ ] 「AnyDesk 已設定」已勾選

---

## 🔒 安全建議

1. **強密碼**
   - 使用強密碼保護 AnyDesk 訪問
   - 定期更換密碼

2. **訪問控制**
   - 僅允許已知的設備連線
   - 記錄所有遠程訪問活動

3. **網路安全**
   - 確保設備在安全的網路環境中
   - 考慮使用 VPN 進行遠程訪問

---

## 📊 AnyDesk 設定狀態

| 設備 | AnyDesk ID | 設定狀態 | 備註 |
|------|------------|----------|------|
| v3_mix_edla_gl | 748464958 | ⏳ 未完成 | 主要 POS 設備 |

---

## 💡 注意事項

1. **AnyDesk ID 是唯一的**
   - 每個設備有唯一的 AnyDesk ID
   - `748464958` 是 v3_mix_edla_gl 的 ID

2. **設定完成後**
   - 記得在 Odoo 中標記為「已設定」
   - 記錄 AnyDesk 密碼（安全儲存）

3. **遠程訪問**
   - 僅在需要時啟用遠程訪問
   - 使用完畢後建議關閉

---

**文件版本**: 1.0  
**最後更新**: 2025-01-07  
**維護者**: 小J (Little J)
