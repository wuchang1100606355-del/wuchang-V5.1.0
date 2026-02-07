#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 在 Odoo shell 中執行此腳本來設置 AI 伺服器

import odoo
from odoo import api, SUPERUSER_ID

# 初始化 Odoo
odoo.tools.config.parse_config([])

# 獲取數據庫名稱
db_name = odoo.tools.config.get('db_name') or 'odoo'

# 連接數據庫
registry = odoo.registry(db_name)

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    params = env['ir.config_parameter'].sudo()
    
    # 設置 AI 伺服器端點
    ai_server_url = "http://host.docker.internal:11434"
    ai_server_host = "host.docker.internal:11434"
    
    # 設置參數
    params.set_param('wuchang.llm_base_url', ai_server_url)
    params.set_param('wuchang.llm.host', ai_server_host)
    params.set_param('wuchang.ai_mode', 'local_ollama')
    
    # 提交
    cr.commit()
    
    print("✅ AI 伺服器設置完成")
    print(f"  - LLM 基礎 URL: {ai_server_url}")
    print(f"  - LLM 主機: {ai_server_host}")
    print(f"  - AI 模式: local_ollama")
