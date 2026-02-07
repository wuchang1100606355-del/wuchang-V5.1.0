#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
execute_plan.py

執行規劃步驟

功能：
- 按照規劃步驟執行任務
- 檢查每個步驟的完成狀態
- 生成執行報告
"""

import sys
import json
import time
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def check_step_status(step_name: str, check_function) -> dict:
    """檢查步驟狀態"""
    try:
        result = check_function()
        return {
            "step": step_name,
            "status": "completed" if result else "pending",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")
        }
    except Exception as e:
        return {
            "step": step_name,
            "status": "error",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")
        }


def check_network_share():
    """檢查網路共享"""
    from pathlib import Path
    test_paths = [
        "Z:\\",
        "\\\\HOME-COMMPUT\\wuchang V5.1.0",
        "\\\\HOME-COMPUTER\\wuchang V5.1.0",
    ]
    
    for path_str in test_paths:
        try:
            if Path(path_str).exists():
                return True
        except:
            continue
    return False


def check_server_connection():
    """檢查伺服器連接"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("10.8.0.1", 8788))
        sock.close()
        return result == 0
    except:
        return False


def check_workspace_config():
    """檢查工作區配置"""
    import os
    required_vars = [
        "WUCHANG_SYSTEM_DB_DIR",
        "WUCHANG_WORKSPACE_OUTDIR",
    ]
    
    for var in required_vars:
        if not os.getenv(var):
            return False
    return True


def check_environment_variables():
    """檢查環境變數"""
    import os
    required_vars = [
        "WUCHANG_COPY_TO",
        "WUCHANG_HEALTH_URL",
    ]
    
    for var in required_vars:
        if not os.getenv(var):
            return False
    return True


def main():
    """主函數"""
    print("=" * 70)
    print("執行規劃步驟檢查")
    print("=" * 70)
    print()
    
    steps = [
        ("網路共享連接", check_network_share),
        ("伺服器連接", check_server_connection),
        ("工作區配置", check_workspace_config),
        ("環境變數", check_environment_variables),
    ]
    
    results = []
    completed = 0
    
    for step_name, check_func in steps:
        print(f"【檢查】{step_name}")
        result = check_step_status(step_name, check_func)
        results.append(result)
        
        if result["status"] == "completed":
            print(f"  ✓ {step_name}：已完成")
            completed += 1
        elif result["status"] == "error":
            print(f"  ✗ {step_name}：錯誤 - {result.get('error', '未知錯誤')}")
        else:
            print(f"  ○ {step_name}：待完成")
        print()
    
    # 生成報告
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "total_steps": len(steps),
        "completed_steps": completed,
        "completion_rate": f"{completed}/{len(steps)}",
        "steps": results
    }
    
    report_file = BASE_DIR / "plan_execution_report.json"
    report_file.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    print("=" * 70)
    print("【執行摘要】")
    print(f"  總步驟數: {len(steps)}")
    print(f"  已完成: {completed}")
    print(f"  待完成: {len(steps) - completed}")
    print(f"  完成率: {completed/len(steps)*100:.1f}%")
    print()
    print(f"執行報告已儲存到: {report_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
