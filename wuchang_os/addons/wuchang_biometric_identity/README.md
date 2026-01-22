# 五常生物辨識身份管理模組

**版本**：17.0.1.0.0  
**建立日期**：2026-01-22  
**用途**：個人身份管理、生物辨識資料記錄、階段三權限認證

---

## 📋 功能說明

### 1. 個人身份管理

- **基本身份資訊**：
  - 姓名（必填）
  - 身份證號碼（選填）
  - 角色（例如：系統創辦人，本系統設計人）
  - 組織（例如：五常物業規劃股份有限公司）

- **可究責對象資訊**：
  - 系統創辦人標記
  - 可究責優先級（1=第一類可究責對象）
  - 設計責任標記
  - 使用責任標記

### 2. 生物辨識資料記錄

- **生物辨識類型**：
  - 人臉識別（預設）
  - 指紋
  - 虹膜
  - 聲紋
  - 其他

- **資料儲存**：
  - 生物辨識資料（二進位，加密儲存）
  - 生物辨識資料檔名
  - 生物辨識資料雜湊值（用於比對）

- **啟用狀態**：
  - 啟用/停用生物辨識驗證

### 3. 生物辨識驗證歷史記錄

- **驗證資訊**：
  - 驗證時間
  - 驗證結果（成功/失敗/待驗證/錯誤）
  - 驗證方法
  - 權限階段（階段一/二/三）
  - MAC 地址
  - 設備資訊

- **操作記錄**：
  - 操作類型
  - 操作詳情（JSON 格式）
  - 錯誤訊息（如果驗證失敗）

### 4. 階段三權限認證整合

- **系統創辦人驗證**：
  - 自動識別系統創辦人（`is_founder=True`, `accountability_priority=1`）
  - 驗證成功後自動授予階段三權限
  - 記錄所有驗證歷史

- **API 端點**：
  - `/api/biometric/verify`：生物辨識驗證
  - `/api/biometric/founder/check`：檢查系統創辦人生物辨識狀態

---

## 🚀 安裝與使用

### 1. 安裝模組

1. 將模組複製到 `wuchang_os/addons/` 目錄
2. 在 Odoo 中啟用開發者模式
3. 前往「應用程式」→「更新應用程式列表」
4. 搜尋「五常生物辨識身份管理」
5. 點擊「安裝」

### 2. 建立系統創辦人身份記錄

1. 前往「生物辨識管理」→「生物辨識身份」
2. 點擊「建立」
3. 填寫基本資訊：
   - **姓名**：江政隆
   - **角色**：系統創辦人，本系統設計人
   - **系統創辦人**：✓
   - **可究責優先級**：1
   - **設計責任**：✓
   - **使用責任**：✓
4. 在「生物辨識資料」頁籤：
   - **啟用生物辨識**：✓
   - **生物辨識類型**：人臉識別
   - **生物辨識資料**：上傳生物辨識資料檔案
5. 在「驗證資訊」頁籤：
   - **MAC 地址**：填入授權設備的 MAC 地址
6. 儲存

### 3. 使用生物辨識驗證

#### 透過 API

```python
import requests
import json

# 生物辨識驗證
response = requests.post('http://localhost:8069/api/biometric/verify', json={
    'person_name': '江政隆',
    'biometric_data': base64_encoded_data,
    'mac_address': '30:9C:23:4A:9B:1B'
})

result = response.json()
if result.get('ok') and result.get('verified'):
    permission_stage = result.get('permission_stage')  # '3' for founder
    print(f"驗證成功，權限階段：{permission_stage}")
```

#### 透過 UI

1. 前往「生物辨識管理」→「生物辨識身份」
2. 選擇系統創辦人身份記錄
3. 點擊「驗證生物辨識」按鈕
4. 系統會執行生物辨識驗證並記錄結果

### 4. 查看驗證記錄

1. 前往「生物辨識管理」→「驗證記錄」
2. 查看所有生物辨識驗證的歷史記錄
3. 可以按驗證時間、結果、權限階段等篩選

---

## 📊 資料模型

### `biometric.identity`（生物辨識身份）

| 欄位 | 類型 | 說明 |
|------|------|------|
| `person_name` | Char | 姓名（必填） |
| `id_number` | Char | 身份證號碼 |
| `role` | Char | 角色 |
| `organization` | Char | 組織 |
| `is_founder` | Boolean | 系統創辦人 |
| `accountability_priority` | Integer | 可究責優先級 |
| `biometric_data` | Binary | 生物辨識資料 |
| `biometric_type` | Selection | 生物辨識類型 |
| `biometric_enabled` | Boolean | 啟用生物辨識 |
| `mac_address` | Char | MAC 地址 |
| `last_verified` | Datetime | 最後驗證時間 |
| `verification_count` | Integer | 驗證次數 |

### `biometric.verification`（生物辨識驗證記錄）

| 欄位 | 類型 | 說明 |
|------|------|------|
| `identity_id` | Many2one | 身份記錄 |
| `verification_time` | Datetime | 驗證時間 |
| `verification_result` | Selection | 驗證結果 |
| `verification_method` | Selection | 驗證方法 |
| `permission_stage` | Selection | 權限階段 |
| `mac_address` | Char | MAC 地址 |
| `operation_type` | Char | 操作類型 |
| `operation_details` | Text | 操作詳情 |

---

## 🔒 安全設定

### 權限控制

- **一般使用者**：只能查看自己的身份記錄和驗證記錄
- **系統管理員**：可以管理所有身份記錄和驗證記錄

### 資料保護

- 生物辨識資料以二進位格式加密儲存
- 所有驗證記錄都會被完整記錄，確保可追溯性
- MAC 地址驗證確保操作來自授權設備

---

## 🔗 整合

### 與階段三權限系統整合

- 生物辨識驗證成功後，自動授予階段三權限
- 驗證記錄會記錄權限階段資訊
- 與 `little_j_policy.py` 整合，檢查生物特徵驗證狀態

### 與個人 AI 綁定整合

- 可以對照 `internal_id_records.json` 中的身份證記錄
- 可以對照 `personal_ai_binding.json` 中的個人綁定資訊

---

## 📝 相關檔案

- **階段三生物特徵認證機制**：`階段三生物特徵認證機制.md`
- **小J三階段權限系統**：`小J三階段權限系統說明.md`
- **個人AI綁定**：`personal_ai_binding.py`
- **政策控制**：`little_j_policy.py`

---

## ✅ 待完成項目

- [ ] 整合實際的人臉識別技術（目前為基本驗證）
- [ ] 生物辨識資料加密實作
- [ ] 生物辨識比對演算法實作
- [ ] 與前端 UI 整合（`wuchang_control_center.html`）

---

**建立時間**：2026-01-22  
**最後更新**：2026-01-22  
**權限歸屬**：系統創辦人，本系統設計人（第一類可究責對象）
