# 執行自動設定並重啟指南

**目的：** 自動將外接硬碟（E:）設定為虛擬記憶體並重新啟動電腦

---

## ⚠️ 重要提醒

1. **需要管理員權限**
2. **會重新啟動電腦**
3. **設定完成後需要重新啟動才能生效**

---

## 🚀 執行步驟

### 方法 1：直接執行（如果已是管理員）

以管理員身份開啟 PowerShell，然後執行：

```powershell
cd "G:\共用雲端硬碟\五常雲端空間"
.\scripts\auto_setup_and_restart.ps1
```

### 方法 2：提升權限執行（推薦）

在任何 PowerShell 視窗中執行：

```powershell
cd "G:\共用雲端硬碟\五常雲端空間"
Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PWD\scripts\auto_setup_and_restart.ps1`""
```

---

## 📋 腳本功能

1. ✅ 檢查管理員權限
2. ✅ 檢查 E: 磁碟狀態
3. ✅ 移除現有分頁檔案設定
4. ✅ 在 E: 磁碟建立新的分頁檔案（16-32 GB）
5. ✅ 顯示 30 秒倒數
6. ✅ 自動重新啟動電腦

---

## 📝 設定參數

- **目標磁碟：** E:
- **初始大小：** 16 GB
- **最大大小：** 32 GB

如需修改，請編輯腳本中的參數。

---

## ✅ 重新啟動後的驗證

電腦重新啟動後，執行以下指令驗證：

```powershell
# 檢查分頁檔案設定
Get-CimInstance -ClassName Win32_PageFileUsage | Select-Object Name, AllocatedBaseSize, CurrentUsage

# 應該看到 E:\pagefile.sys，大小約為 16-32 GB
```

然後測試 Ollama 模型：

```powershell
# 重新啟動 Ollama 容器
docker restart wuchang-ollama-1

# 等待容器啟動
Start-Sleep -Seconds 10

# 測試運行 qwen2:7b 模型
docker exec wuchang-ollama-1 ollama run qwen2:7b "Hello"
```

---

## ⚠️ 注意事項

1. **儲存所有工作**：執行前請儲存所有正在進行的工作
2. **關閉應用程式**：建議關閉不必要的應用程式
3. **連接外接硬碟**：確保 E: 磁碟（外接硬碟）已連接
4. **倒數時間**：有 30 秒時間可以按 Ctrl+C 取消

---

**準備好了嗎？執行上述指令即可開始！** 🚀
