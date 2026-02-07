#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uninstall_and_deploy_workflow.py

完整卸載後進行雙J全面部署工作流程
- 步驟1: 完整卸載
- 步驟2: 設定地端機固定IP
- 步驟3: 配置路由器端口轉發
- 步驟4: 雙J全面部署（自動替換DNS）
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


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry)


def step1_complete_uninstall(backup_dir: Path = None, dry_run: bool = False) -> bool:
    """步驟1: 完整卸載"""
    log("=" * 60, "INFO")
    log("步驟 1: 完整卸載", "INFO")
    log("=" * 60, "INFO")
    
    try:
        import subprocess
        cmd = [sys.executable, str(BASE_DIR / "complete_uninstall.py")]
        
        if backup_dir:
            cmd.extend(["--backup-dir", str(backup_dir)])
        if dry_run:
            cmd.append("--dry-run")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            log("完整卸載成功", "INFO")
            return True
        else:
            log(f"完整卸載失敗: {result.stderr}", "ERROR")
            return False
    except Exception as e:
        log(f"執行完整卸載失敗: {e}", "ERROR")
        return False


def step2_setup_fixed_ip(fixed_ip: str = "192.168.50.100", dry_run: bool = False) -> bool:
    """步驟2: 設定地端機固定IP"""
    log("=" * 60, "INFO")
    log("步驟 2: 設定地端機固定IP", "INFO")
    log("=" * 60, "INFO")
    
    try:
        import subprocess
        cmd = [sys.executable, str(BASE_DIR / "local_machine_fixed_ip_setup.py"),
               "--ip", fixed_ip,
               "--configure-router"]
        
        if dry_run:
            cmd.append("--dry-run")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            log("地端機固定IP設定成功", "INFO")
            return True
        else:
            log(f"地端機固定IP設定失敗: {result.stderr}", "ERROR")
            return False
    except Exception as e:
        log(f"執行地端機固定IP設定失敗: {e}", "ERROR")
        return False


def step3_configure_router_mounts(dry_run: bool = False) -> bool:
    """步驟3: 配置路由器掛載管理"""
    log("=" * 60, "INFO")
    log("步驟 3: 配置路由器掛載管理", "INFO")
    log("=" * 60, "INFO")
    
    try:
        import subprocess
        cmd = [sys.executable, str(BASE_DIR / "router_mount_management.py"),
               "--all"]
        
        if dry_run:
            cmd.append("--dry-run")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            log("路由器掛載管理配置成功", "INFO")
            return True
        else:
            log(f"路由器掛載管理配置失敗: {result.stderr}", "ERROR")
            return False
    except Exception as e:
        log(f"執行路由器掛載管理配置失敗: {e}", "ERROR")
        return False


def step4_dual_j_full_deployment(server_dir: str = None, health_url: str = None, dry_run: bool = False) -> bool:
    """步驟4: 雙J全面部署（自動替換DNS）"""
    log("=" * 60, "INFO")
    log("步驟 4: 雙J全面部署（自動替換DNS）", "INFO")
    log("=" * 60, "INFO")
    
    try:
        import subprocess
        cmd = [sys.executable, str(BASE_DIR / "dual_j_full_deployment.py")]
        
        if server_dir:
            cmd.extend(["--server-dir", server_dir])
        if health_url:
            cmd.extend(["--health-url", health_url])
        if dry_run:
            cmd.append("--dry-run")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            log("雙J全面部署成功", "INFO")
            return True
        else:
            log(f"雙J全面部署失敗: {result.stderr}", "ERROR")
            return False
    except Exception as e:
        log(f"執行雙J全面部署失敗: {e}", "ERROR")
        return False


