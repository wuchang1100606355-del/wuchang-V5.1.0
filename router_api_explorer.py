"""
華碩路由器 API 探索與控管工具
用於發現、測試和記錄路由器的所有 API 端點
"""

import requests
import json
import re
import base64
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import os
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
import time

# 設置 UTF-8 編碼
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

urllib3.disable_warnings(InsecureRequestWarning)


class RouterAPIExplorer:
    """路由器 API 探索器"""
    
    def __init__(self, hostname="192.168.50.84", port=8443, username=None, password=None):
        """
        初始化 API 探索器
        
        Args:
            hostname: 路由器 IP 或域名
            port: 端口號
            username: 用戶名（可選）
            password: 密碼（可選）
        """
        self.hostname = hostname
        self.port = port
        self.base_url = f"https://{hostname}:{port}"
        self.session = requests.Session()
        self.session.verify = False
        
        # 載入證書（如果存在）
        cert_path = os.path.join(os.path.dirname(__file__), "certs", "cert.pem")
        key_path = os.path.join(os.path.dirname(__file__), "certs", "key.pem")
        if os.path.exists(cert_path) and os.path.exists(key_path):
            self.session.cert = (cert_path, key_path)
        
        self.username = username
        self.password = password
        self.logged_in = False
        self.discovered_apis = []
        
    def login(self) -> bool:
        """登入路由器"""
        if not self.username or not self.password:
            return False
        
        try:
            # 獲取登錄頁面
            response = self.session.get(f"{self.base_url}/")
            
            # 準備認證
            auth_string = f"{self.username}:{self.password}"
            auth_encoded = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
            
            # 嘗試登錄
            login_data = {
                "login_authorization": auth_encoded,
                "action_mode": "login"
            }
            
            response = self.session.post(
                f"{self.base_url}/login.cgi",
                data=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logged_in = True
                return True
        except Exception as e:
            print(f"登錄失敗: {e}")
        
        return False
    
    def discover_from_html(self, html_content: str) -> List[str]:
        """從 HTML 內容中發現 API 端點"""
        endpoints = set()
        
        # 查找常見的 API 模式
        patterns = [
            r'["\']([^"\']*\.cgi[^"\']*)["\']',  # .cgi 文件
            r'["\']([^"\']*appGet[^"\']*)["\']',  # appGet
            r'["\']([^"\']*appSet[^"\']*)["\']',  # appSet
            r'["\']([^"\']*apply[^"\']*)["\']',  # apply
            r'hook\s*=\s*["\']([^"\']+)["\']',  # hook 函數
            r'url\s*[:=]\s*["\']([^"\']+)["\']',  # URL 定義
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if match.startswith('/') or match.startswith('http'):
                    endpoints.add(match)
                elif '.cgi' in match or 'appGet' in match or 'appSet' in match:
                    endpoints.add(f'/{match}')
        
        return list(endpoints)
    
    def discover_from_js(self, js_content: str) -> List[str]:
        """從 JavaScript 內容中發現 API 端點"""
        endpoints = set()
        
        # 查找 API 調用
        patterns = [
            r'["\']([^"\']*\.cgi[^"\']*)["\']',
            r'url\s*[:=]\s*["\']([^"\']+)["\']',
            r'["\']([^"\']*appGet[^"\']*)["\']',
            r'["\']([^"\']*appSet[^"\']*)["\']',
            r'\.get\(["\']([^"\']+)["\']',
            r'\.post\(["\']([^"\']+)["\']',
            r'ajax\(["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            for match in matches:
                if match.startswith('/') or match.startswith('http'):
                    endpoints.add(match)
                elif '.cgi' in match:
                    endpoints.add(f'/{match}')
        
        return list(endpoints)
    
    def fetch_page(self, url: str) -> Optional[str]:
        """獲取頁面內容"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"獲取 {url} 失敗: {e}")
        return None
    
    def test_endpoint(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None) -> Dict[str, Any]:
        """測試 API 端點"""
        result = {
            "endpoint": endpoint,
            "method": method,
            "status_code": None,
            "response_time": None,
            "content_type": None,
            "response_size": None,
            "success": False,
            "error": None,
            "sample_response": None
        }
        
        try:
            url = f"{self.base_url}{endpoint}" if endpoint.startswith('/') else f"{self.base_url}/{endpoint}"
            
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(url, params=params, timeout=10)
            else:
                response = self.session.post(url, params=params, data=data, timeout=10)
            
            result["response_time"] = round((time.time() - start_time) * 1000, 2)
            result["status_code"] = response.status_code
            result["content_type"] = response.headers.get('Content-Type', '')
            result["response_size"] = len(response.content)
            result["success"] = response.status_code == 200
            
            # 保存響應樣本（前 500 字元）
            if response.text:
                result["sample_response"] = response.text[:500]
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def explore_common_endpoints(self) -> List[Dict[str, Any]]:
        """探索常見的 API 端點"""
        common_endpoints = [
            # 系統資訊
            "/appGet.cgi",
            "/appGet.cgi?hook=get_wireless_client()",
            "/appGet.cgi?hook=get_client_list()",
            "/appGet.cgi?hook=get_wan_status()",
            "/appGet.cgi?hook=get_lan_status()",
            "/appGet.cgi?hook=get_system_info()",
            "/appGet.cgi?hook=get_firmware_info()",
            
            # 設定相關
            "/appSet.cgi",
            "/apply.cgi",
            "/apply_sec.cgi",
            
            # 登錄相關
            "/login.cgi",
            "/logout.cgi",
            
            # 備份/還原
            "/apply.cgi?action_mode=restore",
            "/apply.cgi?action_mode=backup",
            
            # 狀態頁面
            "/Main_Login.asp",
            "/index.asp",
            "/Main_Status_Content.asp",
            "/Advanced_System_Content.asp",
            "/Advanced_WAN_Content.asp",
            "/Advanced_LAN_Content.asp",
            "/Advanced_Wireless_Content.asp",
            "/Advanced_Firewall_Content.asp",
            "/Advanced_VPN_Content.asp",
            "/Advanced_SettingBackup_Content.asp",
        ]
        
        results = []
        print(f"\n探索 {len(common_endpoints)} 個常見端點...")
        
        for endpoint in common_endpoints:
            print(f"測試: {endpoint}")
            result = self.test_endpoint(endpoint)
            results.append(result)
            if result["success"]:
                print(f"  ✓ 成功 (狀態碼: {result['status_code']}, 響應時間: {result['response_time']}ms)")
            else:
                print(f"  ✗ 失敗 (狀態碼: {result['status_code']}, 錯誤: {result.get('error', 'N/A')})")
            time.sleep(0.1)  # 避免過快請求
        
        return results
    
    def discover_from_web_interface(self) -> List[str]:
        """從 Web 介面發現 API 端點"""
        endpoints = set()
        
        print("\n從 Web 介面發現 API 端點...")
        
        # 獲取主頁面
        main_page = self.fetch_page(f"{self.base_url}/")
        if main_page:
            print("分析主頁面...")
            endpoints.update(self.discover_from_html(main_page))
            
            # 使用 BeautifulSoup 解析（如果可用）
            if HAS_BS4:
                try:
                    soup = BeautifulSoup(main_page, 'html.parser')
                    
                    # 查找所有 script 標籤
                    for script in soup.find_all('script', src=True):
                        script_url = script.get('src')
                        if script_url:
                            endpoints.add(script_url)
                            # 獲取並分析 JavaScript 文件
                            if script_url.startswith('/'):
                                js_content = self.fetch_page(f"{self.base_url}{script_url}")
                                if js_content:
                                    endpoints.update(self.discover_from_js(js_content))
                    
                    # 查找所有連結
                    for link in soup.find_all('a', href=True):
                        href = link.get('href')
                        if href and ('.cgi' in href or 'appGet' in href or 'appSet' in href):
                            endpoints.add(href)
                    
                except Exception as e:
                    print(f"解析 HTML 時發生錯誤: {e}")
            else:
                print("注意: BeautifulSoup4 未安裝，跳過 HTML 深度解析")
        
        return list(endpoints)
    
    def explore_all(self) -> Dict[str, Any]:
        """全面探索路由器 API"""
        print("=" * 60)
        print("華碩路由器 API 探索工具")
        print("=" * 60)
        print(f"目標: {self.base_url}")
        print()
        
        # 登錄（如果提供了憑證）
        if self.username and self.password:
            print("嘗試登錄...")
            if self.login():
                print("✓ 登錄成功")
            else:
                print("✗ 登錄失敗，將以未登錄狀態探索")
        
        all_results = {
            "exploration_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "router_url": self.base_url,
            "logged_in": self.logged_in,
            "common_endpoints": [],
            "discovered_endpoints": [],
            "api_documentation": {}
        }
        
        # 探索常見端點
        all_results["common_endpoints"] = self.explore_common_endpoints()
        
        # 從 Web 介面發現端點
        discovered = self.discover_from_web_interface()
        all_results["discovered_endpoints"] = discovered
        
        # 測試發現的端點
        print(f"\n測試 {len(discovered)} 個發現的端點...")
        for endpoint in discovered[:50]:  # 限制測試數量
            if endpoint.startswith('/') or endpoint.startswith('http'):
                result = self.test_endpoint(endpoint)
                all_results["common_endpoints"].append(result)
        
        return all_results
    
    def save_results(self, results: Dict[str, Any], filename: str = "router_api_discovery.json"):
        """保存探索結果"""
        output_dir = Path("router_api_docs")
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n結果已保存到: {filepath}")
        return filepath


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="華碩路由器 API 探索工具")
    parser.add_argument("--host", default="192.168.50.84", help="路由器 IP 或域名")
    parser.add_argument("--port", type=int, default=8443, help="端口號")
    parser.add_argument("--username", help="用戶名（可選）")
    parser.add_argument("--password", help="密碼（可選）")
    
    args = parser.parse_args()
    
    # 創建探索器
    explorer = RouterAPIExplorer(
        hostname=args.host,
        port=args.port,
        username=args.username,
        password=args.password
    )
    
    # 執行探索
    results = explorer.explore_all()
    
    # 保存結果
    explorer.save_results(results)
    
    # 顯示摘要
    print("\n" + "=" * 60)
    print("探索摘要")
    print("=" * 60)
    successful = [r for r in results["common_endpoints"] if r.get("success")]
    print(f"成功測試的端點: {len(successful)}")
    print(f"發現的端點: {len(results['discovered_endpoints'])}")
    print(f"總測試端點: {len(results['common_endpoints'])}")


if __name__ == "__main__":
    main()
