"""
華碩路由器 API 控管工具
提供完整的路由器 API 控制介面
"""

import requests
import json
import base64
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import os
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path

# 設置 UTF-8 編碼
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

urllib3.disable_warnings(InsecureRequestWarning)


class RouterAPIController:
    """路由器 API 控制器"""
    
    def __init__(self, hostname="192.168.50.84", port=8443, username=None, password=None):
        """
        初始化 API 控制器
        
        Args:
            hostname: 路由器 IP 或域名
            port: 端口號
            username: 用戶名
            password: 密碼
        """
        self.hostname = hostname
        self.port = port
        self.base_url = f"https://{hostname}:{port}"
        self.session = requests.Session()
        self.session.verify = False
        
        # 載入證書
        cert_path = os.path.join(os.path.dirname(__file__), "certs", "cert.pem")
        key_path = os.path.join(os.path.dirname(__file__), "certs", "key.pem")
        if os.path.exists(cert_path) and os.path.exists(key_path):
            self.session.cert = (cert_path, key_path)
        
        self.username = username
        self.password = password
        self.logged_in = False
        
        # 載入 API 文檔（如果存在）
        self.api_docs = self._load_api_docs()
    
    def _load_api_docs(self) -> Dict[str, Any]:
        """載入 API 文檔"""
        docs_path = Path("router_api_docs/router_api_discovery.json")
        if docs_path.exists():
            with open(docs_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def login(self) -> bool:
        """登入路由器"""
        if not self.username or not self.password:
            return False
        
        try:
            auth_string = f"{self.username}:{self.password}"
            auth_encoded = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
            
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
    
    def app_get(self, hook: str, params: Dict = None) -> Optional[Dict]:
        """
        調用 appGet.cgi API
        
        Args:
            hook: hook 函數名稱
            params: 額外參數
        
        Returns:
            API 響應（JSON 或文字）
        """
        url = f"{self.base_url}/appGet.cgi"
        request_params = {"hook": hook}
        if params:
            request_params.update(params)
        
        try:
            response = self.session.get(url, params=request_params, timeout=10)
            if response.status_code == 200:
                try:
                    return response.json()
                except:
                    return response.text
        except Exception as e:
            print(f"API 調用失敗: {e}")
        
        return None
    
    def app_set(self, action_mode: str, action_script: str = "", data: Dict = None) -> bool:
        """
        調用 appSet.cgi API
        
        Args:
            action_mode: 操作模式
            action_script: 操作腳本
            data: 設定數據
        
        Returns:
            是否成功
        """
        url = f"{self.base_url}/appSet.cgi"
        
        request_data = {
            "action_mode": action_mode,
            "action_script": action_script
        }
        
        if data:
            request_data.update(data)
        
        try:
            response = self.session.post(url, data=request_data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"API 調用失敗: {e}")
            return False
    
    def apply_config(self, action_mode: str, data: Dict = None) -> bool:
        """
        應用設定（apply.cgi）
        
        Args:
            action_mode: 操作模式
            data: 設定數據
        
        Returns:
            是否成功
        """
        url = f"{self.base_url}/apply.cgi"
        
        request_data = {"action_mode": action_mode}
        if data:
            request_data.update(data)
        
        try:
            response = self.session.post(url, data=request_data, timeout=30)
            return response.status_code == 200
        except Exception as e:
            print(f"應用設定失敗: {e}")
            return False
    
    # 常用 API 方法
    
    def get_system_info(self) -> Optional[Dict]:
        """獲取系統資訊"""
        return self.app_get("get_system_info()")
    
    def get_wan_status(self) -> Optional[Dict]:
        """獲取 WAN 狀態"""
        return self.app_get("get_wan_status()")
    
    def get_lan_status(self) -> Optional[Dict]:
        """獲取 LAN 狀態"""
        return self.app_get("get_lan_status()")
    
    def get_wireless_clients(self) -> Optional[Dict]:
        """獲取無線客戶端列表"""
        return self.app_get("get_wireless_client()")
    
    def get_client_list(self) -> Optional[Dict]:
        """獲取客戶端列表"""
        return self.app_get("get_client_list()")
    
    def get_firmware_info(self) -> Optional[Dict]:
        """獲取韌體資訊"""
        return self.app_get("get_firmware_info()")
    
    def backup_config(self, output_path: str) -> bool:
        """備份設定"""
        try:
            response = self.session.get(
                f"{self.base_url}/apply.cgi",
                params={"action_mode": "backup"},
                timeout=30
            )
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
        except Exception as e:
            print(f"備份失敗: {e}")
        return False
    
    def restore_config(self, config_file_path: str) -> bool:
        """還原設定"""
        try:
            with open(config_file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    "action_mode": "restore",
                    "action_script": "restore",
                    "next_page": "Advanced_SettingBackup_Content.asp"
                }
                response = self.session.post(
                    f"{self.base_url}/apply.cgi",
                    files=files,
                    data=data,
                    timeout=60
                )
                return response.status_code == 200
        except Exception as e:
            print(f"還原失敗: {e}")
        return False
    
    def get_port_forwarding_rules(self) -> Optional[Dict]:
        """獲取端口轉發規則"""
        return self.app_get("get_port_forwarding_rules()")
    
    def set_port_forwarding_rule(self, rule_data: Dict) -> bool:
        """設定端口轉發規則"""
        return self.app_set("apply", "restart_firewall", rule_data)
    
    def get_ddns_status(self) -> Optional[Dict]:
        """獲取 DDNS 狀態"""
        return self.app_get("get_ddns_status()")
    
    def get_vpn_status(self) -> Optional[Dict]:
        """獲取 VPN 狀態"""
        return self.app_get("get_vpn_status()")
    
    def reboot(self) -> bool:
        """重啟路由器"""
        return self.apply_config("reboot")
    
    def get_all_info(self) -> Dict[str, Any]:
        """獲取所有可用資訊"""
        info = {}
        
        methods = [
            ("system_info", self.get_system_info),
            ("wan_status", self.get_wan_status),
            ("lan_status", self.get_lan_status),
            ("wireless_clients", self.get_wireless_clients),
            ("client_list", self.get_client_list),
            ("firmware_info", self.get_firmware_info),
            ("ddns_status", self.get_ddns_status),
            ("vpn_status", self.get_vpn_status),
        ]
        
        for name, method in methods:
            try:
                result = method()
                if result:
                    info[name] = result
            except Exception as e:
                info[name] = {"error": str(e)}
        
        return info


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="華碩路由器 API 控管工具")
    parser.add_argument("--host", default="192.168.50.84", help="路由器 IP")
    parser.add_argument("--port", type=int, default=8443, help="端口號")
    parser.add_argument("--username", help="用戶名")
    parser.add_argument("--password", help="密碼")
    parser.add_argument("--action", choices=["info", "backup", "restore", "reboot"], help="執行動作")
    parser.add_argument("--file", help="備份/還原檔案路徑")
    
    args = parser.parse_args()
    
    controller = RouterAPIController(
        hostname=args.host,
        port=args.port,
        username=args.username,
        password=args.password
    )
    
    if args.username and args.password:
        if controller.login():
            print("✓ 登錄成功")
        else:
            print("✗ 登錄失敗")
            return
    
    if args.action == "info":
        info = controller.get_all_info()
        print(json.dumps(info, ensure_ascii=False, indent=2))
    elif args.action == "backup" and args.file:
        if controller.backup_config(args.file):
            print(f"✓ 備份成功: {args.file}")
        else:
            print("✗ 備份失敗")
    elif args.action == "restore" and args.file:
        if controller.restore_config(args.file):
            print(f"✓ 還原成功: {args.file}")
        else:
            print("✗ 還原失敗")
    elif args.action == "reboot":
        if controller.reboot():
            print("✓ 重啟命令已發送")
        else:
            print("✗ 重啟失敗")


if __name__ == "__main__":
    main()
