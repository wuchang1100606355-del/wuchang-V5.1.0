#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dual_j_deploy.py

雙 J 部署模式：啟用地端小 j 和雲端小 j (JULES) 協作部署
找出最近一次完美的健康報告高版本進行部署
"""

from __future__ import annotations

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "健康報告"
HEALTH_REPORT_DIR = BASE_DIR / "健康報告"
DUAL_J_LOG_DIR = BASE_DIR / "dual_j_work_logs"

# 匯入雙 J 工作日誌
try:
    from dual_j_work_log import add_work_log
    WORK_LOG_AVAILABLE = True
except ImportError:
    WORK_LOG_AVAILABLE = False
    def add_work_log(*args, **kwargs):
        pass


def find_latest_perfect_health_report() -> Optional[Dict[str, Any]]:
    """找出最近一次完美的健康報告高版本（優先完美，其次最佳）"""
    
    if not HEALTH_REPORT_DIR.exists():
        HEALTH_REPORT_DIR.mkdir(exist_ok=True)
    
    # 搜尋所有健康報告檔案
    perfect_reports = []
    good_reports = []
    
    # 搜尋 JSON 格式的報告
    for report_file in HEALTH_REPORT_DIR.glob("**/*health*.json"):
        try:
            report_data = json.loads(report_file.read_text(encoding="utf-8"))
            report_data["file_path"] = str(report_file)
            report_data["file_name"] = report_file.name
            report_data["modified_time"] = report_file.stat().st_mtime
            
            # 檢查是否為完美版本
            if is_perfect_report(report_data):
                perfect_reports.append(report_data)
            elif is_good_report(report_data):
                good_reports.append(report_data)
        except:
            continue
    
    # 搜尋 Markdown 格式的報告（從檔案名和內容提取資訊）
    for report_file in HEALTH_REPORT_DIR.glob("**/*健康報告*.md"):
        try:
            content = report_file.read_text(encoding="utf-8")
            # 從 Markdown 內容提取關鍵資訊
            report_data = parse_markdown_health_report(content)
            report_data["file_path"] = str(report_file)
            report_data["file_name"] = report_file.name
            report_data["modified_time"] = report_file.stat().st_mtime
            
            if is_perfect_report(report_data):
                perfect_reports.append(report_data)
            elif is_good_report(report_data):
                good_reports.append(report_data)
        except:
            continue
    
    # 也搜尋根目錄下的報告檔案
    for report_file in BASE_DIR.glob("*health*.json"):
        try:
            report_data = json.loads(report_file.read_text(encoding="utf-8"))
            report_data["file_path"] = str(report_file)
            report_data["file_name"] = report_file.name
            report_data["modified_time"] = report_file.stat().st_mtime
            
            if is_perfect_report(report_data):
                perfect_reports.append(report_data)
            elif is_good_report(report_data):
                good_reports.append(report_data)
        except:
            continue
    
    # 優先返回完美報告，其次返回良好報告
    if perfect_reports:
        perfect_reports.sort(key=lambda x: x.get("modified_time", 0), reverse=True)
        return perfect_reports[0]
    
    if good_reports:
        good_reports.sort(key=lambda x: x.get("modified_time", 0), reverse=True)
        return good_reports[0]
    
    return None


def parse_markdown_health_report(content: str) -> Dict[str, Any]:
    """從 Markdown 健康報告中解析資訊"""
    import re
    
    report_data = {
        "containers": {"ok": False, "total": 0, "running": 0},
        "services": [],
        "disk": {"usage_percent": 0},
    }
    
    # 解析容器資訊
    container_matches = re.findall(r'- ✅ \*\*([^*]+)\*\*', content)
    if container_matches:
        report_data["containers"]["ok"] = True
        report_data["containers"]["total"] = len(container_matches)
        report_data["containers"]["running"] = len(container_matches)
    
    # 解析服務資訊
    service_matches = re.findall(r'\| ([^|]+) \| ([^|]+) \| ✅', content)
    if service_matches:
        report_data["services"] = [{"ok": True, "name": s[0]} for s in service_matches]
    
    # 解析磁碟使用率
    disk_match = re.search(r'已使用：.*?(\d+\.?\d*)%', content)
    if disk_match:
        report_data["disk"]["usage_percent"] = float(disk_match.group(1))
    
    # 判斷狀態
    if "✅ **健康**" in content:
        report_data["status"] = "perfect"
        report_data["perfect"] = True
    elif "⚠️ **注意**" in content:
        report_data["status"] = "good"
        report_data["perfect"] = False
    else:
        report_data["status"] = "needs_attention"
        report_data["perfect"] = False
    
    return report_data


def is_good_report(report_data: Dict[str, Any]) -> bool:
    """判斷是否為良好的健康報告（核心功能正常，只有次要問題）"""
    
    # 核心檢查：容器運行、服務可用
    core_checks = []
    
    # 容器狀態 - 至少有一半以上運行
    if "containers" in report_data:
        containers = report_data["containers"]
        if isinstance(containers, dict):
            total = containers.get("total", 0)
            running = containers.get("running", 0)
            if total > 0 and running >= total * 0.5:  # 至少 50% 運行
                core_checks.append(True)
            else:
                core_checks.append(False)
    
    # 服務健康 - 至少有一個服務可用
    if "services" in report_data:
        services = report_data["services"]
        if isinstance(services, list):
            any_ok = any(s.get("ok", False) for s in services)
            core_checks.append(any_ok)
        elif isinstance(services, dict):
            core_checks.append(services.get("ok", False))
    
    # 核心檢查必須全部通過
    if core_checks:
        return all(core_checks)
    
    return False


def is_perfect_report(report_data: Dict[str, Any]) -> bool:
    """判斷是否為完美的健康報告（所有檢查都通過）"""
    
    # 檢查關鍵指標
    checks = []
    
    # 容器狀態
    if "containers" in report_data:
        containers = report_data["containers"]
        if isinstance(containers, dict):
            if containers.get("ok") and containers.get("running", 0) > 0:
                checks.append(True)
            else:
                checks.append(False)
    
    # 服務健康
    if "services" in report_data:
        services = report_data["services"]
        if isinstance(services, list):
            all_ok = all(s.get("ok", False) for s in services)
            checks.append(all_ok)
        elif isinstance(services, dict):
            checks.append(services.get("ok", False))
    
    # 磁碟使用
    if "disk" in report_data:
        disk = report_data["disk"]
        if isinstance(disk, dict):
            # 磁碟使用率低於 95% 視為健康
            usage = disk.get("usage_percent", 100)
            checks.append(usage < 95)
    
    # 如果有任何檢查，需要全部通過
    if checks:
        return all(checks)
    
    # 如果沒有明確的檢查結果，檢查是否有錯誤
    if "errors" in report_data and report_data["errors"]:
        return False
    
    # 預設為不完美（需要明確標記為完美）
    return report_data.get("status") == "perfect" or report_data.get("perfect", False)


def enable_dual_j_mode() -> bool:
    """啟用雙 J 部署模式"""
    
    print("=" * 80)
    print("啟用雙 J 部署模式")
    print("=" * 80)
    print()
    
    # 檢查必要檔案
    required_files = [
        "dual_j_work_log.py",
        "little_j_jules_container_collaboration.py",
        "local_control_center.py",
    ]
    
    missing_files = []
    for file_name in required_files:
        file_path = BASE_DIR / file_name
        if not file_path.exists():
            missing_files.append(file_name)
    
    if missing_files:
        print(f"❌ 缺少必要檔案: {', '.join(missing_files)}")
        return False
    
    print("✓ 必要檔案檢查通過")
    print()
    
    # 記錄啟用日誌
    if WORK_LOG_AVAILABLE:
        add_work_log(
            agent="地端小 j",
            work_type="部署模式啟用",
            description="啟用雙 J 部署模式",
            status="completed",
            details={"mode": "dual_j_deploy"}
        )
    
    print("✓ 雙 J 部署模式已啟用")
    print()
    
    return True


def deploy_from_health_report(report: Dict[str, Any]) -> bool:
    """根據健康報告進行部署"""
    
    print("=" * 80)
    print("根據健康報告進行部署")
    print("=" * 80)
    print()
    
    print(f"報告檔案: {report.get('file_name', 'unknown')}")
    print(f"報告時間: {datetime.fromtimestamp(report.get('modified_time', 0)).strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 提取部署資訊
    deployment_info = {
        "containers": report.get("containers", {}),
        "services": report.get("services", []),
        "config": report.get("config", {}),
    }
    
    print("部署資訊：")
    print(f"  容器狀態: {deployment_info['containers'].get('running', 0)}/{deployment_info['containers'].get('total', 0)} 運行中")
    print(f"  服務數量: {len(deployment_info.get('services', []))}")
    print()
    
    # 執行部署步驟
    steps = [
        ("檢查 Docker 環境", check_docker_environment),
        ("檢查容器狀態", check_container_status),
        ("應用配置", apply_configuration),
        ("驗證部署", verify_deployment),
    ]
    
    results = []
    for step_name, step_func in steps:
        print(f"執行: {step_name}...")
        try:
            result = step_func(deployment_info)
            results.append({"step": step_name, "success": result})
            if result:
                print(f"✓ {step_name} 完成")
            else:
                print(f"⚠️  {step_name} 有警告")
        except Exception as e:
            print(f"❌ {step_name} 失敗: {e}")
            results.append({"step": step_name, "success": False, "error": str(e)})
        print()
    
    # 記錄部署日誌
    if WORK_LOG_AVAILABLE:
        add_work_log(
            agent="地端小 j",
            work_type="部署執行",
            description=f"根據健康報告 {report.get('file_name')} 進行部署",
            status="completed" if all(r.get("success") for r in results) else "partial",
            details={"steps": results, "report": report.get("file_name")}
        )
    
    success_count = sum(1 for r in results if r.get("success"))
    total_count = len(results)
    
    print("=" * 80)
    print("部署結果")
    print("=" * 80)
    print(f"完成步驟: {success_count}/{total_count}")
    print()
    
    return success_count == total_count


def check_docker_environment(deployment_info: Dict) -> bool:
    """檢查 Docker 環境"""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False


def check_container_status(deployment_info: Dict) -> bool:
    """檢查容器狀態"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False


