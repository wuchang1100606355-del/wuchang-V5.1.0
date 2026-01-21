#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
server_deployment_checker.py

伺服器端部署檢查腳本

功能：
- 檢查伺服器容器狀態
- 檢查 DNS 狀態
- 檢查服務可用性
- 產生報告並可同步到 Google Drive
"""

import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"
GDRIVE_REPORTS_DIR = Path("J:/共用雲端硬碟/五常雲端空間/reports/server_deployment") if sys.platform == "win32" else Path("/mnt/gdrive/reports/server_deployment")


def log(message: str, level: str = "INFO", to_console: bool = True):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌",
        "PROGRESS": "🔄"
    }
    icon = icons.get(level, "•")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if to_console:
        print(f"[{timestamp}] {icon} [{level}] {message}")
    
    # 寫入日誌檔案
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"server_deployment_check_{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] [{level}] {message}\n")


def check_container_status():
    """檢查容器狀態"""
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{.Names}}|{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            return None
        
        containers = {}
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            parts = line.split('|', 1)
            if len(parts) == 2:
                containers[parts[0]] = {
                    "status": parts[1],
                    "is_running": "Up" in parts[1],
                    "is_restarting": "Restarting" in parts[1]
                }
        
        return containers
    except Exception as e:
        log(f"檢查容器狀態時發生錯誤: {e}", "ERROR")
        return None


def check_dns_resolution(domain: str):
    """檢查 DNS 解析"""
    try:
        import socket
        ip = socket.gethostbyname(domain)
        return True, ip
    except socket.gaierror:
        return False, None
    except Exception as e:
        return False, str(e)


def check_service_http(url: str, timeout: int = 3):
    """檢查 HTTP 服務"""
    try:
        import requests
        response = requests.get(url, timeout=timeout, verify=False, allow_redirects=True)
        return True, response.status_code
    except requests.exceptions.Timeout:
        return False, "超時"
    except requests.exceptions.ConnectionError:
        return False, "連接失敗"
    except Exception as e:
        return False, str(e)


def check_server_resources():
    """檢查伺服器資源"""
    try:
        import psutil
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2)
        }
    except ImportError:
        log("psutil 未安裝，跳過資源檢查", "WARN")
        return None
    except Exception as e:
        log(f"檢查伺服器資源時發生錯誤: {e}", "WARN")
        return None


def check_deployment_status():
    """檢查部署狀態"""
    log("開始檢查伺服器部署狀態...", "PROGRESS")
    
    report = {
        "server": "伺服器",
        "timestamp": datetime.now().isoformat(),
        "containers": {},
        "dns": {},
        "services": {},
        "resources": {},
        "summary": {
            "total_containers": 0,
            "running_containers": 0,
            "restarting_containers": 0,
            "dns_resolved": 0,
            "services_accessible": 0,
            "health_score": 0
        },
        "issues": []
    }
    
    # 檢查容器
    log("檢查容器狀態...", "PROGRESS")
    containers = check_container_status()
    
    if containers:
        report["containers"] = containers
        report["summary"]["total_containers"] = len(containers)
        
        running = sum(1 for c in containers.values() if c["is_running"])
        restarting = sum(1 for c in containers.values() if c["is_restarting"])
        
        report["summary"]["running_containers"] = running
        report["summary"]["restarting_containers"] = restarting
        
        # 檢查問題容器
        for name, status in containers.items():
            if status["is_restarting"]:
                report["issues"].append({
                    "type": "container_restarting",
                    "severity": "error",
                    "message": f"容器 {name} 正在重啟",
                    "container": name,
                    "status": status["status"]
                })
            elif not status["is_running"]:
                report["issues"].append({
                    "type": "container_stopped",
                    "severity": "error",
                    "message": f"容器 {name} 已停止",
                    "container": name,
                    "status": status["status"]
                })
    else:
        report["issues"].append({
            "type": "docker_unavailable",
            "severity": "error",
            "message": "無法連接 Docker 或取得容器狀態"
        })
    
    # 檢查 DNS
    log("檢查 DNS 解析...", "PROGRESS")
    domains = [
        "app.wuchang.org.tw",
        "ai.wuchang.org.tw",
        "admin.wuchang.org.tw",
        "monitor.wuchang.org.tw"
    ]
    
    for domain in domains:
        resolved, result = check_dns_resolution(domain)
        report["dns"][domain] = {
            "resolved": resolved,
            "ip": result if resolved else None,
            "error": result if not resolved else None
        }
        
        if resolved:
            report["summary"]["dns_resolved"] += 1
        else:
            report["issues"].append({
                "type": "dns_failed",
                "severity": "warn",
                "message": f"DNS 解析失敗: {domain}",
                "domain": domain
            })
    
    # 檢查服務
    log("檢查服務連接...", "PROGRESS")
    services = {
        "app.wuchang.org.tw": "https://app.wuchang.org.tw",
        "ai.wuchang.org.tw": "https://ai.wuchang.org.tw",
        "admin.wuchang.org.tw": "https://admin.wuchang.org.tw",
        "monitor.wuchang.org.tw": "https://monitor.wuchang.org.tw"
    }
    
    for domain, url in services.items():
        accessible, result = check_service_http(url, timeout=3)
        report["services"][domain] = {
            "accessible": accessible,
            "status_code": result if accessible else None,
            "error": result if not accessible else None
        }
        
        if accessible:
            report["summary"]["services_accessible"] += 1
        else:
            report["issues"].append({
                "type": "service_unavailable",
                "severity": "warn",
                "message": f"服務無法訪問: {domain}",
                "url": url,
                "error": result
            })
    
    # 檢查伺服器資源
    log("檢查伺服器資源...", "PROGRESS")
    resources = check_server_resources()
    if resources:
        report["resources"] = resources
        
        # 檢查資源使用率
        if resources["cpu_percent"] > 90:
            report["issues"].append({
                "type": "high_cpu_usage",
                "severity": "warn",
                "message": f"CPU 使用率過高: {resources['cpu_percent']}%",
                "cpu_percent": resources["cpu_percent"]
            })
        
        if resources["memory_percent"] > 90:
            report["issues"].append({
                "type": "high_memory_usage",
                "severity": "warn",
                "message": f"記憶體使用率過高: {resources['memory_percent']}%",
                "memory_percent": resources["memory_percent"]
            })
        
        if resources["disk_percent"] > 90:
            report["issues"].append({
                "type": "low_disk_space",
                "severity": "error",
                "message": f"磁碟空間不足: {resources['disk_percent']}%",
                "disk_percent": resources["disk_percent"]
            })
    
    # 計算健康分數
    total_checks = (
        report["summary"]["total_containers"] +
        len(domains) +
        len(services)
    )
    passed_checks = (
        report["summary"]["running_containers"] +
        report["summary"]["dns_resolved"] +
        report["summary"]["services_accessible"]
    )
    
    if total_checks > 0:
        report["summary"]["health_score"] = round((passed_checks / total_checks) * 100, 2)
    
    log(f"檢查完成，健康分數: {report['summary']['health_score']}%", "OK")
    
    return report


def save_report(report: Dict):
    """儲存報告"""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON 報告
    json_file = REPORTS_DIR / f"server_deployment_status_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Markdown 報告
    md_file = REPORTS_DIR / f"server_deployment_status_{timestamp}.md"
    md_content = generate_markdown_report(report)
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    # 最新報告（覆蓋）
    latest_json = REPORTS_DIR / "server_deployment_status_latest.json"
    with open(latest_json, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    latest_md = REPORTS_DIR / "server_deployment_status_latest.md"
    with open(latest_md, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    log(f"報告已儲存: {json_file}", "OK")
    
    # 同步到 Google Drive（如果可用）
    try:
        if GDRIVE_REPORTS_DIR.exists():
            import shutil
            GDRIVE_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copy2(latest_json, GDRIVE_REPORTS_DIR / latest_json.name)
            shutil.copy2(latest_md, GDRIVE_REPORTS_DIR / latest_md.name)
            log(f"報告已同步到 Google Drive: {GDRIVE_REPORTS_DIR}", "OK")
    except Exception as e:
        log(f"同步到 Google Drive 失敗: {e}", "WARN")
    
    return json_file, md_file


def generate_markdown_report(report: Dict) -> str:
    """產生 Markdown 報告"""
    timestamp = datetime.fromisoformat(report["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
    
    md = f"""# 伺服器部署狀態報告

