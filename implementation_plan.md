# 系統實施規劃步驟

## 當前狀態總結

### ✅ 已完成
1. **控制中心** - 運行中
2. **VPN 連接** - 正常（10.8.0.6 → 10.8.0.1）
3. **網路互通設定** - 已完成
4. **開發者容器** - 已設置
5. **環境變數** - 部分設定（WUCHANG_HEALTH_URL, WUCHANG_COPY_TO）
6. **網路發現** - 已啟用
7. **檔案共用** - 已啟用

### ⚠️ 待完成
1. **網路共享連接** - 路徑不可訪問
2. **伺服器端服務** - 無回應
3. **工作區配置** - 未完整設定
4. **檔案同步** - 需要可訪問的共享路徑
5. **Google Tasks 整合** - 需要 OAuth 憑證

---

## 規劃步驟

### 階段一：網路連接建立（優先級：高）

#### 步驟 1.1：確認網路共享路徑
- [ ] 確認正確的共享伺服器名稱（HOME-COMMPUT vs HOME-COMPUTER）
- [ ] 測試網路連接：`ping HOME-COMMPUT`
- [ ] 掃描網路上的電腦：`net view`
- [ ] 確認共享路徑是否存在

**預期結果**：找到可訪問的共享路徑

#### 步驟 1.2：映射網路磁碟機
- [ ] 使用認證資訊映射：`net use Z: \\正確路徑 /user:帳號 密碼 /persistent:yes`
- [ ] 驗證映射成功：`Test-Path Z:\`
- [ ] 檢查共享內容是否可見

**預期結果**：Z: 磁碟機可訪問，內容可見

#### 步驟 1.3：設定環境變數
- [ ] 確認 `WUCHANG_COPY_TO` 指向正確路徑
- [ ] 驗證環境變數在當前會話和永久設定中都生效

**預期結果**：環境變數正確設定

---

### 階段二：伺服器端服務確認（優先級：高）

#### 步驟 2.1：診斷伺服器端狀態
- [ ] 確認伺服器端控制中心是否運行
- [ ] 確認實際應用伺服器 IP（可能不是 10.8.0.1）
- [ ] 掃描 VPN 網段內的其他 IP（10.8.0.2-10.8.0.10）
- [ ] 檢查防火牆設定

**預期結果**：找到實際的應用伺服器 IP 或確認服務狀態

#### 步驟 2.2：建立伺服器連接
- [ ] 測試 TCP 連接（端口 8788, 8799）
- [ ] 測試 HTTP 健康檢查端點
- [ ] 確認服務可正常回應

**預期結果**：伺服器端服務可正常連接

---

### 階段三：工作區配置（優先級：中）

#### 步驟 3.1：建立 Google Drive 資料夾結構
- [ ] 在 Google Drive 中建立「五常_中控」資料夾
- [ ] 建立子資料夾：
  - `config/` - 設定檔
  - `vault/` - 私密 vault
  - `exchange/` - 設備委派交換檔
  - `artifacts/` - 一般輸出

**預期結果**：資料夾結構建立完成

#### 步驟 3.2：設定工作區環境變數
- [ ] 設定 `WUCHANG_SYSTEM_DB_DIR`
- [ ] 設定 `WUCHANG_WORKSPACE_OUTDIR`
- [ ] 設定 `WUCHANG_WORKSPACE_EXCHANGE_DIR`
- [ ] 設定 `WUCHANG_PII_OUTDIR`
- [ ] 設定 `WUCHANG_ACCOUNTS_PATH`
- [ ] 設定 `WUCHANG_WORKSPACE_MATCHING_PATH`

**預期結果**：所有工作區環境變數設定完成

#### 步驟 3.3：建立配置檔案
- [ ] 建立 `accounts_policy.json`
- [ ] 建立 `workspace_matching.json`
- [ ] 將配置檔案放到對應位置

**預期結果**：配置檔案建立並放置完成

---

### 階段四：檔案同步（優先級：高）

#### 步驟 4.1：驗證同步環境
- [ ] 確認 `WUCHANG_COPY_TO` 可訪問
- [ ] 確認 `WUCHANG_HEALTH_URL` 設定正確
- [ ] 測試檔案讀寫權限

**預期結果**：同步環境就緒

#### 步驟 4.2：執行檔案同步
- [ ] 執行知識庫同步：`python smart_sync.py --profile kb`
- [ ] 執行規則同步：`python smart_sync.py --profile rules`
- [ ] 或執行全部同步：`python sync_all_profiles.py`

**預期結果**：檔案同步完成

---

### 階段五：Google Tasks 整合（優先級：低）

#### 步驟 5.1：設定 OAuth 憑證
- [ ] 從 Google Cloud Console 下載 OAuth 憑證
- [ ] 儲存為 `google_credentials.json`
- [ ] 執行授權流程

**預期結果**：OAuth 憑證設定完成

#### 步驟 5.2：測試 Google Tasks API
- [ ] 測試獲取任務列表
- [ ] 測試從 URL 獲取任務
- [ ] 驗證 API 功能正常

**預期結果**：Google Tasks 整合可用

---

### 階段六：系統驗證（優先級：中）

#### 步驟 6.1：完整系統檢查
- [ ] 執行系統部署狀態檢查：`python system_deployment_status.py`
- [ ] 執行連接狀態檢查：`python check_connection_status.py`
- [ ] 執行工作區對齊檢查：`python workspace_alignment_check.py`

**預期結果**：所有檢查通過

#### 步驟 6.2：生成最終報告
- [ ] 生成系統狀態報告
- [ ] 生成合規檢查報告
- [ ] 生成部署完成報告

**預期結果**：完整報告生成

---

## 執行順序建議

### 立即執行（阻塞問題）
1. **步驟 1.1-1.3**：建立網路共享連接
2. **步驟 2.1-2.2**：確認伺服器端服務

### 短期執行（1-2 天）
3. **步驟 4.1-4.2**：完成檔案同步
4. **步驟 3.1-3.3**：完成工作區配置

### 中期執行（可選）
5. **步驟 5.1-5.2**：Google Tasks 整合
6. **步驟 6.1-6.2**：系統驗證

---

## 風險與注意事項

### 高風險項目
- 網路共享連接失敗可能導致檔案同步無法進行
- 伺服器端服務無回應可能影響系統功能

### 注意事項
- 所有環境變數設定後需要重新啟動終端機或重新登入
- 網路共享需要正確的認證資訊
- 工作區配置需要 Google Drive 同步資料夾

---

## 成功標準

### 階段一成功標準
- [x] VPN 連接正常
- [ ] 網路共享路徑可訪問
- [ ] Z: 磁碟機內容可見

### 階段二成功標準
- [ ] 伺服器端服務可連接
- [ ] 健康檢查端點可回應

### 階段三成功標準
- [ ] 所有工作區環境變數設定完成
- [ ] 配置檔案建立完成

### 階段四成功標準
- [ ] 檔案同步成功執行
- [ ] 本地和伺服器端檔案一致

---

## 工具與腳本

### 已建立的工具
- `fix_network_drive.py` - 修復網路磁碟機
- `enable_local_network.py` - 啟用區域網路
- `enable_vpn_lan.py` - 啟用 VPN 區網
- `check_connection_status.py` - 檢查連接狀態
- `workspace_alignment_check.py` - 工作區對齊檢查
- `auto_resolve_sync_with_full_auth.py` - 全自動同步
- `setup_developer_container.py` - 開發者容器設置

### 建議使用的腳本
- `auto_resolve_sync_with_full_auth.py` - 一鍵執行所有步驟
- `check_breakthrough_status.py` - 檢查突破狀態
- `read_workspace_status.py` - 讀取工作區狀態

---

## 更新日期
2026-01-19
