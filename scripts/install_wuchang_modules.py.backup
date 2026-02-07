#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wuchang OS 模組安裝腳本
安裝所有 Wuchang 相關模組
"""

import sys
import os

# 所有要安裝的 Wuchang 模組
WUCHANG_MODULES = [
    'wuchang_core',
    'wuchang_finance',
    'wuchang_business',
    'wuchang_volunteer',
    'wuchang_community_campaign',
    'wuchang_web_portal',
    'wuchang_design_system',
    'wuchang_ui_compliance',
    'wuchang_property_toolkits',
    'wuchang_award_coach',
    'wuchang_guardian',
    'wuchang_life',
]

def install_modules_docker():
    """使用 Docker Compose 安裝模組"""
    print("=" * 60)
    print("使用 Docker Compose 安裝 Wuchang 模組")
    print("=" * 60)
    
    modules_str = ','.join(WUCHANG_MODULES)
    
    # 構建安裝命令
    cmd = [
        'docker-compose', 'run', '--rm',
        'wuchang-web',
        'odoo',
        '-i', modules_str,
        '--stop-after-init',
        '--db_host=db',
        '--db_user=odoo',
        '--db_password=odoo',
        '--addons-path=/mnt/extra-addons'
    ]
    
    print(f"執行命令: {' '.join(cmd)}")
    print(f"安裝模組: {modules_str}")
    print("-" * 60)
    
    try:
        import subprocess
        result = subprocess.run(cmd, check=True)
        print("=" * 60)
        print("✅ 模組安裝完成！")
        print("=" * 60)
        return True
    except subprocess.CalledProcessError as e:
        print("=" * 60)
        print(f"❌ 安裝失敗: {e}")
        print("=" * 60)
        return False
    except FileNotFoundError:
        print("=" * 60)
        print("❌ 找不到 docker-compose 命令")
        print("請確保 Docker Compose 已安裝並在 PATH 中")
        print("=" * 60)
        return False

def install_modules_local():
    """使用本地 Odoo 安裝模組"""
    print("=" * 60)
    print("使用本地 Odoo 安裝 Wuchang 模組")
    print("=" * 60)
    
    # 嘗試找到 Odoo 可執行文件
    odoo_paths = [
        'C:\\Users\\o0930\\odoo\\odoo-bin',
        'odoo-bin',
        'odoo',
        os.path.join(os.path.dirname(__file__), '..', 'odoo', 'odoo-bin'),
    ]
    
    odoo_bin = None
    for path in odoo_paths:
        if os.path.exists(path) or os.system(f'which {path} 2>/dev/null') == 0:
            odoo_bin = path
            break
    
    if not odoo_bin:
        print("❌ 找不到 Odoo 可執行文件")
        print("請確保 Odoo 已安裝或使用 Docker 方式安裝")
        return False
    
    modules_str = ','.join(WUCHANG_MODULES)
    
    # 構建安裝命令
    workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    addons_path = os.path.join(workspace_path, 'wuchang_os', 'addons')
    
    cmd = [
        odoo_bin,
        '-i', modules_str,
        '--stop-after-init',
        '--addons-path', addons_path,
        '-c', os.path.join(workspace_path, 'config', 'odoo.conf'),
    ]
    
    print(f"執行命令: {' '.join(cmd)}")
    print(f"安裝模組: {modules_str}")
    print("-" * 60)
    
    try:
        import subprocess
        result = subprocess.run(cmd, check=True)
        print("=" * 60)
        print("✅ 模組安裝完成！")
        print("=" * 60)
        return True
    except subprocess.CalledProcessError as e:
        print("=" * 60)
        print(f"❌ 安裝失敗: {e}")
        print("=" * 60)
        return False

def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Wuchang OS 模組安裝工具")
    print("=" * 60)
    print(f"\n將安裝以下 {len(WUCHANG_MODULES)} 個模組：")
    for i, module in enumerate(WUCHANG_MODULES, 1):
        print(f"  {i:2d}. {module}")
    print()
    
    # 檢查是否使用 Docker
    use_docker = False
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--docker', '-d']:
            use_docker = True
        elif sys.argv[1] in ['--local', '-l']:
            use_docker = False
    else:
        # 自動檢測：如果存在 docker-compose.yml 且 docker-compose 可用
        workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        docker_compose_file = os.path.join(workspace_path, 'docker-compose.yml')
        if os.path.exists(docker_compose_file):
            try:
                import subprocess
                subprocess.run(['docker-compose', '--version'], 
                             capture_output=True, check=True)
                use_docker = True
                print("✓ 檢測到 Docker Compose，將使用 Docker 方式安裝")
            except (FileNotFoundError, subprocess.CalledProcessError):
                print("⚠ 未檢測到 Docker Compose，將嘗試本地安裝")
    
    print()
    
    if use_docker:
        success = install_modules_docker()
    else:
        success = install_modules_local()
    
    if success:
        print("\n💡 提示：")
        print("  - 如果使用 Docker，可以運行: docker-compose up -d")
        print("  - 然後訪問: http://localhost:8069")
        print("  - 登入後在 Apps 菜單中可以確認模組安裝狀態")
        return 0
    else:
        print("\n❌ 安裝失敗，請檢查錯誤信息")
        return 1

if __name__ == '__main__':
    sys.exit(main())