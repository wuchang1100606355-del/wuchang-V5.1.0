# 完全移除 VirtualBox 和虛擬機器
# remove_virtualbox_completely.ps1

Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "VirtualBox 完全移除工具" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""

# 檢查是否以管理員權限運行
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "警告: 需要管理員權限來卸載 VirtualBox" -ForegroundColor Yellow
    Write-Host "正在請求提升權限..." -ForegroundColor Yellow
    Write-Host ""
    
    # 以管理員權限重新執行
    $scriptPath = $MyInvocation.MyCommand.Path
    Start-Process powershell.exe -Verb RunAs -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$scriptPath`"" -Wait
    exit
}

Write-Host "已具有管理員權限" -ForegroundColor Green
Write-Host ""

# 1. 停止 VirtualBox 相關服務和進程
Write-Host "【步驟 1】停止 VirtualBox 服務和進程..." -ForegroundColor Yellow
Write-Host ""

$vboxProcesses = Get-Process -Name "VirtualBox*", "VBox*" -ErrorAction SilentlyContinue
if ($vboxProcesses) {
    Write-Host "找到運行中的 VirtualBox 進程，正在停止..." -ForegroundColor Yellow
    $vboxProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "✓ 已停止 VirtualBox 進程" -ForegroundColor Green
} else {
    Write-Host "✓ 沒有運行中的 VirtualBox 進程" -ForegroundColor Green
}
Write-Host ""

# 2. 刪除虛擬機器檔案
Write-Host "【步驟 2】刪除虛擬機器檔案..." -ForegroundColor Yellow
Write-Host ""

$vmPaths = @(
    "$env:USERPROFILE\VirtualBox VMs",
    "C:\VirtualBox VMs"
)

$totalFreed = 0

foreach ($vmPath in $vmPaths) {
    if (Test-Path $vmPath) {
        Write-Host "檢查目錄: $vmPath" -ForegroundColor Cyan
        
        $size = (Get-ChildItem $vmPath -Recurse -ErrorAction SilentlyContinue | 
                 Measure-Object -Property Length -Sum).Sum
        
        if ($size -gt 0) {
            $sizeGB = [math]::Round($size / 1GB, 2)
            Write-Host "  找到虛擬機器檔案: $sizeGB GB" -ForegroundColor Yellow
            
            try {
                Remove-Item $vmPath -Recurse -Force -ErrorAction Stop
                Write-Host "  ✓ 已刪除: $vmPath" -ForegroundColor Green
                $totalFreed += $size
            } catch {
                Write-Host "  ✗ 刪除失敗: $_" -ForegroundColor Red
            }
        } else {
            Write-Host "  ✓ 目錄為空或已刪除" -ForegroundColor Green
        }
        Write-Host ""
    }
}

# 3. 刪除 OVA 備份檔案
Write-Host "【步驟 3】刪除 OVA 備份檔案..." -ForegroundColor Yellow
Write-Host ""

$ovaPaths = @(
    "$env:USERPROFILE\OneDrive\文件\*.ova",
    "$env:USERPROFILE\Documents\*.ova",
    "$env:USERPROFILE\Downloads\*.ova"
)

foreach ($ovaPattern in $ovaPaths) {
    $ovaFiles = Get-ChildItem $ovaPattern -ErrorAction SilentlyContinue
    foreach ($ovaFile in $ovaFiles) {
        if ($ovaFile.Name -like "*Win-VM*" -or $ovaFile.Name -like "*VirtualBox*") {
            $sizeGB = [math]::Round($ovaFile.Length / 1GB, 2)
            Write-Host "找到 OVA 檔案: $($ovaFile.FullName)" -ForegroundColor Yellow
            Write-Host "  大小: $sizeGB GB" -ForegroundColor Yellow
            
            try {
                Remove-Item $ovaFile.FullName -Force -ErrorAction Stop
                Write-Host "  ✓ 已刪除" -ForegroundColor Green
                $totalFreed += $ovaFile.Length
            } catch {
                Write-Host "  ✗ 刪除失敗: $_" -ForegroundColor Red
            }
            Write-Host ""
        }
    }
}

# 4. 卸載 VirtualBox 程式
Write-Host "【步驟 4】卸載 VirtualBox 程式..." -ForegroundColor Yellow
Write-Host ""

$uninstallKeys = @(
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*"
)

$vboxUninstaller = $null

foreach ($keyPath in $uninstallKeys) {
    $apps = Get-ItemProperty $keyPath -ErrorAction SilentlyContinue | 
            Where-Object { $_.DisplayName -like "*VirtualBox*" }
    
    foreach ($app in $apps) {
        Write-Host "找到 VirtualBox 安裝: $($app.DisplayName)" -ForegroundColor Cyan
        Write-Host "  版本: $($app.DisplayVersion)" -ForegroundColor Cyan
        
        if ($app.UninstallString) {
            $vboxUninstaller = $app.UninstallString
            Write-Host "  卸載命令: $vboxUninstaller" -ForegroundColor Cyan
            Write-Host ""
            
            # 提取卸載程式路徑
            if ($vboxUninstaller -match '^"([^"]+)"') {
                $uninstallerPath = $matches[1]
                $uninstallerArgs = $vboxUninstaller.Substring($uninstallerPath.Length + 2).Trim('"')
                
                Write-Host "正在執行卸載..." -ForegroundColor Yellow
                try {
                    if ($uninstallerArgs) {
                        $process = Start-Process -FilePath $uninstallerPath -ArgumentList $uninstallerArgs -Wait -PassThru -NoNewWindow
                    } else {
                        $process = Start-Process -FilePath $uninstallerPath -Wait -PassThru -NoNewWindow
                    }
                    
                    if ($process.ExitCode -eq 0) {
                        Write-Host "  VirtualBox 已卸載" -ForegroundColor Green
                    } else {
                        Write-Host "  卸載程式返回代碼: $($process.ExitCode)" -ForegroundColor Yellow
                        Write-Host "  可能需要手動卸載" -ForegroundColor Yellow
                    }
                } catch {
                    Write-Host "  卸載失敗: $_" -ForegroundColor Red
                    Write-Host "  請手動從設定 > 應用程式中卸載" -ForegroundColor Yellow
                }
            }
            break
        }
    }
    
    if ($vboxUninstaller) { break }
}

if (-not $vboxUninstaller) {
    Write-Host "未找到 VirtualBox 的卸載程式" -ForegroundColor Yellow
    Write-Host "可能已經卸載，或需要手動卸載" -ForegroundColor Yellow
}

Write-Host ""

# 5. 清理殘留檔案和註冊表
Write-Host "【步驟 5】清理殘留檔案..." -ForegroundColor Yellow
Write-Host ""

$cleanupPaths = @(
    "$env:APPDATA\VirtualBox",
    "$env:LOCALAPPDATA\VirtualBox",
    "C:\Program Files\Oracle\VirtualBox",
    "C:\Program Files (x86)\Oracle\VirtualBox"
)

foreach ($cleanupPath in $cleanupPaths) {
    if (Test-Path $cleanupPath) {
        Write-Host "清理: $cleanupPath" -ForegroundColor Cyan
        try {
            Remove-Item $cleanupPath -Recurse -Force -ErrorAction Stop
            Write-Host "  ✓ 已清理" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠ 清理失敗（可能正在使用）: $_" -ForegroundColor Yellow
        }
        Write-Host ""
    }
}

# 總結
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "清理完成" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""

$totalFreedGB = [math]::Round($totalFreed / 1GB, 2)
Write-Host "已釋放空間: $totalFreedGB GB" -ForegroundColor Green
Write-Host ""

Write-Host "注意事項：" -ForegroundColor Yellow
Write-Host "  1. 如果 VirtualBox 未完全卸載，請從「設定 > 應用程式」手動卸載" -ForegroundColor Yellow
Write-Host "  2. 某些檔案可能正在使用，需要重啟後才能刪除" -ForegroundColor Yellow
Write-Host "  3. 建議重啟電腦以確保完全清理" -ForegroundColor Yellow
Write-Host ""
