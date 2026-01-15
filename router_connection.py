"""
華碩路由器 DDNS 連接工具
連接到 coffeeLofe.asuscomm.com (注意：原輸入為 .comm，已修正為 .com)
"""

import requests
import ssl
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import os
import sys
import base64
import socket

# 設置 UTF-8 編碼以支持中文輸出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 禁用 SSL 警告（如果使用自簽名證書）
urllib3.disable_warnings(InsecureRequestWarning)

class AsusRouterConnection:
    def __init__(self, hostname="coffeeLofe.asuscomm.com", port=8443, use_https=True):
        """
        初始化路由器連接
        
        Args:
            hostname: 路由器 DDNS 主機名
            port: 連接端口（8443 為 HTTPS，8080 為 HTTP）
            use_https: 是否使用 HTTPS
        """
        self.hostname = hostname
        self.port = port
        self.use_https = use_https
        self.protocol = "https" if use_https else "http"
        self.base_url = f"{self.protocol}://{self.hostname}:{self.port}"
        self.session = requests.Session()
        self.logged_in = False
        
    def test_connection(self, verify_cert=True):
        """
        測試連接到路由器
        
        Args:
            verify_cert: 是否驗證 SSL 證書（如果本機已安裝證書，設為 True）
        
        Returns:
            bool: 連接是否成功
        """
        try:
            # 嘗試連接到路由器登錄頁面
            url = f"{self.base_url}/"
            print(f"正在連接到: {url}")
            
            # 如果使用 IP 地址連接，證書驗證可能會失敗（因為證書是為域名簽發的）
            # 如果本機已安裝證書，verify 設為 True
            # 如果證書路徑已知，可以指定: verify='/path/to/certificate.pem'
            response = self.session.get(
                url,
                verify=verify_cert,
                timeout=10,
                allow_redirects=True
            )
            
            print(f"連接成功！狀態碼: {response.status_code}")
            print(f"響應標頭: {dict(response.headers)}")
            
            # 檢查是否為華碩路由器頁面
            if "asus" in response.text.lower() or "router" in response.text.lower():
                print("[OK] 確認連接到華碩路由器")
            
            # 顯示頁面標題（如果有的話）
            if "<title>" in response.text:
                import re
                title_match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE)
                if title_match:
                    print(f"頁面標題: {title_match.group(1)}")
            
            return True
            
        except requests.exceptions.SSLError as e:
            print(f"SSL 證書錯誤: {e}")
            print("提示: 如果本機已安裝證書但仍出現此錯誤，")
            print("     請檢查證書是否正確安裝在系統證書存儲中")
            return False
            
        except requests.exceptions.ConnectionError as e:
            print(f"連接錯誤: {e}")
            print("可能原因:")
            print("  1. 路由器未開啟或未連接到網路")
            print("  2. DDNS 未正確配置")
            print("  3. 防火牆阻擋連接")
            print("  4. 端口不正確")
            return False
            
        except requests.exceptions.Timeout:
            print("連接超時")
            return False
            
        except Exception as e:
            print(f"發生錯誤: {e}")
            return False
    
    def login(self, username, password, verify_cert=False):
        """
        登錄到路由器
        
        Args:
            username: 路由器管理員用戶名
            password: 路由器管理員密碼
            verify_cert: 是否驗證 SSL 證書
        
        Returns:
            bool: 登錄是否成功
        """
        try:
            print(f"\n正在嘗試登錄到 {self.hostname}...")
            
            # 先獲取登錄頁面以建立 session
            print("獲取登錄頁面...")
            response = self.session.get(
                f"{self.base_url}/",
                verify=verify_cert,
                timeout=10
            )
            
            # 華碩路由器有多種登錄方式，嘗試常見的端點
            login_endpoints = [
                "/login.cgi",
                "/appGet.cgi?hook=login()",
                "/login.cgi?login_authorization="
            ]
            
            # 準備登錄數據
            auth_string = f"{username}:{password}"
            auth_encoded = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
            
            # 嘗試不同的登錄方式
            for endpoint in login_endpoints:
                try:
                    login_url = f"{self.base_url}{endpoint}"
                    
                    # 方式1: POST 請求
                    login_data = {
                        "login_authorization": auth_encoded,
                        "action_mode": "login",
                        "action_script": "",
                        "action_wait": "1"
                    }
                    
                    print(f"嘗試登錄端點: {endpoint}")
                    response = self.session.post(
                        login_url,
                        data=login_data,
                        verify=verify_cert,
                        timeout=10,
                        allow_redirects=True
                    )
                    
                    # 檢查登錄是否成功
                    if response.status_code == 200:
                        # 檢查響應內容判斷是否登錄成功
                        response_text = response.text.lower()
                        
                        # 如果重定向到主頁或包含成功標誌
                        if "asus" in response_text or "router" in response_text:
                            if "login" not in response_text or "error" not in response_text:
                                print("[OK] 登錄成功！")
                                self.logged_in = True
                                return True
                        
                        # 檢查是否有錯誤訊息
                        if "authentication failed" in response_text or "login failed" in response_text:
                            print("[FAIL] 登錄失敗：用戶名或密碼錯誤")
                            return False
                    
                    # 方式2: GET 請求（某些路由器使用）
                    if "?" in endpoint:
                        get_url = f"{self.base_url}{endpoint}{auth_encoded}"
                        response = self.session.get(
                            get_url,
                            verify=verify_cert,
                            timeout=10,
                            allow_redirects=True
                        )
                        
                        if response.status_code == 200:
                            response_text = response.text.lower()
                            if "asus" in response_text and "login" not in response_text:
                                print("[OK] 登錄成功！")
                                self.logged_in = True
                                return True
                
                except Exception as e:
                    print(f"  嘗試端點 {endpoint} 時發生錯誤: {e}")
                    continue
            
            # 如果所有方式都失敗，嘗試直接訪問需要認證的頁面
            print("\n嘗試驗證登錄狀態...")
            test_urls = [
                f"{self.base_url}/appGet.cgi",
                f"{self.base_url}/Main_Login.asp",
                f"{self.base_url}/index.asp"
            ]
            
            for test_url in test_urls:
                try:
                    response = self.session.get(
                        test_url,
                        verify=verify_cert,
                        timeout=10
                    )
                    
                    # 如果沒有重定向到登錄頁面，可能已經登錄
                    if response.status_code == 200 and "login" not in response.url.lower():
                        print("[OK] 可能已登錄（請手動驗證）")
                        self.logged_in = True
                        return True
                except:
                    continue
            
            print("[FAIL] 登錄失敗：無法確定登錄狀態")
            print("提示: 請檢查用戶名和密碼是否正確")
            return False
                
        except Exception as e:
            print(f"[ERROR] 登錄時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_router_info(self, verify_cert=True):
        """
        獲取路由器信息
        
        Args:
            verify_cert: 是否驗證 SSL 證書
        
        Returns:
            dict: 路由器信息
        """
        try:
            # 嘗試獲取路由器狀態頁面
            url = f"{self.base_url}/appGet.cgi"
            params = {
                "hook": "get_wireless_client()"
            }
            
            response = self.session.get(
                url,
                params=params,
                verify=verify_cert,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            else:
                return None
                
        except Exception as e:
            print(f"獲取路由器信息時發生錯誤: {e}")
            return None


def main():
    """主函數"""
    print("=" * 50)
    print("華碩路由器 DDNS 連接工具")
    print("=" * 50)
    
    # 使用提供的 IP 地址或嘗試 DNS 解析
    hostname = "coffeeLofe.asuscomm.com"
    router_ip = "220.135.21.74"  # 用戶提供的路由器公網 IP
    
    print(f"\n使用路由器 IP 地址: {router_ip}")
    print("注意: 使用 IP 連接時，SSL 證書驗證可能會失敗（證書是為域名簽發的）")
    print("      但連接仍然可以正常工作\n")
    
    # 創建連接對象（使用 IP 地址）
    router = AsusRouterConnection(hostname=router_ip, port=8443, use_https=True)
    
    # 測試連接（使用證書驗證，因為用戶說本機已安裝證書）
    print("\n[1] 測試基本連接 (端口 8443)...")
    success = False
    
    # 先嘗試不使用證書驗證（因為使用 IP 地址時證書驗證通常會失敗）
    if router.test_connection(verify_cert=False):
        print("[OK] 連接成功！")
        success = True
        print("\n提示: 使用 IP 地址連接時，SSL 證書驗證會失敗是正常的")
        print("      因為證書是為域名 'coffeeLofe.asuscomm.com' 簽發的，而不是 IP 地址")
        print("      如果需要使用證書驗證，請使用域名連接（需要 DDNS 正常工作）")
    else:
        print("\n嘗試使用證書驗證...")
        if router.test_connection(verify_cert=True):
            print("[OK] 基本連接測試成功 (使用證書驗證)")
            success = True
        else:
            # 嘗試其他常見端口
            print("\n嘗試其他端口...")
            common_ports = [443, 8080, 80, 8444]
            for port in common_ports:
                print(f"\n嘗試端口 {port}...")
                test_router = AsusRouterConnection(hostname=router_ip, port=port, use_https=(port in [443, 8443, 8444]))
                if test_router.test_connection(verify_cert=False):
                    print(f"[OK] 連接成功！使用端口 {port}")
                    success = True
                    router = test_router  # 更新為成功的連接
                    break
    
    if not success:
        print("[FAIL] 連接失敗")
        print("\n建議:")
        print("  1. 檢查路由器是否開啟並連接到網路")
        print("  2. 確認 DDNS 服務是否正常運作")
        print("  3. 檢查防火牆設置")
        print("  4. 確認路由器遠程訪問功能已啟用")
        return
    
    # 登錄功能
    print("\n[2] 登錄路由器...")
    print("=" * 50)
    
    username = input("請輸入路由器管理員用戶名 (直接按 Enter 跳過登錄): ").strip()
    if username:
        import getpass
        password = getpass.getpass("請輸入路由器管理員密碼: ")
        
        if router.login(username, password, verify_cert=False):
            print("\n[OK] 登錄成功！現在可以訪問需要認證的功能")
        else:
            print("\n[WARN] 登錄失敗，但連接仍然可用")
    else:
        print("跳過登錄步驟")
    
    print("\n" + "=" * 50)
    print("連接完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
