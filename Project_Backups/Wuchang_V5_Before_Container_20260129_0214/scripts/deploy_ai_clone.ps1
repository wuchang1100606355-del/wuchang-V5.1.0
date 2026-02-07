param(
  [string]$Role = "merchant",
  [string]$Version = "1.0",
  [string]$Description = ""
)

$cloneName = "little-j-$Role`:$Version"
Write-Host "[Clone] 複製分身：$cloneName" -ForegroundColor Cyan

# 1. 複製模型
try {
  ollama cp "little-j:latest" $cloneName
  Write-Host "[Clone] ✓ Ollama 模型複製成功" -ForegroundColor Green
} catch {
  Write-Host "[Clone] ✗ Ollama 複製失敗：$_" -ForegroundColor Red
  exit 1
}

# 2. 建立分身資料夾
$roleDir = "C:/wuchang V5.1.0/knowledge_bases/little-j-$Role"
New-Item -ItemType Directory -Force -Path $roleDir | Out-Null
Write-Host "[Clone] ✓ 知識庫資料夾已建立" -ForegroundColor Green

# 3. 建立空白知識庫檔案
@("company_info.md", "procedures.md", "faq.md") | ForEach-Object {
  if (-not (Test-Path (Join-Path $roleDir $_))) {
    @"
# $Role 版小j - $_
## 內容待協會補充
"@ | Out-File -FilePath (Join-Path $roleDir $_) -Encoding UTF8
  }
}

# 4. 建立決策日誌資料夾
$decisionDir = "C:/wuchang V5.1.0/decision_logs/little-j-$Role"
New-Item -ItemType Directory -Force -Path $decisionDir | Out-Null
Write-Host "[Clone] ✓ 決策日誌資料夾已建立" -ForegroundColor Green

# 5. 建立分身清單記錄
$inventory = "C:/wuchang V5.1.0/docs/AI_CLONES_INVENTORY.md"
$entry = @"
## little-j-$Role`:$Version
- **角色**：$Role
- **建立時間**：$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- **描述**：$Description
- **狀態**：部署中
- **知識庫**：$roleDir
- **決策日誌**：$decisionDir

"@
if (Test-Path $inventory) {
  $entry | Add-Content -Path $inventory -Encoding UTF8
} else {
  "# 妹妹分身清單`n`n$entry" | Out-File -FilePath $inventory -Encoding UTF8
}

Write-Host "[Clone] ✓ 分身已登記於清單" -ForegroundColor Green
Write-Host "[Clone] 後續步驟：" -ForegroundColor Yellow
Write-Host "  1. 編輯 docs/AI_ROLES/little-j-$Role`_SYSTEM_PROMPT.md (角色指令)" -ForegroundColor Gray
Write-Host "  2. 於 $roleDir 新增專用知識庫檔案" -ForegroundColor Gray
Write-Host "  3. 執行 rotate_audit_logs.ps1 每日監控決策日誌" -ForegroundColor Gray
Write-Host "  4. 於評議會提交新分身上線案" -ForegroundColor Gray