**檢查時間：** {timestamp}
**伺服器：** {report.get('server', '伺服器')}
**健康分數：** {report['summary']['health_score']}%

---

## 📊 執行摘要

- **總容器數：** {report['summary']['total_containers']}
- **運行中：** {report['summary']['running_containers']} ✅
- **重啟中：** {report['summary']['restarting_containers']} ⚠️
- **DNS 解析成功：** {report['summary']['dns_resolved']}/{len(report['dns'])}
- **服務可訪問：** {report['summary']['services_accessible']}/{len(report['services'])}

"""
    
    # 伺服器資源
    if report.get('resources'):
        md += "## 💻 伺服器資源\n\n"
        md += f"- **CPU 使用率：** {report['resources']['cpu_percent']}%\n"
        md += f"- **記憶體使用率：** {report['resources']['memory_percent']}% (可用: {report['resources']['memory_available_gb']} GB)\n"
        md += f"- **磁碟使用率：** {report['resources']['disk_percent']}% (可用: {report['resources']['disk_free_gb']} GB)\n\n"
        md += "---\n\n"
    
    # 容器狀態
    md += "## 🔍 容器狀態\n\n"
    if report["containers"]:
        for name, status in sorted(report["containers"].items()):
            icon = "✅" if status["is_running"] else "⚠️" if status["is_restarting"] else "❌"
            md += f"- {icon} **{name}**: {status['status']}\n"
    else:
        md += "- 無法取得容器狀態\n"
    
    md += "\n---\n\n## 🌐 DNS 解析\n\n"
    
    for domain, status in sorted(report["dns"].items()):
        icon = "✅" if status["resolved"] else "❌"
        ip_info = f" → {status['ip']}" if status["resolved"] else f" ({status['error']})"
        md += f"- {icon} **{domain}**{ip_info}\n"
    
    md += "\n---\n\n## 🌍 服務訪問\n\n"
    
    for domain, status in sorted(report["services"].items()):
        icon = "✅" if status["accessible"] else "❌"
        status_info = f" (HTTP {status['status_code']})" if status["accessible"] else f" ({status['error']})"
        md += f"- {icon} **{domain}**{status_info}\n"
    
    md += "\n---\n\n## ⚠️ 發現的問題\n\n"
    
    if report["issues"]:
        for issue in report["issues"]:
            severity_icon = "❌" if issue["severity"] == "error" else "⚠️"
            md += f"- {severity_icon} **{issue['type']}**: {issue['message']}\n"
    else:
        md += "- ✅ 未發現問題\n"
    
    md += f"""

