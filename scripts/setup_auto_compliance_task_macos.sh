#!/bin/bash
# macOS/Linux 版本：設置全自動合規和證書檢查定時任務
# 使用 launchd (macOS) 或 systemd (Linux) 創建定時任務
# 合規要求：符合 Google 非營利組織合規要求

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/auto_compliance_certificate_check.py"
PLIST_NAME="com.wuchang.autocompliancecheck"
PLIST_FILE="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"

echo "========================================"
echo "  設置全自動合規和證書檢查定時任務"
echo "  Google 非營利組織合規確認"
echo "  macOS/Linux 版本"
echo "========================================"
echo ""

# 檢查 Python 是否可用
echo "檢查 Python 環境..."
if ! command -v python3 &> /dev/null; then
    echo "  ❌ Python3 未找到，請先安裝 Python"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "  ✓ Python 版本: $PYTHON_VERSION"

# 檢查必要套件
echo "檢查必要套件..."
REQUIRED_PACKAGES=("requests" "dnspython" "urllib3")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import ${package//-/_}" 2>/dev/null; then
        MISSING_PACKAGES+=("$package")
    else
        echo "  ✓ $package 已安裝"
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo "  ⚠ 缺少套件: ${MISSING_PACKAGES[*]}"
    echo "  正在安裝缺少的套件..."
    python3 -m pip install --quiet "${MISSING_PACKAGES[@]}"
    echo "  ✓ 套件安裝完成"
fi

# 檢查腳本文件是否存在
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "  ❌ 檢查腳本不存在: $PYTHON_SCRIPT"
    exit 1
fi
echo "  ✓ 檢查腳本存在: $PYTHON_SCRIPT"
echo ""

# 檢測操作系統並設置
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "檢測到 macOS，使用 launchd 創建定時任務..."
    setup_macos_launchd
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "檢測到 Linux，使用 systemd 創建定時任務..."
    setup_linux_systemd
else
    echo "  ⚠ 未識別的操作系統: $OSTYPE"
    echo "  請手動設置定時任務"
    exit 1
fi

function setup_macos_launchd() {
    # 創建 LaunchAgents 目錄
    mkdir -p "$HOME/Library/LaunchAgents"
    
    # 創建 plist 文件
    cat > "$PLIST_FILE" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_NAME}</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(which python3)</string>
        <string>${PYTHON_SCRIPT}</string>
    </array>
    <key>WorkingDirectory</key>
    <string>${PROJECT_ROOT}</string>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>${PROJECT_ROOT}/logs/compliance_check_stdout.log</string>
    <key>StandardErrorPath</key>
    <string>${PROJECT_ROOT}/logs/compliance_check_stderr.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
EOF
    
    echo "  ✓ LaunchAgent plist 文件已創建: $PLIST_FILE"
    
    # 卸載現有任務（如果存在）
    if launchctl list "$PLIST_NAME" &>/dev/null; then
        echo "  卸載現有任務..."
        launchctl unload "$PLIST_FILE" 2>/dev/null || true
    fi
    
    # 加載新任務
    echo "  加載定時任務..."
    launchctl load "$PLIST_FILE"
    
    echo "  ✓ 定時任務已創建並加載"
    echo ""
    echo "任務詳情:"
    echo "  名稱: $PLIST_NAME"
    echo "  執行頻率: 每小時執行一次（3600 秒）"
    echo "  Python: $(which python3)"
    echo "  腳本: $PYTHON_SCRIPT"
    echo "  日誌: ${PROJECT_ROOT}/logs/compliance_check_*.log"
    echo ""
    echo "管理命令:"
    echo "  查看任務: launchctl list $PLIST_NAME"
    echo "  卸載任務: launchctl unload $PLIST_FILE"
    echo "  重新加載: launchctl unload $PLIST_FILE && launchctl load $PLIST_FILE"
    echo "  查看日誌: tail -f ${PROJECT_ROOT}/logs/compliance_check_*.log"
    echo ""
    
    # 詢問是否立即測試執行
    read -p "是否立即測試執行一次？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "執行測試..."
        python3 "$PYTHON_SCRIPT"
    fi
}

function setup_linux_systemd() {
    SERVICE_NAME="wuchang-autocompliancecheck"
    SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
    TIMER_FILE="/etc/systemd/system/${SERVICE_NAME}.timer"
    
    echo "  需要 sudo 權限來創建 systemd 服務..."
    
    # 創建服務文件
    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Wuchang Auto Compliance and Certificate Check
After=network.target

[Service]
Type=oneshot
User=$USER
WorkingDirectory=${PROJECT_ROOT}
ExecStart=$(which python3) ${PYTHON_SCRIPT}
StandardOutput=append:${PROJECT_ROOT}/logs/compliance_check_stdout.log
StandardError=append:${PROJECT_ROOT}/logs/compliance_check_stderr.log
Environment="PATH=/usr/local/bin:/usr/bin:/bin"

[Install]
WantedBy=multi-user.target
EOF
    
    # 創建定時器文件
    sudo tee "$TIMER_FILE" > /dev/null <<EOF
[Unit]
Description=Run Wuchang Compliance Check Hourly
Requires=${SERVICE_NAME}.service

[Timer]
OnCalendar=hourly
OnBootSec=1h
Persistent=true

[Install]
WantedBy=timers.target
EOF
    
    echo "  ✓ Systemd 服務和定時器文件已創建"
    
    # 重新加載 systemd
    sudo systemctl daemon-reload
    
    # 啟用並啟動定時器
    sudo systemctl enable "${SERVICE_NAME}.timer"
    sudo systemctl start "${SERVICE_NAME}.timer"
    
    echo "  ✓ 定時任務已啟用並啟動"
    echo ""
    echo "任務詳情:"
    echo "  服務名稱: $SERVICE_NAME"
    echo "  執行頻率: 每小時執行一次"
    echo "  Python: $(which python3)"
    echo "  腳本: $PYTHON_SCRIPT"
    echo ""
    echo "管理命令:"
    echo "  查看定時器狀態: sudo systemctl status ${SERVICE_NAME}.timer"
    echo "  查看服務狀態: sudo systemctl status ${SERVICE_NAME}.service"
    echo "  停止定時器: sudo systemctl stop ${SERVICE_NAME}.timer"
    echo "  啟用定時器: sudo systemctl enable ${SERVICE_NAME}.timer"
    echo "  查看日誌: journalctl -u ${SERVICE_NAME}.service"
    echo ""
}

echo ""
echo "========================================"
echo "  ✅ 合規聲明"
echo "========================================"
echo "  符合 Google 非營利組織合規要求"
echo "  所有操作均以合規為最高要件"
echo ""