def add_work_log(agent: str, work_type: str, description: str, status: str = "completed", details: Dict = None, result: str = None):
    """記錄工作日誌"""
    try:
        from dual_j_work_log import add_work_log as _add_work_log
        _add_work_log(agent, work_type, description, status, details, result)
    except ImportError:
        log(f"[工作日誌] {agent}: {work_type} - {description}", "INFO")


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="完整卸載後進行雙J全面部署工作流程")
    parser.add_argument("--backup-dir", default=None, help="備份目錄")
    parser.add_argument("--fixed-ip", default="192.168.50.100", help="地端機固定IP")
    parser.add_argument("--server-dir", default=None, help="伺服器目錄（覆蓋 WUCHANG_COPY_TO）")
    parser.add_argument("--health-url", default=None, help="伺服器健康檢查 URL（覆蓋 WUCHANG_HEALTH_URL）")
    parser.add_argument("--skip-uninstall", action="store_true", help="跳過卸載步驟")
    parser.add_argument("--skip-fixed-ip", action="store_true", help="跳過固定IP設定")
    parser.add_argument("--skip-router", action="store_true", help="跳過路由器配置")
    parser.add_argument("--skip-deployment", action="store_true", help="跳過部署步驟")
    parser.add_argument("--dry-run", action="store_true", help="模擬執行")
    
    args = parser.parse_args()
    
    log("=" * 60, "INFO")
    log("完整卸載後進行雙J全面部署工作流程", "INFO")
    log("=" * 60, "INFO")
    
    if args.dry_run:
        log("【模擬模式】不會實際執行", "INFO")
    
    # 記錄工作日誌
    add_work_log("地端小 j", "完整部署流程", "開始完整卸載和部署流程", "in_progress")
    
    results = {
        "uninstall": None,
        "fixed_ip": None,
        "router": None,
        "deployment": None
    }
    
    # 步驟1: 完整卸載
    if not args.skip_uninstall:
        backup_dir = Path(args.backup_dir) if args.backup_dir else BASE_DIR / "backups"
        results["uninstall"] = step1_complete_uninstall(backup_dir, args.dry_run)
        if not results["uninstall"] and not args.dry_run:
            log("卸載失敗，中止流程", "ERROR")
            return
    else:
        log("跳過卸載步驟", "INFO")
        results["uninstall"] = True
    
    # 步驟2: 設定地端機固定IP
    if not args.skip_fixed_ip:
        results["fixed_ip"] = step2_setup_fixed_ip(args.fixed_ip, args.dry_run)
    else:
        log("跳過固定IP設定", "INFO")
        results["fixed_ip"] = True
    
    # 步驟3: 配置路由器掛載管理
    if not args.skip_router:
        results["router"] = step3_configure_router_mounts(args.dry_run)
    else:
        log("跳過路由器配置", "INFO")
        results["router"] = True
    
    # 步驟4: 雙J全面部署
    if not args.skip_deployment:
        server_dir = args.server_dir or os.getenv("WUCHANG_COPY_TO", "")
        health_url = args.health_url or os.getenv("WUCHANG_HEALTH_URL", "https://wuchang.life/health")
        
        if not server_dir:
            log("錯誤: 請提供 --server-dir 或設定 WUCHANG_COPY_TO 環境變數", "ERROR")
            results["deployment"] = False
        else:
            results["deployment"] = step4_dual_j_full_deployment(server_dir, health_url, args.dry_run)
    else:
        log("跳過部署步驟", "INFO")
        results["deployment"] = True
    
    # 生成報告
    log("\n" + "=" * 60, "INFO")
    log("執行摘要", "INFO")
    log("=" * 60, "INFO")
    log(f"卸載: {'✓' if results['uninstall'] else '✗'}", "INFO")
    log(f"固定IP設定: {'✓' if results['fixed_ip'] else '✗'}", "INFO")
    log(f"路由器配置: {'✓' if results['router'] else '✗'}", "INFO")
    log(f"部署: {'✓' if results['deployment'] else '✗'}", "INFO")
    
    all_success = all(results.values())
    
    # 記錄工作日誌
    if all_success:
        add_work_log("地端小 j", "完整部署流程", "完整卸載和部署流程完成", "completed",
                    results, "所有步驟執行成功")
        log("\n所有步驟執行成功！", "INFO")
    else:
        add_work_log("地端小 j", "完整部署流程", "完整卸載和部署流程部分失敗", "failed",
                    results, "部分步驟執行失敗")
        log("\n部分步驟執行失敗，請檢查日誌", "ERROR")
    
    log("=" * 60, "INFO")
    
    # 儲存報告
    report = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "all_success": all_success,
        "fixed_ip": args.fixed_ip,
        "server_dir": args.server_dir or os.getenv("WUCHANG_COPY_TO", ""),
    }
    
    report_file = BASE_DIR / f"uninstall_deploy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    log(f"\n執行報告已儲存: {report_file}", "INFO")


if __name__ == "__main__":
    main()
