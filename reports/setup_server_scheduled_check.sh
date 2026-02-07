#!/bin/bash
# 伺服器端定時檢查部署狀態設定腳本
# 適用於 Linux 伺服器

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_FILE="$SCRIPT_DIR/server_deployment_checker.py"
PYTHON_PATH=$(which python3 || which python)

echo "========================================"
echo "設定伺服器定時檢查部署狀態"
echo "========================================"
echo ""

# 檢查 Python
if [ -z "$PYTHON_PATH" ]; then
    echo "❌ 錯誤: 未找到 Python"
    exit 1
fi

echo "✓ Python 路徑: $PYTHON_PATH"
echo "✓ 腳本路徑: $SCRIPT_FILE"
echo ""

# 檢查腳本是否存在
if [ ! -f "$SCRIPT_FILE" ]; then
    echo "❌ 錯誤: 腳本不存在: $SCRIPT_FILE"
    exit 1
fi

# 設定檢查頻率
echo "請選擇檢查頻率："
echo "  1. 每小時檢查一次"
echo "  2. 每 2 小時檢查一次"
echo "  3. 每 4 小時檢查一次（推薦）"
echo "  4. 每天檢查一次（上午 8 點）"
echo "  5. 自訂間隔（Cron 格式）"
echo ""

read -p "請選擇 (1-5): " choice

case $choice in
    1)
        CRON_SCHEDULE="0 * * * *"
        DESCRIPTION="每小時"
        ;;
    2)
        CRON_SCHEDULE="0 */2 * * *"
        DESCRIPTION="每 2 小時"
        ;;
    3)
        CRON_SCHEDULE="0 */4 * * *"
        DESCRIPTION="每 4 小時"
        ;;
    4)
        CRON_SCHEDULE="0 8 * * *"
        DESCRIPTION="每天上午 8 點"
        ;;
    5)
        read -p "請輸入 Cron 格式（例如: 0 */6 * * *）: " CRON_SCHEDULE
        DESCRIPTION="自訂"
        ;;
    *)
        echo "❌ 無效的選擇"
        exit 1
        ;;
esac

echo ""
echo "設定 Cron 任務..."
echo ""

# 建立 Cron 任務
CRON_ENTRY="$CRON_SCHEDULE cd $SCRIPT_DIR && $PYTHON_PATH $SCRIPT_FILE >> $SCRIPT_DIR/logs/server_deployment_check_cron.log 2>&1"

# 檢查任務是否已存在
TASK_NAME="server_deployment_check"
EXISTING_TASK=$(crontab -l 2>/dev/null | grep -v "^#" | grep "$SCRIPT_FILE" || true)

if [ -n "$EXISTING_TASK" ]; then
    echo "⚠️  任務已存在，將更新..."
    # 移除舊任務
    crontab -l 2>/dev/null | grep -v "$SCRIPT_FILE" | crontab -
fi

# 新增新任務
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo "✓ Cron 任務已設定: $DESCRIPTION"
echo ""
echo "檢查頻率: $CRON_SCHEDULE ($DESCRIPTION)"
echo ""
echo "下一步："
echo "  1. 查看 Cron 任務: crontab -l"
echo "  2. 手動測試: $PYTHON_PATH $SCRIPT_FILE"
echo "  3. 查看報告: $SCRIPT_DIR/reports/server_deployment_status_latest.md"
echo "  4. 查看日誌: $SCRIPT_DIR/logs/server_deployment_check_*.log"
echo ""
