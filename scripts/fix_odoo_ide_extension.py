#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo IDE 延伸模組安裝問題診斷與修復腳本

此腳本解決以下常見問題：
1. IDE 延伸模組每次都需要重新安裝
2. 模組安裝失敗
3. 模組狀態未正確保存
"""

import sys
import os
import subprocess
import json
from pathlib import Path

# 工作區路徑
WORKSPACE_PATH = Path(__file__).parent.parent

def log(message: str, level: str = "INFO"):
    """記錄訊息"""
    icons = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️",
        "DEBUG": "🔍"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")

def check_docker_containers():
    """檢查 Docker 容器狀態"""
    log("檢查 Docker 容器狀態...", "INFO")
    try:
        result = subprocess.run(
            ['docker-compose', 'ps'],
            cwd=WORKSPACE_PATH,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            log("Docker 容器狀態正常", "SUCCESS")
            return True
        else:
            log("Docker 容器可能未運行", "WARNING")
            return False
    except FileNotFoundError:
        log("找不到 docker-compose 命令", "ERROR")
        return False

def check_module_in_database(module_name='odoo_ide'):
    """檢查模組在資料庫中的狀態"""
    log(f"檢查模組 '{module_name}' 在資料庫中的狀態...", "INFO")
    
    query = f"""
    SELECT name, state, latest_version, author 
    FROM ir_module_module 
    WHERE name = '{module_name}';
    """
    
    try:
        cmd = [
            'docker-compose', 'exec', '-T', 'db',
            'psql', '-U', 'odoo', '-d', 'admin', '-c', query
        ]
        result = subprocess.run(
            cmd,
            cwd=WORKSPACE_PATH,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            output = result.stdout
            if module_name in output:
                log(f"模組 '{module_name}' 存在於資料庫中", "SUCCESS")
                log(f"查詢結果:\n{output}", "DEBUG")
                return True
            else:
                log(f"模組 '{module_name}' 不存在於資料庫中", "WARNING")
                return False
        else:
            log(f"查詢資料庫失敗: {result.stderr}", "ERROR")
            return False
    except Exception as e:
        log(f"檢查模組狀態時發生錯誤: {e}", "ERROR")
        return False

def fix_module_state(module_name='odoo_ide'):
    """修復模組狀態"""
    log(f"修復模組 '{module_name}' 的狀態...", "INFO")
    
    fix_script = f"""
import odoo
from odoo import api, SUPERUSER_ID

# 連接到資料庫
odoo.tools.config['db_name'] = 'admin'
registry = odoo.registry('admin')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {{}})
    
    # 查找模組
    module = env['ir.module.module'].search([
        ('name', '=', '{module_name}')
    ], limit=1)
    
    if module:
        print(f"找到模組: {{module.name}}, 當前狀態: {{module.state}}")
        
        # 如果狀態是 'to install' 或 'to upgrade'，將其設為 'installed'
        if module.state in ['to install', 'to upgrade']:
            module.write({{'state': 'installed'}})
            cr.commit()
            print(f"✅ 已將模組狀態設為 'installed'")
        elif module.state == 'uninstalled':
            # 如果模組已卸載，重新安裝
            print("模組已卸載，嘗試重新安裝...")
            module.button_immediate_install()
            cr.commit()
            print(f"✅ 已重新安裝模組")
        else:
            print(f"模組狀態正常: {{module.state}}")
    else:
        print(f"⚠️ 找不到模組 '{module_name}'")
        print("可能需要先將模組添加到 addons-path 中")
