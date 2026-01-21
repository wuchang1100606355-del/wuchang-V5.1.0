#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
system_health_check.py

系統健康度檢查工具

功能：
- 檢查本機服務運行狀態
- 檢查系統模組可用性
- 檢查系統神經網路狀態
- 檢查環境變數配置
- 評估整體系統健康度
- 生成健康度評分與建議
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

BASE_DIR = Path(__file__).resolve().parent


def check_local_services() -> Dict[str, Any]:
    """檢查本機服務狀態"""
    services = {
        "control_center": {
            "name": "本機中控台",
            "port": 8788,
            "url": "http://127.0.0.1:8788/",
        },
        "little_j_hub": {
            "name": "Little J Hub",
            "port": 8799,
            "url": "http://127.0.0.1:8799/",
        },
    }
    
    try:
        import socket
        results = {}
        for service_id, config in services.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.0)
                result = sock.connect_ex(("127.0.0.1", config["port"]))
                sock.close()
                results[service_id] = {
                    "name": config["name"],
                    "port": config["port"],
                    "running": result == 0,
                    "healthy": result == 0,
                }
            except Exception as e:
                results[service_id] = {
                    "name": config["name"],
                    "port": config["port"],
                    "running": False,
                    "healthy": False,
                    "error": str(e),
                }
        return results
    except Exception as e:
        return {"error": str(e)}


def check_neural_network() -> Dict[str, Any]:
    """檢查系統神經網路狀態"""
    try:
        from system_neural_network import get_neural_network
        nn = get_neural_network()
        if not nn.running:
            nn.start()
        
        perception = nn.get_system_perception()
        
        return {
            "available": True,
            "running": nn.running,
            "total_nodes": perception.get("total_nodes", 0),
            "overall_health": perception.get("overall_health", "unknown"),
            "healthy": perception.get("overall_health") == "healthy",
        }
    except ImportError:
        return {
            "available": False,
            "running": False,
            "healthy": False,
            "error": "module_not_installed",
        }
    except Exception as e:
        return {
            "available": True,
            "running": False,
            "healthy": False,
            "error": str(e),
        }


def check_storage_modules() -> Dict[str, Any]:
    """檢查儲存模組狀態"""
    results = {
        "encrypted_storage": {},
        "pii_storage": {},
    }
    
    # 加密儲存
    try:
        from encrypted_storage_manager import get_storage_manager
        storage = get_storage_manager()
        devices = storage.list_devices()
        results["encrypted_storage"] = {
            "available": True,
            "device_count": len(devices),
            "healthy": True,
        }
    except ImportError:
        results["encrypted_storage"] = {
            "available": False,
            "healthy": False,
            "error": "module_not_installed",
        }
    except Exception as e:
        results["encrypted_storage"] = {
            "available": True,
            "healthy": False,
            "error": str(e),
        }
    
    # 個資儲存
    pii_enabled = os.getenv("WUCHANG_PII_ENABLED", "").strip().lower() == "true"
    try:
        from pii_storage_manager import get_pii_storage_manager
        pii_manager = get_pii_storage_manager()
        results["pii_storage"] = {
            "available": True,
            "enabled": pii_enabled,
            "healthy": True,
            "default_device": pii_manager.default_device_id or "未設定",
        }
    except ImportError:
        results["pii_storage"] = {
            "available": False,
            "enabled": pii_enabled,
            "healthy": False,
            "error": "module_not_installed",
        }
    except Exception as e:
        results["pii_storage"] = {
            "available": True,
            "enabled": pii_enabled,
            "healthy": False,
            "error": str(e),
        }
    
    return results


def check_authorization_system() -> Dict[str, Any]:
    """檢查授權系統狀態"""
    try:
        from authorized_administrators import validate_authorizations
        validation = validate_authorizations()
        return {
            "available": True,
            "healthy": validation.get("valid", True),
            "total_count": validation.get("total_count", 0),
            "valid_count": validation.get("valid_count", 0),
        }
    except ImportError:
        return {
            "available": False,
            "healthy": False,
            "error": "module_not_installed",
        }
    except Exception as e:
        return {
            "available": True,
            "healthy": False,
            "error": str(e),
        }


