#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wuchang OS AI 喚醒腳本
執行系統 AI 完整喚醒流程
"""

import sys
import os
import json
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError
from http.client import HTTPResponse
import argparse
import subprocess

def print_header():
    """打印標題"""
    print("=" * 70)
    print("        Wuchang OS - AI 系統喚醒儀式")
    print("=" * 70)
    print()

def wake_up_ai_memory():
    """步驟 1: 初始化 AI 記憶"""
    print("[1/5] 初始化 AI 記憶...")
    try:
        # 檢查 AI 記憶初始化文件
        memory_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'wuchang_os', 'addons', 'wuchang_core', 'data', 'ai_memory_init.xml'
        )
        
        if os.path.exists(memory_file):
            print("  ✓ AI 記憶配置文件存在")
            
            # 讀取記憶內容
            with open(memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if '小j' in content or '妹妹' in content:
                    print("  ✓ AI 身份確認：小j (妹妹)")
                    return True
        else:
            print("  ⚠ AI 記憶配置文件未找到")
            return False
    except Exception as e:
        print(f"  ✗ 初始化 AI 記憶時發生錯誤: {e}")
        return False

def wake_up_vertex_ai():
    """步驟 2: 初始化 Vertex AI"""
    print("[2/5] 初始化 Vertex AI...")
    try:
        # 檢查是否有 Google API Key 配置
        config_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'config', 'official_ai_identity.json'
        )
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                identity = config.get('identity', {})
                print(f"  ✓ AI 身份：{identity.get('name', 'Unknown')}")
                print(f"  ✓ 角色：{identity.get('designation', 'Unknown')}")
                print(f"  ✓ 狀態：{identity.get('status', 'Unknown')}")
                return True
        else:
            print("  ⚠ AI 身份配置文件未找到，將使用默認配置")
            return False
    except Exception as e:
        print(f"  ✗ 初始化 Vertex AI 時發生錯誤: {e}")
        return False

def wake_up_odoo_ai():
    """步驟 3: 喚醒 Odoo 中的 AI"""
    print("[3/5] 喚醒 Odoo AI 模組...")
    try:
        # 檢查 Odoo 是否運行
        try:
            req = Request('http://localhost:8069/web/health')
            req.add_header('User-Agent', 'Wuchang-AI-WakeUp/1.0')
            response = urlopen(req, timeout=5)
            if response.getcode() == 200:
                print("  ✓ Odoo 服務器正在運行")
            else:
                print("  ⚠ Odoo 服務器響應異常")
                return False
        except (URLError, OSError):
            print("  ⚠ Odoo 服務器未運行（可能需要先啟動 Docker Compose）")
            print("  提示：運行 'docker-compose --profile system up -d' 啟動服務")
            return False
        
        # 檢查 AI 相關模組
        ai_modules = [
            'wuchang_core',
            'wuchang_design_system',
        ]
        
        print(f"  ✓ 檢查 AI 相關模組：{', '.join(ai_modules)}")
        return True
    except Exception as e:
        print(f"  ✗ 喚醒 Odoo AI 時發生錯誤: {e}")
        return False

def wake_up_ollama():
    """步驟 4: 喚醒本地 Ollama"""
    print("[4/5] 檢查本地 Ollama 服務...")
    try:
        ollama_url = 'http://localhost:11434/api/tags'
        try:
            req = Request(ollama_url)
            req.add_header('User-Agent', 'Wuchang-AI-WakeUp/1.0')
            response = urlopen(req, timeout=5)
            if response.getcode() == 200:
                data = json.loads(response.read().decode('utf-8'))
                models = data.get('models', [])
                model_names = [m.get('name', '') for m in models]
                if model_names:
                    print(f"  ✓ Ollama 正在運行")
                    print(f"  ✓ 可用模型：{', '.join(model_names[:3])}")
                    if len(model_names) > 3:
                        print(f"     (共 {len(model_names)} 個模型)")
                    return True
                else:
                    print("  ⚠ Ollama 運行中但無可用模型")
                    return False
            else:
                print("  ⚠ Ollama 響應異常")
                return False
        except (URLError, OSError, json.JSONDecodeError):
            print("  ⚠ Ollama 未運行（可選，系統會回退到雲端模式）")
            print("  提示：運行 'docker-compose --profile ui up -d' 啟動 Ollama")
            return False
    except Exception as e:
        print(f"  ✗ 檢查 Ollama 時發生錯誤: {e}")
        return False

def wake_up_system_services():
    """步驟 5: 檢查系統服務狀態"""
    print("[5/5] 檢查系統服務狀態...")
    try:
        services = {
            'Database': ('http://localhost:8069/web/health', 'Odoo/Database'),
            'Caddy': ('http://localhost:80', 'Web Server'),
        }
        
        all_ok = True
        for service_name, (url, desc) in services.items():
            try:
                req = Request(url)
                req.add_header('User-Agent', 'Wuchang-AI-WakeUp/1.0')
                response = urlopen(req, timeout=3)
                if response.getcode() in [200, 301, 302]:
                    print(f"  ✓ {service_name} ({desc}) 運行正常")
                else:
                    print(f"  ⚠ {service_name} ({desc}) 響應異常")
                    all_ok = False
            except (URLError, OSError):
                print(f"  ⚠ {service_name} ({desc}) 未運行")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print(f"  ✗ 檢查系統服務時發生錯誤: {e}")
        return False

def _run_manual_command(manual_cmd: str) -> bool:
    """Run an optional manual command after wake-up. Returns True if handled successfully."""
    cmd = (manual_cmd or "").strip()
    if not cmd:
        return True

    print()
    print("=" * 70)
    print(f"🧭 MANUAL_CMD: {cmd}")
    print("=" * 70)

    # Network scan trigger (simple keyword routing)
    if any(k in cmd for k in ("掃描", "網路", "scan", "network")):
        print("🔎 觸發：掃描本機網路 (scripts/scan_lan.py)")
        try:
            script_path = os.path.join(os.path.dirname(__file__), "scan_lan.py")
            # Use current interpreter to avoid PATH issues
            proc = subprocess.run([sys.executable, script_path], check=False)
            return proc.returncode == 0
        except Exception as e:
            print(f"  ✗ 執行網路掃描失敗: {e}")
            return False

    print("⚠ 未識別的 MANUAL_CMD（目前僅支援：掃描網路）")
    return False

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="Wuchang OS AI 喚醒腳本")
    parser.add_argument(
        "--manual",
        type=str,
        default="",
        help="可選：喚醒後執行的手動指令（或用環境變數 MANUAL_CMD）",
    )
    args, _ = parser.parse_known_args()

    print_header()
    
    print("開始執行 AI 喚醒儀式...")
    print("-" * 70)
    print()
    
    results = []
    
    # 執行所有喚醒步驟
    results.append(("AI 記憶初始化", wake_up_ai_memory()))
    results.append(("Vertex AI 初始化", wake_up_vertex_ai()))
    results.append(("Odoo AI 模組", wake_up_odoo_ai()))
    results.append(("本地 Ollama", wake_up_ollama()))
    results.append(("系統服務", wake_up_system_services()))

    # Optional manual command routing
    manual_cmd = args.manual or os.environ.get("MANUAL_CMD", "")
    if manual_cmd.strip():
        results.append(("MANUAL_CMD 執行", _run_manual_command(manual_cmd)))
    
    print()
    print("-" * 70)
    print("喚醒儀式完成")
    print("-" * 70)
    print()
    
    # 統計結果
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print(f"成功：{success_count}/{total_count} 項")
    print()
    
    for name, result in results:
        status = "✓" if result else "✗"
        print(f"  {status} {name}")
    
    print()
    
    if success_count == total_count:
        print("=" * 70)
        print("  ✅ AI 系統已完全喚醒！")
        print("=" * 70)
        print()
        print("💡 提示：")
        print("  - 訪問 http://localhost:8069 使用 Odoo 系統")
        print("  - AI 助手已準備就緒")
        return 0
    elif success_count >= total_count - 2:
        print("=" * 70)
        print("  ⚠️  AI 系統部分喚醒")
        print("=" * 70)
        print()
        print("💡 提示：")
        print("  - 核心功能已可用")
        print("  - 部分可選服務未啟動（不影響基本功能）")
        return 0
    else:
        print("=" * 70)
        print("  ❌ AI 系統喚醒失敗")
        print("=" * 70)
        print()
        print("💡 建議：")
        print("  1. 運行 'docker-compose --profile system up -d' 啟動基礎服務")
        print("  2. 運行 'python scripts/install_wuchang_modules_v2.py' 安裝模組")
        print("  3. 檢查系統日誌以獲取詳細錯誤信息")
        return 1

if __name__ == '__main__':
    sys.exit(main())