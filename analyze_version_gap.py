#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_version_gap.py

版本差距原因分析工具

分析可能導致本機與根伺服器版本差距的原因：
1. 環境變數未設定，無法連接到真實伺服器
2. 長時間未同步
3. 在不同位置修改檔案
4. 同步機制未正常運作
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def analyze_version_gap_reasons() -> dict:
    """分析版本差距可能原因"""
    reasons = {
        "environment_not_configured": False,
        "sync_not_performed": False,
        "files_modified_independently": False,
        "sync_mechanism_issues": False,
        "specific_issues": [],
    }
    
    # 1. 檢查環境變數是否設定
    health_url = os.getenv("WUCHANG_HEALTH_URL", "")
    copy_to = os.getenv("WUCHANG_COPY_TO", "")
    
    if not health_url or not copy_to:
        reasons["environment_not_configured"] = True
        reasons["specific_issues"].append(
            "環境變數未設定：無法連接到真實根伺服器進行版本比對"
        )
    
    # 2. 檢查是否有同步記錄
    audit_file = BASE_DIR / "risk_action_audit.jsonl"
    if audit_file.exists():
        try:
            with open(audit_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                sync_records = [l for l in lines if "sync_push" in l.lower()]
                if not sync_records:
                    reasons["sync_not_performed"] = True
                    reasons["specific_issues"].append(
                        "無同步記錄：稽核日誌中未發現同步操作記錄"
                    )
        except Exception:
            pass
    
    # 3. 分析可能的原因
    analysis = {
        "timestamp": __import__("time").strftime("%Y-%m-%dT%H:%M:%S%z"),
        "environment_configured": bool(health_url and copy_to),
        "possible_reasons": [],
        "recommendations": [],
    }
    
    # 可能原因
    if reasons["environment_not_configured"]:
        analysis["possible_reasons"].append({
            "type": "環境變數未設定",
            "description": "WUCHANG_COPY_TO 或 WUCHANG_HEALTH_URL 未設定，無法連接到真實根伺服器",
            "impact": "高",
        })
        analysis["recommendations"].append(
            "設定環境變數：使用 setup_file_sync_env.ps1 或 setup_env_vars.py 設定 WUCHANG_COPY_TO 和 WUCHANG_HEALTH_URL"
        )
    
    if reasons["sync_not_performed"]:
        analysis["possible_reasons"].append({
            "type": "長時間未同步",
            "description": "稽核日誌中無同步記錄，可能長時間未執行同步操作",
            "impact": "高",
        })
        analysis["recommendations"].append(
            "執行同步：使用 smart_sync.py 或 safe_sync_push.py 進行檔案同步"
        )
    
    # 其他常見原因
    analysis["possible_reasons"].extend([
        {
            "type": "本機與伺服器獨立修改",
            "description": "在本機和伺服器上分別修改檔案，未及時同步",
            "impact": "中",
        },
        {
            "type": "同步失敗但未被察覺",
            "description": "同步操作失敗（如健康檢查未通過）但未注意到",
            "impact": "中",
        },
        {
            "type": "使用測試目錄而非真實伺服器",
            "description": "目前連接到測試目錄（如 test_server_dir），而非真實根伺服器",
            "impact": "高",
        },
    ])
    
    analysis["recommendations"].extend([
        "檢查 WUCHANG_COPY_TO 是否指向真實伺服器目錄（非測試目錄）",
        "確認伺服器健康檢查 URL 可達",
        "執行版本差距分析：python check_version_diff.py --profile [kb|rules]",
        "執行擇優同步：python smart_sync.py --profile [kb|rules]",
    ])
    
    return analysis


def print_analysis(analysis: dict) -> None:
    """列印分析報告"""
    # 設定 UTF-8 編碼輸出
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except:
            pass
    
    print("=" * 70)
    print("版本差距原因分析")
    print("=" * 70)
    print(f"分析時間: {analysis['timestamp']}\n")
    
    print("【環境配置狀態】")
    if analysis["environment_configured"]:
        print("  [OK] 環境變數已設定，可連接到根伺服器")
    else:
        print("  [X] 環境變數未設定，無法連接到真實根伺服器")
    print()
    
    print("【可能原因分析】")
    for i, reason in enumerate(analysis["possible_reasons"], 1):
        impact_icon = {"高": "⚠️", "中": "🔶", "低": "ℹ️"}.get(reason["impact"], "•")
        print(f"  {i}. {impact_icon} {reason['type']} (影響: {reason['impact']})")
        print(f"     說明: {reason['description']}")
    print()
    
    print("【改善建議】")
    for i, rec in enumerate(analysis["recommendations"], 1):
        print(f"  {i}. {rec}")
    print()
    
    print("=" * 70)
    print("\n【下一步操作】")
    print("1. 設定環境變數連接真實伺服器")
    print("   python setup_env_vars.py status")
    print("   .\\setup_file_sync_env.ps1")
    print()
    print("2. 檢查真實伺服器版本差距")
    print("   python check_version_diff.py --profile kb")
    print("   python check_version_diff.py --profile rules")
    print()
    print("3. 執行擇優同步")
    print("   python smart_sync.py --profile kb --direction both")
    print("   python sync_all_profiles.py")
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="版本差距原因分析")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式輸出")
    
    args = parser.parse_args()
    
    analysis = analyze_version_gap_reasons()
    
    if args.json:
        import json
        print(json.dumps(analysis, ensure_ascii=False, indent=2))
    else:
        print_analysis(analysis)
