# Git 帳號設定摘要

## 當前配置

- **用戶名稱**: wuchang
- **電子郵件**: admin@wuchang.life
- **認證方式**: HTTPS (使用 Personal Access Token)
- **認證管理器**: Windows Credential Manager (manager-core)
- **預設分支**: main

## 當前狀態

- **當前分支**: migration/ui-total-ai
- **遠程倉庫**: 未設定

## 下一步操作

### 1. 在 GitHub 建立 Personal Access Token

1. 前往 GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 點擊 "Generate new token (classic)"
3. 設定權限：
   - `repo` (完整倉庫權限)
   - `workflow` (如果需要 GitHub Actions)
4. 複製生成的 Token

### 2. 設定遠程倉庫

```powershell
# 設定遠程倉庫（請替換為您的實際倉庫 URL）
git remote add origin https://github.com/wuchang/your-repo.git

# 或更新現有遠程倉庫
git remote set-url origin https://github.com/wuchang/your-repo.git
```

### 3. 推送代碼

```powershell
# 推送當前分支
git push -u origin migration/ui-total-ai

# 推送時會提示輸入：
# Username: wuchang
# Password: <貼上 Personal Access Token>
```

### 4. 使用 SSH（可選）

如果需要使用 SSH，可以執行：

```powershell
.\scripts\setup_git_account_simple.ps1 `
    -Username "wuchang" `
    -Email "admin@wuchang.life" `
    -Service "GitHub" `
    -AuthMethod "SSH"
```

然後將 SSH 公鑰添加到 GitHub 帳號設定中。

## 測試連線

```powershell
# 測試 HTTPS 連線
git ls-remote origin

# 測試 SSH 連線（如果使用 SSH）
ssh -T git@github.com
```
