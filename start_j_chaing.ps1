# 互動工作區管理腳本
# Interactive Workspace Management Script
# Author: Wu Chang Cloud System
# Version: 5.1.0

param(
    [string]$Action = "menu",
    [switch]$AutoApprove,
    [switch]$DelegateToCloud
)

# 設定控制台編碼為 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# 顏色定義
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# 顯示標題
function Show-Header {
    Clear-Host
    Write-ColorOutput "========================================" "Cyan"
    Write-ColorOutput "   五常互動工作區 v5.1.0" "Cyan"
    Write-ColorOutput "   Wu Chang Interactive Workspace" "Cyan"
    Write-ColorOutput "========================================" "Cyan"
    Write-Host ""
}

# 顯示主選單
function Show-Menu {
    Show-Header
    Write-ColorOutput "請選擇操作 (Please select an action):" "Yellow"
    Write-Host ""
    Write-Host "1. 初始化工作區 (Initialize Workspace)"
    Write-Host "2. 讀取最新變更 (Read Latest Changes)"
    Write-Host "3. 執行命令 (Execute Command)"
    Write-Host "4. 認可變更 (Approve Changes)"
    Write-Host "5. 委派至雲端代理程式 (Delegate to Cloud Agent)"
    Write-Host "6. 認可變更並委派 (Approve and Delegate)"
    Write-Host "7. 檢視工作區狀態 (View Workspace Status)"
    Write-Host "8. 離開 (Exit)"
    Write-Host ""
}

# 初始化工作區
function Initialize-Workspace {
    Write-ColorOutput "`n=== 初始化工作區 ===" "Green"
    
    # 檢查 Git 狀態
    Write-ColorOutput "檢查 Git 倉庫狀態..." "Yellow"
    $gitStatus = git status 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✓ Git 倉庫已就緒" "Green"
        Write-Host $gitStatus
    } else {
        Write-ColorOutput "✗ Git 倉庫初始化失敗" "Red"
        return $false
    }
    
    # 檢查分支
    $currentBranch = git branch --show-current
    Write-ColorOutput "當前分支: $currentBranch" "Cyan"
    
    # 創建工作目錄
    $workspaceDir = "workspace_temp"
    if (-not (Test-Path $workspaceDir)) {
        New-Item -ItemType Directory -Path $workspaceDir | Out-Null
        Write-ColorOutput "✓ 已創建工作目錄: $workspaceDir" "Green"
    } else {
        Write-ColorOutput "✓ 工作目錄已存在: $workspaceDir" "Yellow"
    }
    
    Write-ColorOutput "`n工作區初始化完成！" "Green"
    return $true
}

# 讀取最新變更
function Read-LatestChanges {
    Write-ColorOutput "`n=== 讀取最新變更 ===" "Green"
    
    # 獲取 Git 狀態
    Write-ColorOutput "`n--- 工作區狀態 ---" "Cyan"
    git status
    
    # 顯示未暫存的變更
    Write-ColorOutput "`n--- 未暫存的變更 ---" "Cyan"
    $diffOutput = git diff --stat
    if ($diffOutput) {
        Write-Host $diffOutput
    } else {
        Write-ColorOutput "無未暫存的變更" "Yellow"
    }
    
    # 顯示已暫存的變更
    Write-ColorOutput "`n--- 已暫存的變更 ---" "Cyan"
    $cachedDiff = git diff --cached --stat
    if ($cachedDiff) {
        Write-Host $cachedDiff
    } else {
        Write-ColorOutput "無已暫存的變更" "Yellow"
    }
    
    # 顯示最近的提交
    Write-ColorOutput "`n--- 最近的提交 ---" "Cyan"
    git log --oneline -5
    
    return $true
}

# 執行自定義命令
function Execute-CustomCommand {
    param([string]$Command = "")
    
    Write-ColorOutput "`n=== 執行命令 ===" "Green"
    
    if (-not $Command) {
        Write-ColorOutput "請輸入要執行的命令:" "Yellow"
        $Command = Read-Host
    }
    
    if ($Command) {
        Write-ColorOutput "執行: $Command" "Cyan"
        try {
            Invoke-Expression $Command
            Write-ColorOutput "`n✓ 命令執行完成" "Green"
            return $true
        } catch {
            Write-ColorOutput "✗ 命令執行失敗: $_" "Red"
            return $false
        }
    } else {
        Write-ColorOutput "✗ 未提供命令" "Red"
        return $false
    }
}

# 認可變更
function Approve-Changes {
    Write-ColorOutput "`n=== 認可變更 ===" "Green"
    
    # 顯示當前變更
    $status = git status --short
    if (-not $status) {
        Write-ColorOutput "沒有待認可的變更" "Yellow"
        return $true
    }
    
    Write-ColorOutput "待認可的變更:" "Cyan"
    Write-Host $status
    
    # 請求確認
    if (-not $AutoApprove) {
        Write-ColorOutput "`n是否認可這些變更？ (Y/N)" "Yellow"
        $confirmation = Read-Host
        if ($confirmation -ne "Y" -and $confirmation -ne "y") {
            Write-ColorOutput "✗ 已取消認可" "Red"
            return $false
        }
    }
    
    # 添加所有變更
    Write-ColorOutput "添加變更到暫存區..." "Cyan"
    git add -A
    
    # 提交變更
    Write-ColorOutput "請輸入提交訊息 (或按 Enter 使用預設訊息):" "Yellow"
    $commitMessage = Read-Host
    if (-not $commitMessage) {
        $commitMessage = "Update: Interactive workspace changes"
    }
    
    git commit -m $commitMessage
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✓ 變更已認可並提交" "Green"
        return $true
    } else {
        Write-ColorOutput "✗ 提交失敗" "Red"
        return $false
    }
}

