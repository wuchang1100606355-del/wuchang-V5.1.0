#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
觸發 Odoo 模組安裝
合規要求：Google 非營利組織合規
"""

import subprocess
import sys
import time

def run_command(cmd, description):
    """執行命令並顯示結果"""
    print(f"\n{'='*50}")
    print(f"  {description}")
    print(f"{'='*50}\n")
    
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    print(result.stdout)
    if result.stderr:
        print(f"錯誤: {result.stderr}")
    
    return result.returncode == 0

def main():
    """主流程"""
    print("\n" + "="*60)
    print("  🔧 Odoo 模組安裝觸發器")
    print("  ✅ 合規: Google 非營利組織合規要求")
    print("="*60)
    
    # 1. 檢查待安裝模組
    print("\n📋 步驟 1: 檢查待安裝模組...")
    cmd = 'docker-compose exec -T db psql -U odoo -d admin -c "SELECT name, state FROM ir_module_module WHERE state = \'to install\';"'
    run_command(cmd, "待安裝模組列表")
    
    # 2. 使用 Odoo API 觸發安裝
    print("\n🔧 步驟 2: 觸發模組安裝...")
    
    # 創建臨時 Python 腳本在容器內執行
    install_script = """
import odoo
from odoo import api, SUPERUSER_ID

# 連接到資料庫
odoo.tools.config['db_name'] = 'admin'
registry = odoo.registry('admin')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # 獲取待安裝模組
    modules_to_install = env['ir.module.module'].search([
        ('state', '=', 'to install')
    ])
    
    print(f"找到 {len(modules_to_install)} 個待安裝模組:")
    for module in modules_to_install:
        print(f"  - {module.name}")
    
    # 執行安裝
    if modules_to_install:
        print("\\n開始安裝...")
        modules_to_install.button_immediate_install()
        print("✅ 安裝完成")
    else:
        print("⚠️ 沒有待安裝的模組")
"""
    
    # 將腳本寫入臨時文件
    with open('temp_install_script.py', 'w', encoding='utf-8') as f:
        f.write(install_script)
    
    # 複製到容器並執行
    subprocess.run('docker cp temp_install_script.py wuchangv510-wuchang-web-1:/tmp/', shell=True)
    
    cmd = 'docker-compose exec -T wuchang-web python3 /tmp/temp_install_script.py'
    success = run_command(cmd, "執行模組安裝")
    
    # 清理臨時文件
    import os
    if os.path.exists('temp_install_script.py'):
        os.remove('temp_install_script.py')
    
    # 3. 等待安裝完成
    print("\n⏳ 步驟 3: 等待安裝完成...")
    time.sleep(5)
    
    # 4. 驗證安裝結果
    print("\n✅ 步驟 4: 驗證安裝結果...")
    cmd = 'docker-compose exec -T db psql -U odoo -d admin -c "SELECT name, state FROM ir_module_module WHERE name IN (\'stock_sms\', \'wuchang_core\');"'
    run_command(cmd, "模組狀態")
    
    # 5. 檢查字段是否存在
    print("\n🔍 步驟 5: 檢查 stock_move_sms_validation 字段...")
    cmd = 'docker-compose exec -T db psql -U odoo -d admin -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = \'res_config_settings\' AND column_name = \'stock_move_sms_validation\';"'
    run_command(cmd, "字段檢查")
    
    print("\n" + "="*60)
    print("  ✅ 安裝流程完成")
    print("  💡 請刷新瀏覽器頁面 (Ctrl+F5)")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
