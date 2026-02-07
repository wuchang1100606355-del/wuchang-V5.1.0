# 管理每小時時間排程工作
# 提供查看、啟用、停用、執行、刪除等功能

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("status", "enable", "disable", "run", "delete", "info")]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [string]$TaskName = "WuchangHourlyCheck"
)

Write-Host "=== 管理每小時時間排程工作 ===" -ForegroundColor Cyan

switch ($Action) {
    "status" {
        Write-Host "`n[查詢任務狀態]" -ForegroundColor Yellow
        
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            Write-Host "  任務名稱: $($task.TaskName)" -ForegroundColor Green
            Write-Host "  任務狀態: $($task.State)" -ForegroundColor Cyan
            Write-Host "  任務描述: $($task.Description)" -ForegroundColor Cyan
            
            $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
            Write-Host "`n  執行資訊:" -ForegroundColor Yellow
            Write-Host "    下次執行時間: $($taskInfo.NextRunTime)" -ForegroundColor Cyan
            Write-Host "    最後執行時間: $($taskInfo.LastRunTime)" -ForegroundColor Cyan
            Write-Host "    最後執行結果: $($taskInfo.LastTaskResult)" -ForegroundColor Cyan
        } else {
            Write-Host "  ⚠ 任務不存在: $TaskName" -ForegroundColor Yellow
        }
    }
    
    "enable" {
        Write-Host "`n[啟用任務]" -ForegroundColor Yellow
        
        try {
            Enable-ScheduledTask -TaskName $TaskName
            Write-Host "  ✓ 任務已啟用: $TaskName" -ForegroundColor Green
        } catch {
            Write-Host "  ❌ 啟用任務失敗: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    "disable" {
        Write-Host "`n[停用任務]" -ForegroundColor Yellow
        
        try {
            Disable-ScheduledTask -TaskName $TaskName
            Write-Host "  ✓ 任務已停用: $TaskName" -ForegroundColor Green
        } catch {
            Write-Host "  ❌ 停用任務失敗: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    "run" {
        Write-Host "`n[執行任務]" -ForegroundColor Yellow
        
        try {
            Start-ScheduledTask -TaskName $TaskName
            Write-Host "  ✓ 任務已開始執行: $TaskName" -ForegroundColor Green
            Write-Host "  等待 3 秒後查詢狀態..." -ForegroundColor Cyan
            Start-Sleep -Seconds 3
            
            $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
            Write-Host "  執行結果: $($taskInfo.LastTaskResult)" -ForegroundColor Cyan
        } catch {
            Write-Host "  ❌ 執行任務失敗: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    "delete" {
        Write-Host "`n[刪除任務]" -ForegroundColor Yellow
        
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            try {
                Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
                Write-Host "  ✓ 任務已刪除: $TaskName" -ForegroundColor Green
            } catch {
                Write-Host "  ❌ 刪除任務失敗: $($_.Exception.Message)" -ForegroundColor Red
            }
        } else {
            Write-Host "  ⚠ 任務不存在: $TaskName" -ForegroundColor Yellow
        }
    }
    
    "info" {
        Write-Host "`n[任務詳細資訊]" -ForegroundColor Yellow
        
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            Write-Host "  基本資訊:" -ForegroundColor Cyan
            $task | Format-List TaskName, State, Description, Author
            
            Write-Host "`n  動作:" -ForegroundColor Cyan
            $task.Actions | Format-List
            
            Write-Host "`n  觸發器:" -ForegroundColor Cyan
            $task.Triggers | Format-List
            
            Write-Host "`n  設定:" -ForegroundColor Cyan
            $task.Settings | Format-List
            
            $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
            Write-Host "`n  執行資訊:" -ForegroundColor Cyan
            $taskInfo | Format-List
        } else {
            Write-Host "  ⚠ 任務不存在: $TaskName" -ForegroundColor Yellow
        }
    }
}

Write-Host "`n=== 完成 ===" -ForegroundColor Green
