#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列出路由器上的連接設備（名稱和 IP）
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
    print("路由器連接設備列表")
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
    
    total_count = devices_info.get("total_count", 0)
    devices = devices_info.get("devices", [])
    
    print(f"\n連接設備總數: {total_count}")
    print()
    
    if total_count == 0:
        print("⚠️  未找到連接設備")
        print("\n可能原因：")
        print("  1. 路由器登入失敗")
        print("  2. API 端點不正確")
        print("  3. 路由器不支援此功能")
        print("\n建議：")
        print("  1. 檢查路由器認證資訊")
        print("  2. 直接在路由器 Web 介面查看設備列表")
        return
    
    # 顯示設備列表
    print("設備列表：")
    print("=" * 60)
    print(f"{'序號':<6} {'設備名稱':<30} {'IP 地址':<18} {'MAC 地址':<18} {'類型':<10}")
    print("-" * 60)
    
    for idx, device in enumerate(devices, 1):
        name = device.get("name", device.get("hostname", "未知"))
        ip = device.get("ip", "未知")
        mac = device.get("mac", "未知")
        device_type = device.get("type", "未知")
        
        print(f"{idx:<6} {name:<30} {ip:<18} {mac:<18} {device_type:<10}")
    
    print("=" * 60)
    
    # 尋找伺服器（可能有兩個 IP）
    print("\n伺服器設備（可能有多個 IP）：")
    print("-" * 60)
    
    server_devices = []
    for device in devices:
        ip = device.get("ip", "")
        name = device.get("name", device.get("hostname", ""))
        
        # 檢查是否為伺服器（IP 在 192.168.50.x 網段）
        if ip.startswith("192.168.50."):
            server_devices.append({
                "name": name,
                "ip": ip,
                "mac": device.get("mac", ""),
                "type": device.get("type", "")
            })
    
    if server_devices:
        for idx, server in enumerate(server_devices, 1):
            print(f"身份 {idx}:")
            print(f"  名稱: {server['name']}")
            print(f"  IP: {server['ip']}")
            print(f"  MAC: {server['mac']}")
            print(f"  類型: {server['type']}")
            print()
    else:
        print("⚠️  未找到伺服器設備（192.168.50.x）")
        print("\n已知伺服器 IP: 192.168.50.249")
        print("請確認設備列表中是否有此 IP")
    
    # 儲存結果到檔案
    output_file = Path("router_devices_list.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(devices_info, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 設備列表已儲存到: {output_file}")
    
    # 如果有伺服器設備，更新配置建議
    if len(server_devices) >= 2:
        print("\n" + "=" * 60)
        print("雙身份配置建議")
        print("=" * 60)
        print("\n發現兩個伺服器身份：")
        for idx, server in enumerate(server_devices, 1):
            print(f"\n身份 {idx}:")
            print(f"  名稱: {server['name']}")
            print(f"  IP: {server['ip']}")
        
        print("\n建議配置：")
        print("  1. 確認每個服務使用哪個身份")
        print("  2. 更新 cloudflared/config.yml")
        print("  3. 根據服務分配更新 ingress 規則")


if __name__ == "__main__":
    main()
