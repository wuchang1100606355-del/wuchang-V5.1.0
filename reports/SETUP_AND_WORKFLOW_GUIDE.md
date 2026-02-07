# 系統設定與工作流程指南

## 一、Google Tasks API 自動設定流程

### 全自動模式執行

```powershell
python auto_setup_google_tasks.py --auto
```

### 詳細流程步驟

#### 步驟 1: 自動安裝依賴套件
- ✅ 檢查並自動安裝以下套件：
  - `google-auth`
  - `google-auth-oauthlib`
  - `google-auth-httplib2`
  - `google-api-python-client`

#### 步驟 2: 檢查 OAuth 憑證
- 檢查是否存在 `google_credentials.json`
- 如果不存在，進入引導流程

#### 步驟 3: OAuth 憑證設定（需要手動操作）

**3.1 開啟 Google Cloud Console**
- 自動開啟瀏覽器到：https://console.cloud.google.com/
- 或手動訪問

**3.2 建立或選擇專案**
- 點擊頂部專案選擇器
- 建立新專案或選擇現有專案
- 專案名稱建議：「五常系統 Google Tasks」

**3.3 啟用 Google Tasks API**
- 自動開啟：https://console.cloud.google.com/apis/library/tasks.googleapis.com
- 點擊「啟用」按鈕

**3.4 建立 OAuth 2.0 憑證**
- 自動開啟：https://console.cloud.google.com/apis/credentials
- 如果是首次使用，需要先設定「OAuth 同意畫面」：
  - 使用者類型：選擇「外部」
  - 應用程式名稱：輸入「五常系統」
  - 使用者支援電子郵件：選擇您的電子郵件
  - 開發人員聯絡資訊：輸入您的電子郵件
  - 點擊「儲存並繼續」完成設定
- 回到「憑證」頁面，點擊「建立憑證」→「OAuth 用戶端 ID」
- 應用程式類型：選擇「桌面應用程式」
- 名稱：輸入「五常系統 Google Tasks 整合」
- 點擊「建立」

**3.5 下載憑證檔案**
- 在憑證列表中，找到剛建立的 OAuth 用戶端 ID
- 點擊下載圖示（⬇️）或點擊憑證名稱
- 下載 JSON 檔案

**3.6 儲存憑證檔案**
- 將下載的 JSON 檔案重新命名為：`google_credentials.json`
- 放置在專案根目錄：`C:\wuchang V5.1.0\wuchang-V5.1.0\google_credentials.json`
- 腳本會自動檢測（每 3 秒檢查一次，最多等待 5 分鐘）

#### 步驟 4: 自動授權測試
- 自動初始化 Google Tasks 整合
- 自動獲取任務列表驗證授權
- 顯示找到的任務列表

#### 步驟 5: 完成
- ✅ 設定完成
- 可以使用以下工具：
  - `python get_jules_task_direct.py <task_url>`
  - `python upload_diff_to_jules.py --auto-upload`
  - `python sync_from_google_task.py <task_url> <target_file>`

---

## 二、檔案比對與上傳到 JULES 流程

### 2.1 執行檔案比對

```powershell
# 智能比對（自動尋找伺服器路徑）
python compare_files_smart.py --profile all

# 或指定伺服器路徑
python compare_files_smart.py --profile all --server-dir "\\HOME-COMMPUT\wuchang V5.1.0"
```

**輸出內容：**
- 本地檔案資訊（大小、修改時間、SHA256）
- 伺服器端檔案資訊（如果可訪問）
- 檔案差異狀態（相同/不同/僅本地/僅伺服器）

### 2.2 生成差異報告

```powershell
# 生成 Markdown 和 JSON 報告
python generate_diff_report_for_jules.py --format both
```

**生成檔案：**
- `file_diff_report_YYYYMMDD_HHMMSS.md` - Markdown 格式（可複製到 Google Tasks）
- `file_diff_report_YYYYMMDD_HHMMSS.json` - JSON 格式（機器可讀）

### 2.3 上傳到 JULES (Google Tasks)

**方式 1: 自動上傳（需要先完成 OAuth 設定）**

```powershell
python upload_diff_to_jules.py --auto-upload
```

**方式 2: 手動複製**

1. 開啟生成的 Markdown 報告檔案
2. 複製全部內容
3. 在 Google Tasks 中建立新任務
4. 將內容貼到任務備註欄位

**方式 3: 使用現有報告檔案**

```powershell
python upload_diff_to_jules.py --auto-upload --report-file "file_diff_report_20260119_142050.md"
```

---

## 三、從 JULES 獲取任務流程

### 3.1 獲取任務內容

```powershell
# 直接獲取（需要 OAuth 憑證）
python get_jules_task_direct.py "https://jules.google.com/task/18167513009276525148"

# 通過控制中心 API（需要控制中心運行）
python get_jules_task.py "https://jules.google.com/task/18167513009276525148"
```

**輸出：**
- 任務標題
- 任務狀態
- 任務備註（完整內容）
- 到期時間
- 完成時間
- 儲存為 JSON 檔案：`jules_task_<task_id>.json`

### 3.2 使用任務內容覆蓋本地檔案

```powershell
python sync_from_google_task.py "https://jules.google.com/task/18167513009276525148" target_file.txt
```

**功能：**
- 從 Google Tasks 獲取任務內容
- 自動判斷內容類型（JSON 或文字）
- 覆蓋指定的本地檔案

---

