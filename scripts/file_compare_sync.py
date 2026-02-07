#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
file_compare_sync.py

雙方檔案比對與同步工具

功能：
- 比對本機與伺服器檔案差異
- 檢查檔案是否存在、大小、修改時間、SHA256 雜湊值
- 支援比對後同步推送（使用 safe_sync_push.py）
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

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


def compare_files(
    local_files: List[str],
    server_dir: Path,
    local_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """比對本機與伺服器檔案"""
    if local_dir is None:
        local_dir = BASE_DIR
    
    results = {
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
        },
    }
    
    for filename in local_files:
        local_path = (local_dir / filename).resolve()
        server_path = (server_dir / filename).resolve()
        
        local_info = get_file_info(local_path)
        server_info = get_file_info(server_path)
        
        comparison = {
            "filename": filename,
            "local": local_info,
            "server": server_info,
            "status": "unknown",
        }
        
        if local_info is None or not local_info.get("exists"):
            comparison["status"] = "only_server"
            results["summary"]["only_server"] += 1
        elif server_info is None or not server_info.get("exists"):
            comparison["status"] = "only_local"
            results["summary"]["only_local"] += 1
        elif local_info.get("sha256") == server_info.get("sha256"):
            comparison["status"] = "same"
            results["summary"]["same"] += 1
        else:
            comparison["status"] = "different"
            comparison["differences"] = {
                "size": local_info.get("size") != server_info.get("size"),
                "mtime": local_info.get("mtime") != server_info.get("mtime"),
                "sha256": local_info.get("sha256") != server_info.get("sha256"),
            }
            results["summary"]["different"] += 1
        
        results["files"].append(comparison)
        results["summary"]["total"] += 1
    
    return results


def print_comparison(results: Dict[str, Any]) -> None:
    """列印比對結果"""
    # 設定 UTF-8 編碼輸出
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except:
            pass
    
    print("=" * 60)
    print("檔案比對報告")
    print("=" * 60)
    print(f"比對時間: {results['timestamp']}")
    print(f"本機目錄: {results['local_dir']}")
    print(f"伺服器目錄: {results['server_dir']}\n")
    
    summary = results["summary"]
    print("【摘要】")
    print(f"  總檔案數: {summary['total']}")
    print(f"  僅本機存在: {summary['only_local']}")
    print(f"  僅伺服器存在: {summary['only_server']}")
    print(f"  內容不同: {summary['different']}")
    print(f"  內容相同: {summary['same']}\n")
    
    print("【檔案詳情】")
    for file_comp in results["files"]:
        filename = file_comp["filename"]
        status = file_comp["status"]
        
        if status == "same":
            print(f"  [相同] {filename}")
        elif status == "only_local":
            local = file_comp["local"]
            size = local.get("size", 0) if local else 0
            print(f"  [僅本機] {filename} (大小: {size} bytes)")
        elif status == "only_server":
            server = file_comp["server"]
            size = server.get("size", 0) if server else 0
            print(f"  [僅伺服器] {filename} (大小: {size} bytes)")
        elif status == "different":
            local = file_comp["local"]
            server = file_comp["server"]
            local_sha = local.get("sha256", "")[:16] if local else "N/A"
            server_sha = server.get("sha256", "")[:16] if server else "N/A"
            print(f"  [不同] {filename}")
            print(f"    本機 SHA256: {local_sha}...")
            print(f"    伺服器 SHA256: {server_sha}...")
            if file_comp.get("differences"):
                diffs = file_comp["differences"]
                diff_items = [k for k, v in diffs.items() if v]
                print(f"    差異項目: {', '.join(diff_items)}")
    
    print("=" * 60)


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="檔案比對與同步工具")
    parser.add_argument(
        "--files",
        nargs="+",
        help="要比對的檔案清單（檔案名或路徑）",
    )
    parser.add_argument(
        "--profile",
        choices=["kb", "rules"],
        help="使用預設檔案 profile（kb 或 rules）",
    )
    parser.add_argument(
        "--local-dir",
        type=str,
        help="本機目錄（預設為腳本所在目錄）",
    )
    parser.add_argument(
        "--server-dir",
        type=str,
        help="伺服器目錄（SMB/掛載磁碟路徑，也可用 WUCHANG_COPY_TO 環境變數）",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式輸出",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="比對後自動同步（推送差異檔案到伺服器）",
    )
    parser.add_argument(
        "--actor",
        default="system",
        help="操作者（同步時會寫入稽核）",
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
    
    # 執行比對
    results = compare_files(files_to_compare, server_dir, local_dir)
    
    # 輸出結果
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_comparison(results)
    
    # 如果需要同步
    if args.sync:
        # 找出需要推送的檔案（僅本機存在或內容不同）
        files_to_sync = [
            f["filename"]
            for f in results["files"]
            if f["status"] in ("only_local", "different")
        ]
        
        if not files_to_sync:
            print("\n[提示] 所有檔案已同步，無需推送。")
            return 0
        
        print(f"\n[提示] 準備同步 {len(files_to_sync)} 個檔案: {', '.join(files_to_sync)}")
        
        # 使用 safe_sync_push.py 進行同步
        try:
            import subprocess
            cmd = [
                sys.executable,
                str(BASE_DIR / "safe_sync_push.py"),
                "--files",
                *files_to_sync,
                "--actor",
                args.actor,
            ]
            
            health_url = os.getenv("WUCHANG_HEALTH_URL", "")
            if health_url:
                cmd.extend(["--health-url", health_url])
            
            if args.server_dir:
                cmd.extend(["--copy-to", args.server_dir])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("[成功] 同步完成")
                if result.stdout:
                    print(result.stdout)
            else:
                print(f"[失敗] 同步失敗 (返回碼: {result.returncode})", file=sys.stderr)
                if result.stderr:
                    print(result.stderr, file=sys.stderr)
                return result.returncode
        except Exception as e:
            print(f"[錯誤] 同步失敗: {e}", file=sys.stderr)
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
