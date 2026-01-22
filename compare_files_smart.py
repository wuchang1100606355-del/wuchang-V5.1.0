#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compare_files_smart.py

智能檔案比對工具

功能：
- 比對本地和伺服器端檔案
- 如果伺服器不可訪問，至少顯示本地檔案資訊
- 提供多種伺服器路徑嘗試
- 生成詳細比對報告
"""

import sys
import json
import os
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def sha256_file(path: Path) -> str:
    """計算檔案 SHA256"""
    try:
        sha256_hash = hashlib.sha256()
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


def try_server_paths() -> List[str]:
    """嘗試多種伺服器路徑"""
    paths = []
    
    # 1. 環境變數
    env_path = os.getenv("WUCHANG_COPY_TO", "").strip()
    if env_path:
        paths.append(env_path)
    
    # 2. 配置檔案
    config_file = BASE_DIR / "network_interconnection_config.json"
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text(encoding="utf-8"))
            if config.get("server_share"):
                paths.append(config["server_share"])
        except:
            pass
    
    # 3. 常見的映射磁碟機
    for drive in ["Z:", "Y:", "X:"]:
        paths.append(drive)
    
    return paths


def find_accessible_server_path() -> Optional[Path]:
    """尋找可訪問的伺服器路徑"""
    paths = try_server_paths()
    
    for path_str in paths:
        try:
            path = Path(path_str)
            if path.exists():
                # 嘗試列出目錄內容
                try:
                    list(path.iterdir())
                    return path
                except:
                    continue
        except:
            continue
    
    return None


def compare_file_list(files: List[str], server_dir: Optional[Path] = None) -> Dict[str, Any]:
    """比對檔案列表"""
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "local_dir": str(BASE_DIR),
        "server_dir": str(server_dir) if server_dir else None,
        "server_accessible": server_dir is not None and server_dir.exists(),
        "files": [],
        "summary": {
            "total": len(files),
            "only_local": 0,
            "only_server": 0,
            "different": 0,
            "same": 0,
            "local_error": 0,
            "server_error": 0,
        }
    }
    
    for filename in files:
        local_path = BASE_DIR / filename
        server_path = server_dir / filename if server_dir else None
        
        local_info = get_file_info(local_path)
        server_info = get_file_info(server_path) if server_path else None
        
        file_result = {
            "filename": filename,
            "local": local_info,
            "server": server_info,
            "status": "unknown",
        }
        
        if local_info and local_info.get("exists"):
            if server_info and server_info.get("exists"):
                # 兩邊都存在，比較內容
                local_hash = local_info.get("sha256", "")
                server_hash = server_info.get("sha256", "")
                
                if local_hash == server_hash:
                    file_result["status"] = "same"
                    results["summary"]["same"] += 1
                else:
                    file_result["status"] = "different"
                    results["summary"]["different"] += 1
            else:
                # 僅本地存在
                file_result["status"] = "only_local"
                results["summary"]["only_local"] += 1
        elif server_info and server_info.get("exists"):
            # 僅伺服器存在
            file_result["status"] = "only_server"
            results["summary"]["only_server"] += 1
        else:
            # 兩邊都不存在
            file_result["status"] = "missing"
        
        if local_info and local_info.get("error"):
            results["summary"]["local_error"] += 1
        if server_info and server_info.get("error"):
            results["summary"]["server_error"] += 1
        
        results["files"].append(file_result)
    
    return results


def print_comparison_results(results: Dict[str, Any], profile_name: str = ""):
    """列印比對結果"""
    if profile_name:
        print(f"【{profile_name}】")
    
    print(f"  總檔案數: {results['summary']['total']}")
    
    if results["server_accessible"]:
        print(f"  僅本地有: {results['summary']['only_local']}")
        print(f"  僅伺服器有: {results['summary']['only_server']}")
        print(f"  內容不同: {results['summary']['different']}")
        print(f"  內容相同: {results['summary']['same']}")
    else:
        print(f"  ⚠️  伺服器不可訪問，僅顯示本地檔案資訊")
        print(f"  本地存在: {results['summary']['only_local'] + results['summary']['same'] + results['summary']['different']}")
    
    print()
    
    # 顯示檔案詳情
    if results["files"]:
        print("  【檔案詳情】")
        for file_info in results["files"]:
            filename = file_info["filename"]
            status = file_info["status"]
            local_info = file_info.get("local")
            server_info = file_info.get("server")
            
            if status == "only_local":
                if local_info and local_info.get("exists"):
                    size = local_info.get("size", 0)
                    mtime = local_info.get("mtime_iso", "N/A")
                    print(f"    [僅本地] {filename} ({size} bytes, {mtime})")
            elif status == "only_server":
                if server_info and server_info.get("exists"):
                    size = server_info.get("size", 0)
                    mtime = server_info.get("mtime_iso", "N/A")
                    print(f"    [僅伺服器] {filename} ({size} bytes, {mtime})")
            elif status == "different":
                if local_info and server_info:
                    local_size = local_info.get("size", 0)
                    server_size = server_info.get("size", 0)
                    local_mtime = local_info.get("mtime_iso", "N/A")
                    server_mtime = server_info.get("mtime_iso", "N/A")
                    local_hash = local_info.get("sha256", "")[:16]
                    server_hash = server_info.get("sha256", "")[:16]
                    print(f"    [不同] {filename}")
                    print(f"      本地: {local_size} bytes, {local_mtime}, SHA256: {local_hash}...")
                    print(f"      伺服器: {server_size} bytes, {server_mtime}, SHA256: {server_hash}...")
            elif status == "same":
                if local_info:
                    size = local_info.get("size", 0)
                    mtime = local_info.get("mtime_iso", "N/A")
                    print(f"    [相同] {filename} ({size} bytes, {mtime})")
            elif status == "missing":
                print(f"    [缺失] {filename} (兩邊都不存在)")


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="智能檔案比對工具")
    parser.add_argument("--profile", choices=["kb", "rules", "all"], default="all", help="比對配置檔")
    parser.add_argument("--server-dir", default=None, help="伺服器目錄（覆蓋自動檢測）")
    parser.add_argument("--json", action="store_true", help="輸出 JSON 格式報告")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("智能檔案比對")
    print("=" * 70)
    print()
    
    # 尋找伺服器路徑
    server_path = None
    if args.server_dir:
        server_path = Path(args.server_dir)
        if not server_path.exists():
            print(f"⚠️  指定的伺服器路徑不存在: {args.server_dir}")
            server_path = None
    else:
        print("【尋找伺服器路徑】")
        server_path = find_accessible_server_path()
        if server_path:
            print(f"  ✓ 找到可訪問的伺服器路徑: {server_path}")
        else:
            print("  ⚠️  無法找到可訪問的伺服器路徑")
            print("  將僅顯示本地檔案資訊")
        print()
    
    # 獲取要比對的檔案列表
    try:
        from safe_sync_push import DEFAULT_FILES, RULE_FILES
    except ImportError:
        print("錯誤: 無法導入 safe_sync_push 模組")
        return 1
    
    all_results = {}
    
    if args.profile in ("all", "kb"):
        print("【知識庫檔案 (kb)】")
        kb_results = compare_file_list(DEFAULT_FILES, server_path)
        all_results["kb"] = kb_results
        print_comparison_results(kb_results, "知識庫檔案")
        print()
    
    if args.profile in ("all", "rules"):
        print("【規則檔案 (rules)】")
        rules_results = compare_file_list(RULE_FILES, server_path)
        all_results["rules"] = rules_results
        print_comparison_results(rules_results, "規則檔案")
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
    if server_path:
        print(f"僅本地有: {only_local}")
        print(f"僅伺服器有: {only_server}")
        print(f"內容不同: {different}")
        print(f"內容相同: {same}")
    else:
        print(f"本地存在: {only_local + different + same}")
        print("⚠️  伺服器不可訪問，無法完整比對")
        print()
        print("【修復建議】")
        print("  1. 檢查網路連接")
        print("  2. 執行: python fix_network_share_issues.py")
        print("  3. 檢查 VPN 連接狀態")
        print("  4. 確認伺服器共享路徑正確")
    
    print()
    
    if args.json:
        report_file = BASE_DIR / "file_compare_smart_report.json"
        report_file.write_text(
            json.dumps(all_results, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"比對報告已儲存到: {report_file}")
    
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
