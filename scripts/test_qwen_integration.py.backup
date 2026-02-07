#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試地端 LLM 模型 (qwen2:0.5b) 與 Odoo 核心的整合
"""

import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('ODOO_RC', '/etc/odoo/odoo.conf')

try:
    import odoo
    from odoo import api, SUPERUSER_ID
    
    odoo.tools.config.parse_config(['-d', 'admin', '--db_host=db', '--db_user=odoo', '--db_password=odoo'])
    registry = odoo.registry('admin')
    
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        ai_logic = env['wuchang.ai.logic']
        params = env['ir.config_parameter'].sudo()
        
        print("=" * 70)
        print("        測試地端 LLM 模型整合")
        print("=" * 70)
        print()
        
        # 1. 檢查配置
        print("[1/4] 檢查配置參數...")
        mode = ai_logic._get_ai_mode()
        base_url = params.get_param('wuchang.llm_base_url', '')
        model_name = params.get_param('wuchang.ollama_model', '')
        
        print(f"  ✓ AI 模式: {mode}")
        print(f"  ✓ LLM URL: {base_url}")
        print(f"  ✓ 模型名稱: {model_name}")
        
        if mode != 'local_ollama':
            print(f"  ⚠ 警告: AI 模式不是 local_ollama")
        if model_name != 'qwen2:0.5b':
            print(f"  ⚠ 警告: 模型名稱不是 qwen2:0.5b")
        
        # 2. 測試 Ollama 連接
        print("\n[2/4] 測試 Ollama 服務連接...")
        try:
            # 從容器內訪問
            ollama_url = 'http://ollama:11434/api/tags'
            res = requests.get(ollama_url, timeout=5)
            if res.status_code == 200:
                models = res.json().get('models', [])
                qwen_models = [m for m in models if 'qwen2' in m.get('name', '')]
                if qwen_models:
                    print(f"  ✓ Ollama 服務正常")
                    print(f"  ✓ 找到模型: {qwen_models[0]['name']}")
                else:
                    print(f"  ⚠ 未找到 qwen2 模型")
            else:
                print(f"  ✗ Ollama 響應異常: {res.status_code}")
        except Exception as e:
            print(f"  ✗ 連接失敗: {e}")
        
        # 3. 測試 AI 邏輯調用
        print("\n[3/4] 測試 AI 邏輯調用...")
        try:
            test_prompt = "你好，我是小J，請簡單介紹一下自己。"
            system_prompt = "You are Little J (小j), a friendly AI assistant."
            result = ai_logic._call_local_ollama(test_prompt, system_prompt)
            if result:
                print(f"  ✓ AI 調用成功")
                print(f"  ✓ 回應長度: {len(result)} 字符")
                print(f"  ✓ 回應預覽: {result[:100]}...")
            else:
                print(f"  ⚠ AI 調用返回空結果")
        except Exception as e:
            print(f"  ✗ AI 調用失敗: {e}")
        
        # 4. 測試分析功能
        print("\n[4/4] 測試分析功能...")
        try:
            test_context = "今天的系統運行正常，沒有發現問題。"
            result = ai_logic.analyze_operations(test_context)
            if result:
                print(f"  ✓ 分析功能正常")
                print(f"  ✓ 分析結果: {result[:100]}...")
            else:
                print(f"  ⚠ 分析功能返回空結果")
        except Exception as e:
            print(f"  ✗ 分析功能失敗: {e}")
        
        print()
        print("=" * 70)
        print("  ✅ 整合測試完成！")
        print("=" * 70)
        
except ImportError:
    print("錯誤: 無法導入 odoo 模組")
    sys.exit(1)
except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
