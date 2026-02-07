#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 Odoo 系統參數，將地端 LLM 模型 (qwen2:0.5b) 設為小J的主要模型
"""

import sys
import os

# 添加項目路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 配置 Odoo 環境
os.environ.setdefault('ODOO_RC', '/etc/odoo/odoo.conf')

try:
    import odoo
    from odoo import api, SUPERUSER_ID
    
    # 初始化 Odoo 環境
    odoo.tools.config.parse_config(['-d', 'admin', '--db_host=db', '--db_user=odoo', '--db_password=odoo'])
    
    registry = odoo.registry('admin')
    
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        params = env['ir.config_parameter'].sudo()
        
        print("=" * 70)
        print("        更新 Odoo 系統參數 - 地端 LLM 模型")
        print("=" * 70)
        print()
        
        # 更新配置參數
        print("[1/3] 更新 Ollama 模型為 qwen2:0.5b...")
        old_model = params.get_param('wuchang.ollama_model', '')
        params.set_param('wuchang.ollama_model', 'qwen2:0.5b')
        print(f"  ✓ 模型已更新: {old_model} -> qwen2:0.5b")
        
        print("[2/3] 確認 AI 模式為 local_ollama...")
        old_mode = params.get_param('wuchang.ai_mode', '')
        params.set_param('wuchang.ai_mode', 'local_ollama')
        print(f"  ✓ AI 模式已確認: {old_mode if old_mode else '未設置'} -> local_ollama")
        
        print("[3/3] 確認 LLM 服務端點...")
        old_url = params.get_param('wuchang.llm_base_url', '')
        params.set_param('wuchang.llm_base_url', 'http://host.docker.internal:11434')
        print(f"  ✓ LLM URL 已確認: {old_url if old_url else '未設置'} -> http://host.docker.internal:11434")
        
        # 提交更改
        cr.commit()
        
        print()
        print("-" * 70)
        print("配置更新完成")
        print("-" * 70)
        print()
        
        # 驗證配置
        print("驗證配置:")
        print(f"  模型: {params.get_param('wuchang.ollama_model')}")
        print(f"  AI 模式: {params.get_param('wuchang.ai_mode')}")
        print(f"  LLM URL: {params.get_param('wuchang.llm_base_url')}")
        print()
        print("=" * 70)
        print("  ✅ 地端 LLM 模型已成功設為小J的主要模型！")
        print("=" * 70)
        
except ImportError:
    print("錯誤: 無法導入 odoo 模組")
    print("請在 Odoo 容器內執行此腳本")
    sys.exit(1)
except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
