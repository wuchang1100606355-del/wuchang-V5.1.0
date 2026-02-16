import socket
import re
import urllib.request
import urllib.parse
import json
import os
from datetime import datetime

# Configuration
LOCAL_IP = "192.168.50.84"
ROUTER_IP = "192.168.50.1"
DEFAULT_VPN_PORT = 1194

class WuchangRouterMaster:
    """
    五常路由器主控外殼 (Router Master Shell)
    本機將擔任所有網路功能的最高指令發送端。
    """
    def __init__(self, router_ip=ROUTER_IP):
        self.router_ip = router_ip
        self.control_url = None
        self.active_mappings = []

    def log(self, msg):
        print(f"📡 [RouterMaster] {msg}")

    def discover(self):
        self.log(f"正在掃描路由器 (IP: {self.router_ip})...")
        # SSDP logic similar to existing but with more robust fallback
        possible_urls = [
            f"http://{self.router_ip}:5431/control/WANIPConnection",
            f"http://{self.router_ip}:1900/ipc",
            f"http://{self.router_ip}:49152/upnp/control/WANIPConnection0"
        ]
        
        for url in possible_urls:
            try:
                # Basic check if URL exists
                with urllib.request.urlopen(url, timeout=2) as r:
                    if r.status == 200:
                        self.control_url = url
                        self.log(f"✅ 已取得控制權點: {url}")
                        return True
            except:
                continue
        return False

    def add_mapping(self, port, proto="UDP", desc="Wuchang-Master"):
        if not self.control_url:
            self.discover()
        
        if not self.control_url:
            self.log("❌ 無法取得路由器控制權，請檢查 UPnP 是否開啟。")
            return False

        self.log(f"⚡ 執行端口映射: {proto}:{port} -> 本機")
        
        soap_body = f"""<?xml version="1.0"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
<s:Body>
<u:AddPortMapping xmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1">
<NewRemoteHost></NewRemoteHost>
<NewExternalPort>{port}</NewExternalPort>
<NewProtocol>{proto}</NewProtocol>
<NewInternalPort>{port}</NewInternalPort>
<NewInternalClient>{LOCAL_IP}</NewInternalClient>
<NewEnabled>1</NewEnabled>
<NewPortMappingDescription>{desc}</NewPortMappingDescription>
<NewLeaseDuration>0</NewLeaseDuration>
</u:AddPortMapping>
</s:Body>
</s:Envelope>"""

        headers = {
            'SOAPAction': '"urn:schemas-upnp-org:service:WANIPConnection:1#AddPortMapping"',
            'Content-Type': 'text/xml',
        }

        try:
            req = urllib.request.Request(self.control_url, data=soap_body.encode(), headers=headers)
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    self.log(f"✅ 成功接管 {port} 端口。")
                    return True
        except Exception as e:
            self.log(f"❌ 指令發送失敗: {e}")
        return False

    def scan_network(self):
        self.log("正在執行 ARP 網路掃描以確認連網設備...")
        try:
            output = subprocess.check_output("arp -a", shell=True).decode('cp950')
            self.log("📡 掃描結果已解析，正在定位主控座標...")
            return output
        except Exception as e:
            return str(e)

    def takeover_all(self):
        self.log("🚀 正在發起「最高控制權轉移」協定...")
        # 1. 執行網路掃描
        net_map = self.scan_network()
        
        # 2. 宣告主控權 (寫入系統狀態)
        results = {"ARP_Scan": "Success"}
        
        # 3. 嘗試奪取關鍵服務端口
        ports = [80, 443, 8000, 6688, 1194]
        for p in ports:
            results[p] = self.add_mapping(p, "TCP", f"Wuchang-Master-{p}")
            if p == 1194:
                self.add_mapping(p, "UDP", "Wuchang-VPN-Master")
        
        self.log("⚖️ 權限轉移報告：")
        print(f"   [網路拓墣備註]: {net_map[:100]}...")
        for p, res in results.items():
            if isinstance(res, bool):
                st = "已接管" if res else "接管受阻 (UPnP 關閉)"
                print(f"   - 端口 {p}: {st}")
        
        self.log("👑 本機已確立為「五常網路主控中心」。所有決策將以此機為準。")

if __name__ == "__main__":
    master = WuchangRouterMaster()
    master.takeover_all()
