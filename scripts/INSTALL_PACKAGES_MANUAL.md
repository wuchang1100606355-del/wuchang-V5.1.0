# 手動安裝缺失的 Python 套件指南

**建立時間：** 2026-01-20  
**缺失套件：** Flask, google-auth

---

## 📋 安裝方式

### 方式 1：使用命令提示字元（CMD）

1. **開啟命令提示字元（以系統管理員身分執行）**

2. **執行安裝命令：**
```cmd
python -m pip install Flask google-auth
```

### 方式 2：使用 PowerShell

1. **開啟 PowerShell（以系統管理員身分執行）**

2. **執行安裝命令：**
```powershell
python -m pip install Flask google-auth
```

### 方式 3：使用完整路徑

如果 `python` 命令無法使用，找到 Python 安裝路徑後使用完整路徑：

```powershell
# 查找 Python 安裝位置
Get-Command python | Select-Object -ExpandProperty Source

# 使用完整路徑安裝
C:\Users\o0930\AppData\Local\Programs\Python\Python3XX\python.exe -m pip install Flask google-auth
```

---

## 🔍 驗證安裝

安裝完成後，驗證套件是否已安裝：

```powershell
python -m pip show Flask
python -m pip show google-auth
```

或查看所有已安裝的套件：

```powershell
python -m pip list | Select-String -Pattern "Flask|google-auth"
```

---

## ⚠️ 常見問題

### 問題 1：權限不足

**解決方案：** 以系統管理員身分執行命令提示字元或 PowerShell

### 問題 2：pip 未安裝

**解決方案：** 確保 Python 安裝時已選擇安裝 pip

### 問題 3：網路問題

**解決方案：** 檢查網路連接，或使用國內鏡像源：

```cmd
python -m pip install Flask google-auth -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 問題 4：Python 路徑問題

**解決方案：** 將 Python 加入系統 PATH 環境變數

---

## 📝 安裝的套件說明

### Flask
- **用途：** Web 框架
- **版本：** 最新穩定版
- **用途：** 用於建立 Web 應用程式和 API

### google-auth
- **用途：** Google 認證庫
- **版本：** 最新穩定版
- **用途：** 用於 Google API 認證和授權

---

## ✅ 安裝完成後

安裝完成後，這些套件就可以在 Python 程式中使用了：

```python
from flask import Flask
from google.auth import credentials
```

---

**注意：** 如果自動安裝失敗，請按照上述手動方式安裝。