# 委派至雲端代理程式
function Delegate-ToCloudAgent {
    Write-ColorOutput "`n=== 委派至雲端代理程式 ===" "Green"
    
    # 檢查是否有未推送的提交
    $unpushedCommits = git log --branches --not --remotes --oneline
    
    if ($unpushedCommits) {
        Write-ColorOutput "發現未推送的提交:" "Cyan"
        Write-Host $unpushedCommits
        
        Write-ColorOutput "`n推送到遠端倉庫..." "Yellow"
        $currentBranch = git branch --show-current
        
        try {
            git push origin $currentBranch
            
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput "✓ 已成功推送到遠端: origin/$currentBranch" "Green"
                Write-ColorOutput "✓ 變更已委派至雲端代理程式" "Green"
                return $true
            } else {
                Write-ColorOutput "✗ 推送失敗" "Red"
                return $false
            }
        } catch {
            Write-ColorOutput "✗ 推送過程發生錯誤: $_" "Red"
            return $false
        }
    } else {
        Write-ColorOutput "沒有待推送的提交" "Yellow"
        Write-ColorOutput "檢查遠端狀態..." "Cyan"
        git remote -v
        return $true
    }
}

# 認可變更並委派
function Approve-AndDelegate {
    Write-ColorOutput "`n=== 認可變更並委派至雲端 ===" "Green"
    
    # 先認可變更
    $approved = Approve-Changes
    
    if ($approved) {
        # 然後委派到雲端
        $delegated = Delegate-ToCloudAgent
        return $delegated
    } else {
        Write-ColorOutput "✗ 認可失敗，無法委派" "Red"
        return $false
    }
}

# 查看工作區狀態
function Show-WorkspaceStatus {
    Write-ColorOutput "`n=== 工作區狀態 ===" "Green"
    
    # Git 狀態
    Write-ColorOutput "`n--- Git 狀態 ---" "Cyan"
    git status
    
    # 分支信息
    Write-ColorOutput "`n--- 分支信息 ---" "Cyan"
    $currentBranch = git branch --show-current
    Write-ColorOutput "當前分支: $currentBranch" "Yellow"
    
    # 遠端信息
    Write-ColorOutput "`n--- 遠端倉庫 ---" "Cyan"
    git remote -v
    
    # 未推送的提交
    Write-ColorOutput "`n--- 未推送的提交 ---" "Cyan"
    $unpushed = git log --branches --not --remotes --oneline
    if ($unpushed) {
        Write-Host $unpushed
    } else {
        Write-ColorOutput "無未推送的提交" "Yellow"
    }
    
    return $true
}

# 主程序
function Main {
    # 根據參數執行相應操作
    switch ($Action.ToLower()) {
        "init" {
            Show-Header
            Initialize-Workspace
            Read-Host "`n按 Enter 鍵繼續..."
            return
        }
        "read" {
            Show-Header
            Read-LatestChanges
            Read-Host "`n按 Enter 鍵繼續..."
            return
        }
        "execute" {
            Show-Header
            Execute-CustomCommand
            Read-Host "`n按 Enter 鍵繼續..."
            return
        }
        "approve" {
            Show-Header
            Approve-Changes
            Read-Host "`n按 Enter 鍵繼續..."
            return
        }
        "delegate" {
            Show-Header
            Delegate-ToCloudAgent
            Read-Host "`n按 Enter 鍵繼續..."
            return
        }
        "both" {
            Show-Header
            Approve-AndDelegate
            Read-Host "`n按 Enter 鍵繼續..."
            return
        }
        "status" {
            Show-Header
            Show-WorkspaceStatus
            Read-Host "`n按 Enter 鍵繼續..."
            return
        }
        default {
            # 互動式選單模式
            do {
                Show-Menu
                $choice = Read-Host "請選擇 (1-8)"
                
                switch ($choice) {
                    "1" { Initialize-Workspace; Read-Host "`n按 Enter 鍵繼續..." }
                    "2" { Read-LatestChanges; Read-Host "`n按 Enter 鍵繼續..." }
                    "3" { Execute-CustomCommand; Read-Host "`n按 Enter 鍵繼續..." }
                    "4" { Approve-Changes; Read-Host "`n按 Enter 鍵繼續..." }
                    "5" { Delegate-ToCloudAgent; Read-Host "`n按 Enter 鍵繼續..." }
                    "6" { Approve-AndDelegate; Read-Host "`n按 Enter 鍵繼續..." }
                    "7" { Show-WorkspaceStatus; Read-Host "`n按 Enter 鍵繼續..." }
                    "8" { 
                        Write-ColorOutput "`n感謝使用五常互動工作區！" "Green"
                        return 
                    }
                    default { 
                        Write-ColorOutput "`n無效的選擇，請重試" "Red"
                        Start-Sleep -Seconds 2
                    }
                }
            } while ($true)
        }
    }
}

# 執行主程序
try {
    Main
} catch {
    Write-ColorOutput "`n✗ 發生錯誤: $_" "Red"
    Write-ColorOutput "錯誤詳情: $($_.Exception.Message)" "Red"
    exit 1
}
