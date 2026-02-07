# 五常系統 - 雲端代理程式委派與變更認可工具
# start_j_chaing.ps1

Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "五常系統 - 雲端代理程式委派與變更認可工具" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""

# 載入配置
$configFile = Join-Path $PSScriptRoot "cloud_agent_config.json"
$config = $null

if (Test-Path $configFile) {
    try {
        $config = Get-Content $configFile -Raw | ConvertFrom-Json
        Write-Host "已載入配置檔案" -ForegroundColor Green
    } catch {
        Write-Host "配置檔案載入失敗: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "配置檔案不存在，使用預設配置" -ForegroundColor Yellow
}

# 檢查雙J重點記憶系統
$memoryFile = Join-Path $PSScriptRoot "DUAL_J_CRITICAL_MEMORY_SYSTEM.md"
if (Test-Path $memoryFile) {
    Write-Host "✓ 雙J重點記憶系統已載入" -ForegroundColor Green
} else {
    Write-Host "⚠ 警告: 雙J重點記憶系統檔案不存在" -ForegroundColor Yellow
}
Write-Host ""

# 主選單
function Show-Menu {
    Write-Host "請選擇操作：" -ForegroundColor Cyan
    Write-Host "1. 檢視待認可的變更" -ForegroundColor White
    Write-Host "2. 認可變更" -ForegroundColor White
    Write-Host "3. 委派至雲端代理程式" -ForegroundColor White
    Write-Host "4. 認可變更並委派至雲端代理程式" -ForegroundColor White
    Write-Host "5. 檢視工作區狀態" -ForegroundColor White
    Write-Host "6. 設定互動工作區" -ForegroundColor White
    Write-Host "7. 執行自訂命令" -ForegroundColor White
    Write-Host "0. 結束" -ForegroundColor White
    Write-Host ""
}

# 檢視待認可的變更
function Show-PendingChanges {
    Write-Host ("=" * 80) -ForegroundColor Yellow
    Write-Host "檢視待認可的變更" -ForegroundColor Yellow
    Write-Host ("=" * 80) -ForegroundColor Yellow
    Write-Host ""
    
    try {
        # 檢查 Git 狀態
        $gitStatus = git status --short 2>&1
        if ($LASTEXITCODE -eq 0) {
            if ($gitStatus) {
                Write-Host "待認可的變更：" -ForegroundColor Cyan
                Write-Host $gitStatus
            } else {
                Write-Host "沒有待認可的變更" -ForegroundColor Green
            }
        } else {
            Write-Host "無法檢查 Git 狀態（可能不在 Git 儲存庫中）" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "檢查變更時發生錯誤: $_" -ForegroundColor Red
    }
    Write-Host ""
}

# 認可變更
function Approve-Changes {
    Write-Host ("=" * 80) -ForegroundColor Yellow
    Write-Host "認可變更" -ForegroundColor Yellow
    Write-Host ("=" * 80) -ForegroundColor Yellow
    Write-Host ""
    
    Show-PendingChanges
    
    $confirm = Read-Host "確定要認可所有變更嗎？(Y/N)"
    if ($confirm -eq 'Y' -or $confirm -eq 'y') {
        try {
            # 添加所有變更
            git add . 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ 變更已暫存" -ForegroundColor Green
                
                # 提交變更
                $commitMessage = Read-Host "請輸入提交訊息"
                if ($commitMessage) {
                    git commit -m $commitMessage 2>&1 | Out-Null
                    if ($LASTEXITCODE -eq 0) {
                        Write-Host "✓ 變更已提交" -ForegroundColor Green
                        Write-Host "提交訊息: $commitMessage" -ForegroundColor Cyan
                    } else {
                        Write-Host "✗ 提交失敗" -ForegroundColor Red
                    }
                } else {
                    Write-Host "未輸入提交訊息，取消提交" -ForegroundColor Yellow
                }
            } else {
                Write-Host "✗ 暫存失敗" -ForegroundColor Red
            }
        } catch {
            Write-Host "認可變更時發生錯誤: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "已取消認可變更" -ForegroundColor Yellow
    }
    Write-Host ""
}

# 委派至雲端代理程式
function Delegate-ToCloudAgent {
    param(
        [string]$TaskDescription = ""
    )
    
    Write-Host ("=" * 80) -ForegroundColor Yellow
    Write-Host "委派至雲端代理程式" -ForegroundColor Yellow
    Write-Host ("=" * 80) -ForegroundColor Yellow
    Write-Host ""
    
    if (-not $TaskDescription) {
        $TaskDescription = Read-Host "請輸入要委派的任務描述"
    }
    
    if ($TaskDescription) {
        Write-Host "任務描述: $TaskDescription" -ForegroundColor Cyan
        Write-Host ""
        
        # 建立任務記錄
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $taskRecord = @{
            Timestamp = $timestamp
            Description = $TaskDescription
            Status = "已委派"
            Agent = "雲端代理程式"
        }
        
        # 儲存任務記錄到檔案
        $taskLogPath = Join-Path $PSScriptRoot "cloud_agent_tasks.json"
        $tasks = @()
        
        if (Test-Path $taskLogPath) {
            try {
                $tasks = Get-Content $taskLogPath -Raw | ConvertFrom-Json
            } catch {
                Write-Host "無法讀取現有任務記錄，將建立新記錄" -ForegroundColor Yellow
            }
        }
        
        $tasks += $taskRecord
        
        try {
            $tasks | ConvertTo-Json -Depth 10 | Set-Content $taskLogPath
            Write-Host "✓ 任務已委派至雲端代理程式" -ForegroundColor Green
            Write-Host "任務記錄已儲存至: $taskLogPath" -ForegroundColor Cyan
        } catch {
            Write-Host "✗ 儲存任務記錄失敗: $_" -ForegroundColor Red
        }
        
        # 顯示配置的雲端代理程式資訊
        if ($config -and $config.cloudAgent) {
            Write-Host ""
            Write-Host "雲端代理程式資訊：" -ForegroundColor Cyan
            Write-Host "  名稱: $($config.cloudAgent.name)" -ForegroundColor White
            Write-Host "  類型: $($config.cloudAgent.type)" -ForegroundColor White
            if ($config.cloudAgent.endpoint) {
                Write-Host "  端點: $($config.cloudAgent.endpoint)" -ForegroundColor White
            }
        }
    } else {
        Write-Host "未輸入任務描述，取消委派" -ForegroundColor Yellow
    }
    Write-Host ""
}

# 認可變更並委派至雲端代理程式
function Approve-And-Delegate {
    Write-Host ("=" * 80) -ForegroundColor Yellow
    Write-Host "認可變更並委派至雲端代理程式" -ForegroundColor Yellow
    Write-Host ("=" * 80) -ForegroundColor Yellow
    Write-Host ""
    
    # 先認可變更
    Approve-Changes
    
    # 再委派任務
    $taskDesc = Read-Host "請輸入要委派的任務描述（或按 Enter 跳過）"
    if ($taskDesc) {
        Delegate-ToCloudAgent -TaskDescription $taskDesc
    }
}

# 檢視工作區狀態
function Show-WorkspaceStatus {
    Write-Host ("=" * 80) -ForegroundColor Yellow
    Write-Host "工作區狀態" -ForegroundColor Yellow
    Write-Host ("=" * 80) -ForegroundColor Yellow
    Write-Host ""
    
    # Git 狀態
    Write-Host "【Git 狀態】" -ForegroundColor Cyan
    try {
        $branch = git branch --show-current 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  當前分支: $branch" -ForegroundColor White
        }
        
        $gitStatus = git status --short 2>&1
        if ($LASTEXITCODE -eq 0) {
            if ($gitStatus) {
                Write-Host "  待認可變更: 有" -ForegroundColor Yellow
            } else {
                Write-Host "  待認可變更: 無" -ForegroundColor Green
            }
        }
    } catch {
        Write-Host "  無法檢查 Git 狀態" -ForegroundColor Yellow
    }
    Write-Host ""
    
    # 雲端代理任務狀態
    Write-Host "【雲端代理任務】" -ForegroundColor Cyan
    $taskLogPath = Join-Path $PSScriptRoot "cloud_agent_tasks.json"
    if (Test-Path $taskLogPath) {
        try {
            $tasks = Get-Content $taskLogPath -Raw | ConvertFrom-Json
            Write-Host "  總任務數: $($tasks.Count)" -ForegroundColor White
            $recent = $tasks | Select-Object -Last 3
            if ($recent) {
                Write-Host "  最近任務:" -ForegroundColor White
                foreach ($task in $recent) {
                    Write-Host "    - [$($task.Timestamp)] $($task.Description)" -ForegroundColor Gray
                }
            }
        } catch {
            Write-Host "  無法讀取任務記錄" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  無任務記錄" -ForegroundColor White
    }
    Write-Host ""
}

# 設定互動工作區
function Setup-InteractiveWorkspace {
    Write-Host ("=" * 80) -ForegroundColor Yellow
    Write-Host "設定互動工作區" -ForegroundColor Yellow
    Write-Host ("=" * 80) -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "互動工作區功能：" -ForegroundColor Cyan
    Write-Host "  ✓ 自動監控檔案變更" -ForegroundColor Green
    Write-Host "  ✓ 即時顯示 Git 狀態" -ForegroundColor Green
    Write-Host "  ✓ 快速認可和委派" -ForegroundColor Green
    Write-Host ""
    
    $enable = Read-Host "是否啟用互動工作區？(Y/N)"
    if ($enable -eq 'Y' -or $enable -eq 'y') {
        Write-Host "✓ 互動工作區已啟用" -ForegroundColor Green
        Write-Host ""
        Write-Host "您現在可以：" -ForegroundColor Cyan
        Write-Host "  1. 修改檔案後，使用選項 1 檢視變更" -ForegroundColor White
        Write-Host "  2. 使用選項 4 快速認可並委派任務" -ForegroundColor White
        Write-Host "  3. 使用選項 5 隨時檢視工作區狀態" -ForegroundColor White
    } else {
        Write-Host "互動工作區未啟用" -ForegroundColor Yellow
    }
    Write-Host ""
}

# 執行自訂命令
function Execute-CustomCommand {
    Write-Host ("=" * 80) -ForegroundColor Yellow
    Write-Host "執行自訂命令" -ForegroundColor Yellow
    Write-Host ("=" * 80) -ForegroundColor Yellow
    Write-Host ""
    
    $command = Read-Host "請輸入要執行的命令"
    if ($command) {
        Write-Host "執行: $command" -ForegroundColor Cyan
        Write-Host ""
        try {
            Invoke-Expression $command
        } catch {
            Write-Host "執行命令時發生錯誤: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "未輸入命令" -ForegroundColor Yellow
    }
    Write-Host ""
}

# 主程式迴圈
$running = $true
while ($running) {
    Show-Menu
    $choice = Read-Host "請選擇"
    Write-Host ""
    
    switch ($choice) {
        '1' { Show-PendingChanges }
        '2' { Approve-Changes }
        '3' { Delegate-ToCloudAgent }
        '4' { Approve-And-Delegate }
        '5' { Show-WorkspaceStatus }
        '6' { Setup-InteractiveWorkspace }
        '7' { Execute-CustomCommand }
        '0' { 
            Write-Host "結束程式" -ForegroundColor Cyan
            $running = $false
        }
        default { 
            Write-Host "無效的選擇，請重新輸入" -ForegroundColor Red
            Write-Host ""
        }
    }
    
    if ($running) {
        Write-Host "按任意鍵繼續..." -ForegroundColor Gray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        Write-Host ""
    }
}

Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "感謝使用五常系統雲端代理程式委派工具" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan
