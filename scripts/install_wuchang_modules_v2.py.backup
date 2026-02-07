#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wuchang OS 模組安裝腳本 (修正版)
安裝所有 Wuchang 相關模組，自動處理數據庫創建
"""

import sys
import os
import subprocess

# 先安裝的依賴模組（Odoo 標準模組）
DEPENDENCY_MODULES = [
    'point_of_sale',  # wuchang_business 需要
    'stock',          # wuchang_business 需要
]

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

def install_modules_docker(db_name='admin'):
    """使用 Docker Compose 安裝模組"""
    print("=" * 60)
    print("使用 Docker Compose 安裝 Wuchang 模組")
    print("=" * 60)
    
    workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print(f"數據庫名稱: {db_name}")
    print("-" * 60)
    
    # 第一步：先安裝依賴模組
    if DEPENDENCY_MODULES:
        print(f"步驟 1/2: 安裝依賴模組: {', '.join(DEPENDENCY_MODULES)}")
        dep_modules_str = ','.join(DEPENDENCY_MODULES)
        dep_cmd = [
            'docker-compose', 'run', '--rm',
            'wuchang-web',
            'odoo',
            '-d', db_name,
            '-i', dep_modules_str,
            '--stop-after-init',
            '--db_host=db',
            '--db_user=odoo',
            '--db_password=odoo',
            '--addons-path=/mnt/extra-addons',
            '--without-demo=all',
        ]
        
        print(f"執行命令: {' '.join(dep_cmd)}")
        print("-" * 60)
        
        try:
            original_dir = os.getcwd()
            os.chdir(workspace_path)
            dep_result = subprocess.run(dep_cmd, check=False)
            os.chdir(original_dir)
            
            if dep_result.returncode != 0:
                print(f"⚠️  依賴模組安裝可能失敗，退出碼: {dep_result.returncode}")
                print("繼續嘗試安裝 Wuchang 模組...")
            else:
                print("✅ 依賴模組安裝完成")
            print("-" * 60)
        except Exception as e:
            print(f"⚠️  依賴模組安裝出錯: {e}")
            print("繼續嘗試安裝 Wuchang 模組...")
            print("-" * 60)
    
    # 第二步：安裝 Wuchang 模組
    modules_str = ','.join(WUCHANG_MODULES)
    print(f"步驟 2/2: 安裝 Wuchang 模組: {', '.join(WUCHANG_MODULES)}")
    print("-" * 60)
    
    # 構建安裝命令 - 使用 -d 指定數據庫名稱，-i 安裝模組，--stop-after-init 安裝後停止
    cmd = [
        'docker-compose', 'run', '--rm',
        'wuchang-web',
        'odoo',
        '-d', db_name,  # 指定數據庫名稱
        '-i', modules_str,  # 安裝模組
        '--stop-after-init',  # 安裝後停止
        '--db_host=db',
        '--db_user=odoo',
        '--db_password=odoo',
        '--addons-path=/mnt/extra-addons',
        '--without-demo=all',  # 不載入演示數據
    ]
    
    print(f"執行命令: {' '.join(cmd)}")
    print("-" * 60)
    print("正在安裝模組，這可能需要幾分鐘...")
    print("-" * 60)
    
    try:
        # 切換到工作區目錄
        original_dir = os.getcwd()
        os.chdir(workspace_path)
        
        # 執行安裝命令
        result = subprocess.run(cmd, check=False)
        
        os.chdir(original_dir)
        
        if result.returncode == 0:
            print("=" * 60)
            print("✅ 模組安裝完成！")
            print("=" * 60)
            return True
        else:
            print("=" * 60)
            print(f"⚠️  安裝過程完成，退出碼: {result.returncode}")
            print("請檢查上面的日誌以確認安裝狀態")
            print("=" * 60)
            return result.returncode == 0
    except FileNotFoundError:
        print("=" * 60)
        print("❌ 找不到 docker-compose 命令")
        print("請確保 Docker Compose 已安裝並在 PATH 中")
        print("=" * 60)
        return False
    except Exception as e:
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
    
    # 從命令行參數獲取數據庫名稱，默認為 admin
    db_name = 'admin'
    if len(sys.argv) > 1:
        if sys.argv[1].startswith('--db='):
            db_name = sys.argv[1].split('=', 1)[1]
        elif not sys.argv[1].startswith('--'):
            db_name = sys.argv[1]
    
    success = install_modules_docker(db_name)
    
    if success:
        print("\n💡 提示：")
        print("  - 啟動服務: docker-compose up -d")
        print("  - 訪問系統: http://localhost:8069")
        print("  - 登入後在 Apps 菜單中可以確認模組安裝狀態")
        print("  - 如果使用其他數據庫名稱，請使用: python install_wuchang_modules_v2.py <數據庫名稱>")
        return 0
    else:
        print("\n❌ 安裝可能未完全成功，請檢查錯誤信息")
        print("提示：")
        print("  - 確保 Docker 和 Docker Compose 正在運行")
        print("  - 確保數據庫容器 (db) 已啟動")
        print("  - 檢查日誌以獲取詳細錯誤信息")
        return 1

if __name__ == '__main__':
    sys.exit(main())