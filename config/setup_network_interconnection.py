#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_network_interconnection.py

兩機區網互通設定工具

功能：
- 自動檢測網路配置
- 設定兩機之間的連接
- 配置環境變數
- 測試連接
- 授予最高權限執行
"""

import sys
import json
import os
import socket
import subprocess
import platform
from pathlib import Path
from typing import Dict, Any, List, Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def get_local_ip() -> Optional[str]:
    """獲取本機 IP 地址"""
    try:
        # 連接到外部地址以獲取本機 IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return None


def get_network_info() -> Dict[str, Any]:
    """獲取網路資訊"""
    info = {
        "local_ip": get_local_ip(),
        "hostname": socket.gethostname(),
        "platform": platform.system(),
    }
    
    # 獲取網路介面資訊（Windows）
    if platform.system() == "Windows":
        try:
            result = subprocess.run(
                ["ipconfig"],
                capture_output=True,
                text=True,
                timeout=5
            )
            info["ipconfig"] = result.stdout
        except:
            pass
    
    # 檢查 VPN 連接
    info["vpn_connected"] = check_vpn_connection()
    
    return info


def check_vpn_connection() -> bool:
    """檢查 VPN 連接狀態"""
    try:
        if platform.system() == "Windows":
            # 檢查 OpenVPN 適配器
            result = subprocess.run(
                ["ipconfig"],
                capture_output=True,
                text=True,
                timeout=5
            )
            output = result.stdout.lower()
            # 檢查常見的 VPN 關鍵字
            vpn_keywords = ["tap", "tun", "openvpn", "vpn", "pptp", "l2tp"]
            return any(keyword in output for keyword in vpn_keywords)
    except:
        pass
    return False


def resolve_ddns(hostname: str) -> Optional[str]:
    """解析 DDNS 主機名到 IP 地址"""
    try:
        ip = socket.gethostbyname(hostname)
        return ip
    except:
        return None


def test_ddns_connection(hostname: str, port: int = 8443) -> Dict[str, Any]:
    """測試 DDNS 連接"""
    print(f"解析 DDNS: {hostname}...")
    ip = resolve_ddns(hostname)
    
    if not ip:
        return {
            "success": False,
            "hostname": hostname,
            "error": "無法解析 DDNS 主機名"
        }
    
    print(f"  → 解析到 IP: {ip}")
    
    # 測試連接
    conn_test = test_connection(ip, port=port, timeout=5)
    return {
        "success": conn_test.get("reachable", False),
        "hostname": hostname,
        "resolved_ip": ip,
        "port": port,
        "reachable": conn_test.get("reachable", False)
    }


def test_connection(host: str, port: int = 80, timeout: float = 3.0) -> Dict[str, Any]:
    """測試連接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return {
            "success": result == 0,
            "host": host,
            "port": port,
            "reachable": result == 0
        }
    except Exception as e:
        return {
            "success": False,
            "host": host,
            "port": port,
            "error": str(e),
            "reachable": False
        }


def test_smb_connection(share_path: str) -> Dict[str, Any]:
    """測試 SMB 共享連接"""
    try:
        path = Path(share_path)
        if path.exists():
            # 嘗試列出目錄
            try:
                files = list(path.iterdir())
                return {
                    "success": True,
                    "path": share_path,
                    "accessible": True,
                    "file_count": len(files)
                }
            except Exception as e:
                return {
                    "success": False,
                    "path": share_path,
                    "accessible": False,
                    "error": str(e)
                }
        else:
            return {
                "success": False,
                "path": share_path,
                "accessible": False,
                "error": "路徑不存在"
            }
    except Exception as e:
        return {
            "success": False,
            "path": share_path,
            "accessible": False,
            "error": str(e)
        }


def setup_environment_variables(config: Dict[str, Any]) -> bool:
    """設定環境變數"""
    try:
        # 設定當前會話的環境變數
        for key, value in config.items():
            if value:
                os.environ[key] = str(value)
        
        # 如果是 Windows，嘗試永久設定
        if platform.system() == "Windows":
            try:
                import winreg
                for key, value in config.items():
                    if value:
                        reg_key = winreg.OpenKey(
                            winreg.HKEY_CURRENT_USER,
                            "Environment",
                            0,
                            winreg.KEY_SET_VALUE
                        )
                        winreg.SetValueEx(reg_key, key, 0, winreg.REG_EXPAND_SZ, str(value))
                        winreg.CloseKey(reg_key)
            except Exception as e:
                print(f"警告：無法永久設定環境變數: {e}")
        
        return True
    except Exception as e:
        print(f"設定環境變數失敗: {e}")
        return False


