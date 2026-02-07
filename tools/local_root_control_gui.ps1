<#
GUI Root Control Panel (WinForms)
Requires: PowerShell 5+, Windows, Run as Administrator, Docker + docker-compose, project at C:\wuchang V5.1.0
Features: System Control, AI Chat, Web Browsing, Multimedia Upload, Image Generation, Google Workspace APIs
#>
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[void][System.Reflection.Assembly]::LoadWithPartialName('Microsoft.VisualBasic')

# Guard: require admin
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    [System.Windows.Forms.MessageBox]::Show('請以系統管理員模式啟動此面板','權限不足',[System.Windows.Forms.MessageBoxButtons]::OK,[System.Windows.Forms.MessageBoxIcon]::Error)
    exit 1
}

$workspace = 'C:\wuchang V5.1.0'
$compose = Join-Path $workspace 'docker-compose.yml'

function Invoke-Compose($args) {
    if (-not (Test-Path $compose)) { return 'compose file not found' }
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = 'cmd.exe'
    $psi.Arguments = "/c cd /d `"$workspace`" && docker-compose $args"
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $p = [System.Diagnostics.Process]::Start($psi)
    $out = $p.StandardOutput.ReadToEnd()
    $err = $p.StandardError.ReadToEnd()
    $p.WaitForExit()
    return ($out + $err)
}

function Invoke-Cmd($cmd) {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = 'cmd.exe'
    $psi.Arguments = "/c $cmd"
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $p = [System.Diagnostics.Process]::Start($psi)
    $out = $p.StandardOutput.ReadToEnd()
    $err = $p.StandardError.ReadToEnd()
    $p.WaitForExit()
    return ($out + $err)
}

function Search-Web($query) {
    try {
        $encodedQuery = [System.Web.HttpUtility]::UrlEncode($query)
        $searchUrl = "https://html.duckduckgo.com/html/?q=$encodedQuery"
        $response = Invoke-WebRequest -Uri $searchUrl -UseBasicParsing -TimeoutSec 10
        $results = $response.Content -split '<div class="result__snippet">' | Select-Object -Skip 1 -First 5
        $summary = "🔍 搜尋結果（前5筆）：`r`n"
        foreach ($r in $results) {
            $snippet = ($r -split '</div>')[0] -replace '<[^>]+>', '' -replace '&quot;', '"' -replace '&amp;', '&'
            $summary += "- $($snippet.Trim())`r`n"
        }
        return $summary
    } catch {
        return "搜尋失敗：$($_.Exception.Message)"
    }
}

function Fetch-Webpage($url) {
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 15
        $content = $response.Content -replace '<script[^>]*>.*?</script>', '' -replace '<style[^>]*>.*?</style>', ''
        $content = $content -replace '<[^>]+>', ' ' -replace '\s+', ' '
        return $content.Substring(0, [Math]::Min(2000, $content.Length))
    } catch {
        return "無法取得網頁：$($_.Exception.Message)"
    }
}

Add-Type -AssemblyName System.Web

$global:BrowseMode = $false

$form = New-Object System.Windows.Forms.Form
$form.Text = '新北市三重區五常社區發展協會 - 小j AI 總管 ✓ (Google Workspace for Nonprofits 已啟用)'
$form.Size = New-Object System.Drawing.Size(1200,800)
$form.StartPosition = 'CenterScreen'

$btnStart = New-Object System.Windows.Forms.Button
$btnStart.Text = '啟動核心 (up -d)'
$btnStart.Size = New-Object System.Drawing.Size(150,30)
$btnStart.Location = New-Object System.Drawing.Point(20,20)
$btnStart.Add_Click({ $output.Text = Invoke-Compose 'up -d' })

$btnStop = New-Object System.Windows.Forms.Button
$btnStop.Text = '停止核心 (down)'
$btnStop.Size = New-Object System.Drawing.Size(150,30)
$btnStop.Location = New-Object System.Drawing.Point(180,20)
$btnStop.Add_Click({
    $confirm = [System.Windows.Forms.MessageBox]::Show('確定要停止核心服務？','確認', 'YesNo','Warning')
    if ($confirm -eq 'Yes') { $output.Text = Invoke-Compose 'down' }
})

$btnParams = New-Object System.Windows.Forms.Button
$btnParams.Text = '查 AI 參數'
$btnParams.Size = New-Object System.Drawing.Size(150,30)
$btnParams.Location = New-Object System.Drawing.Point(340,20)
$btnParams.Add_Click({
    $cmd = "docker exec wuchangv510-wuchang-web-1 bash -lc `"odoo shell -d admin --db_host=db --db_user=odoo --db_password=odoo <<'PY'
env = env['ir.config_parameter'].sudo()
keys = ['wuchang.cloud_approved','wuchang.google.project_id','wuchang.google.location','wuchang.ai_mode','wuchang.llm_base_url','wuchang.gemini_api_key']
for k in keys:
    print(k, '=>', env.get_param(k))
PY`""
    $output.Text = Invoke-Cmd $cmd
})

$btnLogsOdoo = New-Object System.Windows.Forms.Button
$btnLogsOdoo.Text = 'Odoo 日誌 (新視窗)'
$btnLogsOdoo.Size = New-Object System.Drawing.Size(150,30)
$btnLogsOdoo.Location = New-Object System.Drawing.Point(20,60)
$btnLogsOdoo.Add_Click({ Start-Process powershell "-NoLogo -NoExit -Command `"docker logs -f wuchangv510-wuchang-web-1`"" })

$btnLogsCaddy = New-Object System.Windows.Forms.Button
$btnLogsCaddy.Text = 'Caddy 日誌 (新視窗)'
$btnLogsCaddy.Size = New-Object System.Drawing.Size(150,30)
$btnLogsCaddy.Location = New-Object System.Drawing.Point(180,60)
$btnLogsCaddy.Add_Click({ Start-Process powershell "-NoLogo -NoExit -Command `"docker logs -f wuchangv510-caddy-1`"" })

$btnBrowseMode = New-Object System.Windows.Forms.Button
$btnBrowseMode.Text = '🌐 瀏覽模式: OFF'
$btnBrowseMode.Size = New-Object System.Drawing.Size(150,30)
$btnBrowseMode.Location = New-Object System.Drawing.Point(340,60)
$btnBrowseMode.BackColor = [System.Drawing.Color]::LightGray
$btnBrowseMode.Add_Click({
    $global:BrowseMode = -not $global:BrowseMode
    if ($global:BrowseMode) {
        $btnBrowseMode.Text = '🌐 瀏覽模式: ON'
        $btnBrowseMode.BackColor = [System.Drawing.Color]::LightGreen
        $chatHistory.AppendText("[系統] 瀏覽模式已啟用，可使用：`r`n")
        $chatHistory.AppendText("  - '搜尋：關鍵字' 進行網頁搜尋`r`n")
        $chatHistory.AppendText("  - '訪問：URL' 抓取網頁內容`r`n`r`n")
    } else {
        $btnBrowseMode.Text = '🌐 瀏覽模式: OFF'
        $btnBrowseMode.BackColor = [System.Drawing.Color]::LightGray
        $chatHistory.AppendText("[系統] 瀏覽模式已關閉`r`n`r`n")
    }
})

# 第三排：多媒體與AI功能
$btnUploadFile = New-Object System.Windows.Forms.Button
$btnUploadFile.Text = '📁 上傳檔案'
$btnUploadFile.Size = New-Object System.Drawing.Size(110,30)
$btnUploadFile.Location = New-Object System.Drawing.Point(20,100)
$btnUploadFile.BackColor = [System.Drawing.Color]::FromArgb(135,206,250)
$btnUploadFile.Add_Click({
    $openFileDialog = New-Object System.Windows.Forms.OpenFileDialog
    $openFileDialog.Filter = "所有檔案 (*.*)|*.*|圖片 (*.jpg;*.png;*.gif)|*.jpg;*.png;*.gif|音訊 (*.mp3;*.wav;*.m4a)|*.mp3;*.wav;*.m4a|影片 (*.mp4;*.avi;*.mkv)|*.mp4;*.avi;*.mkv"
    $openFileDialog.Title = "選擇要上傳的檔案"
    $openFileDialog.Multiselect = $true
    
    if ($openFileDialog.ShowDialog() -eq 'OK') {
        $chatHistory.AppendText("[系統] 準備上傳 $($openFileDialog.FileNames.Count) 個檔案...`r`n")
        foreach ($file in $openFileDialog.FileNames) {
            $fileName = [System.IO.Path]::GetFileName($file)
            $destPath = "$workspace\uploads\$fileName"
            New-Item -ItemType Directory -Force -Path "$workspace\uploads" | Out-Null
            Copy-Item -Path $file -Destination $destPath -Force
            $chatHistory.AppendText("✓ 已複製: $fileName → uploads/`r`n")
            
            # 通知Odoo處理檔案
            $fileType = [System.IO.Path]::GetExtension($file).ToLower()
            $odooCmd = @"
docker exec wuchangv510-wuchang-web-1 bash -lc "odoo shell -d admin --db_host=db --db_user=odoo --db_password=odoo <<'PYUPLOAD'
ai_logic = env['wuchang.ai.logic']
file_path = '/mnt/jules-config/../uploads/$fileName'
file_type = '$fileType'
print('[小j] 已收到檔案:', file_path, '類型:', file_type)
# 未來可擴展：圖片分析、語音轉文字等
PYUPLOAD"
"@
            $result = Invoke-Cmd $odooCmd
            $chatHistory.AppendText("$result`r`n")
        }
        $chatHistory.AppendText("`r`n")
    }
})

$btnUploadFolder = New-Object System.Windows.Forms.Button
$btnUploadFolder.Text = '📂 上傳資料夾'
$btnUploadFolder.Size = New-Object System.Drawing.Size(110,30)
$btnUploadFolder.Location = New-Object System.Drawing.Point(140,100)
$btnUploadFolder.BackColor = [System.Drawing.Color]::FromArgb(135,206,250)
$btnUploadFolder.Add_Click({
    $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
    $folderBrowser.Description = "選擇要上傳的資料夾"
    $folderBrowser.ShowNewFolderButton = $false
    
    if ($folderBrowser.ShowDialog() -eq 'OK') {
        $sourceFolder = $folderBrowser.SelectedPath
        $folderName = [System.IO.Path]::GetFileName($sourceFolder)
        $destFolder = "$workspace\uploads\$folderName"
        
        $chatHistory.AppendText("[系統] 正在複製資料夾: $folderName...`r`n")
        Copy-Item -Path $sourceFolder -Destination $destFolder -Recurse -Force
        
        $fileCount = (Get-ChildItem -Path $destFolder -Recurse -File).Count
        $chatHistory.AppendText("✓ 已複製資料夾: $folderName ($fileCount 個檔案)`r`n`r`n")
    }
})

$btnGenerateImage = New-Object System.Windows.Forms.Button
$btnGenerateImage.Text = '🎨 生成圖像'
$btnGenerateImage.Size = New-Object System.Drawing.Size(110,30)
$btnGenerateImage.Location = New-Object System.Drawing.Point(260,100)
$btnGenerateImage.BackColor = [System.Drawing.Color]::FromArgb(255,182,193)
$btnGenerateImage.Add_Click({
    $prompt = [Microsoft.VisualBasic.Interaction]::InputBox("請輸入圖像描述（英文效果較佳）：", "AI 圖像生成", "A beautiful sunset over mountains")
    if ($prompt) {
        $chatHistory.AppendText("[系統] 正在使用 Vertex AI Imagen 生成圖像...`r`n")
        $chatHistory.AppendText("提示詞: $prompt`r`n")
        
        $imageCmd = @"
docker exec wuchangv510-wuchang-web-1 bash -lc "odoo shell -d admin --db_host=db --db_user=odoo --db_password=odoo <<'PYIMAGE'
from vertexai.preview.vision_models import ImageGenerationModel
import base64
import os

try:
    model = ImageGenerationModel.from_pretrained('imagegeneration@006')
    response = model.generate_images(prompt='$($prompt.Replace("'","\'"))', number_of_images=1)
    
    if response.images:
        img_data = response.images[0]._image_bytes
        output_path = '/mnt/jules-config/../uploads/generated_image.png'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(img_data)
        print('[小j] 圖像已生成: uploads/generated_image.png')
    else:
        print('[小j] 圖像生成失敗：無回應')
except Exception as e:
    print('[小j] 圖像生成錯誤:', str(e))
    print('提示：請確認已啟用 Vertex AI Imagen API')
PYIMAGE"
"@
        $result = Invoke-Cmd $imageCmd
        $chatHistory.AppendText("$result`r`n`r`n")
    }
})

$btnGoogleWorkspace = New-Object System.Windows.Forms.Button
$btnGoogleWorkspace.Text = '☁️ Google 服務'
$btnGoogleWorkspace.Size = New-Object System.Drawing.Size(110,30)
$btnGoogleWorkspace.Location = New-Object System.Drawing.Point(380,100)
$btnGoogleWorkspace.BackColor = [System.Drawing.Color]::FromArgb(144,238,144)
$btnGoogleWorkspace.Add_Click({
    $services = @(
        "1. Drive API - 文件儲存",
        "2. Docs API - 文件編輯",
        "3. Sheets API - 試算表",
        "4. Gmail API - 郵件發送",
        "5. Calendar API - 行事曆"
    )
    $choice = [Microsoft.VisualBasic.Interaction]::InputBox($services -join "`n`n" + "`n`n請輸入服務編號(1-5)：", "Google Workspace for Nonprofits", "1")
    
    $serviceName = switch ($choice) {
        "1" { "drive" }
        "2" { "docs" }
        "3" { "sheets" }
        "4" { "gmail" }
        "5" { "calendar" }
        default { "" }
    }
    
    if ($serviceName) {
        $chatHistory.AppendText("[系統] 正在初始化 Google $serviceName API...`r`n")
        $googleCmd = @"
docker exec wuchangv510-wuchang-web-1 bash -lc "odoo shell -d admin --db_host=db --db_user=odoo --db_password=odoo <<'PYGOOGLE'
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

try:
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not creds_path or not os.path.exists(creds_path):
        print('[小j] 錯誤：找不到服務帳戶金鑰')
        print('請確認 config/gcp/littlej-sa.json 已正確配置')
    else:
        creds = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=['https://www.googleapis.com/auth/$serviceName']
        )
        service = build('$serviceName', 'v3', credentials=creds)
        print('[小j] $serviceName API 已就緒！')
        print('提示：非營利組織可享有 Google Workspace 免費方案')
        print('請至 google.com/nonprofits 申請認證')
except Exception as e:
    print('[小j] API 初始化失敗:', str(e))
PYGOOGLE"
"@
        $result = Invoke-Cmd $googleCmd
        $chatHistory.AppendText("$result`r`n`r`n")
    }
})

$output = New-Object System.Windows.Forms.TextBox
$output.Multiline = $true
$output.ScrollBars = 'Vertical'
$output.ReadOnly = $true
$output.Font = New-Object System.Drawing.Font('Consolas',9)
$output.Location = New-Object System.Drawing.Point(20,140)
$output.Size = New-Object System.Drawing.Size(500,280)

# AI Chat Section
$lblChat = New-Object System.Windows.Forms.Label
$lblChat.Text = '💬 與小j對話（本地優先/雲端備援 + 多媒體分析）'
$lblChat.Font = New-Object System.Drawing.Font('Microsoft JhengHei',10,[System.Drawing.FontStyle]::Bold)
$lblChat.Location = New-Object System.Drawing.Point(540,20)
$lblChat.Size = New-Object System.Drawing.Size(620,25)

$chatHistory = New-Object System.Windows.Forms.TextBox
$chatHistory.Multiline = $true
$chatHistory.ScrollBars = 'Vertical'
$chatHistory.ReadOnly = $true
$chatHistory.Font = New-Object System.Drawing.Font('Microsoft JhengHei',9)
$chatHistory.Location = New-Object System.Drawing.Point(540,50)
$chatHistory.Size = New-Object System.Drawing.Size(620,550)
$chatHistory.BackColor = [System.Drawing.Color]::FromArgb(240,248,255)

$txtQuestion = New-Object System.Windows.Forms.TextBox
$txtQuestion.Font = New-Object System.Drawing.Font('Microsoft JhengHei',9)
$txtQuestion.Location = New-Object System.Drawing.Point(540,610)
$txtQuestion.Size = New-Object System.Drawing.Size(520,30)
$txtQuestion.Text = '請問小j...'
$txtQuestion.ForeColor = [System.Drawing.Color]::Gray
$txtQuestion.Add_GotFocus({
    if ($txtQuestion.Text -eq '請問小j...') {
        $txtQuestion.Text = ''
        $txtQuestion.ForeColor = [System.Drawing.Color]::Black
    }
})
$txtQuestion.Add_LostFocus({
    if ($txtQuestion.Text -eq '') {
        $txtQuestion.Text = '請問小j...'
        $txtQuestion.ForeColor = [System.Drawing.Color]::Gray
    }
})

$btnAsk = New-Object System.Windows.Forms.Button
$btnAsk.Text = '發送'
$btnAsk.Size = New-Object System.Drawing.Size(90,30)
$btnAsk.Location = New-Object System.Drawing.Point(1070,610)
$btnAsk.BackColor = [System.Drawing.Color]::FromArgb(70,130,180)
$btnAsk.ForeColor = [System.Drawing.Color]::White
$btnAsk.FlatStyle = 'Flat'
$btnAsk.Add_Click({
    $q = $txtQuestion.Text
    if ($q -eq '' -or $q -eq '請問小j...') { return }
    
    $chatHistory.AppendText("你: $q`r`n")
    $txtQuestion.Text = ''
    
    $contextData = ""
    $originalQ = $q
    
    # 瀏覽模式處理
    if ($global:BrowseMode) {
        if ($q -match '^搜尋[：:](.*)'  -or $q -match '^search[：:](.*)') {
            $query = $matches[1].Trim()
            $chatHistory.AppendText("[系統] 正在搜尋: $query...`r`n")
            $contextData = Search-Web $query
            $chatHistory.AppendText("$contextData`r`n")
            $q = "根據以下搜尋結果回答：`n$contextData`n原問題：$query"
        }
        elseif ($q -match '^訪問[：:](.*)'  -or $q -match '^visit[：:](.*)') {
            $url = $matches[1].Trim()
            $chatHistory.AppendText("[系統] 正在訪問: $url...`r`n")
            $contextData = Fetch-Webpage $url
            $chatHistory.AppendText("[系統] 已擷取網頁內容（前2000字）`r`n")
            $q = "請分析以下網頁內容：`n$contextData"
        }
        elseif ($q -match 'https?://') {
            $url = ($q -split ' ')[0]
            $chatHistory.AppendText("[系統] 偵測到網址，正在訪問: $url...`r`n")
            $contextData = Fetch-Webpage $url
            $chatHistory.AppendText("[系統] 已擷取網頁內容`r`n")
            $q = $q.Replace($url, "網頁內容：$contextData")
        }
    }
    
    # Call AI via Odoo
    $aiCmd = @"
docker exec wuchangv510-wuchang-web-1 bash -lc "odoo shell -d admin --db_host=db --db_user=odoo --db_password=odoo <<'PYEND'
ai_logic = env['wuchang.ai.logic']
try:
    response = ai_logic.analyze_operations('$($q.Replace("'","\'"))')
    print(response)
except Exception as e:
    print('[小j] 抱歉，哥哥，我遇到了點困難：', e)
PYEND"
"@
    
    $chatHistory.AppendText("小j: [思考中...]`r`n")
    $form.Refresh()
    
    $answer = Invoke-Cmd $aiCmd
    $chatHistory.Text = $chatHistory.Text.Replace('[思考中...]', $answer.Trim())
    $chatHistory.AppendText("`r`n`r`n")
    $chatHistory.SelectionStart = $chatHistory.Text.Length
    $chatHistory.ScrollToCaret()
})

# Status bar
$statusBar = New-Object System.Windows.Forms.Label
$statusBar.Text = '✓ 五常社區發展協會 | admin@wuchang.life | Google Workspace Business Standard (FREE) | 本地優先/雲端備援 | 創始人: 江政隆 F1247717117'
$statusBar.Font = New-Object System.Drawing.Font('Microsoft JhengHei',9,[System.Drawing.FontStyle]::Bold)
$statusBar.Location = New-Object System.Drawing.Point(20,430)
$statusBar.Size = New-Object System.Drawing.Size(500,100)
$statusBar.ForeColor = [System.Drawing.Color]::DarkGreen
$statusBar.BackColor = [System.Drawing.Color]::FromArgb(200,255,200)

$form.Controls.AddRange(@($btnStart,$btnStop,$btnParams,$btnLogsOdoo,$btnLogsCaddy,$btnBrowseMode,$btnUploadFile,$btnUploadFolder,$btnGenerateImage,$btnGoogleWorkspace,$output,$lblChat,$chatHistory,$txtQuestion,$btnAsk,$statusBar))
[void]$form.ShowDialog()
