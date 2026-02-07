#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
comprehensive_system_health_check.py

全面系統健康度檢查
整合容器、服務、網路、檔案系統、路由器等各方面檢查
"""

import sys
import json
import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 設定 UTF-8 編碼輸出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icons = {"INFO": "ℹ️", "OK": "✅", "WARN": "⚠️", "ERROR": "❌"}
    icon = icons.get(level, "•")
    print(f"{icon} [{timestamp}] [{level}] {message}")


def check_docker_containers() -> Dict[str, Any]:
    """檢查Docker容器狀態"""
    log("檢查Docker容器狀態...", "INFO")
    
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{.Names}}|{{.Status}}|{{.Image}}"],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            return {"ok": False, "error": "Docker未運行或不可用"}
        
        containers = []
        running = []
        stopped = []
        
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            parts = line.split('|', 2)
            if len(parts) >= 2:
                container = {
                    "name": parts[0],
                    "status": parts[1],
                    "image": parts[2] if len(parts) > 2 else ""
                }
                containers.append(container)
                
                if "Up" in container["status"]:
                    running.append(container)
                else:
                    stopped.append(container)
        
        health_score = (len(running) / len(containers) * 100) if containers else 0
        
        return {
            "ok": True,
            "total": len(containers),
            "running": len(running),
            "stopped": len(stopped),
            "health_score": round(health_score, 1),
            "containers": containers
        }
    except FileNotFoundError:
        return {"ok": False, "error": "Docker未安裝"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def check_disk_space() -> Dict[str, Any]:
    """檢查磁碟空間"""
    log("檢查磁碟空間...", "INFO")
    
    try:
        if sys.platform == 'win32':
            result = subprocess.run(
                ["wmic", "logicaldisk", "get", "size,freespace,caption"],
                capture_output=True,
                text=True,
                timeout=5,
                encoding='utf-8',
                errors='replace'
            )
            
            disks = []
            for line in result.stdout.strip().split('\n')[1:]:
                if not line.strip():
                    continue
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        caption = parts[0]
                        size = int(parts[1])
                        free = int(parts[2])
                        used = size - free
                        usage_percent = (used / size * 100) if size > 0 else 0
                        
                        disks.append({
                            "drive": caption,
                            "total_gb": round(size / (1024**3), 2),
                            "used_gb": round(used / (1024**3), 2),
                            "free_gb": round(free / (1024**3), 2),
                            "usage_percent": round(usage_percent, 1)
                        })
                    except:
                        continue
            
            # 檢查主要磁碟（通常是C:）
            main_disk = next((d for d in disks if d["drive"] == "C:"), None)
            if main_disk:
                health_score = 100 - main_disk["usage_percent"]
                if main_disk["usage_percent"] > 90:
                    health_score = 0
                elif main_disk["usage_percent"] > 80:
                    health_score = health_score * 0.5
            else:
                health_score = 50
            
            return {
                "ok": True,
                "disks": disks,
                "main_disk": main_disk,
                "health_score": round(health_score, 1)
            }
        else:
            result = subprocess.run(
                ["df", "-h"],
                capture_output=True,
                text=True,
                timeout=5
            )
            # 簡化處理
            return {"ok": True, "health_score": 75}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def check_local_services() -> Dict[str, Any]:
    """檢查本地服務"""
    log("檢查本地服務...", "INFO")
    
    services = {
        "local_control_center": {"port": 8788, "url": "http://127.0.0.1:8788"},
        "little_j_hub": {"port": 8799, "url": "http://127.0.0.1:8799"},
    }
    
    results = {}
    all_ok = True
    
    for name, config in services.items():
        try:
            import requests
            response = requests.get(f"{config['url']}/api/local/health", timeout=2)
            results[name] = {
                "ok": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds()
            }
            if not results[name]["ok"]:
                all_ok = False
        except:
            results[name] = {"ok": False, "error": "無回應"}
            all_ok = False
    
    health_score = (sum(1 for r in results.values() if r.get("ok")) / len(results) * 100) if results else 0
    
    return {
        "ok": all_ok,
        "services": results,
        "health_score": round(health_score, 1)
    }


def check_router_status() -> Dict[str, Any]:
    """檢查路由器狀態"""
    log("檢查路由器狀態...", "INFO")
    
    try:
        from router_integration import get_router_integration
        
        router = get_router_integration()
        if not router.logged_in:
            router.login()
        
        status = router.get_router_status()
        devices = router.get_connected_devices()
        traffic = router.get_network_traffic()
        
        return {
            "ok": True,
            "router_model": "ASUS RT-BE86U",
            "connected_devices": devices.get("total_count", 0),
            "network_traffic": {
                "upload_mbps": traffic.get("upload_speed_mbps", 0),
                "download_mbps": traffic.get("download_speed_mbps", 0)
            },
            "health_score": 100  # 如果能連接就視為健康
        }
    except ImportError:
        return {"ok": False, "error": "路由器整合模組不可用", "health_score": 0}
    except Exception as e:
        return {"ok": False, "error": str(e), "health_score": 0}


def check_file_system() -> Dict[str, Any]:
    """檢查檔案系統"""
    log("檢查檔案系統...", "INFO")
    
    issues = []
    warnings = []
    
    # 檢查重要檔案
    important_files = [
        "jules_memory_bank.json",
        "local_control_center.py",
        "wuchang_control_center.html",
        "dual_j_work_log.py",
    ]
    
    missing_files = []
    for file_name in important_files:
        file_path = BASE_DIR / file_name
        if not file_path.exists():
            missing_files.append(file_name)
    
    if missing_files:
        issues.append(f"缺少重要檔案: {', '.join(missing_files)}")
    
    # 檢查目錄結構
    important_dirs = [
        "dual_j_work_logs",
        "健康報告",
        "certs",
    ]
    
    missing_dirs = []
    for dir_name in important_dirs:
        dir_path = BASE_DIR / dir_name
        if not dir_path.exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        warnings.append(f"缺少目錄: {', '.join(missing_dirs)}")
    
    health_score = 100
    if missing_files:
        health_score -= len(missing_files) * 20
    if missing_dirs:
        health_score -= len(missing_dirs) * 5
    health_score = max(0, health_score)
    
    return {
        "ok": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "health_score": round(health_score, 1)
    }


def check_dns_configuration() -> Dict[str, Any]:
    """檢查DNS配置"""
    log("檢查DNS配置...", "INFO")
    
    issues = []
    
    # 檢查DNS更改清單
    dns_list_files = list(BASE_DIR.glob("dns_change_list_*.json"))
    if dns_list_files:
        latest_dns_list = max(dns_list_files, key=lambda p: p.stat().st_mtime)
        try:
            with open(latest_dns_list, 'r', encoding='utf-8') as f:
                dns_data = json.load(f)
                total_files = dns_data.get("summary", {}).get("total_files_need_change", 0)
                if total_files > 0:
                    issues.append(f"仍有 {total_files} 個檔案需要DNS更改")
        except:
            pass
    
    health_score = 100 if len(issues) == 0 else 70
    
    return {
        "ok": len(issues) == 0,
        "issues": issues,
        "health_score": round(health_score, 1)
    }


def generate_comprehensive_health_report() -> Dict[str, Any]:
    """生成全面健康報告"""
    log("=" * 60, "INFO")
    log("全面系統健康度檢查", "INFO")
    log("=" * 60, "INFO")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "checks": {},
        "overall_health_score": 0,
        "issues": [],
        "warnings": [],
        "recommendations": []
    }
    
    # 1. 檢查Docker容器
    log("\n[檢查 1] Docker容器", "INFO")
    containers_check = check_docker_containers()
    report["checks"]["containers"] = containers_check
    if not containers_check.get("ok"):
        report["issues"].append(f"容器檢查失敗: {containers_check.get('error', '未知錯誤')}")
    elif containers_check.get("stopped", 0) > 0:
        report["warnings"].append(f"{containers_check.get('stopped', 0)} 個容器已停止")
    
    # 2. 檢查磁碟空間
    log("\n[檢查 2] 磁碟空間", "INFO")
    disk_check = check_disk_space()
    report["checks"]["disk"] = disk_check
    if disk_check.get("ok") and disk_check.get("main_disk"):
        main_disk = disk_check["main_disk"]
        if main_disk["usage_percent"] > 90:
            report["issues"].append(f"磁碟空間嚴重不足: {main_disk['usage_percent']}% 已使用")
        elif main_disk["usage_percent"] > 80:
            report["warnings"].append(f"磁碟空間不足: {main_disk['usage_percent']}% 已使用")
    
    # 3. 檢查本地服務
    log("\n[檢查 3] 本地服務", "INFO")
    services_check = check_local_services()
    report["checks"]["services"] = services_check
    if not services_check.get("ok"):
        report["issues"].append("部分本地服務無回應")
    
    # 4. 檢查路由器
    log("\n[檢查 4] 路由器狀態", "INFO")
    router_check = check_router_status()
    report["checks"]["router"] = router_check
    if not router_check.get("ok"):
        report["warnings"].append(f"路由器檢查失敗: {router_check.get('error', '未知錯誤')}")
    
    # 5. 檢查檔案系統
    log("\n[檢查 5] 檔案系統", "INFO")
    filesystem_check = check_file_system()
    report["checks"]["filesystem"] = filesystem_check
    if filesystem_check.get("issues"):
        report["issues"].extend(filesystem_check["issues"])
    if filesystem_check.get("warnings"):
        report["warnings"].extend(filesystem_check["warnings"])
    
    # 6. 檢查DNS配置
    log("\n[檢查 6] DNS配置", "INFO")
    dns_check = check_dns_configuration()
    report["checks"]["dns"] = dns_check
    if dns_check.get("issues"):
        report["warnings"].extend(dns_check["issues"])
    
    # 計算總體健康分數
    health_scores = []
    for check_name, check_result in report["checks"].items():
        if isinstance(check_result, dict) and "health_score" in check_result:
            health_scores.append(check_result["health_score"])
    
    if health_scores:
        report["overall_health_score"] = round(sum(health_scores) / len(health_scores), 1)
    
    # 生成建議
    if report["overall_health_score"] < 70:
        report["recommendations"].append("系統健康度偏低，建議立即處理發現的問題")
    if disk_check.get("main_disk", {}).get("usage_percent", 0) > 90:
        report["recommendations"].append("清理磁碟空間或擴充儲存容量")
    if containers_check.get("stopped", 0) > 0:
        report["recommendations"].append("檢查並重啟已停止的容器")
    
    return report


def main():
    """主函數"""
    report = generate_comprehensive_health_report()
    
    # 輸出摘要
    log("\n" + "=" * 60, "INFO")
    log("健康檢查摘要", "INFO")
    log("=" * 60, "INFO")
    log(f"總體健康分數: {report['overall_health_score']}/100", "INFO")
    log(f"發現問題: {len(report['issues'])} 個", "ERROR" if report['issues'] else "INFO")
    log(f"警告: {len(report['warnings'])} 個", "WARN" if report['warnings'] else "INFO")
    
    if report['issues']:
        log("\n問題列表:", "ERROR")
        for issue in report['issues']:
            log(f"  - {issue}", "ERROR")
    
    if report['warnings']:
        log("\n警告列表:", "WARN")
        for warning in report['warnings']:
            log(f"  - {warning}", "WARN")
    
    if report['recommendations']:
        log("\n建議:", "INFO")
        for rec in report['recommendations']:
            log(f"  - {rec}", "INFO")
    
    # 儲存報告
    report_file = BASE_DIR / f"comprehensive_health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    log(f"\n完整報告已儲存: {report_file}", "INFO")
    
    # 記錄工作日誌
    try:
        from dual_j_work_log import add_work_log
        add_work_log(
            "地端小 j",
            "系統健康檢查",
            "執行全面系統健康度檢查",
            "completed",
            {
                "overall_health_score": report["overall_health_score"],
                "issues_count": len(report["issues"]),
                "warnings_count": len(report["warnings"])
            },
            f"健康分數: {report['overall_health_score']}/100"
        )
    except:
        pass
    
    log("\n檢查完成！", "INFO")
    log("=" * 60, "INFO")


if __name__ == "__main__":
    main()
