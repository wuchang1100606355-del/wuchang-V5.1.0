# UI筆電共享設定步驟

**專案路徑**: `C:\wuchang V5.1.0`  
**UI筆電IP**: `192.168.50.84`

---

## 🎯 目標

在UI筆電上設定共享，讓本地系統可以訪問 `C:\wuchang V5.1.0`

---

## 📋 設定步驟

### 方法1: 設定資料夾共享（推薦）

#### 步驟1: 開啟資料夾內容

1. 在UI筆電上，找到 `C:\wuchang V5.1.0` 資料夾
2. **右鍵點擊**該資料夾
3. 選擇「**內容**」或「**屬性**」

#### 步驟2: 設定共用

1. 切換到「**共用**」標籤
2. 點擊「**進階共用**」按鈕
3. 勾選「**共用這個資料夾**」
4. 在「**共用名稱**」欄位輸入：`wuchang`（或您喜歡的名稱）
5. 點擊「**權限**」按鈕

#### 步驟3: 設定權限

1. 在權限視窗中，點擊「**新增**」
2. 輸入 `Everyone` 或特定用戶名
3. 勾選「**讀取**」和「**變更**」權限（或「**完全控制**」）
4. 點擊「**確定**」

#### 步驟4: 完成設定

1. 點擊「**確定**」關閉所有視窗
2. 共享設定完成！

#### 步驟5: 測試連接

設定完成後，告訴我共享名稱，我會測試連接。

---

### 方法2: 使用Windows管理共享（需要管理員權限）

如果方法1不可用，可以啟用Windows管理共享：

#### 步驟1: 啟用管理共享

在UI筆電上以管理員身份執行PowerShell：

```powershell
# 啟用管理共享
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" -Name "AutoShareServer" -Value 1 -Type DWord
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" -Name "AutoShareWks" -Value 1 -Type DWord

# 重啟Server服務
Restart-Service LanmanServer
```

#### 步驟2: 測試訪問

然後可以通過 `\\192.168.50.84\C$\wuchang V5.1.0` 訪問

---

### 方法3: 使用SSH（如果已啟用）

如果UI筆電已啟用SSH服務：

1. 確認SSH服務運行
2. 提供SSH用戶名和密碼
3. 我可以通過SSH讀取檔案

---

## 🧪 設定完成後

設定完成後，請告訴我：

1. **共享名稱**（例如：`wuchang`）
2. 或**已啟用管理共享**
3. 或**SSH認證資訊**

然後我會執行：

```powershell
# 測試共享連接
python scripts/test_ui_connection.py --method share --path "\\192.168.50.84\wuchang"

# 或測試管理共享
python scripts/test_ui_connection.py --method path --path "\\192.168.50.84\C$\wuchang V5.1.0"
```

---

## ⚠️ 注意事項

1. **防火牆**: 確保Windows防火牆允許檔案和印表機共用
2. **網路設定**: 確保兩台電腦在同一網路
3. **權限**: 確保設定了適當的讀取權限
4. **用戶認證**: 可能需要提供用戶名和密碼

---

## 💡 快速檢查

設定完成後，可以在UI筆電上測試：

```powershell
# 檢查共享是否生效
Get-SmbShare | Where-Object { $_.Name -like "*wuchang*" }
```

或在本地系統測試：

```powershell
# 測試網絡連接
ping 192.168.50.84

# 測試共享訪問
Test-Path "\\192.168.50.84\wuchang"
```

---

**設定完成後，請告訴我共享名稱或使用的訪問方式！** ✨
