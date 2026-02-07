#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 總成小 J API 服務
提供最高權限開發者 UI 的 API 端點
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
from pathlib import Path

# 添加路徑
SUPERVISOR_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SUPERVISOR_ROOT))

from core.supervisor import get_supervisor

app = Flask(__name__)
CORS(app)

# 初始化總成系統
supervisor = get_supervisor()


@app.route('/')
def index():
    """首頁重定向到開發者 UI"""
    return send_from_directory('ui', 'developer_ui.html')


@app.route('/developer-ui')
def developer_ui():
    """開發者 UI"""
    return send_from_directory('ui', 'developer_ui.html')


@app.route('/api/supervisor/status', methods=['GET'])
def get_status():
    """取得系統狀態"""
    try:
        capabilities = supervisor.get_all_capabilities()
        return jsonify(capabilities)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/supervisor/capabilities', methods=['GET'])
def get_capabilities():
    """取得能力清單"""
    try:
        capabilities = supervisor.get_all_capabilities()
        # 確保返回正確的結構
        return jsonify({
            "capabilities": capabilities.get('capabilities', {})
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/supervisor/test-permissions', methods=['POST', 'GET'])
def test_permissions():
    """測試權限"""
    try:
        result = supervisor.test_permissions()
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/supervisor/execute', methods=['POST'])
def execute_command():
    """執行命令"""
    try:
        data = request.json
        command = data.get('command')
        params = data.get('params', {})
        
        if not command:
            return jsonify({"status": "error", "message": "缺少命令參數"}), 400
        
        result = supervisor.execute_command(command, params)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/supervisor/spatiotemporal/suggest', methods=['POST'])
def spatiotemporal_suggest():
    """時空建議（快捷端點）"""
    try:
        data = request.json
        result = supervisor.execute_command('spatiotemporal.suggest', data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/supervisor/spatiotemporal/schedule', methods=['POST'])
def spatiotemporal_schedule():
    """排程活動（快捷端點）"""
    try:
        data = request.json
        result = supervisor.execute_command('spatiotemporal.schedule', data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/supervisor/spatiotemporal/analyze', methods=['POST'])
def spatiotemporal_analyze():
    """分析模式（快捷端點）"""
    try:
        data = request.json
        result = supervisor.execute_command('spatiotemporal.analyze', data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("AI 總成小 J - 最高權限開發者 UI")
    print("=" * 60)
    print(f"開發者 UI: http://localhost:8888/developer-ui")
    print(f"API 文檔: http://localhost:8888/api/supervisor/status")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8888, debug=True)
