"""
路由器整合模組
用於將路由器納入系統資源，提供連線裝置和網路流量資訊
"""

import requests
import json
import base64
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import time

# 設置 UTF-8 編碼
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

urllib3.disable_warnings(InsecureRequestWarning)


class RouterIntegration:
    """路由器整合類別"""
    
    def __init__(self, hostname="192.168.50.84", port=8443, username=None, password=None):
        """
        初始化路由器整合
        
        Args:
            hostname: 路由器 IP
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
        
        # 流量歷史記錄（用於繪圖）
        self.traffic_history = {
            "upload": [],
            "download": [],
            "timestamps": []
        }
        
        # 從環境變數或設定檔讀取認證資訊
        self._load_credentials()
    
    def _load_credentials(self):
        """從環境變數或設定檔載入認證資訊"""
        # 優先使用環境變數
        if not self.username:
            self.username = os.getenv("ROUTER_USERNAME")
        if not self.password:
            self.password = os.getenv("ROUTER_PASSWORD")
        
        # 如果環境變數沒有，嘗試從設定檔讀取
        if not self.username or not self.password:
            config_path = os.path.join(os.path.dirname(__file__), "router_config.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        self.username = self.username or config.get("username")
                        self.password = self.password or config.get("password")
                except:
                    pass
    
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
    
    def get_connected_devices(self) -> Dict[str, Any]:
        """
        獲取連線裝置列表
        
        Returns:
            包含連線裝置資訊的字典
        """
        try:
            # 嘗試獲取無線客戶端
            wireless_clients = self._get_wireless_clients()
            
            # 嘗試獲取所有客戶端列表
            all_clients = self._get_client_list()
            
            # 合併結果
            devices = []
            device_macs = set()
            
            # 處理無線客戶端
            if wireless_clients:
                if isinstance(wireless_clients, dict):
                    # 解析無線客戶端資料
                    for key, value in wireless_clients.items():
                        if isinstance(value, dict) and 'mac' in value:
                            mac = value.get('mac', '').upper()
                            if mac and mac not in device_macs:
                                devices.append({
                                    "mac": mac,
                                    "ip": value.get('ip', ''),
                                    "name": value.get('name', ''),
                                    "type": "wireless",
                                    "signal": value.get('rssi', 0),
                                    "connected_time": value.get('connected_time', 0)
                                })
                                device_macs.add(mac)
            
            # 處理所有客戶端列表
            if all_clients:
                if isinstance(all_clients, dict):
                    for key, value in all_clients.items():
                        if isinstance(value, dict):
                            mac = value.get('mac', '').upper()
                            if mac and mac not in device_macs:
                                devices.append({
                                    "mac": mac,
                                    "ip": value.get('ip', ''),
                                    "name": value.get('name', value.get('hostname', '')),
                                    "type": value.get('type', 'unknown'),
                                    "signal": value.get('rssi', 0),
                                    "connected_time": value.get('connected_time', 0)
                                })
                                device_macs.add(mac)
            
            return {
                "total_count": len(devices),
                "devices": devices,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "total_count": 0,
                "devices": [],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_wireless_clients(self) -> Optional[Dict]:
        """獲取無線客戶端"""
        try:
            url = f"{self.base_url}/appGet.cgi"
            params = {"hook": "get_wireless_client()"}
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                try:
                    return response.json()
                except:
                    # 嘗試解析文字格式
                    text = response.text
                    if text:
                        return {"raw": text}
        except:
            pass
        return None
    
    def _get_client_list(self) -> Optional[Dict]:
        """獲取所有客戶端列表"""
        try:
            url = f"{self.base_url}/appGet.cgi"
            params = {"hook": "get_client_list()"}
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                try:
                    return response.json()
                except:
                    text = response.text
                    if text:
                        return {"raw": text}
        except:
            pass
        return None
    
    def get_network_traffic(self) -> Dict[str, Any]:
        """
        獲取網路流量資訊
        
        Returns:
            包含流量資訊的字典
        """
        try:
            # 嘗試獲取流量監控資料
            traffic_data = self._get_traffic_monitor()
            
            # 獲取 WAN 狀態（可能包含流量資訊）
            wan_status = self._get_wan_status()
            
            # 解析流量資料
            upload_speed = 0
            download_speed = 0
            upload_total = 0
            download_total = 0
            
            if traffic_data:
                if isinstance(traffic_data, dict):
                    upload_speed = traffic_data.get('upload_speed', 0)
                    download_speed = traffic_data.get('download_speed', 0)
                    upload_total = traffic_data.get('upload_total', 0)
                    download_total = traffic_data.get('download_total', 0)
            
            if wan_status:
                if isinstance(wan_status, dict):
                    # 從 WAN 狀態中提取流量資訊
                    if 'upload' in wan_status:
                        upload_speed = wan_status.get('upload', 0)
                    if 'download' in wan_status:
                        download_speed = wan_status.get('download', 0)
            
            # 記錄到歷史
            current_time = datetime.now()
            self.traffic_history["upload"].append(upload_speed)
            self.traffic_history["download"].append(download_speed)
            self.traffic_history["timestamps"].append(current_time.isoformat())
            
            # 保持最近 60 筆記錄（每分鐘一筆，約1小時）
            max_history = 60
            if len(self.traffic_history["upload"]) > max_history:
                self.traffic_history["upload"] = self.traffic_history["upload"][-max_history:]
                self.traffic_history["download"] = self.traffic_history["download"][-max_history:]
                self.traffic_history["timestamps"] = self.traffic_history["timestamps"][-max_history:]
            
            return {
                "upload_speed": upload_speed,  # bps
                "download_speed": download_speed,  # bps
                "upload_total": upload_total,  # bytes
                "download_total": download_total,  # bytes
                "upload_speed_mbps": round(upload_speed / 1000000, 2),  # Mbps
                "download_speed_mbps": round(download_speed / 1000000, 2),  # Mbps
                "history": {
                    "upload": self.traffic_history["upload"][-30:],  # 最近30筆
                    "download": self.traffic_history["download"][-30:],
                    "timestamps": self.traffic_history["timestamps"][-30:]
                },
                "timestamp": current_time.isoformat()
            }
            
        except Exception as e:
            return {
                "upload_speed": 0,
                "download_speed": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_traffic_monitor(self) -> Optional[Dict]:
        """獲取流量監控資料"""
        try:
            url = f"{self.base_url}/appGet.cgi"
            params = {"hook": "get_traffic_monitor()"}
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                try:
                    return response.json()
                except:
                    text = response.text
                    if text:
                        return {"raw": text}
        except:
            pass
        return None
    
    def _get_wan_status(self) -> Optional[Dict]:
        """獲取 WAN 狀態"""
        try:
            url = f"{self.base_url}/appGet.cgi"
            params = {"hook": "get_wan_status()"}
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                try:
                    return response.json()
                except:
                    text = response.text
                    if text:
                        return {"raw": text}
        except:
            pass
        return None
    
    def get_router_status(self) -> Dict[str, Any]:
        """
        獲取路由器完整狀態
        
        Returns:
            包含所有狀態資訊的字典
        """
        try:
            system_info = self._get_system_info()
            wan_status = self._get_wan_status()
            devices = self.get_connected_devices()
            traffic = self.get_network_traffic()
            
            return {
                "router_model": "ASUS RT-BE86U",
                "hostname": self.hostname,
                "external_ip": "220.135.21.74",
                "ddns": "coffeeLofe.asuscomm.com",
                "system_info": system_info,
                "wan_status": wan_status,
                "connected_devices": devices,
                "network_traffic": traffic,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_system_info(self) -> Optional[Dict]:
        """獲取系統資訊"""
        try:
            url = f"{self.base_url}/appGet.cgi"
            params = {"hook": "get_system_info()"}
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                try:
                    return response.json()
                except:
                    text = response.text
                    if text:
                        return {"raw": text}
        except:
            pass
        return None


# 單例實例（用於系統整合）
_router_integration_instance = None

def get_router_integration() -> RouterIntegration:
    """獲取路由器整合實例（單例模式）"""
    global _router_integration_instance
    if _router_integration_instance is None:
        _router_integration_instance = RouterIntegration()
        # 嘗試登錄
        if _router_integration_instance.username and _router_integration_instance.password:
            _router_integration_instance.login()
    return _router_integration_instance
