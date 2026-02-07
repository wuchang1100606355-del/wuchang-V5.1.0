#!/bin/bash
# ==============================================================================
# Wuchang OS v5.0.0 - Rapid Deployment Protocol (Twin-Turbo)
# ==============================================================================
# 這是為了讓您在開發過程中，能以最快速度將代碼變更應用到 Odoo 核心。
#
# 原理：
# 1. 不停止主服務，先啟動一個「臨時工 (Temporary Worker)」容器。
# 2. 由臨時工負責對資料庫執行 -u (Update) 升級指令。
# 3. 資料庫更新完畢後，才重啟主服務 (Web Node)。
# ==============================================================================

echo ">>> [1/3] 啟動五常熱部署協議 (Initiating Hot-Deploy)..."

# 定義要更新的模組列表 (可根據需求增減)
MODULES="wuchang_core,wuchang_business,wuchang_web_portal"

echo ">>> [2/3] 正在更新資料庫結構 (Database Schema Update)..."
echo "    Target Modules: "
# 使用 docker-compose run 開一個新容器來執行升級，不佔用 8069 port
docker-compose run --rm wuchang-web odoo -u  --stop-after-init --db_host=db --db_user=odoo --db_password=odoo

if [ True -eq 0 ]; then
    echo ">>> [3/3] 資料庫更新成功！正在重啟 Web 節點..."
    docker-compose restart wuchang-web
    echo ">>> 部署完成 (Deployment Complete)！"
    echo "    請訪問: http://localhost:8069"
else
    echo "!!! [ERROR] 資料庫更新失敗，請檢查日誌。"
    exit 1
fi
