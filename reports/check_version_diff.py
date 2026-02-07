#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_version_diff.py

版本差距分析工具

功能：
- 分析本機與伺服器之間的版本差距
- 比較檔案修改時間、大小、內容差異
- 生成版本差距報告
- 提供同步建議
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

BASE_DIR = Path(__file__).resolve().parent


def sha256_file(path: Path) -> str:
    """計算檔案 SHA256 雜湊值"""
    sha256_hash = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        return f"error: {str(e)}"


def get_file_info(path: Path) -> Optional[Dict[str, Any]]:
    """獲取檔案資訊"""
    try:
        if not path.exists():
            return None
        
        stat = path.stat()
        return {
            "path": str(path),
            "name": path.name,
            "exists": True,
            "size": stat.st_size,
            "mtime": stat.st_mtime,
            "mtime_iso": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(stat.st_mtime)),
            "sha256": sha256_file(path),
        }
    except Exception as e:
        return {
            "path": str(path),
            "name": path.name if path else "unknown",
            "exists": False,
            "error": str(e),
        }


def analyze_version_diff(
    files: List[str],
    local_dir: Path,
    server_dir: Optional[Path],
) -> Dict[str, Any]:
    """分析版本差距"""
    if not server_dir or not server_dir.exists():
        return {
            "error": "伺服器目錄不存在或未設定",
            "server_dir": str(server_dir) if server_dir else None,
        }
    
    analysis = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "local_dir": str(local_dir),
        "server_dir": str(server_dir),
        "files": [],
        "summary": {
            "total": 0,
            "only_local": 0,
            "only_server": 0,
            "different": 0,
            "same": 0,
            "local_newer": 0,
            "server_newer": 0,
        },
    }
    
    for filename in files:
        local_path = (local_dir / filename).resolve()
        server_path = (server_dir / filename).resolve()
        
        local_info = get_file_info(local_path)
        server_info = get_file_info(server_path)
        
        file_diff = {
            "filename": filename,
            "local": local_info,
            "server": server_info,
            "diff_type": "unknown",
            "time_diff_seconds": None,
            "size_diff": None,
        }
        
        analysis["summary"]["total"] += 1
        
        if local_info is None or not local_info.get("exists"):
            file_diff["diff_type"] = "only_server"
            analysis["summary"]["only_server"] += 1
        elif server_info is None or not server_info.get("exists"):
            file_diff["diff_type"] = "only_local"
            analysis["summary"]["only_local"] += 1
        elif local_info.get("sha256") == server_info.get("sha256"):
            file_diff["diff_type"] = "same"
            analysis["summary"]["same"] += 1
        else:
            file_diff["diff_type"] = "different"
            analysis["summary"]["different"] += 1
            
            # 比較修改時間
            local_mtime = local_info.get("mtime", 0)
            server_mtime = server_info.get("mtime", 0)
            time_diff = local_mtime - server_mtime
            file_diff["time_diff_seconds"] = time_diff
            
            if time_diff > 0:
                analysis["summary"]["local_newer"] += 1
            elif time_diff < 0:
                analysis["summary"]["server_newer"] += 1
            
            # 比較大小
            local_size = local_info.get("size", 0)
            server_size = server_info.get("size", 0)
            file_diff["size_diff"] = local_size - server_size
        
        analysis["files"].append(file_diff)
    
    return analysis


