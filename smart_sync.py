#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
smart_sync.py

擇優同步工具 - 智能選擇較佳版本進行同步（雙向模式）

功能：
- 比對本機與雲端檔案
- 根據修改時間、檔案大小、SHA256 選擇較佳版本
- 雙向同步（本機↔雲端）：僅同步到五常雲端空間
- 優先規則：較新的版本、較大的檔案（表示內容更完整）

注意：
- 本系統支援雙向同步：本地端夾下載五常雲端空間變更，本地進行變更上傳雲端空間
- 僅同步到「五常雲端空間」目錄
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

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
            "exists": True,
            "size": stat.st_size,
            "mtime": stat.st_mtime,
            "mtime_iso": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(stat.st_mtime)),
            "sha256": sha256_file(path),
        }
    except Exception as e:
        return {
            "path": str(path),
            "exists": False,
            "error": str(e),
        }


def choose_better_version(
    local_info: Optional[Dict[str, Any]],
    server_info: Optional[Dict[str, Any]],
) -> Optional[str]:
    """
    選擇較佳版本
    規則：
    1. 如果只有一個存在，選擇存在的版本
    2. 如果都存在，比較修改時間（較新者優先）
    3. 如果修改時間相同，比較檔案大小（較大者優先，表示內容更完整）
    4. 如果都相同，保持不變（無需同步）
    
    返回: "local", "server", 或 None（無需同步）
    """
    local_exists = local_info and local_info.get("exists")
    server_exists = server_info and server_info.get("exists")
    
    # 只有一方存在
    if local_exists and not server_exists:
        return "local"
    if server_exists and not local_exists:
        return "server"
    
    # 都不存在
    if not local_exists and not server_exists:
        return None
    
    # 都存在，比較內容
    local_sha = local_info.get("sha256", "") if local_info else ""
    server_sha = server_info.get("sha256", "") if server_info else ""
    
    # SHA256 相同，無需同步
    if local_sha and server_sha and local_sha == server_sha:
        return None
    
    # 比較修改時間（較新者優先）
    local_mtime = local_info.get("mtime", 0) if local_info else 0
    server_mtime = server_info.get("mtime", 0) if server_info else 0
    
    if local_mtime > server_mtime:
        return "local"
    if server_mtime > local_mtime:
        return "server"
    
    # 修改時間相同，比較檔案大小（較大者優先）
    local_size = local_info.get("size", 0) if local_info else 0
    server_size = server_info.get("size", 0) if server_info else 0
    
    if local_size > server_size:
        return "local"
    if server_size > local_size:
        return "server"
    
    # 都相同但 SHA256 不同（異常情況），選擇本機版本
    return "local"


def atomic_copy(src: Path, dst: Path) -> bool:
    """原子性複製檔案"""
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(delete=False, dir=str(dst.parent), prefix=dst.name + ".", suffix=".tmp") as tf:
            tmp_path = Path(tf.name)
        try:
            shutil.copy2(src, tmp_path)
            os.replace(str(tmp_path), str(dst))  # atomic on same volume
            return True
        finally:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except Exception:
                    pass
    except Exception as e:
        print(f"[錯誤] 複製失敗 {src} -> {dst}: {e}", file=sys.stderr)
        return False


def smart_sync(
    files: List[str],
    local_dir: Path,
    server_dir: Path,
    dry_run: bool = False,
    direction: str = "both",  # 預設改為雙向同步
) -> Dict[str, Any]:
    """
    擇優同步（雙向模式）
    
    direction:
    - "local": 只同步到本機（從雲端拉取較佳版本）
    - "server": 只同步到伺服器（推送較佳版本到雲端）
    - "both": 雙向同步（根據擇優結果決定方向）- 預設
    
    注意：本系統支援雙向同步，本地端夾下載五常雲端空間變更，本地進行變更上傳雲端空間
    """
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "local_dir": str(local_dir),
        "server_dir": str(server_dir),
        "direction": direction,
        "dry_run": dry_run,
        "files": [],
        "summary": {
            "total": 0,
            "synced_to_server": 0,
            "synced_to_local": 0,
            "no_sync_needed": 0,
            "failed": 0,
        },
    }
    
    for filename in files:
        local_path = (local_dir / filename).resolve()
        server_path = (server_dir / filename).resolve()
        
        local_info = get_file_info(local_path)
        server_info = get_file_info(server_path)
        
        better_version = choose_better_version(local_info, server_info)
        
        file_result = {
            "filename": filename,
            "local": local_info,
            "server": server_info,
            "better_version": better_version,
            "action": None,
            "synced": False,
            "error": None,
        }
        
        results["summary"]["total"] += 1
        
        if better_version is None:
            file_result["action"] = "skip"
            results["summary"]["no_sync_needed"] += 1
        elif better_version == "local" and direction in ("server", "both"):
            # 本機版本較佳，同步到伺服器
            file_result["action"] = "push_to_server"
            if not dry_run:
                if local_info and local_info.get("exists"):
                    success = atomic_copy(local_path, server_path)
                    if success:
                        file_result["synced"] = True
                        results["summary"]["synced_to_server"] += 1
                    else:
                        file_result["error"] = "copy_failed"
                        results["summary"]["failed"] += 1
                else:
                    file_result["error"] = "source_not_exists"
                    results["summary"]["failed"] += 1
            else:
                results["summary"]["synced_to_server"] += 1  # 模擬計數
        elif better_version == "server" and direction in ("local", "both"):
            # 伺服器版本較佳，同步到本機
            file_result["action"] = "pull_to_local"
            if not dry_run:
                if server_info and server_info.get("exists"):
                    success = atomic_copy(server_path, local_path)
                    if success:
                        file_result["synced"] = True
                        results["summary"]["synced_to_local"] += 1
                    else:
                        file_result["error"] = "copy_failed"
                        results["summary"]["failed"] += 1
                else:
                    file_result["error"] = "source_not_exists"
                    results["summary"]["failed"] += 1
            else:
                results["summary"]["synced_to_local"] += 1  # 模擬計數
        else:
            # 方向限制導致無法同步
            file_result["action"] = "skip_direction"
            results["summary"]["no_sync_needed"] += 1
        
        results["files"].append(file_result)
    
    return results


