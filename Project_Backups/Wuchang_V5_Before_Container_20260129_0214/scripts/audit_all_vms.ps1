$accounts = @("admin@wuchang.life", "wuchang1100606355@gmail.com")

foreach ($account in $accounts) {
    Write-Host "`n========================================================" -ForegroundColor Cyan
    Write-Host "正在檢查帳號: $account" -ForegroundColor Cyan
    Write-Host "========================================================"
    
    # 切換帳號
    gcloud config set account $account | Out-Null
    
    # 獲取該帳號下的所有專案
    $projects = gcloud projects list --format="value(projectId)"
    
    if (-not $projects) {
        Write-Host "  -> 此帳號下沒有發現任何專案。" -ForegroundColor Yellow
        continue
    }

    foreach ($project in $projects) {
        Write-Host "`n  正在掃描專案: $project" -ForegroundColor Green
        
        # 嘗試列出該專案下的 VM
        try {
            # 使用 invoke-expression 或直接執行，並捕獲錯誤以免權限不足中斷腳本
            $vms = gcloud compute instances list --project="$project" --format="table(name, zone, status, networkInterfaces[0].accessConfigs[0].natIP)" 2>&1
            
            # 檢查輸出是否包含錯誤訊息
            if ($vms -is [System.Array] -and $vms[0].ToString().Contains("ERROR")) {
                 Write-Host "    [!] 無法存取 Compute API (可能是 API 未啟用或權限不足)" -ForegroundColor DarkGray
            }
            elseif ($vms -is [System.Array] -and $vms.Count -gt 1) {
                # gcloud table output has a header, so count > 1 means there is data (or just check content)
                # 簡單過濾：如果只有標題行，表示沒有 VM
                $vms | Out-String | Write-Host
            }
            else {
                # 再次確認是否為空 (gcloud 有時回傳空字串)
                $vmsStr = $vms | Out-String
                if ($vmsStr.Trim().Length -gt 0 -and -not $vmsStr.Contains("Listed 0 items")) {
                     Write-Host $vmsStr
                } else {
                     Write-Host "    -> 無 VM 實例" -ForegroundColor Gray
                }
            }
        }
        catch {
            Write-Host "    [!] 發生錯誤: $_" -ForegroundColor Red
        }
    }
}

# 恢復原本的帳號設定 (假設是 gmail)
Write-Host "`n========================================================"
Write-Host "掃描完成，正在恢復預設帳號: wuchang1100606355@gmail.com"
gcloud config set account wuchang1100606355@gmail.com | Out-Null