---

**報告產生時間：** {timestamp}
"""
    
    return md


def main():
    """主函數"""
    print("=" * 70)
    print("伺服器部署狀態檢查")
    print("=" * 70)
    print()
    
    log("開始執行伺服器部署檢查...", "PROGRESS")
    
    # 執行檢查
    report = check_deployment_status()
    
    if not report:
        log("檢查失敗", "ERROR")
        return 1
    
    # 儲存報告
    json_file, md_file = save_report(report)
    
    # 顯示摘要
    print()
    print("=" * 70)
    print("【檢查結果摘要】")
    print("=" * 70)
    print()
    
    print(f"健康分數: {report['summary']['health_score']}%")
    print(f"運行中的容器: {report['summary']['running_containers']}/{report['summary']['total_containers']}")
    print(f"DNS 解析成功: {report['summary']['dns_resolved']}/{len(report['dns'])}")
    print(f"服務可訪問: {report['summary']['services_accessible']}/{len(report['services'])}")
    
    if report.get('resources'):
        print(f"CPU 使用率: {report['resources']['cpu_percent']}%")
        print(f"記憶體使用率: {report['resources']['memory_percent']}%")
        print(f"磁碟使用率: {report['resources']['disk_percent']}%")
    
    print()
    
    if report["issues"]:
        print(f"發現 {len(report['issues'])} 個問題:")
        for issue in report["issues"]:
            icon = "❌" if issue["severity"] == "error" else "⚠️"
            print(f"  {icon} {issue['message']}")
    else:
        print("✅ 未發現問題")
    
    print()
    log(f"報告已儲存: {md_file}", "OK")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        log("操作已取消", "WARN")
        sys.exit(0)
    except Exception as e:
        log(f"發生錯誤: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)
