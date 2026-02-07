#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_all_profiles.py

執行所有 profile 的最優同步

功能：
- 按順序執行所有 profile 的擇優同步
- 生成完整同步報告
- 驗證同步結果
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent


def sync_profile(profile: str, server_dir: Path, dry_run: bool = False) -> Dict[str, Any]:
    """執行單一 profile 的同步"""
    try:
        from smart_sync import smart_sync
        from safe_sync_push import DEFAULT_FILES, RULE_FILES
        
        if profile == "kb":
            files = DEFAULT_FILES
        elif profile == "rules":
            files = RULE_FILES
        else:
            return {"error": f"未知的 profile: {profile}"}
        
        results = smart_sync(
            files,
            BASE_DIR,
            server_dir,
            dry_run=dry_run,
            direction="both",
        )
        
        return {
            "profile": profile,
            "success": True,
            "results": results,
        }
    except Exception as e:
        return {
            "profile": profile,
            "success": False,
            "error": str(e),
        }


def sync_all_profiles(
    server_dir: str,
    profiles: List[str] = ["kb", "rules"],
    dry_run: bool = False,
) -> Dict[str, Any]:
    """執行所有 profile 的同步"""
    server_path = Path(server_dir).expanduser().resolve()
    
    summary = {
        "timestamp": __import__("time").strftime("%Y-%m-%dT%H:%M:%S%z"),
        "server_dir": str(server_path),
        "dry_run": dry_run,
        "profiles": [],
        "overall": {
            "total_profiles": len(profiles),
            "successful": 0,
            "failed": 0,
            "total_files_synced": 0,
        },
    }
    
    for profile in profiles:
        profile_result = sync_profile(profile, server_path, dry_run=dry_run)
        summary["profiles"].append(profile_result)
        
        if profile_result.get("success"):
            summary["overall"]["successful"] += 1
            results = profile_result.get("results", {})
            summary_data = results.get("summary", {})
            summary["overall"]["total_files_synced"] += (
                summary_data.get("synced_to_server", 0) +
                summary_data.get("synced_to_local", 0)
            )
        else:
            summary["overall"]["failed"] += 1
    
    return summary


def print_summary(summary: Dict[str, Any]) -> None:
    """列印同步摘要"""
    # 設定 UTF-8 編碼輸出
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except:
            pass
    
    mode_str = "（模擬模式）" if summary.get("dry_run") else ""
    
    print("=" * 70)
    print(f"最優同步完整報告 {mode_str}")
    print("=" * 70)
    print(f"同步時間: {summary['timestamp']}")
    print(f"伺服器目錄: {summary['server_dir']}\n")
    
    overall = summary["overall"]
    print("【整體摘要】")
    print(f"  總 Profile 數: {overall['total_profiles']}")
    print(f"  成功: {overall['successful']}")
    print(f"  失敗: {overall['failed']}")
    print(f"  同步檔案總數: {overall['total_files_synced']}\n")
    
    print("【各 Profile 詳情】")
    for profile_result in summary["profiles"]:
        profile = profile_result["profile"]
        if profile_result.get("success"):
            results = profile_result.get("results", {})
            summary_data = results.get("summary", {})
            print(f"\n  Profile: {profile}")
            print(f"    狀態: [成功]")
            print(f"    同步到伺服器: {summary_data.get('synced_to_server', 0)}")
            print(f"    同步到本機: {summary_data.get('synced_to_local', 0)}")
            print(f"    無需同步: {summary_data.get('no_sync_needed', 0)}")
            print(f"    失敗: {summary_data.get('failed', 0)}")
        else:
            print(f"\n  Profile: {profile}")
            print(f"    狀態: [失敗]")
            print(f"    錯誤: {profile_result.get('error', 'unknown')}")
    
    print("\n" + "=" * 70)


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="執行所有 profile 的最優同步")
    parser.add_argument(
        "--server-dir",
        type=str,
        help="伺服器目錄（也可用 WUCHANG_COPY_TO 環境變數）",
    )
    parser.add_argument(
        "--profiles",
        nargs="+",
        choices=["kb", "rules"],
        default=["kb", "rules"],
        help="要同步的 profile 清單（預設：kb rules）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="模擬模式（不實際執行同步）",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式輸出",
    )
    
    args = parser.parse_args()
    
    # 決定伺服器目錄
    server_dir_str = args.server_dir or os.getenv("WUCHANG_COPY_TO", "")
    
    if not server_dir_str:
        print("錯誤: 請提供 --server-dir 參數或設定 WUCHANG_COPY_TO 環境變數", file=sys.stderr)
        return 1
    
    # 執行所有 profile 的同步
    summary = sync_all_profiles(
        server_dir_str,
        profiles=args.profiles,
        dry_run=args.dry_run,
    )
    
    # 輸出結果
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print_summary(summary)
    
    # 返回碼
    if summary["overall"]["failed"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
