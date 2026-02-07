#!/bin/bash
# 五常 AI - Server 端 UI 控制客戶端啟動腳本
# 在 Server (192.168.50.249) 執行

echo "====================================================="
echo "  🎮 五常 AI - Server 端 UI 控制客戶端"
echo "====================================================="
echo ""

# 檢查 Python3
echo "檢查 Python 環境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 找不到 Python3！請先安裝 Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION"
echo ""

# 檢查依賴
echo "檢查依賴套件..."
PACKAGES_OK=true

for pkg in websockets dotenv; do
    if ! python3 -c "import $pkg" &> /dev/null; then
        echo "❌ 缺少套件: $pkg"
        PACKAGES_OK=false
    else
        echo "✅ $pkg 已安裝"
    fi
done

if [ "$PACKAGES_OK" = false ]; then
    echo ""
    echo "正在安裝缺少的套件..."
    python3 -m pip install -r requirements.txt
    echo ""
fi

# 檢查 .env 文件
echo "檢查配置文件..."
if [ ! -f ".env" ]; then
    echo "⚠️  找不到 .env 文件，使用預設配置"
    echo "建議複製 .env.example 為 .env 並修改密鑰"
else
    echo "✅ .env 配置已找到"
fi
echo ""

# 顯示網路資訊
echo "網路資訊:"
echo "  Server IP: 192.168.50.249"
echo "  目標本機: 192.168.50.84:8765"
echo ""

# 啟動客戶端
echo "====================================================="
echo "  🚀 正在啟動客戶端..."
echo "====================================================="
echo ""
echo "互動模式：按 q 退出"
echo ""

python3 server_ui_client.py "$@"
