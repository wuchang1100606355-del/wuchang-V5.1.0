# 合規檢查清單

**檢查日期**：2026-01-15  
**檢查範圍**：完整系統合規狀態

---

## ✅ 基本合規要求

### Google for Nonprofits 驗證

- [x] **已完成 Google for Nonprofits 驗證**（永久事實）
- [x] 驗證狀態記錄在 `AGENT_CONSTITUTION.md`

### 基本隱私保護

- [x] **除法律規範及政府公示外無個資**（預設狀態）
- [x] 合規聲明完整記錄
- [x] 系統感知功能不包含個資

---

## ✅ 個資處理功能（啟用時）

### 功能啟用控制

- [x] **個資處理功能預設未啟用**
- [x] 需明確設定 `WUCHANG_PII_ENABLED=true` 才能啟用
- [x] 未啟用時返回空資料或提示

### 授權機制

- [x] **個資使用需獲得明確授權**
- [x] 授權記錄完整（`accountable_person_authorizations.json`）
- [x] 每次存取都檢查授權
- [x] 支援授權撤銷

### 加密儲存

- [x] **個資加密儲存**
- [x] 使用 Fernet 對稱加密（AES 128 位元）
- [x] 使用 PBKDF2 金鑰衍生函數
- [x] 儲存於外接儲存裝置

### 設備辨識

- [x] **設備辨識機制**
- [x] 自動偵測外接儲存裝置
- [x] 設備註冊表（`device_registry.json`）
- [x] 設備資訊記錄完整

### 變動記錄

- [x] **變動記錄完整（硬編碼）**
- [x] 所有變動記錄在 `storage_change_log.jsonl`
- [x] 包含時間戳、變動類型、設備 ID、操作者
- [x] 每個記錄都有 SHA-256 雜湊值

---

## ⚠️ 需注意事項

### 檔案安全性

- [ ] **硬編碼記錄檔案不在公開版本控制系統中**
  - [ ] `device_registry.json` 已加入 `.gitignore`
  - [ ] `storage_change_log.jsonl` 已加入 `.gitignore`
  - [ ] `accountable_person_authorizations.json` 已加入 `.gitignore`
  - [ ] 實施檔案存取權限控制

### 加密金鑰管理

- [ ] **金鑰備份機制**
  - [ ] 實施加密金鑰備份
  - [ ] 使用密碼保護的備份檔案
  - [ ] 金鑰輪換機制

### 外接裝置安全

- [ ] **外接裝置物理安全**
  - [ ] 實施裝置存取控制
  - [ ] 定期檢查裝置完整性
  - [ ] 裝置遺失處理流程

---

## 📊 合規狀態總結

### 已符合項目

✅ **基本合規**：
- Google for Nonprofits 驗證已完成
- 基本隱私保護符合規範
- 個資處理功能可控制啟用/停用
- 個資處理需明確授權
- 個資加密儲存
- 設備辨識與記錄完整
- 變動記錄完整

### 需注意項目

⚠️ **檔案安全性**：
- 硬編碼記錄檔案需確保不在公開版本控制系統中
- 需實施檔案存取權限控制

⚠️ **金鑰管理**：
- 需實施金鑰備份機制
- 需考慮金鑰輪換機制

---

## 🔧 立即行動項目

1. **確認 `.gitignore` 設定**
   ```bash
   # 確認以下檔案已加入 .gitignore
   - device_registry.json
   - storage_change_log.jsonl
   - accountable_person_authorizations.json
   - encrypted_storage_config.json
   - *.encrypted
   ```

2. **設定檔案存取權限**
   ```powershell
   # Windows: 設定檔案存取權限
   icacls device_registry.json /grant "Administrators:F" /deny "Users:R"
   icacls storage_change_log.jsonl /grant "Administrators:F" /deny "Users:R"
   icacls accountable_person_authorizations.json /grant "Administrators:F" /deny "Users:R"
   ```

3. **驗證個資處理功能狀態**
   ```powershell
   # 檢查環境變數
   echo $env:WUCHANG_PII_ENABLED
   echo $env:WUCHANG_PII_STORAGE_DEVICE
   ```

---

## 📝 合規聲明確認

### 核心合規聲明

1. ✅ 本系統除法律規範須依法揭露及政府公示資訊中公開揭露之外無可供識別之個資，應屬合規（預設狀態）
2. ✅ 本系統可究責之自然人不在隱私權保護規範內
3. ✅ 本系統及AI程序設計之可究責自然人不在隱私權保護規範內
4. ✅ 本系統經授權之獨立管理權限自然人不在隱私權保護規範內
5. ✅ 此兩種自然人除姓名外其餘不得公開揭露，但須紀錄於本系統之硬編碼
6. ✅ 個資使用需獲得明確授權
7. ✅ 個資處理功能需明確啟用（WUCHANG_PII_ENABLED=true）
8. ✅ 個資加密儲存於外接儲存裝置
9. ✅ 設備辨識與變動記錄完整（硬編碼）

---

**檢查結論**：**基本合規，需完成檔案安全性設定**

**下次檢查日期**：2026-04-15（每季度檢查）