## 四、檔案同步流程

### 4.1 以本地檔案為準進行修補

```powershell
# 模擬執行
python patch_from_local.py --profile all --dry-run

# 實際執行
python patch_from_local.py --profile all
```

**功能：**
- 使用 `safe_sync_push.py` 將本地變更推送到伺服器
- 以本地檔案為準覆蓋伺服器端檔案

### 4.2 擇優同步

```powershell
# 雙向擇優同步
python smart_sync.py --profile all --direction both

# 僅推送到伺服器
python smart_sync.py --profile all --direction server

# 僅從伺服器拉取
python smart_sync.py --profile all --direction local
```

**功能：**
- 根據修改時間和檔案大小選擇較佳版本
- 自動同步到對應端

### 4.3 完整同步所有配置檔

```powershell
python sync_all_profiles.py
```

**功能：**
- 同步所有定義的配置檔（kb, rules）
- 使用 `smart_sync.py` 執行

---

## 五、環境校準流程

### 5.1 兩方環境校準

```powershell
python calibrate_both_environments.py
```

**功能：**
- 檢查本地環境變數
- 檢查伺服器端環境變數（如果可訪問）
- 比對兩方環境差異
- 生成校準建議
- 生成校準腳本：`apply_environment_calibration.ps1`

### 5.2 應用環境校準

```powershell
# 執行自動生成的校準腳本
.\apply_environment_calibration.ps1
```

---

## 六、網路共享修復流程

### 6.1 診斷網路共享問題

```powershell
# 模擬執行
python fix_network_share_issues.py --dry-run

# 實際修復
python fix_network_share_issues.py
```

**修復內容：**
- 啟用文件和打印機共享
- 啟用功能發現服務（FDResPub, FDHost）
- 配置 SMB 版本（啟用 SMB 2.0/3.0，停用 SMB 1.0）
- 測試網路共享連接

### 6.2 測試網路共享

```powershell
python fix_network_share_issues.py --test-share "\\HOME-COMMPUT\wuchang V5.1.0"
```

---

## 七、完整工作流程範例

### 場景 1: 首次設定並上傳差異報告

```powershell
# 1. 自動設定 Google Tasks API
python auto_setup_google_tasks.py --auto

# 2. 比對檔案
python compare_files_smart.py --profile all

# 3. 生成報告
python generate_diff_report_for_jules.py --format both

# 4. 上傳到 JULES
python upload_diff_to_jules.py --auto-upload
```

### 場景 2: 從 JULES 獲取任務並執行

```powershell
# 1. 獲取任務內容
python get_jules_task_direct.py "https://jules.google.com/task/18167513009276525148"

# 2. 如果任務包含檔案內容，同步到本地
python sync_from_google_task.py "https://jules.google.com/task/18167513009276525148" target_file.txt

# 3. 執行任務中的指令（手動或自動化）
```

### 場景 3: 修復網路問題並同步檔案

```powershell
# 1. 修復網路共享
python fix_network_share_issues.py

# 2. 校準環境
python calibrate_both_environments.py

# 3. 同步檔案
python sync_all_profiles.py
```

---

## 八、工具清單

### Google Tasks 相關
- `auto_setup_google_tasks.py` - 自動設定 Google Tasks API
- `get_jules_task_direct.py` - 直接獲取 Google Tasks 任務
- `get_jules_task.py` - 通過控制中心 API 獲取任務
- `upload_diff_to_jules.py` - 上傳差異報告到 Google Tasks
- `sync_from_google_task.py` - 從 Google Tasks 同步內容到本地檔案

### 檔案比對與同步
- `compare_files_smart.py` - 智能檔案比對工具
- `generate_diff_report_for_jules.py` - 生成差異報告
- `patch_from_local.py` - 以本地檔案為準進行修補
- `smart_sync.py` - 擇優同步工具
- `sync_all_profiles.py` - 同步所有配置檔

### 環境管理
- `calibrate_both_environments.py` - 兩方環境校準
- `setup_env_vars.py` - 環境變數統一設定

### 網路修復
- `fix_network_share_issues.py` - 修復網路共享問題
- `enable_vpn_lan.py` - 啟用 VPN LAN
- `enable_network_discovery.py` - 啟用網路探索

---

## 九、常見問題

### Q: OAuth 憑證設定失敗怎麼辦？

A: 
1. 確認已啟用 Google Tasks API
2. 確認 OAuth 同意畫面已設定
3. 確認憑證類型為「桌面應用程式」
4. 確認憑證檔案路徑正確

### Q: 無法訪問伺服器端檔案？

A:
1. 執行 `python fix_network_share_issues.py` 修復網路共享
2. 檢查 VPN 連接狀態
3. 確認伺服器共享路徑正確
4. 檢查防火牆規則

### Q: 檔案比對結果不準確？

A:
1. 確認兩端檔案路徑正確
2. 檢查檔案編碼是否一致
3. 確認網路連接穩定
4. 使用 `--json` 參數查看詳細資訊

---

## 十、快速參考

### 最常用的命令

```powershell
# 設定 Google Tasks API（首次使用）
python auto_setup_google_tasks.py --auto

# 比對檔案並生成報告
python generate_diff_report_for_jules.py --format both

# 上傳報告到 JULES
python upload_diff_to_jules.py --auto-upload

# 從 JULES 獲取任務
python get_jules_task_direct.py <task_url>

# 同步檔案
python sync_all_profiles.py
```
