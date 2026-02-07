"""
物業管理模組與路由器整合
提供物業管理系統所需的網路基礎設施控制介面
"""

from router_full_control import RouterFullControl, get_router_full_control
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class PropertyManagementRouterIntegration:
    """物業管理路由器整合類別"""
    
    def __init__(self, property_id: str = "wuchang_community"):
        """
        初始化物業管理路由器整合
        
        Args:
            property_id: 物業 ID
        """
        self.property_id = property_id
        self.router = get_router_full_control()
    
    def initialize_network_infrastructure(self) -> Dict[str, Any]:
        """
        初始化物業管理網路基礎設施
        
        包括：
        - 端口轉發設定
        - 訪客網路設定
        - 防火牆規則
        - DNS/DDNS 設定
        """
        result = {
            "property_id": self.property_id,
            "initialization_time": datetime.now().isoformat(),
            "steps": [],
            "success": True
        }
        
        # 1. 設定物業管理系統端口轉發
        setup_result = self.router.setup_property_management_network(
            property_id=self.property_id,
            guest_network=True
        )
        result["steps"].extend(setup_result.get("steps", []))
        if not setup_result.get("success"):
            result["success"] = False
        
        # 2. 驗證設定
        status = self.router.get_property_network_status(self.property_id)
        result["network_status"] = status
        
        return result
    
    def get_network_dashboard(self) -> Dict[str, Any]:
        """獲取網路儀表板資料（供 UI 顯示）"""
        devices = self.router.get_connected_devices()
        status = self.router.get_property_network_status(self.property_id)
        system_info = self.router.get_system_info()
        ddns_status = self.router.get_ddns_status()
        
        return {
            "property_id": self.property_id,
            "connected_devices": {
                "total": devices.get("total_count", 0),
                "list": devices.get("devices", [])
            },
            "network_status": status,
            "system_info": system_info,
            "ddns": ddns_status,
            "timestamp": datetime.now().isoformat()
        }
    
    def add_device_port_forward(self, 
                               device_name: str,
                               device_ip: str,
                               external_port: int,
                               internal_port: int = None,
                               description: str = "") -> bool:
        """
        為物業管理設備添加端口轉發
        
        Args:
            device_name: 設備名稱
            device_ip: 設備 IP
            external_port: 外部端口
            internal_port: 內部端口
            description: 描述
        """
        if not description:
            description = f"{self.property_id}-{device_name}"
        
        return self.router.add_port_forwarding_rule(
            external_port=external_port,
            internal_ip=device_ip,
            internal_port=internal_port,
            description=description
        )
    
    def get_device_network_info(self, device_mac: str) -> Optional[Dict[str, Any]]:
        """
        獲取設備網路資訊
        
        Args:
            device_mac: 設備 MAC 地址
        """
        devices = self.router.get_connected_devices()
        for device in devices.get("devices", []):
            if device.get("mac", "").upper() == device_mac.upper():
                return {
                    "device": device,
                    "property_id": self.property_id,
                    "timestamp": datetime.now().isoformat()
                }
        return None
    
    def setup_guest_network_for_event(self, 
                                      event_name: str,
                                      duration_hours: int = 24,
                                      password: str = None) -> Dict[str, Any]:
        """
        為物業活動設定臨時訪客網路
        
        Args:
            event_name: 活動名稱
            duration_hours: 持續時間（小時）
            password: 密碼（如果為 None，則自動生成）
        """
        if not password:
            # 自動生成密碼
            import random
            import string
            password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        ssid = f"{self.property_id}-{event_name}"
        
        success = self.router.enable_guest_network(
            band="5G",
            ssid=ssid,
            password=password,
            duration_hours=duration_hours
        )
        
        return {
            "event_name": event_name,
            "ssid": ssid,
            "password": password,
            "duration_hours": duration_hours,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_network_usage_report(self, days: int = 7) -> Dict[str, Any]:
        """
        獲取網路使用報告
        
        Args:
            days: 報告天數
        """
        # 這裡可以整合流量監控資料
        devices = self.router.get_connected_devices()
        port_rules = self.router.get_port_forwarding_rules()
        
        return {
            "property_id": self.property_id,
            "report_period_days": days,
            "connected_devices_count": devices.get("total_count", 0),
            "active_port_forwarding_rules": len(port_rules),
            "timestamp": datetime.now().isoformat()
        }


# 物業管理專用路由器控制實例
_property_router_integration = None

def get_property_router_integration(property_id: str = "wuchang_community") -> PropertyManagementRouterIntegration:
    """獲取物業管理路由器整合實例"""
    global _property_router_integration
    if _property_router_integration is None or _property_router_integration.property_id != property_id:
        _property_router_integration = PropertyManagementRouterIntegration(property_id)
    return _property_router_integration


if __name__ == "__main__":
    # 測試
    integration = get_property_router_integration("wuchang_community")
    
    print("物業管理路由器整合測試")
    print("=" * 60)
    
    # 獲取網路儀表板
    dashboard = integration.get_network_dashboard()
    print("\n網路儀表板:")
    print(json.dumps(dashboard, ensure_ascii=False, indent=2))
    
    # 獲取網路使用報告
    report = integration.get_network_usage_report(days=7)
    print("\n網路使用報告:")
    print(json.dumps(report, ensure_ascii=False, indent=2))
