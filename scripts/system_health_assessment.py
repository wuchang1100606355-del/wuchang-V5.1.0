#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
system_health_assessment.py

系統健康度評估

功能：
- 檢查容器狀態
- 檢查資源使用情況
- 檢查服務可用性
- 產生健康度評分
- 記錄到工作日誌
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"

# 匯入工作日誌管理器
sys.path.insert(0, str(BASE_DIR / "scripts"))
try:
    from work_log_manager import WorkLogManager
    log_manager = WorkLogManager()
except ImportError:
    log_manager = None

def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌",
        "PROGRESS": "🔄"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")

def check_containers() -> Dict:
    """檢查容器狀態"""
    log("檢查容器狀態...", "PROGRESS")
    
    result = {
        "total": 0,
        "running": 0,
        "stopped": 0,
        "restarting": 0,
        "containers": []
    }
    
    try:
        # 檢查所有容器
        cmd = ["docker", "ps", "-a", "--format", "{{.Names}}|{{.Status}}|{{.Ports}}"]
        output = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if output.returncode == 0:
            lines = [line.strip() for line in output.stdout.strip().split('\n') if line.strip()]
            result["total"] = len(lines)
            
            for line in lines:
                parts = line.split('|')
                if len(parts) >= 2:
                    name = parts[0]
                    status = parts[1]
                    ports = parts[2] if len(parts) > 2 else ""
                    
                    container_info = {
                        "name": name,
                        "status": status,
                        "ports": ports
                    }
                    result["containers"].append(container_info)
                    
                    if "Up" in status:
                        result["running"] += 1
                    elif "Restarting" in status:
                        result["restarting"] += 1
                    else:
                        result["stopped"] += 1
            
            log(f"✓ 發現 {result['total']} 個容器 ({result['running']} 運行中, {result['stopped']} 已停止, {result['restarting']} 重啟中)", "OK")
        else:
            log(f"✗ 檢查容器失敗: {output.stderr}", "ERROR")
    except Exception as e:
        log(f"✗ 檢查容器時發生錯誤: {e}", "ERROR")
    
    return result

def check_resources() -> Dict:
    """檢查資源使用情況"""
    log("檢查資源使用情況...", "PROGRESS")
    
    result = {
        "memory": {},
        "disk": {},
        "cpu": {}
    }
    
    try:
        # 檢查記憶體（使用 PowerShell）
        import platform
        if platform.system() == "Windows":
            cmd = ["powershell", "-Command", "Get-CimInstance -ClassName Win32_OperatingSystem | Select-Object -ExpandProperty FreePhysicalMemory"]
            output = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if output.returncode == 0:
                free_memory_kb = int(output.stdout.strip())
                free_memory_gb = free_memory_kb / (1024 * 1024)
                result["memory"]["free_gb"] = round(free_memory_gb, 2)
                log(f"✓ 可用記憶體: {result['memory']['free_gb']} GB", "OK")
    except Exception as e:
        log(f"✗ 檢查記憶體時發生錯誤: {e}", "ERROR")
    
    try:
        # 檢查磁碟空間
        disk = Path(BASE_DIR)
        stat = disk.stat()
        # 使用 PowerShell 檢查磁碟空間
        cmd = ["powershell", "-Command", f"Get-PSDrive -Name {(str(disk)[0] if str(disk) else 'G')} | Select-Object -ExpandProperty Free"]
        output = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if output.returncode == 0:
            try:
                free_bytes = int(output.stdout.strip())
                free_gb = free_bytes / (1024**3)
                result["disk"]["free_gb"] = round(free_gb, 2)
                log(f"✓ 可用磁碟空間: {result['disk']['free_gb']} GB", "OK")
            except:
                result["disk"]["free_gb"] = None
    except Exception as e:
        log(f"✗ 檢查磁碟空間時發生錯誤: {e}", "ERROR")
    
    return result

def check_services() -> Dict:
    """檢查服務可用性"""
    log("檢查服務可用性...", "PROGRESS")
    
    services = {
        "odoo": {"port": 8069, "status": "unknown"},
        "portainer": {"port": 9000, "status": "unknown"},
        "ollama": {"port": 11434, "status": "unknown"},
        "uptime_kuma": {"port": 3001, "status": "unknown"}
    }
    
    try:
        import socket
        for service_name, service_info in services.items():
            port = service_info["port"]
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                if result == 0:
                    services[service_name]["status"] = "available"
                    log(f"✓ {service_name} (端口 {port}) 可用", "OK")
                else:
                    services[service_name]["status"] = "unavailable"
                    log(f"⚠️ {service_name} (端口 {port}) 不可用", "WARN")
            except Exception as e:
                services[service_name]["status"] = "error"
                log(f"✗ 檢查 {service_name} 時發生錯誤: {e}", "ERROR")
    except Exception as e:
        log(f"✗ 檢查服務時發生錯誤: {e}", "ERROR")
    
    return services

