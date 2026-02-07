# Start J Chaing - 互動工作區與雲端代理程式管理工具
# Interactive Workspace and Cloud Agent Management Tool
# Version: 1.0.0

<#
.SYNOPSIS
    五常雲端空間互動工作區管理工具
    
.DESCRIPTION
    此工具提供以下功能：
    1. 設定互動工作區
    2. 讀取作業區最新變更
    3. 執行腳本和命令
    4. 認可變更
    5. 委派至雲端代理程式
    
.EXAMPLE
    .\start_j_chaing.ps1
    啟動互動式工作區管理介面
    
.EXAMPLE
    .\start_j_chaing.ps1 -AutoApprove -DelegateToCloud
    自動認可變更並委派至雲端代理程式
#>

param(
    [switch]$AutoApprove,      # 自動認可變更
    [switch]$DelegateToCloud,  # 委派至雲端代理程式
    [switch]$Interactive,      # 互動模式（預設）
    [string]$WorkspacePath = (Get-Location).Path  # 工作區路徑
)

# 設定編碼為 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# 顏色常數
$Colors = @{
    Header = "Cyan"
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "White"
    Prompt = "Magenta"
}

# 函數：顯示標題
function Show-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host ("=" * 80) -ForegroundColor $Colors.Header
    Write-Host $Title -ForegroundColor $Colors.Header
    Write-Host ("=" * 80) -ForegroundColor $Colors.Header
    Write-Host ""
}

# 函數：顯示功能選單
function Show-Menu {
    Write-Host "請選擇功能：" -ForegroundColor $Colors.Prompt
    Write-Host "  1. 設定互動工作區" -ForegroundColor $Colors.Info
    Write-Host "  2. 讀取作業區最新變更" -ForegroundColor $Colors.Info
    Write-Host "  3. 執行命令或腳本" -ForegroundColor $Colors.Info
    Write-Host "  4. 認可變更" -ForegroundColor $Colors.Info
    Write-Host "  5. 委派至雲端代理程式" -ForegroundColor $Colors.Info
    Write-Host "  6. 認可變更 + 委派至雲端代理程式" -ForegroundColor $Colors.Info
    Write-Host "  7. 查看工作區狀態" -ForegroundColor $Colors.Info
    Write-Host "  0. 退出" -ForegroundColor $Colors.Info
    Write-Host ""
}

# 函數：設定互動工作區
function Set-InteractiveWorkspace {
    Show-Header "設定互動工作區"
    
    Write-Host "當前工作區路徑: $WorkspacePath" -ForegroundColor $Colors.Info
    
    # 檢查是否為 Git 倉庫
    $isGitRepo = Test-Path (Join-Path $WorkspacePath ".git")
    if ($isGitRepo) {
        Write-Host "✓ 已識別為 Git 倉庫" -ForegroundColor $Colors.Success
    } else {
        Write-Host "⚠ 非 Git 倉庫" -ForegroundColor $Colors.Warning
    }
    
    # 檢查 uts 目錄
    $utsPath = Join-Path $WorkspacePath "uts"
    if (Test-Path $utsPath) {
        Write-Host "✓ 找到 uts 工具目錄" -ForegroundColor $Colors.Success
        $scripts = Get-ChildItem -Path $utsPath -Filter "*.ps1"
        Write-Host "  可用腳本數量: $($scripts.Count)" -ForegroundColor $Colors.Info
    }
    
    Write-Host ""
    Write-Host "互動工作區已準備就緒" -ForegroundColor $Colors.Success
}

# 函數：讀取最新變更
function Read-LatestChanges {
    Show-Header "讀取作業區最新變更"
    
    # 檢查是否為 Git 倉庫
    if (-not (Test-Path (Join-Path $WorkspacePath ".git"))) {
        Write-Host "錯誤: 當前目錄不是 Git 倉庫" -ForegroundColor $Colors.Error
        return
    }
    
    # 顯示 Git 狀態
    Write-Host "Git 狀態：" -ForegroundColor $Colors.Info
    Push-Location $WorkspacePath
    try {
        git status
        Write-Host ""
        
        # 顯示未提交的變更
        Write-Host "未提交的變更：" -ForegroundColor $Colors.Info
        git diff --stat
        Write-Host ""
        
        # 顯示最近的提交
        Write-Host "最近的提交：" -ForegroundColor $Colors.Info
        git log --oneline -5
    } finally {
        Pop-Location
    }
}

