#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
quick_file_compare.py

快速檔案比對工具

功能：
- 比對本地和伺服器端檔案
- 顯示檔案差異（大小、修改時間、SHA256）
- 支援多種配置檔（kb, rules, all）
"""

import sys
import json
import os
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent

# 嘗試導入現有的比對工具
try:
    from file_compare_sync import compare_files, get_file_info, sha256_file
    from safe_sync_push import DEFAULT_FILES, RULE_FILES
except ImportError:
    print("錯誤: 無法導入必要的模組")
    sys.exit(1)


def compare_all_profiles(server_dir: str = None, output_json: bool = False):
    """比對所有配置檔"""
    if not server_dir:
        server_dir = os.getenv("WUCHANG_COPY_TO", "")
        if not server_dir:
            # 嘗試從配置檔案讀取
            config_file = BASE_DIR / "network_interconnection_config.json"
            if config_file.exists():
                try:
                    config = json.loads(config_file.read_text(encoding="utf-8"))
                    server_dir = config.get("server_share", "")
                except:
                    pass
    
    if not server_dir:
        print("錯誤: 未指定伺服器目錄")
        print("請設定 WUCHANG_COPY_TO 環境變數或提供 --server-dir 參數")
        return None
    
    server_path = Path(server_dir)
    
    if not server_path.exists():
        print(f"錯誤: 伺服器目錄不存在: {server_dir}")
        print("請檢查網路連接和共享路徑")
        return None
    
    print("=" * 70)
    print("檔案比對報告")
    print("=" * 70)
    print(f"本地目錄: {BASE_DIR}")
    print(f"伺服器目錄: {server_dir}")
    print()
    
    all_results = {}
    
    # 比對 kb profile
    print("【知識庫檔案 (kb)】")
    kb_results = compare_files(DEFAULT_FILES, server_path, BASE_DIR)
    all_results["kb"] = kb_results
    print_comparison_results(kb_results)
    print()
    
    # 比對 rules profile
    print("【規則檔案 (rules)】")
    rules_results = compare_files(RULE_FILES, server_path, BASE_DIR)
    all_results["rules"] = rules_results
    print_comparison_results(rules_results)
    print()
    
    # 摘要
    print("=" * 70)
    print("【比對摘要】")
    print("=" * 70)
    
    total_files = 0
    only_local = 0
    only_server = 0
    different = 0
    same = 0
    
    for profile, results in all_results.items():
        summary = results.get("summary", {})
        total_files += summary.get("total", 0)
        only_local += summary.get("only_local", 0)
        only_server += summary.get("only_server", 0)
        different += summary.get("different", 0)
        same += summary.get("same", 0)
    
    print(f"總檔案數: {total_files}")
    print(f"僅本地有: {only_local}")
    print(f"僅伺服器有: {only_server}")
    print(f"內容不同: {different}")
    print(f"內容相同: {same}")
    print()
    
    if output_json:
        report_file = BASE_DIR / "file_compare_report.json"
        report_file.write_text(
            json.dumps(all_results, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"比對報告已儲存到: {report_file}")
    
    print("=" * 70)
    
    return all_results


def print_comparison_results(results: dict):
    """列印比對結果"""
    summary = results.get("summary", {})
    files = results.get("files", [])
    
    print(f"  總檔案數: {summary.get('total', 0)}")
    print(f"  僅本地有: {summary.get('only_local', 0)}")
    print(f"  僅伺服器有: {summary.get('only_server', 0)}")
    print(f"  內容不同: {summary.get('different', 0)}")
    print(f"  內容相同: {summary.get('same', 0)}")
    print()
    
    if files:
        print("  【檔案詳情】")
        for file_info in files:
            filename = file_info.get("filename", "")
            status = file_info.get("status", "unknown")
            local_info = file_info.get("local")
            server_info = file_info.get("server")
            
            if status == "only_local":
                print(f"    [僅本地] {filename}")
                if local_info:
                    print(f"      大小: {local_info.get('size', 0)} bytes")
                    print(f"      修改時間: {local_info.get('mtime_iso', 'N/A')}")
            elif status == "only_server":
                print(f"    [僅伺服器] {filename}")
                if server_info:
                    print(f"      大小: {server_info.get('size', 0)} bytes")
                    print(f"      修改時間: {server_info.get('mtime_iso', 'N/A')}")
            elif status == "different":
                print(f"    [不同] {filename}")
                if local_info and server_info:
                    print(f"      本地: {local_info.get('size', 0)} bytes, {local_info.get('mtime_iso', 'N/A')}")
                    print(f"      伺服器: {server_info.get('size', 0)} bytes, {server_info.get('mtime_iso', 'N/A')}")
                    local_hash = local_info.get('sha256', '')[:16]
                    server_hash = server_info.get('sha256', '')[:16]
                    print(f"      SHA256: 本地={local_hash}..., 伺服器={server_hash}...")
            elif status == "same":
                print(f"    [相同] {filename}")
                if local_info:
                    print(f"      大小: {local_info.get('size', 0)} bytes")
                    print(f"      修改時間: {local_info.get('mtime_iso', 'N/A')}")


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="快速檔案比對工具")
    parser.add_argument("--profile", choices=["kb", "rules", "all"], default="all", help="比對配置檔")
    parser.add_argument("--server-dir", default=None, help="伺服器目錄（覆蓋環境變數）")
    parser.add_argument("--json", action="store_true", help="輸出 JSON 格式報告")
    
    args = parser.parse_args()
    
    if args.profile == "all":
        results = compare_all_profiles(args.server_dir, args.json)
    else:
        # 單一配置檔比對
        if not args.server_dir:
            args.server_dir = os.getenv("WUCHANG_COPY_TO", "")
            if not args.server_dir:
                config_file = BASE_DIR / "network_interconnection_config.json"
                if config_file.exists():
                    try:
                        config = json.loads(config_file.read_text(encoding="utf-8"))
                        args.server_dir = config.get("server_share", "")
                    except:
                        pass
        
        if not args.server_dir:
            print("錯誤: 未指定伺服器目錄")
            sys.exit(1)
        
        server_path = Path(args.server_dir)
        if not server_path.exists():
            print(f"錯誤: 伺服器目錄不存在: {args.server_dir}")
            sys.exit(1)
        
        print("=" * 70)
        print("檔案比對報告")
        print("=" * 70)
        print(f"配置檔: {args.profile}")
        print(f"本地目錄: {BASE_DIR}")
        print(f"伺服器目錄: {args.server_dir}")
        print()
        
        if args.profile == "kb":
            files_to_compare = DEFAULT_FILES
            print("【知識庫檔案 (kb)】")
        else:
            files_to_compare = RULE_FILES
            print("【規則檔案 (rules)】")
        
        results = compare_files(files_to_compare, server_path, BASE_DIR)
        print_comparison_results(results)
        
        if args.json:
            report_file = BASE_DIR / f"file_compare_{args.profile}_report.json"
            report_file.write_text(
                json.dumps(results, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            print(f"比對報告已儲存到: {report_file}")
        
        print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
