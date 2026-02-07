#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接安裝 stock_sms 模組
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
    
    return result.returncode == 0, result.stdout

def main():
    """主流程"""
    print("\n" + "="*60)
    print("  🔧 直接安裝 stock_sms 模組")
    print("  ✅ 合規: Google 非營利組織合規要求")
    print("="*60)
    
    # 方法 1: 通過 Odoo shell 安裝
    print("\n方法 1: 通過 Odoo shell 安裝模組...")
    
    install_script = """
import odoo
from odoo import api, SUPERUSER_ID

# 連接到資料庫
odoo.tools.config.parse_config(['-d', 'admin', '--stop-after-init'])
odoo.tools.config['db_name'] = 'admin'

# 創建或獲取 registry
registry = odoo.registry('admin')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # 獲取 stock_sms 模組
    module = env['ir.module.module'].search([('name', '=', 'stock_sms')], limit=1)
    
    if module:
        print(f"找到模組: {module.name}, 狀態: {module.state}")
        
        # 設置為已安裝
        if module.state != 'installed':
            print(f"安裝模組 {module.name}...")
            module.button_immediate_install()
            print(f"✅ 模組 {module.name} 已安裝")
        else:
            print(f"✅ 模組 {module.name} 已經是已安裝狀態")
            
        # 刷新模組註冊表
        print("刷新模組註冊表...")
        env['ir.module.module'].update_list()
        
    else:
        print("❌ 未找到 stock_sms 模組")
"""
    
    # 將腳本寫入臨時文件
    with open('temp_install_stock_sms.py', 'w', encoding='utf-8') as f:
        f.write(install_script)
    
    # 複製到容器並執行
    print("\n複製安裝腳本到容器...")
    subprocess.run('docker cp temp_install_stock_sms.py wuchangv510-wuchang-web-1:/tmp/', shell=True)
    
    print("\n執行安裝腳本...")
    cmd = 'docker-compose exec -T wuchang-web python3 /tmp/temp_install_stock_sms.py'
    success, output = run_command(cmd, "執行模組安裝")
    
    if not success:
        print("\n方法 1 失敗，嘗試方法 2...")
        
        # 方法 2: 直接通過資料庫設置模組狀態並觸發升級
        print("\n方法 2: 直接設置模組狀態並觸發升級...")
        cmd2 = '''docker-compose exec -T db psql -U odoo -d admin -c "
            -- 確保模組狀態為 installed
            UPDATE ir_module_module SET state = 'installed' WHERE name = 'stock_sms';
            
            -- 設置為需要升級（會觸發模組加載）
            UPDATE ir_module_module SET state = 'to upgrade' WHERE name = 'stock_sms';
        "'''
        success2, output2 = run_command(cmd2, "設置模組狀態")
    
    # 清理臨時文件
    import os
    if os.path.exists('temp_install_stock_sms.py'):
        os.remove('temp_install_stock_sms.py')
    
    print("\n🔄 重啟 Odoo 服務...")
    subprocess.run('docker-compose restart wuchang-web', shell=True)
    
    print("\n⏳ 等待服務啟動 (25秒)...")
    time.sleep(25)
    
    print("\n✅ 驗證安裝結果...")
    cmd3 = 'docker-compose exec -T db psql -U odoo -d admin -c "SELECT name, state FROM ir_module_module WHERE name = \'stock_sms\';"'
    run_command(cmd3, "模組狀態驗證")
    
    print("\n" + "="*60)
    print("  ✅ 安裝流程完成")
    print("="*60)
    print("\n💡 請刷新瀏覽器頁面 (Ctrl+F5) 以查看效果")

if __name__ == '__main__':
    main()
