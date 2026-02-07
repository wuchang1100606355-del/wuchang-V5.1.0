#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_system_update_status.py

檢查系統更新狀態

功能：
- 檢查系統部署狀態
- 檢查服務運行狀態
- 檢查檔案同步狀態
- 檢查環境變數配置
- 生成更新狀態報告
"""

import sys
import json
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def check_services() -> Dict[str, Any]:
    """檢查服務運行狀態"""
    services = {
        "control_center": {
            "name": "本機中控台",
            "port": 8788,
            "url": "http://127.0.0.1:8788/",
            "running": False
        },
        "little_j_hub": {
            "name": "Little J Hub",
            "port": 8799,
            "url": "http://127.0.0.1:8799/",
            "running": False
        }
    }
    
    try:
        import socket
        for service_id, service in services.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(("127.0.0.1", service["port"]))
                sock.close()
                services[service_id]["running"] = (result == 0)
            except:
                services[service_id]["running"] = False
    except:
        pass
    
    return services


def check_environment_variables() -> Dict[str, Any]:
    """檢查環境變數配置"""
    env_vars = {
        "WUCHANG_HEALTH_URL": os.getenv("WUCHANG_HEALTH_URL", ""),
        "WUCHANG_COPY_TO": os.getenv("WUCHANG_COPY_TO", ""),
        "WUCHANG_HUB_URL": os.getenv("WUCHANG_HUB_URL", ""),
        "WUCHANG_HUB_TOKEN": os.getenv("WUCHANG_HUB_TOKEN", ""),
        "WUCHANG_SYSTEM_DB_DIR": os.getenv("WUCHANG_SYSTEM_DB_DIR", ""),
        "WUCHANG_WORKSPACE_OUTDIR": os.getenv("WUCHANG_WORKSPACE_OUTDIR", ""),
        "WUCHANG_PII_ENABLED": os.getenv("WUCHANG_PII_ENABLED", ""),
    }
    
    configured = {k: bool(v) for k, v in env_vars.items()}
    total = len(env_vars)
    configured_count = sum(configured.values())
    
    return {
        "total": total,
        "configured": configured_count,
        "missing": total - configured_count,
        "variables": configured,
        "values": {k: "***" if "TOKEN" in k else v for k, v in env_vars.items()}
    }


def check_file_sync_status() -> Dict[str, Any]:
    """檢查檔案同步狀態"""
    try:
        from smart_sync import smart_sync
        from safe_sync_push import DEFAULT_FILES, RULE_FILES
        
        server_dir = os.getenv("WUCHANG_COPY_TO", "")
        if not server_dir:
            return {
                "available": False,
                "reason": "WUCHANG_COPY_TO 未設定"
            }
        
        server_path = Path(server_dir).expanduser().resolve()
        if not server_path.exists():
            return {
                "available": False,
                "reason": "伺服器目錄不存在"
            }
        
        # 檢查 KB profile
        kb_results = smart_sync(
            DEFAULT_FILES,
            BASE_DIR,
            server_path,
            dry_run=True,
            direction="both"
        )
        
        # 檢查 Rules profile
        rules_results = smart_sync(
            RULE_FILES,
            BASE_DIR,
            server_path,
            dry_run=True,
            direction="both"
        )
        
        kb_synced = kb_results["summary"]["no_sync_needed"]
        kb_total = kb_results["summary"]["total"]
        rules_synced = rules_results["summary"]["no_sync_needed"]
        rules_total = rules_results["summary"]["total"]
        
        return {
            "available": True,
            "kb": {
                "synced": kb_synced,
                "total": kb_total,
                "sync_rate": (kb_synced / kb_total * 100) if kb_total > 0 else 0
            },
            "rules": {
                "synced": rules_synced,
                "total": rules_total,
                "sync_rate": (rules_synced / rules_total * 100) if rules_total > 0 else 0
            }
        }
    except Exception as e:
        return {
            "available": False,
            "reason": str(e)
        }


def check_deployment_status() -> Dict[str, Any]:
    """檢查部署狀態"""
    try:
        from system_deployment_status import get_deployment_status
        return get_deployment_status()
    except Exception as e:
        return {
            "available": False,
            "error": str(e)
        }


def check_google_tasks_setup() -> Dict[str, Any]:
    """檢查 Google Tasks 設定"""
    credentials_path = BASE_DIR / "google_credentials.json"
    token_path = BASE_DIR / "google_token.json"
    
    return {
        "credentials_configured": credentials_path.exists(),
        "token_available": token_path.exists(),
        "ready": credentials_path.exists()
    }


def generate_update_report() -> Dict[str, Any]:
    """生成更新狀態報告"""
    report = {
        "timestamp": __import__("time").strftime("%Y-%m-%dT%H:%M:%S%z"),
        "services": check_services(),
        "environment": check_environment_variables(),
        "file_sync": check_file_sync_status(),
        "google_tasks": check_google_tasks_setup(),
    }
    
    # 檢查部署狀態
    deployment = check_deployment_status()
    if deployment.get("available"):
        report["deployment"] = deployment
    
    # 計算整體狀態
    services_ok = all(s["running"] for s in report["services"].values())
    env_ok = report["environment"]["configured"] >= 2  # 至少設定 2 個主要變數
    sync_ok = report["file_sync"].get("available", False)
    
    report["overall_status"] = "ready" if (services_ok and env_ok) else "needs_setup"
    report["update_complete"] = services_ok and env_ok and sync_ok
    
    return report


def print_report(report: Dict[str, Any]):
    """列印報告"""
    print("=" * 70)
    print("系統更新狀態報告")
    print("=" * 70)
    print(f"檢查時間: {report['timestamp']}")
    print()
    
    # 服務狀態
    print("【服務運行狀態】")
    for service_id, service in report["services"].items():
        status = "✓ 運行中" if service["running"] else "✗ 未運行"
        print(f"  {status} - {service['name']} ({service['port']})")
    print()
    
    # 環境變數
    env = report["environment"]
    print("【環境變數配置】")
    print(f"  已設定: {env['configured']}/{env['total']}")
    if env["missing"] > 0:
        print(f"  ⚠️  缺少 {env['missing']} 個環境變數")
        print("  建議執行: .\\setup_file_sync_env.ps1")
    else:
        print("  ✓ 所有環境變數已設定")
    print()
    
    # 檔案同步
    sync = report["file_sync"]
    if sync.get("available"):
        print("【檔案同步狀態】")
        kb = sync.get("kb", {})
        rules = sync.get("rules", {})
        print(f"  KB Profile: {kb.get('synced', 0)}/{kb.get('total', 0)} 已同步 ({kb.get('sync_rate', 0):.1f}%)")
        print(f"  Rules Profile: {rules.get('synced', 0)}/{rules.get('total', 0)} 已同步 ({rules.get('sync_rate', 0):.1f}%)")
        if kb.get("sync_rate", 0) == 100 and rules.get("sync_rate", 0) == 100:
            print("  ✓ 所有檔案已同步")
        else:
            print("  ⚠️  建議執行: python sync_all_profiles.py")
    else:
        print("【檔案同步狀態】")
        print(f"  ✗ 無法檢查: {sync.get('reason', '未知原因')}")
    print()
    
    # Google Tasks
    gt = report["google_tasks"]
    print("【Google Tasks 整合】")
    if gt["ready"]:
        print("  ✓ OAuth 憑證已設定")
        if gt["token_available"]:
            print("  ✓ Token 已授權")
        else:
            print("  ⚠️  Token 未授權，需要執行授權流程")
    else:
        print("  ✗ OAuth 憑證未設定")
        print("  參考: GOOGLE_TASKS_QUICK_SETUP.md")
    print()
    
    # 整體狀態
    print("【整體狀態】")
    if report["update_complete"]:
        print("  ✓ 系統更新完成")
        print("  ✓ 所有服務運行正常")
        print("  ✓ 環境變數已配置")
        print("  ✓ 檔案已同步")
    else:
        print("  ⚠️  系統需要更新或配置")
        if not all(s["running"] for s in report["services"].values()):
            print("  - 部分服務未運行")
        if env["missing"] > 0:
            print("  - 環境變數未完全設定")
        if not sync.get("available") or sync.get("kb", {}).get("sync_rate", 0) < 100:
            print("  - 檔案需要同步")
    print()
    print("=" * 70)


def main():
    """主函數"""
    report = generate_update_report()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report)
    
    # 返回碼
    return 0 if report["update_complete"] else 1


if __name__ == "__main__":
    sys.exit(main())
