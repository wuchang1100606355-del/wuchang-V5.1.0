# Docker Desktop 中文化指南

## 概述

Docker Desktop 官方版本在 Windows 上**並未提供**內建的語言切換功能。本指南提供使用第三方漢化包將 Docker Desktop 中文化的方法。

## ⚠️ 重要注意事項

1. **版本相容性**：漢化包必須與您安裝的 Docker Desktop 版本對應
2. **安全性**：使用第三方漢化包需注意來源信任度
3. **維護性**：Docker Desktop 更新後可能需要重新套用漢化包
4. **官方支援**：使用漢化包後若出現問題，官方可能不支援非官方修改引起的 bug

## 快速開始

### 方法一：使用自動化腳本（推薦）

1. 以**系統管理員身分**執行 PowerShell
2. 執行 docker_desktop_chinese_setup.ps1 腳本：
   `powershell
   .\docker_desktop_chinese_setup.ps1
   `
3. 按照提示操作：
   - 關閉 Docker Desktop
   - 選擇下載方式（自動或手動）
   - 確認套用漢化包
4. 重新啟動 Docker Desktop

### 方法二：手動操作

#### 步驟 1：下載漢化包

前往 GitHub 倉庫下載對應版本的漢化包：
- 倉庫：https://github.com/asxez/DockerDesktop-CN
- 下載頁面：https://github.com/asxez/DockerDesktop-CN/releases

**重要**：請下載與您 Docker Desktop 版本對應的 pp.asar 檔案

#### 步驟 2：備份原始檔案

1. 關閉 Docker Desktop（系統托盤右鍵 → Quit Docker Desktop）
2. 找到 Docker Desktop 資源目錄：
   `
   C:\Program Files\Docker\Docker\resources
   `
3. 備份 pp.asar 檔案：
   `powershell
   Copy-Item "C:\Program Files\Docker\Docker\resources\app.asar" "C:\Program Files\Docker\Docker\resources\app.asar.backup"
   `

#### 步驟 3：套用漢化包

1. 將下載的 pp.asar 檔案複製到資源目錄
2. 覆蓋原有的 pp.asar 檔案
3. 重新啟動 Docker Desktop

## 還原為英文版本

### 使用腳本還原

執行 docker_desktop_chinese_setup.ps1，當偵測到備份檔案時選擇還原選項。

### 手動還原

1. 關閉 Docker Desktop
2. 還原備份檔案：
   `powershell
   Copy-Item "C:\Program Files\Docker\Docker\resources\app.asar.backup" "C:\Program Files\Docker\Docker\resources\app.asar" -Force
   `
3. 重新啟動 Docker Desktop

## 檢查 Docker Desktop 版本

### 方法一：透過設定介面

1. 開啟 Docker Desktop
2. 點擊右上角設定圖示（齒輪）
3. 在 "General" 或 "About" 頁面查看版本號

### 方法二：透過 PowerShell

`powershell
(Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Docker Desktop").DisplayVersion
`

### 方法三：透過命令列

`powershell
docker --version
docker version
`

## 常見問題

### Q: 套用漢化包後 Docker Desktop 無法啟動？

A: 
1. 確認漢化包版本與 Docker Desktop 版本相符
2. 還原原始檔案（使用備份）
3. 重新下載正確版本的漢化包

### Q: 部分介面仍為英文？

A: 這是正常現象，漢化包可能無法覆蓋所有文字內容，特別是動態生成的內容。

### Q: Docker Desktop 更新後需要重新套用嗎？

A: 是的，更新後原始檔案會被覆蓋，需要重新套用漢化包。

### Q: 如何確認漢化包來源安全？

A: 
- 從官方 GitHub 倉庫下載：https://github.com/asxez/DockerDesktop-CN
- 檢查檔案 SHA256 校驗碼（如果倉庫有提供）
- 使用防毒軟體掃描下載的檔案

## 相關資源

- Docker Desktop 官方文件：https://docs.docker.com/desktop/
- 漢化包 GitHub 倉庫：https://github.com/asxez/DockerDesktop-CN
- Docker Desktop 下載：https://www.docker.com/products/docker-desktop

## 免責聲明

使用第三方漢化包屬於非官方修改，使用者需自行承擔風險。建議在套用前先備份原始檔案，並了解如何還原。
