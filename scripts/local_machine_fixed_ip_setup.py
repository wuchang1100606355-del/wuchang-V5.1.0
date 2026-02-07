#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
local_machine_fixed_ip_setup.py

地端機統一固定IP設定
- 設定本機固定IP
- 在路由器上配置端口轉發
- 由路由器調配轉發和掛載
"""

import sys
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 設定 UTF-8 編碼輸出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent

# 地端機固定IP配置
LOCAL_MACHINE_CONFIG = {
    "fixed_ip": "192.168.50.100",  # 地端機固定IP
    "subnet_mask": "255.255.255.0",
    "gateway": "192.168.50.84",  # 路由器IP
    "dns_primary": "8.8.8.8",
    "dns_secondary": "8.8.4.4",
    "mac_address": None,  # 將自動獲取
}

# 需要轉發的端口（地端機服務）
PORT_FORWARDING_RULES = [
    {
        "name": "Local Control Center",
        "external_port": 8788,
        "internal_port": 8788,
        "protocol": "TCP",
        "description": "地端機控制中心"
    },
    {
        "name": "Little J Hub",
        "external_port": 8799,
        "internal_port": 8799,
        "protocol": "TCP",
        "description": "地端機 Little J Hub"
    },
    {
        "name": "Ollama API",
        "external_port": 11434,
        "internal_port": 11434,
        "protocol": "TCP",
        "description": "地端機 Ollama API"
    },
    {
        "name": "Open WebUI",
        "external_port": 3000,
        "internal_port": 3000,
        "protocol": "TCP",
        "description": "地端機 Open WebUI"
    },
]


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry)


def get_mac_address() -> Optional[str]:
    """獲取本機 MAC 地址"""
    try:
        import uuid
        mac = uuid.getnode()
        mac_str = ':'.join(['{:02x}'.format((mac >> elements) & 0xff) for elements in range(0, 2*6, 2)][::-1])
        return mac_str.upper()
    except Exception as e:
        log(f"獲取 MAC 地址失敗: {e}", "ERROR")
        return None


def get_current_ip_config() -> Dict[str, Any]:
    """獲取當前IP配置"""
    log("獲取當前IP配置...", "INFO")
    
    config = {
        "ip": None,
        "subnet_mask": None,
        "gateway": None,
        "dns": [],
        "mac_address": get_mac_address()
    }
    
    try:
        if sys.platform == 'win32':
            # Windows: 使用 ipconfig
            result = subprocess.run(
                ["ipconfig", "/all"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            output = result.stdout
            for line in output.split('\n'):
                line = line.strip()
                if 'IPv4' in line or 'IP Address' in line:
                    # 提取IP地址
                    parts = line.split(':')
                    if len(parts) > 1:
                        ip = parts[-1].strip()
                        if ip and not ip.startswith('('):
                            config["ip"] = ip
                elif 'Subnet Mask' in line:
                    parts = line.split(':')
                    if len(parts) > 1:
                        config["subnet_mask"] = parts[-1].strip()
                elif 'Default Gateway' in line:
                    parts = line.split(':')
                    if len(parts) > 1:
                        config["gateway"] = parts[-1].strip()
                elif 'DNS Servers' in line or 'DNS' in line:
                    parts = line.split(':')
                    if len(parts) > 1:
                        dns = parts[-1].strip()
                        if dns and dns not in config["dns"]:
                            config["dns"].append(dns)
        else:
            # Linux/Mac: 使用 ip 或 ifconfig
            try:
                result = subprocess.run(
                    ["ip", "addr", "show"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                # 解析輸出
                # ... (簡化處理)
            except:
                pass
        
        log(f"當前IP: {config['ip']}", "INFO")
        return config
    except Exception as e:
        log(f"獲取IP配置失敗: {e}", "ERROR")
        return config


def set_fixed_ip_windows(config: Dict[str, Any]) -> bool:
    """在 Windows 上設定固定IP"""
    log("設定 Windows 固定IP...", "INFO")
    
    try:
        # 獲取網路介面卡名稱
        result = subprocess.run(
            ["netsh", "interface", "show", "interface"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # 找到活動的介面（通常是乙太網路或Wi-Fi）
        interface_name = None
        for line in result.stdout.split('\n'):
            if 'Connected' in line or '已連線' in line:
                parts = line.split()
                if len(parts) > 3:
                    interface_name = ' '.join(parts[3:])
                    break
        
        if not interface_name:
            # 嘗試使用預設名稱
            interface_name = "乙太網路"  # 或 "Ethernet"
        
        log(f"使用網路介面: {interface_name}", "INFO")
        
        # 設定固定IP
        commands = [
            ["netsh", "interface", "ip", "set", "address", f'name="{interface_name}"', "static", 
             config["fixed_ip"], config["subnet_mask"], config["gateway"]],
            ["netsh", "interface", "ip", "set", "dns", f'name="{interface_name}"', "static", 
             config["dns_primary"], "primary"],
            ["netsh", "interface", "ip", "add", "dns", f'name="{interface_name}"', 
             config["dns_secondary"], "index=2"],
        ]
        
        for cmd in commands:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                log(f"設定失敗: {' '.join(cmd)}", "ERROR")
                log(f"錯誤: {result.stderr}", "ERROR")
                return False
        
        log("固定IP設定成功", "INFO")
        return True
        
    except Exception as e:
        log(f"設定固定IP失敗: {e}", "ERROR")
        return False


def configure_router_port_forwarding(config: Dict[str, Any]) -> bool:
    """在路由器上配置端口轉發"""
    log("配置路由器端口轉發...", "INFO")
    
    try:
        from router_full_control import get_router_full_control
        
        router = get_router_full_control()
        if not router.logged_in:
            if not router.login():
                log("路由器登錄失敗", "ERROR")
                return False
        
        # 配置每個端口轉發規則
        success_count = 0
        for rule in PORT_FORWARDING_RULES:
            log(f"  配置端口轉發: {rule['name']} ({rule['external_port']} -> {config['fixed_ip']}:{rule['internal_port']})", "INFO")
            
            success = router.add_port_forwarding_rule(
                external_port=rule["external_port"],
                internal_ip=config["fixed_ip"],
                internal_port=rule["internal_port"],
                protocol=rule["protocol"],
                description=f"地端機-{rule['description']}"
            )
            
            if success:
                success_count += 1
                log(f"    ✓ 配置成功", "INFO")
            else:
                log(f"    ✗ 配置失敗", "ERROR")
        
        log(f"端口轉發配置完成: {success_count}/{len(PORT_FORWARDING_RULES)}", "INFO")
        return success_count == len(PORT_FORWARDING_RULES)
        
    except ImportError:
        log("路由器控制模組不可用", "WARN")
        return False
    except Exception as e:
        log(f"配置路由器端口轉發失敗: {e}", "ERROR")
        return False


def save_local_machine_config(config: Dict[str, Any]) -> Path:
    """儲存地端機配置"""
    config_file = BASE_DIR / "local_machine_config.json"
    config["last_updated"] = datetime.now().isoformat()
    config_file.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    log(f"地端機配置已儲存: {config_file}", "INFO")
    return config_file


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="地端機統一固定IP設定")
    parser.add_argument("--ip", default=None, help="固定IP地址（預設: 192.168.50.100）")
    parser.add_argument("--gateway", default=None, help="閘道地址（預設: 192.168.50.84）")
    parser.add_argument("--configure-router", action="store_true", help="同時配置路由器端口轉發")
    parser.add_argument("--dry-run", action="store_true", help="模擬執行")
    
    args = parser.parse_args()
    
    log("=" * 60, "INFO")
    log("地端機統一固定IP設定", "INFO")
    log("=" * 60, "INFO")
    
    # 1. 獲取當前配置
    log("\n[步驟 1] 獲取當前IP配置", "INFO")
    current_config = get_current_ip_config()
    
    # 2. 準備固定IP配置
    log("\n[步驟 2] 準備固定IP配置", "INFO")
    fixed_config = LOCAL_MACHINE_CONFIG.copy()
    if args.ip:
        fixed_config["fixed_ip"] = args.ip
    if args.gateway:
        fixed_config["gateway"] = args.gateway
    if current_config.get("mac_address"):
        fixed_config["mac_address"] = current_config["mac_address"]
    
    log(f"固定IP: {fixed_config['fixed_ip']}", "INFO")
    log(f"閘道: {fixed_config['gateway']}", "INFO")
    log(f"MAC地址: {fixed_config.get('mac_address', 'N/A')}", "INFO")
    
    # 3. 設定固定IP
    if not args.dry_run:
        log("\n[步驟 3] 設定固定IP", "INFO")
        if sys.platform == 'win32':
            success = set_fixed_ip_windows(fixed_config)
            if not success:
                log("設定固定IP失敗，請手動設定", "ERROR")
                return
        else:
            log("非 Windows 系統，請手動設定固定IP", "WARN")
    else:
        log("\n[模擬模式] 不會實際設定固定IP", "INFO")
    
    # 4. 配置路由器端口轉發
    if args.configure_router and not args.dry_run:
        log("\n[步驟 4] 配置路由器端口轉發", "INFO")
        configure_router_port_forwarding(fixed_config)
    elif args.configure_router:
        log("\n[模擬模式] 不會實際配置路由器", "INFO")
    
    # 5. 儲存配置
    log("\n[步驟 5] 儲存配置", "INFO")
    config_file = save_local_machine_config(fixed_config)
    
    # 6. 生成配置摘要
    log("\n配置摘要:", "INFO")
    log(f"  固定IP: {fixed_config['fixed_ip']}", "INFO")
    log(f"  閘道: {fixed_config['gateway']}", "INFO")
    log(f"  端口轉發規則: {len(PORT_FORWARDING_RULES)} 個", "INFO")
    for rule in PORT_FORWARDING_RULES:
        log(f"    - {rule['name']}: {rule['external_port']} -> {fixed_config['fixed_ip']}:{rule['internal_port']}", "INFO")
    
    log("\n設定完成！", "INFO")
    log("=" * 60, "INFO")


if __name__ == "__main__":
    main()
