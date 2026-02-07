# Git 帳號設定範例
# 請修改以下參數後執行

# 範例 1: GitHub 使用 HTTPS
.\scripts\setup_git_account_simple.ps1 `
    -Username "your-github-username" `
    -Email "your-email@example.com" `
    -Service "GitHub" `
    -AuthMethod "HTTPS" `
    -RemoteUrl "https://github.com/your-username/your-repo.git"

# 範例 2: GitHub 使用 SSH
.\scripts\setup_git_account_simple.ps1 `
    -Username "your-github-username" `
    -Email "your-email@example.com" `
    -Service "GitHub" `
    -AuthMethod "SSH" `
    -RemoteUrl "git@github-your-username:your-username/your-repo.git"

# 範例 3: GitLab 使用 HTTPS
.\scripts\setup_git_account_simple.ps1 `
    -Username "your-gitlab-username" `
    -Email "your-email@example.com" `
    -Service "GitLab" `
    -AuthMethod "HTTPS" `
    -RemoteUrl "https://gitlab.com/your-username/your-repo.git"
