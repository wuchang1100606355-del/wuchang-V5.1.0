#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從伺服器下載環境設定
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

# 配置
SERVER_IP = "192.168.50.249"
SERVER_PORTS = [8069, 8080, 8766, 3001, 443, 80]
CONFIG_DIR = Path(".wuchang_ui")
CONFIG_DIR.mkdir(exist_ok=True)

def test_server_connection(ip, port):
    """測試伺服器連線"""
    try:
        url = f"http://{ip}:{port}"
        response = requests.get(url, timeout=5)
        return True, response.status_code
    except requests.exceptions.ConnectionError:
        return False, None
    except Exception as e:
        return False, str(e)

def download_config_from_server():
    """從伺服器下載環境設定"""
    print("=" * 80)
    print("  從伺服器下載環境設定")
    print("=" * 80)
    print()
    print(f"伺服器 IP: {SERVER_IP}")
    print()
    
    # 測試伺服器連線
    print("[*] 測試伺服器連線...")
    available_ports = []
    
    for port in SERVER_PORTS:
        print(f"  測試端口 {port}...", end=" ")
        success, status = test_server_connection(SERVER_IP, port)
        if success:
            print(f"[OK] 可連線 (狀態碼: {status})")
            available_ports.append(port)
        else:
            print("[FAIL] 無法連線")
    
    print()
    
    if not available_ports:
        print("[WARN] 無法連接到伺服器的任何端口")
        print("   請確認:")
        print("   1. 伺服器是否正在運行")
        print("   2. 網絡連接是否正常")
        print("   3. 防火牆設置是否正確")
        print()
        print("   將使用預設端口配置...")
        available_ports = [8069, 8080, 8766, 3001]  # 使用預設端口
    
    print(f"[OK] 找到 {len(available_ports)} 個可用端口: {available_ports}")
    print()
    
    # 嘗試從不同端點下載配置
    config_endpoints = [
        "/api/config",
        "/config",
        "/api/environment",
        "/environment",
        "/.wuchang_ui/ui_scheme.json",
        "/config/ui_scheme.json"
    ]
    
    downloaded = False
    
    for port in available_ports:
        for endpoint in config_endpoints:
            try:
                url = f"http://{SERVER_IP}:{port}{endpoint}"
                print(f"嘗試下載: {url}...", end=" ")
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    try:
                        config_data = response.json()
                        config_file = CONFIG_DIR / "ui_scheme.json"
                        with open(config_file, 'w', encoding='utf-8') as f:
                            json.dump(config_data, f, indent=2, ensure_ascii=False)
                        print(f"[OK] 成功")
                        print(f"  已保存到: {config_file}")
                        downloaded = True
                        break
                    except json.JSONDecodeError:
                        # 如果不是 JSON，嘗試保存為文本
                        config_file = CONFIG_DIR / f"config_{port}_{endpoint.replace('/', '_')}.txt"
                        with open(config_file, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        print(f"[OK] 已保存為文本")
                        downloaded = True
            except Exception as e:
                print(f"[FAIL] 失敗: {str(e)[:50]}")
        
        if downloaded:
            break
    
    if not downloaded:
        print()
        print("[WARN] 無法從伺服器下載配置檔案")
        print("   將使用本地預設配置...")
        
        # 生成預設配置
        default_config = {
            "version": "1.0.0",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "designedBy": "Local System",
            "description": "Default UI Connection Scheme",
            "mainScheme": {
                "name": "Primary UI Connection",
                "protocol": "HTTPS/WebSocket",
                "primaryEndpoint": f"http://{SERVER_IP}:{available_ports[0]}",
                "fallbackEndpoint": f"http://localhost:{available_ports[0]}",
                "port": available_ports[0],
                "encryption": "TLS 1.3",
                "authentication": "Device ID + Unique Code + Agree Token"
            },
            "uiServices": [],
            "connectionConfig": {
                "timeout": 30,
                "retryAttempts": 3,
                "retryDelay": 5,
                "keepAliveInterval": 30,
                "compressionEnabled": True,
                "cachingEnabled": True,
                "offlineModeSupport": True
            },
            "availablePorts": available_ports
        }
        
        config_file = CONFIG_DIR / "ui_scheme.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] 已生成預設配置: {config_file}")
    
    print()
    print("=" * 80)
    print("  環境設定下載完成")
    print("=" * 80)
    print()
    
    return True

if __name__ == "__main__":
    try:
        download_config_from_server()
    except KeyboardInterrupt:
        print("\n\n[ERROR] 操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