def auto_authorize_and_setup():
    """自動授權並執行設定"""
    print("=" * 70)
    print("兩機區網互通設定（自動授權模式）")
    print("=" * 70)
    print()
    
    # 檢查控制中心
    try:
        import requests
        response = requests.get("http://127.0.0.1:8788/api/local/health", timeout=2)
        if response.status_code != 200:
            print("⚠️  控制中心未運行，將跳過授權步驟")
            control_center_available = False
        else:
            control_center_available = True
    except:
        control_center_available = False
        print("⚠️  控制中心未運行，將跳過授權步驟")
    
    # 獲取網路資訊
    print("【步驟 1：檢測網路配置】")
    network_info = get_network_info()
    print(f"  本機 IP: {network_info.get('local_ip', '未知')}")
    print(f"  主機名稱: {network_info.get('hostname', '未知')}")
    print()
    
    # 讀取配置
    config_file = BASE_DIR / "network_interconnection_config.json"
    if config_file.exists():
        print("【步驟 2：載入網路配置】")
        try:
            config = json.loads(config_file.read_text(encoding="utf-8"))
            print("✓ 已載入配置檔案")
        except Exception as e:
            config = {}
            print(f"✗ 配置檔案格式錯誤: {e}，將使用環境變數或預設值")
    else:
        config = {}
        print("【步驟 2：網路配置設定】")
        print("未找到配置檔案，將從環境變數讀取或使用預設值")
        print("提示：建立 network_interconnection_config.json 以自動配置")
    
    # 設定伺服器資訊（優先順序：配置檔案 > 環境變數 > 預設值）
    # 支援 DDNS 或 IP 地址
    server_ddns = config.get("server_ddns") or os.getenv("WUCHANG_SERVER_DDNS", "")
    server_ip = (
        config.get("server_ip") or 
        os.getenv("WUCHANG_SERVER_IP", "") or
        network_info.get("local_ip", "")
    )
    
    # 如果提供了 DDNS，解析為 IP
    if server_ddns:
        print(f"解析 DDNS: {server_ddns}...")
        resolved_ip = resolve_ddns(server_ddns)
        if resolved_ip:
            server_ip = resolved_ip
            print(f"  → 解析到 IP: {resolved_ip}")
        else:
            print(f"  ⚠️  無法解析 DDNS，將使用配置的 IP")
    
    server_share = (
        config.get("server_share") or 
        os.getenv("WUCHANG_COPY_TO", "")
    )
    
    health_url = (
        config.get("health_url") or 
        os.getenv("WUCHANG_HEALTH_URL", "")
    )
    
    hub_url = (
        config.get("hub_url") or 
        os.getenv("WUCHANG_HUB_URL", "")
    )
    
    hub_token = (
        config.get("hub_token") or 
        os.getenv("WUCHANG_HUB_TOKEN", "")
    )
    
    # OpenVPN 配置
    vpn_config = config.get("vpn", {})
    vpn_enabled = vpn_config.get("enabled", False) or os.getenv("WUCHANG_VPN_ENABLED", "").lower() == "true"
    vpn_server = vpn_config.get("server") or os.getenv("WUCHANG_VPN_SERVER", "")
    
    print(f"  連接方式: {'DDNS' if server_ddns else 'IP 地址' if server_ip else '未設定'}")
    if server_ddns:
        print(f"  DDNS: {server_ddns}")
    print(f"  伺服器 IP: {server_ip or '(未設定)'}")
    print(f"  伺服器共享: {server_share or '(未設定)'}")
    print(f"  健康檢查 URL: {health_url or '(未設定)'}")
    print(f"  Hub URL: {hub_url or '(未設定)'}")
    if vpn_enabled:
        print(f"  VPN: 已啟用 ({vpn_server or '未設定伺服器'})")
    else:
        print(f"  VPN: 未啟用")
    
    print()
    
    # 測試連接
    print("【步驟 3：測試連接】")
    
    # 測試 DDNS（如果提供）
    if server_ddns:
        ddns_test = test_ddns_connection(server_ddns, port=8443)
        if ddns_test.get("success"):
            print(f"✓ DDNS {server_ddns} 可達 (IP: {ddns_test.get('resolved_ip')})")
        else:
            print(f"✗ DDNS {server_ddns} 不可達: {ddns_test.get('error', '未知錯誤')}")
    
    # 測試 IP 連接
    if server_ip:
        print(f"測試連接到 {server_ip}...")
        conn_test = test_connection(server_ip, port=80, timeout=3)
        if conn_test.get("reachable"):
            print(f"✓ {server_ip} 可達")
        else:
            print(f"✗ {server_ip} 不可達（可能正常，如果伺服器未開啟 HTTP 服務）")
    
    # 檢查 VPN 連接
    if vpn_enabled:
        print("檢查 VPN 連接...")
        if network_info.get("vpn_connected"):
            print("✓ VPN 連接已建立")
        else:
            print("⚠️  VPN 未連接，建議先建立 VPN 連接")
    
    if server_share:
        print(f"測試 SMB 共享 {server_share}...")
        smb_test = test_smb_connection(server_share)
        if smb_test.get("accessible"):
            print(f"✓ SMB 共享可訪問（{smb_test.get('file_count', 0)} 個檔案）")
        else:
            print(f"✗ SMB 共享不可訪問: {smb_test.get('error', '未知錯誤')}")
    
    if health_url:
        print(f"測試健康檢查 URL {health_url}...")
        try:
            import requests
            response = requests.get(health_url, timeout=3)
            if response.status_code == 200:
                print(f"✓ 健康檢查 URL 可達")
            else:
                print(f"⚠️  健康檢查 URL 回應: {response.status_code}")
        except Exception as e:
            print(f"✗ 健康檢查 URL 不可達: {e}")
    
    print()
    
    # 設定環境變數
    print("【步驟 4：設定環境變數】")
    env_config = {}
    if server_share:
        env_config["WUCHANG_COPY_TO"] = server_share
    if health_url:
        env_config["WUCHANG_HEALTH_URL"] = health_url
    if hub_url:
        env_config["WUCHANG_HUB_URL"] = hub_url
    if hub_token:
        env_config["WUCHANG_HUB_TOKEN"] = hub_token
    
    if env_config:
        if setup_environment_variables(env_config):
            print("✓ 環境變數已設定")
            for key, value in env_config.items():
                print(f"  {key} = {value}")
        else:
            print("✗ 環境變數設定失敗")
    else:
        print("⚠️  未設定任何環境變數（未提供伺服器資訊）")
    
    print()
    
    # 儲存配置
    print("【步驟 5：儲存配置】")
    final_config = {
        "server_ddns": server_ddns,
        "server_ip": server_ip,
        "server_share": server_share,
        "health_url": health_url,
        "hub_url": hub_url,
        "hub_token": "***" if hub_token else "",
        "vpn": {
            "enabled": vpn_enabled,
            "server": vpn_server
        },
        "local_ip": network_info.get("local_ip"),
        "hostname": network_info.get("hostname"),
        "vpn_connected": network_info.get("vpn_connected", False),
        "timestamp": __import__("time").strftime("%Y-%m-%dT%H:%M:%S%z")
    }
    
    try:
        config_file.write_text(
            json.dumps(final_config, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"✓ 配置已儲存到: {config_file}")
    except Exception as e:
        print(f"✗ 儲存配置失敗: {e}")
    
    print()
    
    # 如果控制中心可用，嘗試自動授權
    if control_center_available:
        print("【步驟 6：自動授權（可選）】")
        try:
            from auto_authorize_and_execute import main as auto_auth_main
            print("正在執行自動授權...")
            # 這裡可以調用自動授權，但需要配置檔案
            print("⚠️  需要配置 auto_auth_config.json 才能自動授權")
        except:
            print("⚠️  自動授權模組不可用")
    
    print()
    print("=" * 70)
    print("【設定完成】")
    print()
    print("已完成的設定：")
    if env_config:
        print("  ✓ 環境變數已設定")
    if config_file.exists():
        print(f"  ✓ 配置已儲存")
    print()
    print("【下一步】")
    print("1. 驗證環境變數：python setup_env_vars.py status")
    print("2. 測試連接：python check_server_connection.py")
    print("3. 執行檔案同步：python sync_all_profiles.py")
    print()
    print("=" * 70)


def main():
    """主函數"""
    try:
        auto_authorize_and_setup()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