# 函數：執行命令
function Invoke-Command {
    Show-Header "執行命令或腳本"
    
    Write-Host "請輸入要執行的命令或腳本路徑：" -ForegroundColor $Colors.Prompt
    $command = Read-Host
    
    if ([string]::IsNullOrWhiteSpace($command)) {
        Write-Host "未輸入命令" -ForegroundColor $Colors.Warning
        return
    }
    
    Write-Host ""
    Write-Host "執行中: $command" -ForegroundColor $Colors.Info
    Write-Host ""
    
    try {
        Push-Location $WorkspacePath
        Invoke-Expression $command
        Write-Host ""
        Write-Host "✓ 執行完成" -ForegroundColor $Colors.Success
    } catch {
        Write-Host "✗ 執行失敗: $_" -ForegroundColor $Colors.Error
    } finally {
        Pop-Location
    }
}

# 函數：認可變更
function Approve-Changes {
    Show-Header "認可變更"
    
    # 檢查是否為 Git 倉庫
    if (-not (Test-Path (Join-Path $WorkspacePath ".git"))) {
        Write-Host "錯誤: 當前目錄不是 Git 倉庫" -ForegroundColor $Colors.Error
        return $false
    }
    
    Push-Location $WorkspacePath
    try {
        # 檢查是否有變更
        $status = git status --porcelain
        if ([string]::IsNullOrWhiteSpace($status)) {
            Write-Host "沒有需要認可的變更" -ForegroundColor $Colors.Info
            return $true
        }
        
        Write-Host "待認可的變更：" -ForegroundColor $Colors.Info
        git status --short
        Write-Host ""
        
        if (-not $AutoApprove) {
            $confirm = Read-Host "確認認可這些變更? (y/n)"
            if ($confirm -ne 'y' -and $confirm -ne 'Y') {
                Write-Host "已取消認可" -ForegroundColor $Colors.Warning
                return $false
            }
        }
        
        # 獲取提交訊息
        if (-not $AutoApprove) {
            Write-Host "請輸入提交訊息：" -ForegroundColor $Colors.Prompt
            $commitMessage = Read-Host
        } else {
            $commitMessage = "自動認可變更 - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        }
        
        if ([string]::IsNullOrWhiteSpace($commitMessage)) {
            $commitMessage = "認可變更 - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        }
        
        # 加入所有變更
        git add .
        Write-Host "✓ 已加入所有變更" -ForegroundColor $Colors.Success
        
        # 提交變更
        git commit -m $commitMessage
        Write-Host "✓ 變更已認可" -ForegroundColor $Colors.Success
        
        return $true
    } catch {
        Write-Host "✗ 認可失敗: $_" -ForegroundColor $Colors.Error
        return $false
    } finally {
        Pop-Location
    }
}

# 函數：委派至雲端代理程式
function Delegate-ToCloudAgent {
    Show-Header "委派至雲端代理程式"
    
    # 檢查是否為 Git 倉庫
    if (-not (Test-Path (Join-Path $WorkspacePath ".git"))) {
        Write-Host "錯誤: 當前目錄不是 Git 倉庫" -ForegroundColor $Colors.Error
        return $false
    }
    
    Push-Location $WorkspacePath
    try {
        # 檢查遠端倉庫
        $remotes = git remote -v
        if ([string]::IsNullOrWhiteSpace($remotes)) {
            Write-Host "警告: 未設定遠端倉庫" -ForegroundColor $Colors.Warning
            return $false
        }
        
        Write-Host "遠端倉庫：" -ForegroundColor $Colors.Info
        Write-Host $remotes
        Write-Host ""
        
        # 獲取當前分支
        $currentBranch = git rev-parse --abbrev-ref HEAD
        Write-Host "當前分支: $currentBranch" -ForegroundColor $Colors.Info
        
        if (-not $DelegateToCloud) {
            $confirm = Read-Host "確認推送到遠端倉庫 (雲端代理程式)? (y/n)"
            if ($confirm -ne 'y' -and $confirm -ne 'Y') {
                Write-Host "已取消委派" -ForegroundColor $Colors.Warning
                return $false
            }
        }
        
        # 推送到遠端
        Write-Host ""
        Write-Host "正在推送到雲端代理程式..." -ForegroundColor $Colors.Info
        git push origin $currentBranch
        
        Write-Host ""
        Write-Host "✓ 已成功委派至雲端代理程式" -ForegroundColor $Colors.Success
        Write-Host "  分支: $currentBranch" -ForegroundColor $Colors.Info
        
        return $true
    } catch {
        Write-Host "✗ 委派失敗: $_" -ForegroundColor $Colors.Error
        return $false
    } finally {
        Pop-Location
    }
}

# 函數：查看工作區狀態
function Show-WorkspaceStatus {
    Show-Header "工作區狀態"
    
    Write-Host "工作區路徑: $WorkspacePath" -ForegroundColor $Colors.Info
    Write-Host ""
    
    # Git 狀態
    if (Test-Path (Join-Path $WorkspacePath ".git")) {
        Push-Location $WorkspacePath
        try {
            Write-Host "Git 資訊：" -ForegroundColor $Colors.Header
            
            $branch = git rev-parse --abbrev-ref HEAD
            Write-Host "  當前分支: $branch" -ForegroundColor $Colors.Info
            
            $remote = git config --get "branch.$branch.remote"
            if ($remote) {
                Write-Host "  遠端倉庫: $remote" -ForegroundColor $Colors.Info
            }
            
            $status = git status --porcelain
            if ([string]::IsNullOrWhiteSpace($status)) {
                Write-Host "  狀態: ✓ 乾淨 (無待提交變更)" -ForegroundColor $Colors.Success
            } else {
                $changes = ($status -split "`n").Count
                Write-Host "  狀態: ⚠ 有 $changes 個待提交變更" -ForegroundColor $Colors.Warning
            }
        } finally {
            Pop-Location
        }
    } else {
        Write-Host "⚠ 非 Git 倉庫" -ForegroundColor $Colors.Warning
    }
    
    Write-Host ""
    
    # 檢查工具目錄
    $utsPath = Join-Path $WorkspacePath "uts"
    if (Test-Path $utsPath) {
        Write-Host "工具目錄 (uts)：" -ForegroundColor $Colors.Header
        $scripts = Get-ChildItem -Path $utsPath -Filter "*.ps1"
        Write-Host "  PowerShell 腳本: $($scripts.Count) 個" -ForegroundColor $Colors.Info
        foreach ($script in $scripts | Select-Object -First 5) {
            Write-Host "    - $($script.Name)" -ForegroundColor $Colors.Info
        }
        if ($scripts.Count -gt 5) {
            Write-Host "    ... 和其他 $($scripts.Count - 5) 個腳本" -ForegroundColor $Colors.Info
        }
    }
}

# 主程式
function Main {
    Show-Header "五常雲端空間 - 互動工作區與雲端代理程式管理工具"
    
    # 自動模式
    if ($AutoApprove -or $DelegateToCloud) {
        if ($AutoApprove) {
            $approved = Approve-Changes
            if (-not $approved) {
                Write-Host "自動認可失敗，程式結束" -ForegroundColor $Colors.Error
                exit 1
            }
        }
        
        if ($DelegateToCloud) {
            $delegated = Delegate-ToCloudAgent
            if (-not $delegated) {
                Write-Host "自動委派失敗，程式結束" -ForegroundColor $Colors.Error
                exit 1
            }
        }
        
        return
    }
    
    # 互動模式
    while ($true) {
        Show-Menu
        
        $choice = Read-Host "請選擇 (0-7)"
        
        switch ($choice) {
            "1" { Set-InteractiveWorkspace }
            "2" { Read-LatestChanges }
            "3" { Invoke-Command }
            "4" { Approve-Changes }
            "5" { Delegate-ToCloudAgent }
            "6" {
                $approved = Approve-Changes
                if ($approved) {
                    Delegate-ToCloudAgent
                }
            }
            "7" { Show-WorkspaceStatus }
            "0" {
                Write-Host ""
                Write-Host "感謝使用，再見！" -ForegroundColor $Colors.Success
                Write-Host ""
                return
            }
            default {
                Write-Host "無效的選擇，請重試" -ForegroundColor $Colors.Warning
            }
        }
        
        Write-Host ""
        Write-Host "按 Enter 鍵繼續..." -ForegroundColor $Colors.Prompt
        Read-Host | Out-Null
        Clear-Host
        Show-Header "五常雲端空間 - 互動工作區與雲端代理程式管理工具"
    }
}

# 執行主程式
Main
