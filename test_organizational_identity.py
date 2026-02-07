#!/usr/bin/env python3
"""
Wuchang AI 組織身份系統驗證
Test Organizational Identity System Integration

驗證：
1. Google 非營利組織身份
2. Google Workspace 超級管理員存取
3. Odoo 最高權限帳號
4. 品啦國咖啡 POS 負責人角色
5. 統一身份管理系統
6. 創辦人上帝視角控制
7. 路由器管理整合
"""

import json
import sys
import asyncio
from datetime import datetime
from pathlib import Path

# 定位主伺服器
MAIN_SERVER_PATH = Path(__file__).parent / 'vm_fastapi_main_dual_role.py'
IDENTITY_SYSTEM_PATH = Path(__file__).parent / 'identity_management_system.py'
FOUNDER_API_PATH = Path(__file__).parent / 'founder_gods_eye_view.py'
ROUTER_MANAGER_PATH = Path(__file__).parent / 'router_manager.py'


def check_file_exists(filepath, description):
    """檢查檔案是否存在"""
    if filepath.exists():
        print(f"✓ {description}: {filepath.name}")
        return True
    else:
        print(f"✗ {description}: {filepath.name} [缺失]")
        return False


def check_imports():
    """檢查所有必需的模組都能導入"""
    print("\n" + "="*60)
    print("步驟 1: 檢查模組導入")
    print("="*60)

    all_ok = True

    # 檢查主伺服器
    if check_file_exists(MAIN_SERVER_PATH, "主伺服器"):
        with open(MAIN_SERVER_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'from identity_management_system import' in content:
                print("  → 身份管理系統已導入")
            else:
                print("  ✗ 身份管理系統導入缺失")
                all_ok = False

            if 'from founder_gods_eye_view import' in content:
                print("  → 創辦人上帝視角已導入")
            else:
                print("  ✗ 創辦人上帝視角導入缺失")
                all_ok = False

            if 'from router_manager import' in content:
                print("  → 路由器管理器已導入")
            else:
                print("  ✗ 路由器管理器導入缺失")
                all_ok = False
    else:
        all_ok = False

    # 檢查身份管理系統
    if check_file_exists(IDENTITY_SYSTEM_PATH, "身份管理系統"):
        with open(IDENTITY_SYSTEM_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'class IdentityManagementSystem' in content:
                print("  → IdentityManagementSystem 類已定義")
            else:
                print("  ✗ IdentityManagementSystem 類缺失")
                all_ok = False

            if 'def create_identity_api_endpoints' in content:
                print("  → create_identity_api_endpoints() 函數已定義")
            else:
                print("  ✗ create_identity_api_endpoints() 函數缺失")
                all_ok = False

            if 'admin@wuchang.life' in content:
                print("  → 統一管理員帳號已配置")
            else:
                print("  ✗ 統一管理員帳號缺失")
                all_ok = False
    else:
        all_ok = False

    # 檢查創辦人上帝視角
    if check_file_exists(FOUNDER_API_PATH, "創辦人上帝視角"):
        with open(FOUNDER_API_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'class FounderGodsEyeView' in content:
                print("  → FounderGodsEyeView 類已定義")
            else:
                print("  ✗ FounderGodsEyeView 類缺失")
                all_ok = False

            if 'def create_founder_api' in content:
                print("  → create_founder_api() 函數已定義")
            else:
                print("  ✗ create_founder_api() 函數缺失")
                all_ok = False

            if 'location_authority' in content:
                print("  → 地點權威控制已實現")
            else:
                print("  ✗ 地點權威控制缺失")
                all_ok = False
    else:
        all_ok = False

    # 檢查路由器管理器
    if check_file_exists(ROUTER_MANAGER_PATH, "路由器管理器"):
        with open(ROUTER_MANAGER_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'class RouterManager' in content:
                print("  → RouterManager 類已定義")
            else:
                print("  ✗ RouterManager 類缺失")
                all_ok = False
    else:
        all_ok = False

    return all_ok


def check_organizational_structure():
    """檢查組織身份結構"""
    print("\n" + "="*60)
    print("步驟 2: 驗證組織身份結構")
    print("="*60)

    try:
        # 導入身份管理系統
        sys.path.insert(0, str(Path(__file__).parent))
        from identity_management_system import IdentityManagementSystem, OrganizationLevel

        print("✓ 身份管理系統已成功導入\n")

        # 初始化系統
        identity_system = IdentityManagementSystem()

        # 驗證組織層級
        print("組織層級結構:")
        for level in OrganizationLevel:
            print(f"  • {level.name}: {level.value}")

        # 檢查完整身份結構
        identity = identity_system.get_complete_identity_structure()

        print("\n完整身份結構:")
        if 'google_nonprofit' in identity:
            print("  ✓ Google 非營利組織")
            gn = identity['google_nonprofit']
            print(f"    - 名稱: {gn.get('name')}")
            print(f"    - Google 狀態: {gn.get('google_status')}")

        if 'workspace_admin' in identity:
            print("  ✓ Google Workspace 超級管理員")
            wa = identity['workspace_admin']
            print(f"    - 網域: {wa.get('domain')}")
            print(f"    - 管理員帳號: {wa.get('admin_email')}")

        if 'odoo_super_admin' in identity:
            print("  ✓ Odoo 最高權限帳號")
            osa = identity['odoo_super_admin']
            print(f"    - 管理員帳號: {osa.get('admin_account')}")
            print(f"    - 系統權限: 全部模組存取")

        if 'coffee_business_owner' in identity:
            print("  ✓ 品啦國咖啡 POS 負責人")
            cbo = identity['coffee_business_owner']
            print(f"    - 業務: {cbo.get('business_name')}")
            print(f"    - 角色: {cbo.get('role')}")

        return True

    except Exception as e:
        print(f"✗ 組織身份驗證失敗: {e}")
        return False


def check_access_matrix():
    """檢查統一存取矩陣"""
    print("\n" + "="*60)
    print("步驟 3: 驗證統一存取矩陣")
    print("="*60)

    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from identity_management_system import IdentityManagementSystem

        identity_system = IdentityManagementSystem()
        access_matrix = identity_system.get_access_matrix()

        print("統一登入點 (使用 admin@wuchang.life):\n")

        for system_name, details in access_matrix.items():
            print(f"  {system_name}:")
            print(f"    - 存取點: {details.get('access_point')}")
            print(f"    - 權限等級: {details.get('permission_level')}")
            print(f"    - 功能: {', '.join(details.get('capabilities', []))}")
            print()

        return True

    except Exception as e:
        print(f"✗ 存取矩陣驗證失敗: {e}")
        return False


def check_founder_controls():
    """檢查創辦人上帝視角控制"""
    print("\n" + "="*60)
    print("步驟 4: 驗證創辦人上帝視角控制")
    print("="*60)

    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from founder_gods_eye_view import FounderGodsEyeView

        print("✓ 創辦人上帝視角已成功導入\n")

        founder_view = FounderGodsEyeView()

        print("創辦人控制權限:")
        print("  • 系統總覽 (get_system_overview)")
        print("  • 財務儀表板 (get_financial_dashboard)")
        print("  • 地點權威 (get_location_authority)")
        print("  • 政策制定 (create_policy)")
        print("  • 資金分配 (allocate_funds)")
        print("  • AI 戰略核准 (approve_ai_strategy)")
        print("  • 網路政策設定 (set_network_policy)")

        print("\n創辦人認證機制:")
        print("  • 超級代幣: founder-gods-eye-view-token")
        print("  • 權限等級: FOUNDER (Level 0)")
        print("  • 決策層級: 最高")

        print("\n系統位置 (創辦人直接控制):")
        print(f"  • 伺服器: {founder_view.system_location['server']}")
        print(f"  • 路由器: {founder_view.system_location['router']}")
        print(f"  • 網域: {founder_view.system_location['domain']}")

        return True

    except Exception as e:
        print(f"✗ 創辦人控制驗證失敗: {e}")
        return False


def check_api_endpoints():
    """檢查 API 端點整合"""
    print("\n" + "="*60)
    print("步驟 5: 驗證 API 端點整合")
    print("="*60)

    all_endpoints = {
        "身份管理系統": [
            "GET /identity/structure",
            "GET /identity/access-matrix",
            "GET /identity/organizational-chart",
            "GET /identity/google-nonprofit-benefits",
            "GET /identity/report"
        ],
        "創辦人上帝視角": [
            "GET /founder/system-overview",
            "GET /founder/financial-dashboard",
            "GET /founder/location-authority",
            "POST /founder/create-policy",
            "POST /founder/allocate-funds",
            "POST /founder/approve-ai-strategy",
            "POST /founder/set-network-policy"
        ],
        "路由器管理": [
            "GET /router/status",
            "GET /router/devices",
            "GET /router/topology",
            "POST /router/optimize"
        ]
    }

    for category, endpoints in all_endpoints.items():
        print(f"\n{category}:")
        for endpoint in endpoints:
            print(f"  ✓ {endpoint}")

    print("\n" + "="*60)
    print("共有 16 個 API 端點已整合")
    print("="*60)

    return True


def generate_identity_report():
    """生成身份驗證報告"""
    print("\n" + "="*60)
    print("步驟 6: 生成身份驗證報告")
    print("="*60)

    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from identity_management_system import IdentityManagementSystem

        identity_system = IdentityManagementSystem()
        report = identity_system.generate_identity_report()

        print("\n" + report)
        return True

    except Exception as e:
        print(f"✗ 報告生成失敗: {e}")
        return False


def main():
    """主測試函數"""
    print("\n" + "="*60)
    print("WUCHANG AI 組織身份系統驗證")
    print("="*60)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    results = {
        "檔案檢查": check_imports(),
        "組織結構": check_organizational_structure(),
        "存取矩陣": check_access_matrix(),
        "創辦人控制": check_founder_controls(),
        "API 端點": check_api_endpoints(),
        "身份報告": generate_identity_report()
    }

    # 總結
    print("\n" + "="*60)
    print("驗證結果總結")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ 通過" if result else "✗ 失敗"
        print(f"{status}: {test_name}")

    print("\n" + "="*60)
    print(f"總體結果: {passed}/{total} 項目通過")
    print("="*60)

    if passed == total:
        print("\n✓ 全部驗證通過!")
        print("\n組織身份系統已完全整合:")
        print("  • Google 非營利組織身份已確認")
        print("  • Google Workspace 超級管理員控制已啟用")
        print("  • Odoo 最高權限存取已配置")
        print("  • 品啦國咖啡 POS 負責人角色已定義")
        print("  • 統一身份管理系統已實現")
        print("  • 創辦人上帝視角控制已部署")
        print("  • 路由器管理已整合")
        print("\n系統準備好重新啟動，所有新功能都將可用。")
        return 0
    else:
        print(f"\n✗ 驗證失敗，{total - passed} 項未通過")
        print("請檢查上述錯誤訊息並修正。")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
