#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""驗證地端 LLM 模型配置"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('ODOO_RC', '/etc/odoo/odoo.conf')

try:
    import odoo
    from odoo import api, SUPERUSER_ID
    
    odoo.tools.config.parse_config(['-d', 'admin', '--db_host=db', '--db_user=odoo', '--db_password=odoo'])
    registry = odoo.registry('admin')
    
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        params = env['ir.config_parameter'].sudo()
        ai_logic = env['wuchang.ai.logic']
        
        print("=" * 70)
        print("        驗證地端 LLM 模型配置")
        print("=" * 70)
        print()
        
        model = params.get_param('wuchang.ollama_model')
        mode = params.get_param('wuchang.ai_mode')
        url = params.get_param('wuchang.llm_base_url')
        
        print("最終配置:")
        print(f"  模型: {model}")
        print(f"  AI 模式: {mode}")
        print(f"  LLM URL: {url}")
        print()
        
        if model == 'qwen2:0.5b' and mode == 'local_ollama':
            print("✅ 配置正確！小J已使用地端 LLM 模型作為主要模型。")
        else:
            print("⚠ 配置可能需要調整")
        
        print("=" * 70)
        
except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()
