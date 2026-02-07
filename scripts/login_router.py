"""
華碩路由器登錄腳本
"""

import sys
import getpass
from router_connection import AsusRouterConnection

def main():
    print("=" * 60)
    print("華碩路由器登錄工具")
    print("=" * 60)
    
    # 路由器連接信息
    router_ip = "220.135.21.74"
    port = 8443
    
    print(f"\n路由器 IP: {router_ip}")
    print(f"端口: {port}")
    print("=" * 60)
    
    # 創建連接對象
    router = AsusRouterConnection(hostname=router_ip, port=port, use_https=True)
    
    # 測試連接
    print("\n[1] 測試連接...")
    if not router.test_connection(verify_cert=False):
        print("[FAIL] 無法連接到路由器")
        return
    
    print("[OK] 連接成功\n")
    
    # 獲取登錄憑證
    print("[2] 登錄...")
    print("-" * 60)
    
    # 從命令行參數獲取用戶名和密碼（如果提供）
    if len(sys.argv) >= 3:
        username = sys.argv[1]
        password = sys.argv[2]
        print(f"使用命令行提供的憑證")
    elif len(sys.argv) == 2:
        # 只提供了用戶名，提示輸入密碼
        username = sys.argv[1]
        try:
            password = getpass.getpass("請輸入路由器管理員密碼: ")
        except (EOFError, KeyboardInterrupt):
            print("\n操作已取消")
            return
    else:
        try:
            username = input("請輸入路由器管理員用戶名: ").strip()
            if not username:
                print("未提供用戶名，退出")
                return
            
            password = getpass.getpass("請輸入路由器管理員密碼: ")
            if not password:
                print("未提供密碼，退出")
                return
        except (EOFError, KeyboardInterrupt):
            print("\n操作已取消")
            return
    
    # 執行登錄
    print(f"\n正在登錄用戶: {username}...")
    if router.login(username, password, verify_cert=False):
        print("\n" + "=" * 60)
        print("[成功] 已登錄到路由器！")
        print("=" * 60)
        
        # 嘗試獲取路由器信息
        print("\n[3] 獲取路由器信息...")
        info = router.get_router_info(verify_cert=False)
        if info:
            print("路由器信息:")
            print(info)
    else:
        print("\n" + "=" * 60)
        print("[失敗] 登錄失敗")
        print("=" * 60)
        print("\n可能原因:")
        print("  1. 用戶名或密碼錯誤")
        print("  2. 路由器登錄功能被禁用")
        print("  3. 需要額外的認證步驟")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用戶中斷操作")
    except Exception as e:
        print(f"\n發生錯誤: {e}")
        import traceback
        traceback.print_exc()
