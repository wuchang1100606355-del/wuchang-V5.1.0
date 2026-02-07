param(
  [string]$ServerUrl = "http://localhost:8080",
  [string]$OutRoot = "C:/wuchang V5.1.0/logs/evidence"
)

$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$outDir = Join-Path $OutRoot $ts
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

function Save-Json($obj, $path) {
  ($obj | ConvertTo-Json -Depth 10) | Out-File -FilePath $path -Encoding UTF8
}

function Save-Url($url, $path) {
  try { Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $path -TimeoutSec 15 } catch { }
}

Write-Host "[Pack] 目錄：$outDir" -ForegroundColor Cyan

# 1) 匯出伺服器端可稽核資料
try {
  $devices = Invoke-RestMethod -Method Get -Uri "$ServerUrl/devices"
  Save-Json $devices (Join-Path $outDir 'devices.json')
} catch {}

try {
  $arp = Invoke-RestMethod -Method Get -Uri "$ServerUrl/network/arp"
  Save-Json $arp (Join-Path $outDir 'arp.json')
} catch {}

# 事件 CSV 與 JSONL
Save-Url "$ServerUrl/events/export.csv" (Join-Path $outDir 'events.csv')
$eventsLog = "C:/wuchang V5.1.0/events.log.jsonl"
if (Test-Path $eventsLog) { Copy-Item $eventsLog (Join-Path $outDir 'events.log.jsonl') -Force }

# 2) 本地 LLM 佐證
try {
  $body = @{ prompt = "Evidence check: 請簡短回答你是本地或雲端來源" } | ConvertTo-Json -Compress
  $llm = Invoke-RestMethod -Method Post -Uri "$ServerUrl/llm/chat" -Body $body -ContentType "application/json"
  Save-Json $llm (Join-Path $outDir 'llm_chat.json')
} catch {}

# 3) 技能列表與範例
try {
  $skills = Invoke-RestMethod -Method Get -Uri "$ServerUrl/skills"
  Save-Json $skills (Join-Path $outDir 'skills.json')
} catch {}

try {
  $sbody = @{ name = 'translate'; input = @{ text = '歡迎來到里民服務站'; target = 'vi' } } | ConvertTo-Json -Compress
  $sres = Invoke-RestMethod -Method Post -Uri "$ServerUrl/skills/execute" -Body $sbody -ContentType "application/json"
  Save-Json $sres (Join-Path $outDir 'skill_translate_vi.json')
} catch {}

# 4) 文件與佐證
$docs = @(
  'C:/wuchang V5.1.0/docs/COMMUNITY_AI_BLUEPRINT.md',
  'C:/wuchang V5.1.0/docs/NEW_MERCHANT_SERVICE_FLOW.md',
  'C:/wuchang V5.1.0/docs/HARDWARE_REQUIREMENTS.md'
)
foreach ($d in $docs) { if (Test-Path $d) { Copy-Item $d $outDir -Force } }

# 5) 若有螢幕錄影，拷貝最新一支
$recDir = 'C:/wuchang V5.1.0/logs'
if (Test-Path $recDir) {
  $latest = Get-ChildItem $recDir -Filter 'screen-*.mp4' -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  if ($latest) { Copy-Item $latest.FullName (Join-Path $outDir $latest.Name) -Force }
}

# 6) 說明 README
$readme = @"
# Wuchang AI 證據包

- 產出時間：$ts
- 伺服器：$ServerUrl

檔案說明：
- devices.json：目前註冊裝置（含 last_seen）
- arp.json：區域網路 ARP 掃描
- events.csv / events.log.jsonl：所有操作事件（註冊/心跳/指令/技能/LLM）
- llm_chat.json：/llm/chat 取樣回覆（含 source=local/vertex）
- skills.json / skill_translate_vi.json：技能清單與翻譯範例
- screen-*.mp4：現場錄影檔（如有）
- COMMUNITY_AI_BLUEPRINT.md：社區AI藍圖
- NEW_MERCHANT_SERVICE_FLOW.md：新商家導入SOP
- HARDWARE_REQUIREMENTS.md：硬體建議與檢核

驗證建議：
1) 對照 llm_chat.json 的 source 與 events.* 的 llm.chat 事件
2) 打開 devices.json 確認 last_seen 持續更新
3) 對照 events.csv 中的 command.push 與現場錄影畫面
"@
$readme | Out-File -FilePath (Join-Path $outDir 'README.md') -Encoding UTF8

# 7) 壓縮
$zip = Join-Path $OutRoot ("evidence-$ts.zip")
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path (Join-Path $outDir '*') -DestinationPath $zip -Force
Write-Host "[Pack] 已完成：$zip" -ForegroundColor Green