def calculate_health_score(containers: Dict, resources: Dict, services: Dict) -> Dict:
    """計算健康度評分"""
    score = 0
    max_score = 100
    details = {}
    
    # 容器狀態 (30分)
    if containers.get("total", 0) > 0:
        running_ratio = containers.get("running", 0) / containers.get("total", 1)
        container_score = running_ratio * 30
        if containers.get("restarting", 0) > 0:
            container_score *= 0.8  # 有重啟容器扣分
        score += container_score
        details["containers"] = {
            "score": round(container_score, 1),
            "max": 30,
            "details": f"{containers.get('running', 0)}/{containers.get('total', 0)} 運行中"
        }
    else:
        details["containers"] = {"score": 0, "max": 30, "details": "未發現容器"}
    
    # 資源使用 (30分)
    resource_score = 30
    if resources.get("memory", {}).get("free_gb"):
        free_mem = resources["memory"]["free_gb"]
        if free_mem < 1:
            resource_score *= 0.5  # 記憶體不足
        elif free_mem < 2:
            resource_score *= 0.7
    if resources.get("disk", {}).get("free_gb"):
        free_disk = resources["disk"]["free_gb"]
        if free_disk < 10:
            resource_score *= 0.8  # 磁碟空間不足
    score += resource_score
    details["resources"] = {
        "score": round(resource_score, 1),
        "max": 30,
        "details": f"記憶體: {resources.get('memory', {}).get('free_gb', 'N/A')} GB, 磁碟: {resources.get('disk', {}).get('free_gb', 'N/A')} GB"
    }
    
    # 服務可用性 (40分)
    service_score = 0
    available_count = sum(1 for s in services.values() if s.get("status") == "available")
    total_count = len(services)
    if total_count > 0:
        service_score = (available_count / total_count) * 40
    score += service_score
    details["services"] = {
        "score": round(service_score, 1),
        "max": 40,
        "details": f"{available_count}/{total_count} 服務可用"
    }
    
    # 總分
    total_score = round(score, 1)
    
    # 評級
    if total_score >= 90:
        grade = "優秀"
    elif total_score >= 80:
        grade = "良好"
    elif total_score >= 70:
        grade = "一般"
    elif total_score >= 60:
        grade = "需改善"
    else:
        grade = "警告"
    
    return {
        "total_score": total_score,
        "max_score": max_score,
        "grade": grade,
        "details": details
    }

def generate_health_report(containers: Dict, resources: Dict, services: Dict, health_score: Dict) -> str:
    """產生健康度報告"""
    report_lines = [
        "# 系統健康度評估報告",
        "",
        f"**評估時間：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 📊 健康度總評",
        "",
        f"- **總分：** {health_score['total_score']}/{health_score['max_score']}",
        f"- **評級：** {health_score['grade']}",
        "",
        "### 評分明細",
        "",
    ]
    
    for category, detail in health_score["details"].items():
        report_lines.append(f"#### {category}")
        report_lines.append(f"- **得分：** {detail['score']}/{detail['max']}")
        report_lines.append(f"- **詳情：** {detail['details']}")
        report_lines.append("")
    
    report_lines.extend([
        "## 📦 容器狀態",
        "",
        f"- **總容器數：** {containers.get('total', 0)}",
        f"- **運行中：** {containers.get('running', 0)}",
        f"- **已停止：** {containers.get('stopped', 0)}",
        f"- **重啟中：** {containers.get('restarting', 0)}",
        "",
        "### 容器列表",
        "",
    ])
    
    for container in containers.get("containers", [])[:10]:  # 顯示前10個
        status_icon = "✅" if "Up" in container.get("status", "") else "❌"
        report_lines.append(f"- {status_icon} {container.get('name', 'N/A')}: {container.get('status', 'N/A')}")
    
    report_lines.extend([
        "",
        "## 💾 資源使用",
        "",
        f"- **可用記憶體：** {resources.get('memory', {}).get('free_gb', 'N/A')} GB",
        f"- **可用磁碟空間：** {resources.get('disk', {}).get('free_gb', 'N/A')} GB",
        "",
        "## 🌐 服務可用性",
        "",
    ])
    
    for service_name, service_info in services.items():
        status_icon = "✅" if service_info.get("status") == "available" else "❌"
        report_lines.append(f"- {status_icon} {service_name} (端口 {service_info.get('port', 'N/A')}): {service_info.get('status', 'unknown')}")
    
    return "\n".join(report_lines)

def main():
    """主函數"""
    print("=" * 70)
    print("系統健康度評估")
    print("權限等級：🔐 最高權限")
    print("=" * 70)
    print()
    
    if log_manager:
        log_manager.log_work(
            work_type="系統健康度評估",
            work_content="進行系統健康度評估（容器、資源、服務）",
            agent="little_j",
            status="進行中",
            permission_level="最高權限"
        )
    
    # 檢查容器
    containers = check_containers()
    
    # 檢查資源
    resources = check_resources()
    
    # 檢查服務
    services = check_services()
    
    # 計算健康度評分
    health_score = calculate_health_score(containers, resources, services)
    
    # 顯示評分結果
    print()
    log(f"系統健康度總評: {health_score['total_score']}/{health_score['max_score']} ({health_score['grade']})", "INFO")
    print()
    log("評分明細:", "INFO")
    for category, detail in health_score["details"].items():
        log(f"  {category}: {detail['score']}/{detail['max']} - {detail['details']}", "INFO")
    
    # 產生報告
    report = generate_health_report(containers, resources, services, health_score)
    report_file = REPORTS_DIR / f"SYSTEM_HEALTH_ASSESSMENT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_file.write_text(report, encoding='utf-8')
    log(f"✓ 健康度報告已儲存: {report_file}", "OK")
    
    # 記錄完成
    if log_manager:
        result_summary = (
            f"健康度總評: {health_score['total_score']}/{health_score['max_score']} ({health_score['grade']}), "
            f"容器: {containers.get('running', 0)}/{containers.get('total', 0)} 運行中, "
            f"服務: {sum(1 for s in services.values() if s.get('status') == 'available')}/{len(services)} 可用"
        )
        
        log_manager.log_work(
            work_type="系統健康度評估",
            work_content="進行系統健康度評估（容器、資源、服務）",
            agent="little_j",
            status="完成",
            result=result_summary,
            related_files=[str(report_file)],
            permission_level="最高權限"
        )
    
    log("✅ 系統健康度評估完成", "OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
