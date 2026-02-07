#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定 Odoo 中的 AI 小 J 專用金鑰
將時空系統的 API 金鑰配置到 Odoo 系統參數中
"""

import sys
import os

# 嘗試導入 Odoo
try:
    import odoo
    from odoo import api, SUPERUSER_ID
    ODOO_AVAILABLE = True
except ImportError:
    ODOO_AVAILABLE = False
    print("警告: Odoo 未安裝，將使用 XMLRPC 方式設定")


def setup_via_odoo_shell(env):
    """透過 Odoo shell 設定（推薦）"""
    print("透過 Odoo shell 設定系統參數...")
    
    param = env['ir.config_parameter'].sudo()
    
    # 時空系統設定
    param.set_param('spatiotemporal.system.enabled', 'True')
    print("✓ spatiotemporal.system.enabled = True")
    
    param.set_param('ai.j.spatiotemporal.authorization', 'full')
    print("✓ ai.j.spatiotemporal.authorization = full")
    
    param.set_param('ai.j.cloud.compute.enabled', 'True')
    print("✓ ai.j.cloud.compute.enabled = True")
    
    param.set_param('spatiotemporal.system.version', '1.0.0')
    print("✓ spatiotemporal.system.version = 1.0.0")
    
    param.set_param('spatiotemporal.system.path', r'C:\wuchang V5.1.0\spatiotemporal_system')
    print("✓ spatiotemporal.system.path 已設定")
    
    # API 金鑰（AI 小 J 專用）- 預設為空，需手動填入
    param.set_param('ai.j.openai.api.key', '')
    print("✓ ai.j.openai.api.key 已建立（請在 Odoo 中填入）")
    
    param.set_param('ai.j.anthropic.api.key', '')
    print("✓ ai.j.anthropic.api.key 已建立（請在 Odoo 中填入）")
    
    param.set_param('ai.j.google.api.key', '')
    print("✓ ai.j.google.api.key 已建立（請在 Odoo 中填入）")
    
    param.set_param('ai.j.google.calendar.enabled', 'True')
    print("✓ ai.j.google.calendar.enabled = True")
    
    param.set_param('ai.j.spatiotemporal.capabilities', 
                   '時空事件管理,時間空間建議,排程優化,活動模式分析,空間使用率預測,社區服務管理')
    print("✓ ai.j.spatiotemporal.capabilities 已設定")
    
    env.cr.commit()
    print("\n✓ 所有系統參數已設定完成！")
    print("\n下一步: 在 Odoo 中填入 API 金鑰")
    print("  設定 > 技術 > 參數 > 系統參數")
    print("  - ai.j.openai.api.key")
    print("  - ai.j.anthropic.api.key")
    print("  - ai.j.google.api.key")


def setup_via_xmlrpc():
    """透過 XMLRPC 設定（備用方案）"""
    try:
        import xmlrpc.client
        
        URL = os.getenv('ODOO_URL', 'http://localhost:8069')
        DB = os.getenv('ODOO_DB', 'odoo')
        USER = os.getenv('ODOO_USER', 'admin')
        PASS = os.getenv('ODOO_PASS', 'admin')
        
        print(f"透過 XMLRPC 連接到 {URL}...")
        
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        uid = common.authenticate(DB, USER, PASS, {})
        
        if not uid:
            print("✗ 認證失敗")
            return False
        
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
        
        # 設定參數
        params = {
            'spatiotemporal.system.enabled': 'True',
            'ai.j.spatiotemporal.authorization': 'full',
            'ai.j.cloud.compute.enabled': 'True',
            'spatiotemporal.system.version': '1.0.0',
            'spatiotemporal.system.path': r'C:\wuchang V5.1.0\spatiotemporal_system',
            'ai.j.openai.api.key': '',
            'ai.j.anthropic.api.key': '',
            'ai.j.google.api.key': '',
            'ai.j.google.calendar.enabled': 'True',
            'ai.j.spatiotemporal.capabilities': '時空事件管理,時間空間建議,排程優化,活動模式分析,空間使用率預測,社區服務管理'
        }
        
        for key, value in params.items():
            try:
                models.execute_kw(DB, uid, PASS, 'ir.config_parameter', 'set_param', [key, value])
                print(f"✓ {key} = {value}")
            except Exception as e:
                print(f"✗ 設定 {key} 失敗: {e}")
        
        print("\n✓ 所有系統參數已設定完成！")
        return True
        
    except Exception as e:
        print(f"✗ XMLRPC 設定失敗: {e}")
        return False


def main():
    """主函數"""
    print("=" * 60)
    print("AI 小 J 專用金鑰設定 - Odoo 系統參數配置")
    print("=" * 60)
    print()
    
    if ODOO_AVAILABLE and 'env' in globals():
        # 在 Odoo shell 中執行
        setup_via_odoo_shell(env)
    else:
        # 使用 XMLRPC
        print("使用 XMLRPC 方式設定...")
        print("請設定環境變數:")
        print("  - ODOO_URL (預設: http://localhost:8069)")
        print("  - ODOO_DB (預設: odoo)")
        print("  - ODOO_USER (預設: admin)")
        print("  - ODOO_PASS (預設: admin)")
        print()
        
        if setup_via_xmlrpc():
            print("\n✓ 設定完成！")
        else:
            print("\n✗ 設定失敗，請檢查連線設定")
            print("\n替代方案: 在 Odoo shell 中執行此腳本")
            print("  odoo-bin shell -d <database> -r <user> -w <password>")
            print("  exec(open('spatiotemporal_system/scripts/setup_odoo_keys.py').read())")


if __name__ == "__main__":
    main()
