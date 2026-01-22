"""
華碩路由器設定檔案匯入工具
用於匯入 Settings_RT-BE86U.CFG 設定檔案到路由器
"""

import os
import sys
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from pathlib import Path

# 設置 UTF-8 編碼
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 禁用 SSL 警告
urllib3.disable_warnings(InsecureRequestWarning)

# 路由器連接資訊
ROUTER_IP = "192.168.50.84"  # 本地 IP
ROUTER_EXTERNAL_IP = "220.135.21.74"  # 外部 IP
ROUTER_PORT = 8443
ROUTER_URL = f"https://{ROUTER_IP}:{ROUTER_PORT}"

# 設定檔案路徑
CONFIG_FILE = r"J:\我的雲端硬碟\Bound\Downloads\Settings_RT-BE86U.CFG"


def check_config_file():
    """檢查設定檔案是否存在"""
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ 設定檔案不存在: {CONFIG_FILE}")
        return False
    
    file_size = os.path.getsize(CONFIG_FILE)
    print(f"✅ 找到設定檔案: {CONFIG_FILE}")
    print(f"   檔案大小: {file_size:,} bytes")
    
    # 檢查檔案格式
    with open(CONFIG_FILE, 'rb') as f:
        header = f.read(100)
        print(f"   檔案前 100 bytes (hex): {header.hex()[:200]}")
    
    return True


def login_to_router(username, password):
    """登入路由器並取得 session"""
    session = requests.Session()
    session.verify = False  # 忽略 SSL 證書驗證
    
    try:
        # 嘗試登入
        login_url = f"{ROUTER_URL}/login.cgi"
        
        # 華碩路由器登入通常需要特定的參數
        login_data = {
            'login_authorization': '',  # 需要 base64 編碼的 username:password
            'username': username,
            'password': password
        }
        
        # 先獲取登入頁面
        response = session.get(f"{ROUTER_URL}/", timeout=10)
        print(f"✅ 連接到路由器: {ROUTER_URL}")
        
        # 嘗試登入（實際的登入端點可能不同）
        # 這裡需要根據實際的路由器 API 調整
        print("⚠️  注意：實際登入方式需要根據路由器型號調整")
        print("   請參考路由器管理介面的登入流程")
        
        return session
        
    except Exception as e:
        print(f"❌ 連接路由器失敗: {e}")
        return None


def import_config_file(session, config_file_path):
    """匯入設定檔案到路由器"""
    try:
        # 讀取設定檔案
        with open(config_file_path, 'rb') as f:
            config_data = f.read()
        
        print(f"\n📤 準備匯入設定檔案...")
        print(f"   檔案大小: {len(config_data):,} bytes")
        
        # 華碩路由器匯入設定的端點（需要根據實際 API 調整）
        import_url = f"{ROUTER_URL}/apply.cgi"
        
        # 準備上傳資料
        files = {
            'file': ('Settings_RT-BE86U.CFG', config_data, 'application/octet-stream')
        }
        
        data = {
            'action_mode': 'apply',
            'action_script': 'restore',
            'next_page': 'Advanced_SettingBackup_Content.asp'
        }
        
        print(f"⚠️  注意：實際的匯入端點和參數需要根據路由器型號調整")
        print(f"   建議使用 Web 介面手動匯入設定檔案")
        
        # 這裡只是示範，實際執行需要正確的 API 端點
        # response = session.post(import_url, files=files, data=data, timeout=60)
        
        return True
        
    except Exception as e:
        print(f"❌ 匯入設定檔案失敗: {e}")
        return False


def main():
    """主函數"""
    print("=" * 60)
    print("華碩路由器設定檔案匯入工具")
    print("=" * 60)
    print()
    
    # 檢查設定檔案
    if not check_config_file():
        return
    
    print()
    print("=" * 60)
    print("匯入方式說明")
    print("=" * 60)
    print()
    print("方法一：通過 Web 介面匯入（推薦）")
    print("  1. 開啟瀏覽器，連接到路由器管理介面")
    print(f"     本地: https://{ROUTER_IP}:{ROUTER_PORT}")
    print(f"     遠端: https://{ROUTER_EXTERNAL_IP}:{ROUTER_PORT}")
    print()
    print("  2. 登入路由器管理介面")
    print()
    print("  3. 進入「系統管理」→「設定」→「備份/還原設定」")
    print()
    print("  4. 點擊「選擇檔案」或「瀏覽」")
    print()
    print(f"  5. 選擇設定檔案: {CONFIG_FILE}")
    print()
    print("  6. 點擊「上傳」或「還原」按鈕")
    print()
    print("  7. 等待路由器重新啟動並套用設定")
    print()
    print("方法二：通過 API 匯入（需要正確的 API 端點）")
    print("  ⚠️  此方法需要知道路由器的具體 API 端點")
    print("  ⚠️  不同型號的路由器 API 可能不同")
    print("  ⚠️  建議先使用方法一確認設定檔案格式正確")
    print()
    print("=" * 60)
    print()
    
    # 詢問是否要嘗試 API 匯入
    try:
        choice = input("是否要嘗試通過 API 匯入？(y/N): ").strip().lower()
        if choice == 'y':
            username = input("請輸入路由器管理員用戶名: ").strip()
            password = input("請輸入路由器管理員密碼: ").strip()
            
            session = login_to_router(username, password)
            if session:
                import_config_file(session, CONFIG_FILE)
        else:
            print("已取消 API 匯入")
            print("請使用 Web 介面手動匯入設定檔案")
    except KeyboardInterrupt:
        print("\n操作已取消")
    except Exception as e:
        print(f"發生錯誤: {e}")


if __name__ == "__main__":
    main()
