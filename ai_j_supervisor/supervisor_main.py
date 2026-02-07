# Odoo 內建 AI 小J 啟動腳本
# 執行此腳本即可啟動最高權限 AI 總成小J（Flask API 服務）

import os
import sys
from ai_j_supervisor.api import supervisor_api

if __name__ == "__main__":
    # 可根據需要設置環境變數
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    # 啟動 Flask API 服務
    supervisor_api.app.run(host="0.0.0.0", port=8888, debug=False)