def print_sync_results(results: Dict[str, Any]) -> None:
    """列印同步結果"""
    # 設定 UTF-8 編碼輸出
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except:
            pass
    
    mode_str = "（模擬模式）" if results.get("dry_run") else ""
    direction_str = {
        "local": "伺服器→本機",
        "server": "本機→伺服器",
        "both": "雙向擇優同步",
    }.get(results.get("direction", "both"), "雙向")
    
    print("=" * 60)
    print(f"擇優同步報告 {mode_str}")
    print("=" * 60)
    print(f"同步時間: {results['timestamp']}")
    print(f"同步方向: {direction_str}")
    print(f"本機目錄: {results['local_dir']}")
    print(f"伺服器目錄: {results['server_dir']}\n")
    
    summary = results["summary"]
    print("【摘要】")
    print(f"  總檔案數: {summary['total']}")
    print(f"  同步到伺服器: {summary['synced_to_server']}")
    print(f"  同步到本機: {summary['synced_to_local']}")
    print(f"  無需同步: {summary['no_sync_needed']}")
    print(f"  失敗: {summary['failed']}\n")
    
    print("【檔案詳情】")
    for file_result in results["files"]:
        filename = file_result["filename"]
        action = file_result["action"]
        better = file_result["better_version"]
        
        if action == "skip":
            print(f"  [跳過] {filename} (兩邊內容相同)")
        elif action == "skip_direction":
            print(f"  [跳過] {filename} (方向限制)")
        elif action == "push_to_server":
            status_icon = "[成功]" if file_result.get("synced") else "[失敗]"
            print(f"  {status_icon} {filename} -> 伺服器 (本機版本較佳)")
            if better == "local":
                local_info = file_result.get("local", {})
                if local_info:
                    print(f"    本機: {local_info.get('mtime_iso', 'N/A')}, {local_info.get('size', 0)} bytes")
        elif action == "pull_to_local":
            status_icon = "[成功]" if file_result.get("synced") else "[失敗]"
            print(f"  {status_icon} {filename} <- 伺服器 (伺服器版本較佳)")
            if better == "server":
                server_info = file_result.get("server", {})
                if server_info:
                    print(f"    伺服器: {server_info.get('mtime_iso', 'N/A')}, {server_info.get('size', 0)} bytes")
        
        if file_result.get("error"):
            print(f"    錯誤: {file_result['error']}")
    
    print("=" * 60)


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="擇優同步工具")
    parser.add_argument(
        "--files",
        nargs="+",
        help="要同步的檔案清單",
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
        "--direction",
        choices=["local", "server", "both"],
        default="both",
        help="同步方向：both(雙向擇優，預設), server(本機→雲端), local(雲端→本機)",
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
    
    # 決定要同步的檔案
    if args.files:
        files_to_sync = args.files
    elif args.profile:
        if args.profile == "kb":
            from safe_sync_push import DEFAULT_FILES
            files_to_sync = DEFAULT_FILES
        elif args.profile == "rules":
            from safe_sync_push import RULE_FILES
            files_to_sync = RULE_FILES
        else:
            print("錯誤: 未知的 profile", file=sys.stderr)
            return 1
    else:
        print("錯誤: 請提供 --files 或 --profile 參數", file=sys.stderr)
        return 1
    
    # 決定目錄
    local_dir = Path(args.local_dir).resolve() if args.local_dir else BASE_DIR
    
    # 優先使用雲端同步配置
    try:
        from cloud_sync_config import get_wuchang_cloud_path, validate_cloud_path
        cloud_path = get_wuchang_cloud_path()
        if cloud_path:
            server_dir_str = str(cloud_path)
        else:
            server_dir_str = args.server_dir or os.getenv("WUCHANG_COPY_TO", "")
    except ImportError:
        server_dir_str = args.server_dir or os.getenv("WUCHANG_COPY_TO", "")
    
    if not server_dir_str:
        print("錯誤: 請提供 --server-dir 參數或設定 WUCHANG_COPY_TO 環境變數", file=sys.stderr)
        print("提示: 建議使用 cloud_sync_config.py 配置五常雲端空間路徑", file=sys.stderr)
        return 1
    
    server_dir = Path(server_dir_str).expanduser().resolve()
    
    # 驗證路徑是否在五常雲端空間內（單向同步限制）
    try:
        from cloud_sync_config import validate_cloud_path
        if not validate_cloud_path(server_dir):
            print(f"警告: 目標路徑不在五常雲端空間內: {server_dir}", file=sys.stderr)
            print("提示: 單向同步僅允許同步到「五常雲端空間」目錄", file=sys.stderr)
            if args.direction != "server":
                print("錯誤: 單向同步模式下，direction 必須為 'server'", file=sys.stderr)
                return 1
    except ImportError:
        pass  # 如果無法導入配置模組，跳過驗證
    
    # 執行擇優同步
    results = smart_sync(
        files_to_sync,
        local_dir,
        server_dir,
        dry_run=args.dry_run,
        direction=args.direction,
    )
    
    # 輸出結果
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_sync_results(results)
    
    # 返回碼
    if results["summary"]["failed"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