def print_version_diff_report(analysis: Dict[str, Any]) -> None:
    """列印版本差距報告"""
    # 設定 UTF-8 編碼輸出
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except:
            pass
    
    if "error" in analysis:
        print(f"[錯誤] {analysis['error']}")
        return
    
    print("=" * 70)
    print("版本差距分析報告")
    print("=" * 70)
    print(f"分析時間: {analysis['timestamp']}")
    print(f"本機目錄: {analysis['local_dir']}")
    print(f"伺服器目錄: {analysis['server_dir']}\n")
    
    summary = analysis["summary"]
    print("【差距摘要】")
    print(f"  總檔案數: {summary['total']}")
    print(f"  內容相同: {summary['same']}")
    print(f"  內容不同: {summary['different']}")
    print(f"    本機較新: {summary['local_newer']}")
    print(f"    伺服器較新: {summary['server_newer']}")
    print(f"  僅本機存在: {summary['only_local']}")
    print(f"  僅伺服器存在: {summary['only_server']}\n")
    
    # 計算差距程度
    total_diff = summary['different'] + summary['only_local'] + summary['only_server']
    sync_rate = (summary['same'] / summary['total'] * 100) if summary['total'] > 0 else 0
    
    print("【同步狀態】")
    print(f"  同步率: {sync_rate:.1f}%")
    print(f"  差距檔案數: {total_diff}")
    
    if sync_rate >= 90:
        gap_level = "差距很小"
    elif sync_rate >= 70:
        gap_level = "差距中等"
    elif sync_rate >= 50:
        gap_level = "差距較大"
    else:
        gap_level = "差距很大"
    
    print(f"  差距程度: {gap_level}\n")
    
    # 詳細檔案差異
    if total_diff > 0:
        print("【差異檔案詳情】")
        for file_diff in analysis["files"]:
            diff_type = file_diff["diff_type"]
            if diff_type == "same":
                continue
            
            filename = file_diff["filename"]
            print(f"\n  檔案: {filename}")
            print(f"    差異類型: {diff_type}")
            
            local = file_diff.get("local")
            server = file_diff.get("server")
            
            if diff_type == "only_local":
                if local:
                    print(f"    本機: {local.get('mtime_iso')} ({local.get('size')} bytes)")
                    print(f"    伺服器: 不存在")
            elif diff_type == "only_server":
                if server:
                    print(f"    本機: 不存在")
                    print(f"    伺服器: {server.get('mtime_iso')} ({server.get('size')} bytes)")
            elif diff_type == "different":
                if local and server:
                    print(f"    本機: {local.get('mtime_iso')} ({local.get('size')} bytes)")
                    print(f"    伺服器: {server.get('mtime_iso')} ({server.get('size')} bytes)")
                    
                    time_diff = file_diff.get("time_diff_seconds", 0)
                    if time_diff > 0:
                        hours = time_diff / 3600
                        print(f"    時間差距: 本機較新 {abs(hours):.1f} 小時")
                    elif time_diff < 0:
                        hours = abs(time_diff) / 3600
                        print(f"    時間差距: 伺服器較新 {hours:.1f} 小時")
                    
                    size_diff = file_diff.get("size_diff", 0)
                    if size_diff != 0:
                        print(f"    大小差距: {size_diff:+d} bytes")
    
    print("\n" + "=" * 70)
    
    # 建議
    print("\n【同步建議】")
    if summary['local_newer'] > 0 or summary['only_local'] > 0:
        print(f"  • 建議執行同步到伺服器 ({summary['local_newer'] + summary['only_local']} 個檔案)")
        print("    命令: python smart_sync.py --profile [kb|rules] --direction server")
    
    if summary['server_newer'] > 0 or summary['only_server'] > 0:
        print(f"  • 建議從伺服器同步 ({summary['server_newer'] + summary['only_server']} 個檔案)")
        print("    命令: python smart_sync.py --profile [kb|rules] --direction local")
    
    if total_diff == 0:
        print("  • 所有檔案已同步，無需操作")


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="版本差距分析工具")
    parser.add_argument(
        "--files",
        nargs="+",
        help="要比對的檔案清單",
    )
    parser.add_argument(
        "--profile",
        choices=["kb", "rules"],
        help="使用預設檔案 profile",
    )
    parser.add_argument(
        "--local-dir",
        type=str,
        help="本機目錄（預設為腳本所在目錄）",
    )
    parser.add_argument(
        "--server-dir",
        type=str,
        help="伺服器目錄（也可用 WUCHANG_COPY_TO 環境變數）",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式輸出",
    )
    
    args = parser.parse_args()
    
    # 決定要比對的檔案
    if args.files:
        files_to_compare = args.files
    elif args.profile:
        if args.profile == "kb":
            from safe_sync_push import DEFAULT_FILES
            files_to_compare = DEFAULT_FILES
        elif args.profile == "rules":
            from safe_sync_push import RULE_FILES
            files_to_compare = RULE_FILES
        else:
            print("錯誤: 未知的 profile", file=sys.stderr)
            return 1
    else:
        print("錯誤: 請提供 --files 或 --profile 參數", file=sys.stderr)
        return 1
    
    # 決定目錄
    local_dir = Path(args.local_dir).resolve() if args.local_dir else BASE_DIR
    server_dir_str = args.server_dir or os.getenv("WUCHANG_COPY_TO", "")
    
    if not server_dir_str:
        print("錯誤: 請提供 --server-dir 參數或設定 WUCHANG_COPY_TO 環境變數", file=sys.stderr)
        return 1
    
    server_dir = Path(server_dir_str).expanduser().resolve()
    
    # 執行版本差距分析
    analysis = analyze_version_diff(files_to_compare, local_dir, server_dir)
    
    # 輸出結果
    if args.json:
        print(json.dumps(analysis, ensure_ascii=False, indent=2))
    else:
        print_version_diff_report(analysis)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
