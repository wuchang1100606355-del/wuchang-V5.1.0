# 🧹 電腦整理與清理清單 (建議執行)

為了讓新環境 (WSL2) 跑得更順暢，建議您清理以下在 Windows 環境遺留的暫存檔與備份。

## 🗑️ 建議刪除/封存的檔案 (目前佔用空間)

這些檔案多為舊備份或臨時下載檔，建議移至外部硬碟或刪除：

| 檔案名稱 | 路徑 | 大小 (MB) | 建議動作 |
| :--- | :--- | :--- | :--- |
| wuchang_backup.zip | C:\wuchang V5.1.0\ | ~4,997 MB | 移至備份硬碟 |
| wuchang_marrow_index.json | C:\wuchang V5.1.0\ | ~2,252 MB | 確認後刪除 (若為舊索引) |
| wuchang_core.zip | C:\wuchang V5.1.0\ | ~484 MB | 移至備份硬碟 |
| wuchang_deploy_package.zip | C:\wuchang V5.1.0\ | ~8 MB | 刪除 (舊部署檔) |
| Wuchang_Rescue_System.zip | C:\wuchang V5.1.0\ | ~23 MB | 移至備份硬碟 |

## 🛠️ 系統清理步驟

1. **清理 Docker 舊映像檔**：
   - 打開 PowerShell 執行：docker system prune (這會清除沒在用的容器與快取)。
   
2. **移除 Windows 下的 Python 虛擬環境**：
   - 既然要改用 WSL，Windows 下的 .venv 資料夾可以刪除 (通常很大)。
   - 刪除 C:\wuchang V5.1.0\.venv。

3. **歸檔舊日誌**：
   - *.log 檔案 (如 utomation.log) 如果不需要查閱舊紀錄，可以刪除。

## �� 整理後的預期狀態
- 專案根目錄只保留核心程式碼。
- 所有開發工作轉移至 WSL (Linux)。
- Windows 只負責「顯示」與「瀏覽」。
