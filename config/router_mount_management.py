#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
router_mount_management.py

路由器掛載管理
- 由路由器調配轉發和掛載
- 管理地端機的固定IP和端口轉發
- 統一管理網路掛載點
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 設定 UTF-8 編碼輸出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent

# 地端機配置
LOCAL_MACHINES = [
    {
        "name": "地端機-主控",
        "fixed_ip": "192.168.50.100",
        "mac_address": None,  # 將自動獲取或設定
        "services": [
            {"name": "Local Control Center", "port": 8788},
            {"name": "Little J Hub", "port": 8799},
            {"name": "Ollama API", "port": 11434},
        ]
    }
]

# 掛載點配置（由路由器管理）
MOUNT_POINTS = [
    {
        "name": "伺服器共享",
        "type": "SMB",
        "server": "wuchang.life",
        "share": "wuchang",
        "mount_point": "Z:",
        "local_path": "Z:\\",
    }
]


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry)


def configure_local_machine_fixed_ip(machine_config: Dict[str, Any]) -> bool:
    """配置地端機固定IP"""
    log(f"配置地端機固定IP: {machine_config['fixed_ip']}", "INFO")
    
    try:
        # 使用 local_machine_fixed_ip_setup.py
        import subprocess
        result = subprocess.run(
            [sys.executable, str(BASE_DIR / "local_machine_fixed_ip_setup.py"),
             "--ip", machine_config["fixed_ip"],
             "--gateway", "192.168.50.84"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            log("地端機固定IP設定成功", "INFO")
            return True
        else:
            log(f"地端機固定IP設定失敗: {result.stderr}", "ERROR")
            return False
    except Exception as e:
        log(f"配置地端機固定IP失敗: {e}", "ERROR")
        return False


def setup_router_port_forwarding_for_machine(machine_config: Dict[str, Any]) -> bool:
    """為地端機設定路由器端口轉發"""
    log(f"為 {machine_config['name']} 設定路由器端口轉發...", "INFO")
    
    try:
        from router_full_control import get_router_full_control
        
        router = get_router_full_control()
        if not router.logged_in:
            if not router.login():
                log("路由器登錄失敗", "ERROR")
                return False
        
        success_count = 0
        for service in machine_config.get("services", []):
            log(f"  配置端口轉發: {service['name']} ({service['port']})", "INFO")
            
            success = router.add_port_forwarding_rule(
                external_port=service["port"],
                internal_ip=machine_config["fixed_ip"],
                internal_port=service["port"],
                protocol="TCP",
                description=f"{machine_config['name']}-{service['name']}"
            )
            
            if success:
                success_count += 1
                log(f"    ✓ 配置成功", "INFO")
            else:
                log(f"    ✗ 配置失敗", "ERROR")
        
        log(f"端口轉發配置完成: {success_count}/{len(machine_config.get('services', []))}", "INFO")
        return success_count == len(machine_config.get("services", []))
        
    except ImportError:
        log("路由器控制模組不可用", "WARN")
        return False
    except Exception as e:
        log(f"配置路由器端口轉發失敗: {e}", "ERROR")
        return False


def configure_mount_points() -> bool:
    """配置掛載點（由路由器調配）"""
    log("配置掛載點...", "INFO")
    
    success = True
    for mount in MOUNT_POINTS:
        log(f"配置掛載點: {mount['name']} ({mount['mount_point']})", "INFO")
        
        if mount["type"] == "SMB":
            # Windows SMB 掛載
            if sys.platform == 'win32':
                try:
                    # 檢查是否已掛載
                    result = subprocess.run(
                        ["net", "use", mount["mount_point"]],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    if mount["mount_point"] in result.stdout:
                        log(f"  ✓ 已掛載: {mount['mount_point']}", "INFO")
                    else:
                        # 嘗試掛載
                        log(f"  嘗試掛載: {mount['server']}\\{mount['share']}", "INFO")
                        # 注意：實際掛載需要認證，這裡只記錄
                        log(f"  請手動掛載: net use {mount['mount_point']} \\\\{mount['server']}\\{mount['share']}", "INFO")
                except Exception as e:
                    log(f"  掛載檢查失敗: {e}", "ERROR")
                    success = False
        else:
            log(f"  不支援的掛載類型: {mount['type']}", "WARN")
    
    return success


def get_router_port_forwarding_status() -> Dict[str, Any]:
    """獲取路由器端口轉發狀態"""
    log("獲取路由器端口轉發狀態...", "INFO")
    
    try:
        from router_full_control import get_router_full_control
        
        router = get_router_full_control()
        if not router.logged_in:
            router.login()
        
        rules = router.get_port_forwarding_rules()
        
        # 過濾地端機相關的規則
        local_machine_rules = []
        for rule in rules:
            if isinstance(rule, dict):
                desc = rule.get("desc", "")
                if "地端機" in desc or "local" in desc.lower():
                    local_machine_rules.append(rule)
        
        return {
            "total_rules": len(rules),
            "local_machine_rules": len(local_machine_rules),
            "rules": local_machine_rules
        }
    except Exception as e:
        log(f"獲取路由器狀態失敗: {e}", "ERROR")
        return {"error": str(e)}


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="路由器掛載管理 - 由路由器調配轉發和掛載")
    parser.add_argument("--setup-local-machine", action="store_true", help="設定地端機固定IP")
    parser.add_argument("--setup-router-forwarding", action="store_true", help="設定路由器端口轉發")
    parser.add_argument("--setup-mounts", action="store_true", help="設定掛載點")
    parser.add_argument("--status", action="store_true", help="查看狀態")
    parser.add_argument("--all", action="store_true", help="執行所有設定")
    parser.add_argument("--dry-run", action="store_true", help="模擬執行")
    
    args = parser.parse_args()
    
    log("=" * 60, "INFO")
    log("路由器掛載管理 - 由路由器調配轉發和掛載", "INFO")
    log("=" * 60, "INFO")
    
    if args.all or args.setup_local_machine:
        # 設定地端機固定IP
        log("\n[步驟 1] 設定地端機固定IP", "INFO")
        for machine in LOCAL_MACHINES:
            if not args.dry_run:
                configure_local_machine_fixed_ip(machine)
            else:
                log(f"  [模擬] 將設定 {machine['name']} 為 {machine['fixed_ip']}", "INFO")
    
    if args.all or args.setup_router_forwarding:
        # 設定路由器端口轉發
        log("\n[步驟 2] 設定路由器端口轉發", "INFO")
        for machine in LOCAL_MACHINES:
            if not args.dry_run:
                setup_router_port_forwarding_for_machine(machine)
            else:
                log(f"  [模擬] 將為 {machine['name']} 設定端口轉發", "INFO")
    
    if args.all or args.setup_mounts:
        # 設定掛載點
        log("\n[步驟 3] 設定掛載點", "INFO")
        if not args.dry_run:
            configure_mount_points()
        else:
            log("  [模擬] 將設定掛載點", "INFO")
    
    if args.status:
        # 查看狀態
        log("\n[狀態查詢] 路由器端口轉發狀態", "INFO")
        status = get_router_port_forwarding_status()
        log(f"  總規則數: {status.get('total_rules', 0)}", "INFO")
        log(f"  地端機規則數: {status.get('local_machine_rules', 0)}", "INFO")
        if status.get("rules"):
            log("  地端機端口轉發規則:", "INFO")
            for rule in status["rules"]:
                log(f"    - {rule}", "INFO")
    
    log("\n執行完成！", "INFO")
    log("=" * 60, "INFO")


if __name__ == "__main__":
    main()