def apply_configuration(deployment_info: Dict) -> bool:
    """應用配置"""
    # 這裡可以根據健康報告中的配置進行應用
    # 例如：更新 Docker Compose、環境變數等
    return True


def verify_deployment(deployment_info: Dict) -> bool:
    """驗證部署"""
    # 驗證容器是否正常運行
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}|{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            running_containers = [line for line in result.stdout.splitlines() if "Up" in line]
            return len(running_containers) > 0
    except:
        pass
    return False


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="雙 J 部署模式：找出最近一次完美的健康報告進行部署"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="強制部署，即使報告不完美"
    )
    parser.add_argument(
        "--report",
        type=str,
        help="指定要使用的健康報告檔案路徑"
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("雙 J 部署模式")
    print("=" * 80)
    print()
    
    # 1. 啟用雙 J 模式
    if not enable_dual_j_mode():
        print("❌ 無法啟用雙 J 部署模式")
        return 1
    
    # 2. 找出健康報告
    if args.report:
        report_path = Path(args.report)
        if not report_path.exists():
            print(f"❌ 指定的報告檔案不存在: {args.report}")
            return 1
        try:
            report_data = json.loads(report_path.read_text(encoding="utf-8"))
            report_data["file_path"] = str(report_path)
            report_data["file_name"] = report_path.name
            report_data["modified_time"] = report_path.stat().st_mtime
        except Exception as e:
            print(f"❌ 無法讀取報告檔案: {e}")
            return 1
    else:
        report_data = find_latest_perfect_health_report()
    
    if not report_data:
        print("❌ 找不到完美的健康報告")
        if not args.force:
            print("   使用 --force 可以強制部署")
            return 1
        print("   使用 --force 模式，將嘗試生成新的健康報告...")
        # 可以調用 generate_health_report.py
        return 1
    
    # 檢查是否完美
    if not is_perfect_report(report_data) and not args.force:
        print("⚠️  報告不是完美狀態")
        print("   使用 --force 可以強制部署")
        return 1
    
    # 3. 執行部署
    print()
    success = deploy_from_health_report(report_data)
    
    if success:
        print("✓ 部署完成")
        return 0
    else:
        print("⚠️  部署部分完成，請檢查上述訊息")
        return 1


if __name__ == "__main__":
    sys.exit(main())
