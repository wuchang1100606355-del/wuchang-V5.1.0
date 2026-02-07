#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設置 AI 伺服器端點
將 Ollama 端點設為 http://host.docker.internal:11434
"""

import os
import sys

# 添加 Odoo 路徑
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ODOO_PATH = os.path.join(BASE_PATH, 'wuchang_os')

sys.path.insert(0, ODOO_PATH)

try:
    import odoo
    from odoo import api, SUPERUSER_ID
    import odoo.tools.config as config
except ImportError as e:
    print(f"❌ 無法導入 Odoo: {e}")
    print("請確保在 Odoo 環境中運行此腳本")
    sys.exit(1)

def set_ai_server():
    """設置 AI 伺服器端點"""
    
    # 目標端點
    ai_server_url = "http://host.docker.internal:11434"
    
    print("=" * 80)
    print("  設置 AI 伺服器端點")
    print("=" * 80)
    print()
    print(f"目標端點: {ai_server_url}")
    print()
    
    try:
        # 獲取數據庫名稱
        db_name = config.get('db_name') or os.environ.get('POSTGRES_DB') or 'odoo'
        print(f"數據庫: {db_name}")
        print()
        
        # 連接 Odoo
        odoo.tools.config.parse_config([])
        registry = odoo.registry(db_name)
        
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            params = env['ir.config_parameter'].sudo()
            
            # 設置 LLM 基礎 URL（用於 Ollama API 調用）
            old_base_url = params.get_param('wuchang.llm_base_url', '')
            params.set_param('wuchang.llm_base_url', ai_server_url)
            print(f"✅ 已設置 wuchang.llm_base_url")
            if old_base_url:
                print(f"   舊值: {old_base_url}")
            print(f"   新值: {ai_server_url}")
            print()
            
            # 設置 LLM 主機（用於其他配置）
            old_host = params.get_param('wuchang.llm.host', '')
            # 從 URL 提取主機部分
            host_part = "host.docker.internal:11434"
            params.set_param('wuchang.llm.host', host_part)
            print(f"✅ 已設置 wuchang.llm.host")
            if old_host:
                print(f"   舊值: {old_host}")
            print(f"   新值: {host_part}")
            print()
            
            # 確保 AI 模式為 local_ollama
            current_mode = params.get_param('wuchang.ai_mode', '')
            if current_mode != 'local_ollama':
                params.set_param('wuchang.ai_mode', 'local_ollama')
                print(f"✅ 已設置 AI 模式為 local_ollama")
                if current_mode:
                    print(f"   舊模式: {current_mode}")
                print()
            
            # 提交更改
            cr.commit()
            
            print("=" * 80)
            print("✅ AI 伺服器設置完成")
            print("=" * 80)
            print()
            print("配置摘要:")
            print(f"  - LLM 基礎 URL: {ai_server_url}")
            print(f"  - LLM 主機: {host_part}")
            print(f"  - AI 模式: local_ollama")
            print()
            print("💡 提示: 請確保 Ollama 服務運行在 http://host.docker.internal:11434")
            
            return True
            
    except Exception as e:
        print(f"❌ 設置失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = set_ai_server()
    sys.exit(0 if success else 1)