def check_environment_config() -> Dict[str, Any]:
    """檢查環境變數配置"""
    env_vars = {
        "WUCHANG_HEALTH_URL": os.getenv("WUCHANG_HEALTH_URL", ""),
        "WUCHANG_COPY_TO": os.getenv("WUCHANG_COPY_TO", ""),
        "WUCHANG_HUB_URL": os.getenv("WUCHANG_HUB_URL", ""),
        "WUCHANG_HUB_TOKEN": os.getenv("WUCHANG_HUB_TOKEN", ""),
        "WUCHANG_PII_ENABLED": os.getenv("WUCHANG_PII_ENABLED", ""),
    }
    
    configured_count = sum(1 for v in env_vars.values() if v)
    total_count = len(env_vars)
    
    return {
        "total_variables": total_count,
        "configured_count": configured_count,
        "completion_rate": configured_count / total_count if total_count > 0 else 0,
        "variables": {k: bool(v) for k, v in env_vars.items()},
        "healthy": configured_count >= 2,  # 至少 2 個核心變數已設定
    }


def calculate_health_score(checks: Dict[str, Any]) -> Dict[str, Any]:
    """計算系統健康度評分"""
    total_weight = 0
    score = 0
    
    # 本機服務 (權重: 30%)
    if "local_services" in checks:
        services = checks["local_services"]
        if isinstance(services, dict) and "error" not in services:
            running_count = sum(1 for s in services.values() if s.get("running"))
            total_count = len(services)
            services_score = (running_count / total_count) * 30 if total_count > 0 else 0
            score += services_score
            total_weight += 30
    
    # 系統神經網路 (權重: 25%)
    if "neural_network" in checks:
        nn = checks["neural_network"]
        if nn.get("available") and nn.get("healthy"):
            score += 25
        total_weight += 25
    
    # 儲存模組 (權重: 20%)
    if "storage" in checks:
        storage = checks["storage"]
        storage_score = 0
        if storage.get("encrypted_storage", {}).get("healthy"):
            storage_score += 10
        if storage.get("pii_storage", {}).get("healthy"):
            storage_score += 10
        score += storage_score
        total_weight += 20
    
    # 授權系統 (權重: 10%)
    if "authorization" in checks:
        auth = checks["authorization"]
        if auth.get("available") and auth.get("healthy"):
            score += 10
        total_weight += 10
    
    # 環境配置 (權重: 15%)
    if "environment" in checks:
        env = checks["environment"]
        completion = env.get("completion_rate", 0)
        score += completion * 15
        total_weight += 15
    
    # 計算百分比
    health_score = (score / total_weight * 100) if total_weight > 0 else 0
    
    # 評級
    if health_score >= 90:
        grade = "A - 優秀"
    elif health_score >= 75:
        grade = "B - 良好"
    elif health_score >= 60:
        grade = "C - 一般"
    elif health_score >= 40:
        grade = "D - 需改善"
    else:
        grade = "F - 緊急"
    
    return {
        "score": round(health_score, 1),
        "grade": grade,
        "max_score": 100,
        "components": {
            "services": score,
            "max_weight": total_weight,
        },
    }


def get_health_recommendations(checks: Dict[str, Any]) -> List[str]:
    """生成健康度改善建議"""
    recommendations = []
    
    # 檢查本機服務
    if "local_services" in checks:
        services = checks["local_services"]
        if isinstance(services, dict) and "error" not in services:
            not_running = [s["name"] for s in services.values() if not s.get("running")]
            if not_running:
                recommendations.append(f"啟動未運行的服務: {', '.join(not_running)}")
    
    # 檢查環境變數
    if "environment" in checks:
        env = checks["environment"]
        if env.get("completion_rate", 0) < 0.5:
            recommendations.append("設定更多環境變數以啟用完整功能（建議使用 setup_env_vars.py）")
    
    # 檢查神經網路
    if "neural_network" in checks:
        nn = checks["neural_network"]
        if not nn.get("available"):
            recommendations.append("檢查系統神經網路模組是否正確安裝")
        elif not nn.get("running"):
            recommendations.append("啟動系統神經網路以獲得系統感知功能")
    
    # 檢查儲存模組
    if "storage" in checks:
        storage = checks["storage"]
        if not storage.get("encrypted_storage", {}).get("healthy"):
            recommendations.append("檢查加密儲存模組狀態")
        pii_storage = storage.get("pii_storage", {})
        if pii_storage.get("available") and not pii_storage.get("enabled"):
            recommendations.append("如需個資處理功能，設定 WUCHANG_PII_ENABLED=true")
    
    if not recommendations:
        recommendations.append("系統狀態良好，無需立即改善")
    
    return recommendations


