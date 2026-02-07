# 建立 GitHub 倉庫指南

## 方式 1: 使用 GitHub 網頁介面

1. **登入 GitHub**
   - 前往 https://github.com
   - 使用帳號 `wuchang` 登入

2. **建立新倉庫**
   - 點擊右上角 "+" → "New repository"
   - 倉庫名稱：`wuchang-os` 或 `wuchang-v5.1.0`
   - 描述：`五常智慧社區雲系統 (Wuchang OS)`
   - 選擇：Private（私有）或 Public（公開）
   - **不要**勾選 "Initialize with README"（因為本地已有代碼）
   - 點擊 "Create repository"

3. **複製倉庫 URL**
   - 複製 HTTPS URL（例如：`https://github.com/wuchang/wuchang-os.git`）

4. **設定遠程倉庫**
   ```powershell
   .\scripts\setup_git_remote.ps1 -RepositoryUrl "https://github.com/wuchang/wuchang-os.git"
   ```

## 方式 2: 使用 GitHub CLI（如果已安裝）

```powershell
# 安裝 GitHub CLI（如果尚未安裝）
winget install GitHub.cli

# 登入 GitHub
gh auth login

# 建立新倉庫
gh repo create wuchang-os --private --description "五常智慧社區雲系統 (Wuchang OS)"

# 設定遠程倉庫
git remote add origin https://github.com/wuchang/wuchang-os.git
```

## 方式 3: 使用現有倉庫

如果您已經有 GitHub 倉庫，直接設定：

```powershell
.\scripts\setup_git_remote.ps1 -RepositoryUrl "https://github.com/your-username/your-repo.git"
```

## 認證設定

### HTTPS 方式（推薦）

1. **建立 Personal Access Token**
   - 前往：https://github.com/settings/tokens
   - 點擊 "Generate new token (classic)"
   - 設定名稱：`Wuchang OS - Local Development`
   - 選擇權限：
     - ✅ `repo` (完整倉庫權限)
     - ✅ `workflow` (如果需要 GitHub Actions)
   - 點擊 "Generate token"
   - **重要**：立即複製 Token（只會顯示一次）

2. **使用 Token**
   - 推送時，用戶名輸入：`wuchang`
   - 密碼輸入：`<Personal Access Token>`
   - Windows 認證管理器會自動儲存

### SSH 方式

1. **生成 SSH 金鑰**（如果尚未生成）
   ```powershell
   ssh-keygen -t rsa -b 4096 -C "admin@wuchang.life" -f "$env:USERPROFILE\.ssh\id_rsa_wuchang"
   ```

2. **複製公鑰**
   ```powershell
   Get-Content "$env:USERPROFILE\.ssh\id_rsa_wuchang.pub" | Set-Clipboard
   ```

3. **添加到 GitHub**
   - 前往：https://github.com/settings/keys
   - 點擊 "New SSH key"
   - 貼上公鑰內容
   - 點擊 "Add SSH key"

4. **設定遠程倉庫使用 SSH**
   ```powershell
   git remote set-url origin git@github.com:wuchang/wuchang-os.git
   ```

## 推送代碼

設定完成後，推送代碼：

```powershell
# 添加所有變更
git add .

# 提交變更
git commit -m "feat: 整合 Google Workspace 和完整系統設定"

# 推送到遠程倉庫
git push -u origin migration/ui-total-ai
```
