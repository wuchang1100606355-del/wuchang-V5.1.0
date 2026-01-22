#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查詢 SERVER 2 IP 地址

使用地端小J的權限查詢路由器設備列表，找出 SERVER 2 的 IP 地址
"""

import sys
import json
from pathlib import Path

# 設定 UTF-8 編碼
if sys.platform == 'win32':
    try:
        import io
        if not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        if not isinstance(sys.stderr, io.TextIOWrapper):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

try:
    from router_integration import RouterIntegration
    ROUTER_AVAILABLE = True
except ImportError:
    ROUTER_AVAILABLE = False
    print("❌ router_integration 模組未找到")

def main():
    """主函數"""
    print("=" * 60)
    print("查詢 SERVER 2 IP 地址")
    print("=" * 60)
    print()
    
    if not ROUTER_AVAILABLE:
        print("❌ 無法載入路由器模組")
        return
    
    # 建立路由器連接
    router = RouterIntegration(hostname="192.168.50.84", port=8443)
    
    # 檢查認證資訊
    if not router.username or not router.password:
        print("⚠️  路由器認證資訊未設定")
        print("\n請設定認證資訊：")
        print("  1. 環境變數：ROUTER_USERNAME 和 ROUTER_PASSWORD")
        print("  2. 或建立 router_config.json 檔案")
        print()
        
        # 嘗試從用戶輸入獲取
        try:
            username = input("請輸入路由器用戶名（直接按 Enter 跳過）: ").strip()
            if username:
                password = input("請輸入路由器密碼: ").strip()
                router.username = username
                router.password = password
            else:
                print("跳過登入，嘗試直接查詢...")
        except (EOFError, KeyboardInterrupt):
            print("\n操作已取消")
            return
    
    # 嘗試登入
    if router.username and router.password:
        print("正在登入路由器...")
        if router.login():
            print("✅ 路由器登入成功")
        else:
            print("❌ 路由器登入失敗")
            print("  將嘗試直接查詢（可能無法取得完整資訊）")
    else:
        print("⚠️  未提供認證資訊，嘗試直接查詢...")
    
    print()
    print("正在查詢連接設備...")
    print("-" * 60)
    
    # 獲取設備列表
    devices_info = router.get_connected_devices()
    
    # 顯示結果
    if devices_info.get("error"):
        print(f"❌ 查詢錯誤: {devices_info['error']}")
        return
    
    devices = devices_info.get("devices", [])
    
    # 尋找 SERVER 2
    print("\n正在尋找 SERVER 2...")
    print("-" * 60)
    
    server2_devices = []
    for device in devices:
        name = device.get("name", device.get("hostname", "")).lower()
        ip = device.get("ip", "")
        mac = device.get("mac", "")
        
        # 檢查是否為 SERVER 2（支援多種變體）
        if ("server 2" in name or "server2" in name or 
            "svrver 2" in name or "svrver2" in name or
            mac == "1C:3E:84:67:C0:16"):
            server2_devices.append({
                "name": device.get("name", device.get("hostname", "")),
                "ip": ip,
                "mac": mac,
                "type": device.get("type", ""),
                "ipv6": device.get("ipv6", "")
            })
    
    if server2_devices:
        print(f"\n✅ 找到 {len(server2_devices)} 個 SERVER 2 設備：")
        print()
        for idx, server2 in enumerate(server2_devices, 1):
            print(f"設備 {idx}:")
            print(f"  名稱: {server2['name']}")
            print(f"  IPv4: {server2['ip'] if server2['ip'] else '❌ 未找到（待確認）'}")
            print(f"  IPv6: {server2['ipv6'] if server2.get('ipv6') else '❌ 未找到'}")
            print(f"  MAC: {server2['mac']}")
            print(f"  類型: {server2['type']}")
            print()
        
        # 儲存結果
        output_file = Path("server2_ip_info.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "query_time": __import__('datetime').datetime.now().isoformat(),
                "server2_devices": server2_devices,
                "total_found": len(server2_devices)
            }, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 結果已儲存到: {output_file}")
        
        # 如果有 IPv4，顯示建議
        for server2 in server2_devices:
            if server2['ip']:
                print(f"\n📋 SERVER 2 IPv4 地址：{server2['ip']}")
                print("\n建議更新以下檔案：")
                print("  - jules_memory_bank.json")
                print("  - little_j_permanent_permissions.json")
                print("  - cloudflared/config.yml（如果需要）")
    else:
        print("❌ 未找到 SERVER 2 設備")
        print("\n可能原因：")
        print("  1. 設備名稱不是 'server 2' 或 'svrver 2'")
        print("  2. MAC 地址不是 '1C:3E:84:67:C0:16'")
        print("  3. 設備未連接到路由器")
        print("  4. 路由器登入失敗，無法取得完整資訊")
        print("\n已知資訊：")
        print("  - 名稱：server 2（或 svrver 2）")
        print("  - MAC：1C:3E:84:67:C0:16")
        print("  - IPv6：fe80::cdf9:2266:dc55:bcc6")
        print("  - IPv4：待確認")
        print("\n建議：")
        print("  1. 在路由器 Web 介面查看設備列表")
        print("  2. 在伺服器上執行 'ip addr show' 查看 WiFi 網卡 IP")
        print("  3. 檢查設備是否正確連接到路由器")


if __name__ == "__main__":
    main()
