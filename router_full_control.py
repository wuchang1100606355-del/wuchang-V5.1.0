"""
路由器完整控制模組
用於物業管理系統的網路基礎設施控制
提供完整的 DNS、DDNS、端口轉發、防火牆等控制能力
"""

import requests
import json
import base64
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import time
import re

# 設置 UTF-8 編碼
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

urllib3.disable_warnings(InsecureRequestWarning)


class RouterFullControl:
    """路由器完整控制類別 - 用於物業管理系統"""
    
    def __init__(self, hostname="192.168.50.84", port=8443, username=None, password=None):
        """
        初始化路由器完整控制
        
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
        
        # 從環境變數或設定檔讀取認證資訊
        self._load_credentials()
    
    def _load_credentials(self):
        """從環境變數或設定檔載入認證資訊"""
        if not self.username:
            self.username = os.getenv("ROUTER_USERNAME")
        if not self.password:
            self.password = os.getenv("ROUTER_PASSWORD")
        
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
    
    def _app_get(self, hook: str, params: Dict = None) -> Optional[Dict]:
        """調用 appGet.cgi API"""
        try:
            url = f"{self.base_url}/appGet.cgi"
            request_params = {"hook": hook}
            if params:
                request_params.update(params)
            
            response = self.session.get(url, params=request_params, timeout=10)
            if response.status_code == 200:
                try:
                    return response.json()
                except:
                    # 嘗試解析文字格式
                    text = response.text
                    return {"raw": text, "text": text}
        except Exception as e:
            print(f"API 調用失敗: {e}")
        return None
    
    def _app_set(self, action_mode: str, action_script: str = "", data: Dict = None) -> bool:
        """調用 appSet.cgi API"""
        try:
            url = f"{self.base_url}/appSet.cgi"
            request_data = {
                "action_mode": action_mode,
                "action_script": action_script
            }
            if data:
                request_data.update(data)
            
            response = self.session.post(url, data=request_data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"API 調用失敗: {e}")
            return False
    
    # ========== DNS/DDNS 控制 ==========
    
    def get_ddns_status(self) -> Dict[str, Any]:
        """獲取 DDNS 狀態"""
        result = self._app_get("get_ddns_status()")
        return {
            "status": result,
            "ddns_hostname": "coffeeLofe.asuscomm.com",
            "external_ip": "220.135.21.74",
            "timestamp": datetime.now().isoformat()
        }
    
    def update_ddns(self, hostname: str, service: str = "asuscomm.com") -> bool:
        """更新 DDNS 設定"""
        data = {
            "ddns_hostname": hostname,
            "ddns_server": service,
            "ddns_enable": "1"
        }
        return self._app_set("apply", "restart_ddns", data)
    
    def get_dns_settings(self) -> Dict[str, Any]:
        """獲取 DNS 設定"""
        result = self._app_get("get_dns_settings()")
        return {
            "settings": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def set_dns_servers(self, primary: str, secondary: str = "") -> bool:
        """設定 DNS 伺服器"""
        data = {
            "dns_server1": primary,
            "dns_server2": secondary
        }
        return self._app_set("apply", "restart_dns", data)
    
    # ========== 端口轉發控制 ==========
    
    def get_port_forwarding_rules(self) -> List[Dict[str, Any]]:
        """獲取所有端口轉發規則"""
        result = self._app_get("get_port_forwarding_rules()")
        if isinstance(result, dict):
            # 解析端口轉發規則
            rules = []
            # 華碩路由器通常使用 vts_* 參數
            for i in range(20):  # 通常最多 20 條規則
                rule = {}
                for key in ["enable", "port", "ipaddr", "proto", "desc"]:
                    value = result.get(f"vts_{key}_x{i}")
                    if value:
                        rule[key] = value
                if rule:
                    rules.append(rule)
            return rules
        return []
    
    def add_port_forwarding_rule(self, 
                                 external_port: int,
                                 internal_ip: str,
                                 internal_port: int = None,
                                 protocol: str = "TCP",
                                 description: str = "") -> bool:
        """
        添加端口轉發規則
        
        Args:
            external_port: 外部端口
            internal_ip: 內部 IP
            internal_port: 內部端口（如果為 None，則與外部端口相同）
            protocol: 協議 (TCP/UDP/BOTH)
            description: 描述
        """
        if internal_port is None:
            internal_port = external_port
        
        # 找到第一個可用的規則索引
        existing_rules = self.get_port_forwarding_rules()
        rule_index = len(existing_rules)
        
        data = {
            f"vts_enable_x{rule_index}": "1",
            f"vts_port_x{rule_index}": str(external_port),
            f"vts_ipaddr_x{rule_index}": internal_ip,
            f"vts_port_local_x{rule_index}": str(internal_port),
            f"vts_proto_x{rule_index}": protocol.upper(),
            f"vts_desc_x{rule_index}": description or f"Port {external_port} -> {internal_ip}:{internal_port}"
        }
        
        return self._app_set("apply", "restart_firewall", data)
    
    def remove_port_forwarding_rule(self, rule_index: int) -> bool:
        """移除端口轉發規則"""
        data = {
            f"vts_enable_x{rule_index}": "0"
        }
        return self._app_set("apply", "restart_firewall", data)
    
    # ========== 防火牆控制 ==========
    
    def get_firewall_rules(self) -> List[Dict[str, Any]]:
        """獲取防火牆規則"""
        result = self._app_get("get_firewall_rules()")
        if isinstance(result, dict):
            # 解析防火牆規則
            rules = []
            for i in range(50):  # 通常最多 50 條規則
                rule = {}
                for key in ["enable", "name", "src_ip", "dst_ip", "port", "proto", "action"]:
                    value = result.get(f"filter_{key}_{i}")
                    if value:
                        rule[key] = value
                if rule:
                    rules.append(rule)
            return rules
        return []
    
    def add_firewall_rule(self,
                         name: str,
                         src_ip: str = "",
                         dst_ip: str = "",
                         port: str = "",
                         protocol: str = "TCP",
                         action: str = "ACCEPT") -> bool:
        """
        添加防火牆規則
        
        Args:
            name: 規則名稱
            src_ip: 來源 IP（空字串表示所有）
            dst_ip: 目標 IP（空字串表示所有）
            port: 端口（空字串表示所有）
            protocol: 協議 (TCP/UDP/ICMP/ALL)
            action: 動作 (ACCEPT/DROP/REJECT)
        """
        existing_rules = self.get_firewall_rules()
        rule_index = len(existing_rules)
        
        data = {
            f"filter_enable_{rule_index}": "1",
            f"filter_name_{rule_index}": name,
            f"filter_src_ip_{rule_index}": src_ip,
            f"filter_dst_ip_{rule_index}": dst_ip,
            f"filter_port_{rule_index}": port,
            f"filter_proto_{rule_index}": protocol.upper(),
            f"filter_action_{rule_index}": action.upper()
        }
        
        return self._app_set("apply", "restart_firewall", data)
    
    # ========== 無線網路控制 ==========
    
    def get_wireless_settings(self, band: str = "2.4G") -> Dict[str, Any]:
        """獲取無線網路設定"""
        hook_map = {
            "2.4G": "get_wireless_2g_settings()",
            "5G": "get_wireless_5g_settings()",
            "6G": "get_wireless_6g_settings()"
        }
        hook = hook_map.get(band, hook_map["2.4G"])
        result = self._app_get(hook)
        return {
            "band": band,
            "settings": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def set_wireless_ssid(self, band: str, ssid: str, password: str = "") -> bool:
        """設定無線網路 SSID 和密碼"""
        data = {}
        if band == "2.4G":
            data["wl_ssid"] = ssid
            if password:
                data["wl_wpa_psk"] = password
        elif band == "5G":
            data["wl1_ssid"] = ssid
            if password:
                data["wl1_wpa_psk"] = password
        elif band == "6G":
            data["wl2_ssid"] = ssid
            if password:
                data["wl2_wpa_psk"] = password
        
        return self._app_set("apply", "restart_wireless", data)
    
    # ========== 訪客網路控制 ==========
    
    def get_guest_network_status(self) -> Dict[str, Any]:
        """獲取訪客網路狀態"""
        result = self._app_get("get_guest_network_status()")
        return {
            "status": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def enable_guest_network(self, band: str, ssid: str, password: str, duration_hours: int = 24) -> bool:
        """啟用訪客網路"""
        data = {}
        if band == "2.4G":
            data["wl_guest_enable"] = "1"
            data["wl_guest_ssid"] = ssid
            data["wl_guest_wpa_psk"] = password
        elif band == "5G":
            data["wl1_guest_enable"] = "1"
            data["wl1_guest_ssid"] = ssid
            data["wl1_guest_wpa_psk"] = password
        
        # 設定時限（如果路由器支援）
        if duration_hours > 0:
            data["wl_guest_time"] = str(duration_hours)
        
        return self._app_set("apply", "restart_wireless", data)
    
    # ========== 物業管理專用功能 ==========
    
    def setup_property_management_network(self, 
                                         property_id: str,
                                         internal_ip_range: str = "192.168.50.0/24",
                                         guest_network: bool = True) -> Dict[str, Any]:
        """
        為物業管理模組設定網路環境
        
        Args:
            property_id: 物業 ID
            internal_ip_range: 內部 IP 範圍
            guest_network: 是否啟用訪客網路
        """
        result = {
            "property_id": property_id,
            "setup_time": datetime.now().isoformat(),
            "steps": [],
            "success": True
        }
        
        # 1. 設定端口轉發（物業管理系統常用端口）
        ports = [
            (8069, "Odoo ERP"),
            (5000, "Control Center"),
            (8788, "Local Control Center"),
            (65433, "SSH Custom")
        ]
        
        for port, desc in ports:
            if self.add_port_forwarding_rule(
                external_port=port,
                internal_ip="192.168.50.84",  # 預設內部 IP
                description=f"{property_id}-{desc}"
            ):
                result["steps"].append(f"端口轉發 {port} 設定成功")
            else:
                result["steps"].append(f"端口轉發 {port} 設定失敗")
                result["success"] = False
        
        # 2. 設定訪客網路（如果啟用）
        if guest_network:
            guest_ssid = f"Wuchang-{property_id}-Guest"
            guest_password = f"Guest{property_id[:4]}"
            if self.enable_guest_network("5G", guest_ssid, guest_password, 24):
                result["steps"].append("訪客網路設定成功")
            else:
                result["steps"].append("訪客網路設定失敗")
        
        return result
    
    def get_property_network_status(self, property_id: str) -> Dict[str, Any]:
        """獲取物業網路狀態"""
        devices = self.get_connected_devices()
        port_rules = self.get_port_forwarding_rules()
        firewall_rules = self.get_firewall_rules()
        ddns_status = self.get_ddns_status()
        
        # 過濾與該物業相關的規則
        property_rules = [
            rule for rule in port_rules 
            if property_id in rule.get("desc", "")
        ]
        
        return {
            "property_id": property_id,
            "connected_devices": devices.get("total_count", 0),
            "port_forwarding_rules": len(property_rules),
            "firewall_rules": len(firewall_rules),
            "ddns_status": ddns_status,
            "external_ip": "220.135.21.74",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_connected_devices(self) -> Dict[str, Any]:
        """獲取連線裝置（從 router_integration 借用邏輯）"""
        try:
            from router_integration import RouterIntegration
            router = RouterIntegration(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password
            )
            if not router.logged_in:
                router.login()
            return router.get_connected_devices()
        except:
            return {"total_count": 0, "devices": []}
    
    # ========== 系統控制 ==========
    
    def reboot(self) -> bool:
        """重啟路由器"""
        return self._app_set("reboot", "")
    
    def get_system_info(self) -> Dict[str, Any]:
        """獲取系統資訊"""
        result = self._app_get("get_system_info()")
        return {
            "info": result,
            "router_model": "ASUS RT-BE86U",
            "hostname": self.hostname,
            "external_ip": "220.135.21.74",
            "ddns": "coffeeLofe.asuscomm.com",
            "timestamp": datetime.now().isoformat()
        }
    
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


# 單例實例
_router_full_control_instance = None

def get_router_full_control() -> RouterFullControl:
    """獲取路由器完整控制實例（單例模式）"""
    global _router_full_control_instance
    if _router_full_control_instance is None:
        _router_full_control_instance = RouterFullControl()
        if _router_full_control_instance.username and _router_full_control_instance.password:
            _router_full_control_instance.login()
    return _router_full_control_instance


if __name__ == "__main__":
    # 測試
    router = RouterFullControl()
    if router.login():
        print("登錄成功")
        print("\n系統資訊:")
        print(json.dumps(router.get_system_info(), ensure_ascii=False, indent=2))
        print("\nDDNS 狀態:")
        print(json.dumps(router.get_ddns_status(), ensure_ascii=False, indent=2))
    else:
        print("登錄失敗")