def get_system_health() -> Dict[str, Any]:
    """獲取完整系統健康度報告"""
    checks = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "local_services": check_local_services(),
        "neural_network": check_neural_network(),
        "storage": check_storage_modules(),
        "authorization": check_authorization_system(),
        "environment": check_environment_config(),
    }
    
    # 計算健康度評分
    health_score = calculate_health_score(checks)
    
    # 生成建議
    recommendations = get_health_recommendations(checks)
    
    return {
        "checks": checks,
        "health_score": health_score,
        "recommendations": recommendations,
    }


def print_health_report(report: Dict[str, Any]) -> None:
    """列印健康度報告"""
    # 設定 UTF-8 編碼輸出
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except:
            pass
    
    print("=" * 70)
    print("系統健康度檢查報告")
    print("=" * 70)
    print(f"檢查時間: {report['checks']['timestamp']}\n")
    
    # 健康度評分
    score = report["health_score"]
    print("【系統健康度評分】")
    print(f"  評分: {score['score']:.1f} / {score['max_score']}")
    print(f"  等級: {score['grade']}\n")
    
    # 本機服務狀態
    if "local_services" in report["checks"]:
        services = report["checks"]["local_services"]
        if "error" not in services:
            print("【本機服務狀態】")
            for service_id, service in services.items():
                status_icon = "[運行中]" if service.get("running") else "[未運行]"
                print(f"  {status_icon} {service['name']} (端口 {service['port']})")
            print()
    
    # 系統模組狀態
    print("【系統模組狀態】")
    
    # 神經網路
    nn = report["checks"].get("neural_network", {})
    nn_status = "[正常]" if nn.get("healthy") else "[異常]"
    print(f"  {nn_status} 系統神經網路: ", end="")
    if nn.get("available"):
        print(f"運行中 ({nn.get('total_nodes', 0)} 節點, 健康狀態: {nn.get('overall_health', 'unknown')})")
    else:
        print("不可用")
    print()
    
    # 儲存模組
    storage = report["checks"].get("storage", {})
    encrypted = storage.get("encrypted_storage", {})
    pii = storage.get("pii_storage", {})
    
    encrypted_status = "[正常]" if encrypted.get("healthy") else "[異常]"
    print(f"  {encrypted_status} 加密儲存: ", end="")
    if encrypted.get("available"):
        print(f"可用 ({encrypted.get('device_count', 0)} 個裝置)")
    else:
        print("不可用")
    
    pii_status = "[正常]" if pii.get("healthy") else "[異常]"
    pii_enabled = "[已啟用]" if pii.get("enabled") else "[未啟用]"
    print(f"  {pii_status} 個資儲存: {pii_enabled}")
    print()
    
    # 授權系統
    auth = report["checks"].get("authorization", {})
    auth_status = "[正常]" if auth.get("healthy") else "[異常]"
    print(f"  {auth_status} 授權系統: ", end="")
    if auth.get("available"):
        print(f"可用 ({auth.get('valid_count', 0)} / {auth.get('total_count', 0)} 有效授權)")
    else:
        print("不可用")
    print()
    
    # 環境配置
    env = report["checks"].get("environment", {})
    completion = env.get("completion_rate", 0) * 100
    print(f"【環境配置完成度】: {completion:.0f}%")
    print(f"  已設定: {env.get('configured_count', 0)} / {env.get('total_variables', 0)}")
    print()
    
    # 改善建議
    print("【改善建議】")
    for i, rec in enumerate(report["recommendations"], 1):
        print(f"  {i}. {rec}")
    
    print("\n" + "=" * 70)


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="系統健康度檢查工具")
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式輸出",
    )
    
    args = parser.parse_args()
    
    report = get_system_health()
    
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_health_report(report)


if __name__ == "__main__":
    main()
