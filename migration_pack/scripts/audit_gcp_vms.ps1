$accounts = @("wuchang1100606355@gmail.com", "admin@wuchang.life")
$results = @()

Write-Host "開始 GCP VM 跨帳號清查..."

foreach ($account in $accounts) {
    Write-Host "`n[帳號] 切換至: $account"
    gcloud config set account $account | Out-Null

    $projects = gcloud projects list --format="value(projectId)"
    
    if (-not $projects) {
        Write-Host "  無專案。"
        continue
    }

    foreach ($proj in $projects) {
        Write-Host "  [專案] 掃描: $proj"
        try {
            # 嘗試列出 VM，忽略錯誤 (例如 API 未啟用)
            $vms = gcloud compute instances list --project $proj --format="csv[no-heading](name,status,zone,machineType)" 2>$null
            
            if ($vms) {
                foreach ($vm in $vms) {
                    if ([string]::IsNullOrWhiteSpace($vm)) { continue }
                    $parts = $vm -split ","
                    
                    # 處理可能的空值
                    $vmName = if ($parts.Count -gt 0) { $parts[0] } else { "Unknown" }
                    $status = if ($parts.Count -gt 1) { $parts[1] } else { "Unknown" }
                    $zone   = if ($parts.Count -gt 2) { $parts[2] } else { "Unknown" }
                    $type   = if ($parts.Count -gt 3) { $parts[3] } else { "Unknown" }

                    $results += [PSCustomObject]@{
                        Account = $account
                        Project = $proj
                        VMName = $vmName
                        Status = $status
                        Zone = $zone
                        Type = $type
                    }
                    Write-Host "    -> 發現 VM: $vmName ($status)" -ForegroundColor Green
                }
            }
        } catch {
            # 忽略錯誤
        }
    }
}

# 恢復原本的帳號
gcloud config set account "wuchang1100606355@gmail.com" | Out-Null

# 輸出 Markdown 表格
Write-Host "`n### GCP VM 資源總結表"
Write-Host "| 帳號 | 專案 ID | VM 名稱 | 狀態 | 區域 (Zone) | 規格 |"
Write-Host "|---|---|---|---|---|---|"

if ($results.Count -eq 0) {
    Write-Host "| - | - | 無任何 VM | - | - | - |"
} else {
    foreach ($r in $results) {
        Write-Host "| $($r.Account) | $($r.Project) | $($r.VMName) | $($r.Status) | $($r.Zone) | $($r.Type) |"
    }
}
