# 🖥️ 五常 OS 環境遷移與優化計畫 (Windows -> WSL2)

## 🎯 目標
將現有的混合式開發環境，轉換為基於 WSL2 (Windows Subsystem for Linux) 的標準化架構，以解決「py 老是有問題」的路徑與權限衝突，並最大化發揮 RTX 4070 的 AI 運算能力。

## 🏗️ 目標架構圖

| 層級 | 元件 | 角色 | 備註 |
| :--- | :--- | :--- | :--- |
| **User Interface** | Windows 11 | 顯示與操作 | 瀏覽器、VS Code、終端機介面 |
| **Compute Core** | WSL2 (Ubuntu) | 運算核心 | 所有程式碼與指令都在此執行 |
| **AI Acceleration** | NVIDIA Driver | GPU 加速 | 透過 WSL2 直接調用 RTX 4070 |
| **Services** | Docker Desktop | 容器管理 | Odoo, PostgreSQL, AI Models |

---

## 📅 執行步驟 (Checklist)

### 第一階段：WSL2 基礎建設
- [ ] **確認 WSL 狀態**：確保 Ubuntu 已安裝且為 WSL 2 版本 (已完成)。
- [ ] **安裝 Windows Terminal**：建議從 Microsoft Store 安裝，方便切換 Ubuntu/PowerShell。
- [ ] **設定 Docker Desktop**：
    - 進入 Docker Settings -> Resources -> WSL Integration。
    - 勾選 Ubuntu，讓 Docker 指令能在 WSL 裡直接使用。

### 第二階段：程式碼遷移 (大搬家)
- [ ] **建立專案目錄**：
    - 打開 Ubuntu 終端機。
    - 執行 mkdir -p ~/projects/wuchang_v5。
- [ ] **搬移程式碼**：
    - 不要在 Windows 的 C:\ 下跑 Linux 程式。
    - 將 C:\wuchang V5.1.0 的內容複製到 WSL：
      `ash
      # 在 Ubuntu 終端機執行
      cp -r /mnt/c/wuchang\ V5.1.0/* ~/projects/wuchang_v5/
      `

### 第三階段：環境配置
- [ ] **安裝 Python & 依賴** (在 WSL 內)：
    `ash
    sudo apt update && sudo apt install python3-pip python3-venv
    cd ~/projects/wuchang_v5
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    `
- [ ] **驗證 GPU 加速**：
    - 在 WSL 內執行 
vidia-smi 確認能看到顯卡。

### 第四階段：服務重啟
- [ ] **啟動 Docker 服務**：
    - 在 WSL 專案目錄下執行 docker compose up -d。
- [ ] **測試 AI 服務**：
    - 執行 m_fastapi_main_new.py (現在路徑對了，權限也對了)。

---

## ⚠️ 注意事項
1. **VS Code 連線**：請安裝 VS Code 的 WSL 擴充套件。以後打開專案時，左下角應顯示 WSL: Ubuntu，而不是 Windows。
2. **路徑習慣**：改用 /home/user/... (Linux 風格)，忘掉 C:\ (Windows 風格)。