"""
    
    # 將腳本寫入臨時文件
    temp_script = WORKSPACE_PATH / 'temp_fix_ide_module.py'
    try:
        with open(temp_script, 'w', encoding='utf-8') as f:
            f.write(fix_script)
        
        # 複製到容器並執行
        log("執行修復腳本...", "INFO")
        subprocess.run(
            ['docker', 'cp', str(temp_script), 'wuchangv510-wuchang-web-1:/tmp/'],
            check=False
        )
        
        result = subprocess.run(
            ['docker-compose', 'exec', '-T', 'wuchang-web', 
             'python3', '/tmp/temp_fix_ide_module.py'],
            cwd=WORKSPACE_PATH,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            log("修復腳本執行成功", "SUCCESS")
            log(f"輸出:\n{result.stdout}", "DEBUG")
            return True
        else:
            log(f"修復腳本執行失敗: {result.stderr}", "ERROR")
            return False
    except Exception as e:
        log(f"執行修復腳本時發生錯誤: {e}", "ERROR")
        return False
    finally:
        # 清理臨時文件
        if temp_script.exists():
            temp_script.unlink()

def check_addons_path():
    """檢查 addons-path 配置"""
    log("檢查 addons-path 配置...", "INFO")
    
    # 檢查 docker-compose.yml 中的 addons-path 配置
    docker_compose_files = [
        WORKSPACE_PATH / 'docker-compose.yml',
        WORKSPACE_PATH / 'docker-compose.override.yml'
    ]
    
    for compose_file in docker_compose_files:
        if compose_file.exists():
            log(f"檢查 {compose_file.name}...", "DEBUG")
            try:
                with open(compose_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'addons' in content.lower() or 'ADDONS' in content:
                        log(f"在 {compose_file.name} 中找到 addons 相關配置", "SUCCESS")
            except Exception as e:
                log(f"讀取 {compose_file.name} 時發生錯誤: {e}", "WARNING")
    
    # 檢查實際的 addons 目錄
    addons_paths = [
        WORKSPACE_PATH / 'wuchang_os' / 'addons',
        WORKSPACE_PATH / 'addons',
    ]
    
    for addons_path in addons_paths:
        if addons_path.exists():
            log(f"找到 addons 目錄: {addons_path}", "SUCCESS")
            # 檢查是否有 odoo_ide 模組
            ide_module_path = addons_path / 'odoo_ide'
            if ide_module_path.exists():
                log(f"找到 odoo_ide 模組: {ide_module_path}", "SUCCESS")
            else:
                log(f"在 {addons_path} 中未找到 odoo_ide 模組", "WARNING")
        else:
            log(f"addons 目錄不存在: {addons_path}", "WARNING")

def install_ide_module_via_cli(module_name='odoo_ide'):
    """通過 CLI 安裝 IDE 模組"""
    log(f"通過 CLI 安裝模組 '{module_name}'...", "INFO")
    
    cmd = [
        'docker-compose', 'run', '--rm',
        'wuchang-web',
        'odoo',
        '-d', 'admin',
        '-i', module_name,
        '--stop-after-init',
        '--db_host=db',
        '--db_user=odoo',
        '--db_password=odoo',
        '--addons-path=/mnt/extra-addons',
    ]
    
    log(f"執行命令: {' '.join(cmd)}", "DEBUG")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=WORKSPACE_PATH,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            log(f"模組 '{module_name}' 安裝成功", "SUCCESS")
            return True
        else:
            log(f"模組 '{module_name}' 安裝失敗", "ERROR")
            log(f"錯誤輸出:\n{result.stderr}", "ERROR")
            return False
    except Exception as e:
        log(f"安裝模組時發生錯誤: {e}", "ERROR")
        return False

def create_module_state_persistence_script():
    """創建模組狀態持久化腳本"""
    log("創建模組狀態持久化腳本...", "INFO")
    
    script_content = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Odoo IDE 模組狀態持久化腳本
在 Odoo 啟動時自動執行，確保 IDE 模組狀態正確
\"\"\"

import odoo
from odoo import api, SUPERUSER_ID

def ensure_ide_module_installed():
    \"\"\"確保 IDE 模組已正確安裝\"\"\"
    db_name = odoo.tools.config.get('db_name', 'admin')
    
    try:
        registry = odoo.registry(db_name)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            
            # 檢查 IDE 相關模組
            ide_modules = ['odoo_ide', 'web_editor', 'web_unsplash']
            
            for module_name in ide_modules:
                module = env['ir.module.module'].search([
                    ('name', '=', module_name)
                ], limit=1)
                
                if module:
                    if module.state in ['to install', 'to upgrade']:
                        print(f"修復模組 {module_name} 狀態: {module.state} -> installed")
                        module.write({'state': 'installed'})
                        cr.commit()
                    elif module.state == 'uninstalled':
                        print(f"重新安裝模組 {module_name}")
                        module.button_immediate_install()
                        cr.commit()
    
    except Exception as e:
        print(f"確保 IDE 模組安裝時發生錯誤: {e}")

if __name__ == '__main__':
    ensure_ide_module_installed()
"""
    
    script_path = WORKSPACE_PATH / 'scripts' / 'persist_ide_module_state.py'
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        log(f"已創建持久化腳本: {script_path}", "SUCCESS")
        return True
    except Exception as e:
        log(f"創建持久化腳本時發生錯誤: {e}", "ERROR")
        return False

def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("  🔧 Odoo IDE 延伸模組問題診斷與修復工具")
    print("=" * 60)
    
    # 步驟 1: 檢查 Docker 容器
    print("\n📋 步驟 1: 檢查 Docker 容器狀態")
    if not check_docker_containers():
        log("請先啟動 Docker 容器", "ERROR")
        return 1
    
    # 步驟 2: 檢查 addons-path
    print("\n📋 步驟 2: 檢查 addons-path 配置")
    check_addons_path()
    
    # 步驟 3: 檢查模組狀態
    print("\n📋 步驟 3: 檢查模組在資料庫中的狀態")
    module_exists = check_module_in_database('odoo_ide')
    
    # 步驟 4: 修復模組狀態
    print("\n📋 步驟 4: 修復模組狀態")
    if module_exists:
        fix_module_state('odoo_ide')
    else:
        log("模組不存在於資料庫中，嘗試安裝...", "INFO")
        install_ide_module_via_cli('odoo_ide')
    
    # 步驟 5: 創建持久化腳本
    print("\n📋 步驟 5: 創建模組狀態持久化腳本")
    create_module_state_persistence_script()
    
    print("\n" + "=" * 60)
    print("  ✅ 診斷與修復完成")
    print("=" * 60)
    print("\n💡 建議:")
    print("  1. 檢查 Odoo 日誌以確認模組是否正確安裝")
    print("  2. 在 Odoo 後台確認模組狀態")
    print("  3. 如果問題持續，請檢查模組檔案權限")
    print("  4. 確保 addons-path 包含 IDE 模組所在目錄")
    print("\n")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
