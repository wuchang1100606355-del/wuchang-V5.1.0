# UI筆電管線配置指南

**執行時間**: 2026-01-12  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)

---

## 🎯 目標

配置網絡連接，讓系統可以直接讀取UI筆電上的wuchang專案檔案。

---

## 🔧 配置方式選擇

### 方式1: 設定網絡共享（推薦，最簡單）

#### 步驟1: 在UI筆電上設定共享

1. **找到wuchang專案資料夾**
   - 例如：`C:\wuchang V5.1.0` 或 `D:\wuchang V5.1.0`

2. **右鍵點擊資料夾** → 選擇「內容」

3. **切換到「共用」標籤**

4. **點擊「進階共用」**

5. **勾選「共用這個資料夾」**

6. **設定共用名稱**（例如：`wuchang`）

7. **設定權限**：
   - 點擊「權限」
   - 添加「Everyone」或特定用戶
   - 給予「讀取」或「完全控制」權限

8. **確定並套用**

#### 步驟2: 測試連接

在本地系統執行：
```powershell
# 測試網絡共享是否可訪問
Test-Path "\\192.168.50.84\wuchang"

# 如果成功，列出檔案
Get-ChildItem "\\192.168.50.84\wuchang" | Select-Object -First 10
```

#### 步驟3: 使用工具讀取

```powershell
python scripts/read_ui_laptop_files.py --remote-path "\\192.168.50.84\wuchang" --list-only
```

---

### 方式2: 映射網絡驅動器

#### 步驟1: 映射驅動器

在本地系統執行：
```powershell
# 映射網絡驅動器（需要先設定共享）
net use Z: \\192.168.50.84\wuchang /persistent:yes

# 如果需要認證
net use Z: \\192.168.50.84\wuchang /user:username password /persistent:yes
```

#### 步驟2: 使用本地路徑

```powershell
python scripts/read_ui_laptop_files.py --remote-path "Z:\" --list-only
```

---

### 方式3: 使用SSH（如果UI筆電支援）

#### 步驟1: 確認SSH服務運行

在UI筆電上執行：
```powershell
# 檢查SSH服務狀態
Get-Service sshd

# 如果未運行，啟動SSH服務
Start-Service sshd
```

#### 步驟2: 提供SSH認證資訊

需要提供：
- SSH用戶名
- SSH密碼（或使用SSH金鑰）

#### 步驟3: 使用SSH連接

```powershell
# 先安裝paramiko
pip install paramiko

# 使用SSH連接
python scripts/read_ui_laptop_files.py `
  --ssh-host "192.168.50.84" `
  --ssh-user "username" `
  --ssh-password "password" `
  --remote-path "C:\wuchang V5.1.0" `
  --list-only
```

---

### 方式4: 直接提供完整路徑

如果專案位於已知位置，可以直接提供完整路徑：

```powershell
# 例如：專案在用戶的Desktop
python scripts/read_ui_laptop_files.py `
  --remote-path "\\192.168.50.84\Users\username\Desktop\wuchang V5.1.0" `
  --list-only
```

---

## 📋 配置檢查清單

### 在UI筆電上：

- [ ] 確認wuchang專案的完整路徑
- [ ] 設定網絡共享（如果選擇方式1）
- [ ] 確認防火牆允許網絡共享
- [ ] 確認SSH服務運行（如果選擇方式3）
- [ ] 記錄用戶名和密碼（如果需要認證）

### 在本地系統上：

- [ ] 確認可以ping通UI筆電：`ping 192.168.50.84`
- [ ] 測試網絡共享連接：`Test-Path "\\192.168.50.84\wuchang"`
- [ ] 測試SSH連接：`Test-NetConnection -ComputerName 192.168.50.84 -Port 22`
- [ ] 準備好認證資訊（如果需要）

---

## 🧪 測試工具

執行以下命令測試連接：

```powershell
# 測試網絡共享
python scripts/test_ui_connection.py --method share --path "\\192.168.50.84\wuchang"

# 測試SSH
python scripts/test_ui_connection.py --method ssh --host "192.168.50.84" --user "username" --password "password"

# 測試完整路徑
python scripts/test_ui_connection.py --method path --path "\\192.168.50.84\Users\username\Desktop\wuchang V5.1.0"
```

---

## 💡 常見問題

### Q1: 無法訪問網絡共享

**解決方法**:
1. 檢查防火牆設置
2. 確認網絡共享已正確設定
3. 確認用戶有適當權限
4. 嘗試使用 `net use` 命令建立連接

### Q2: SSH連接失敗

**解決方法**:
1. 確認SSH服務運行
2. 檢查SSH端口是否開放
3. 確認用戶名和密碼正確
4. 檢查SSH配置

### Q3: 權限不足

**解決方法**:
1. 以管理員身份執行
2. 確認共享權限設置正確
3. 使用有權限的用戶帳號

---

## 📝 配置完成後

配置完成後，請告訴我：
1. 使用的配置方式（共享/SSH/路徑）
2. 完整的訪問路徑
3. 如果需要認證，提供用戶名和密碼（或使用SSH金鑰）

然後我就可以開始讀取UI筆電上的檔案了！

---

**報告生成時間**: 2026-01-12  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)

---

*「請選擇一種配置方式，我會協助您完成設定並開始讀取檔案！」* ✨
