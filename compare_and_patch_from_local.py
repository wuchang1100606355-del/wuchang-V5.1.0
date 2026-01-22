#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compare_and_patch_from_local.py

以本地檔案進行比對修補

功能：
- 比對本地和伺服器端檔案
- 以本地檔案為準進行修補
- 將本地變更推送到伺服器端
- 生成比對和修補報告
"""

import sys
import json
import os
import hashlib
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Any

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def sha256_file(file_path: Path) -> str:
    """計算檔案 SHA256"""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return ""


def compare_files(local_path: Path, server_path: Path) -> Dict[str, Any]:
    """比對兩個檔案"""
    result = {
        "local_exists": local_path.exists(),
        "server_exists": server_path.exists(),
        "same": False,
        "local_newer": False,
        "server_newer": False,
        "local_hash": "",
        "server_hash": "",
        "local_size": 0,
        "server_size": 0,
        "local_mtime": 0,
        "server_mtime": 0,
    }
    
    if local_path.exists():
        result["local_size"] = local_path.stat().st_size
        result["local_mtime"] = local_path.stat().st_mtime
        result["local_hash"] = sha256_file(local_path)
    
    if server_path.exists():
        result["server_size"] = server_path.stat().st_size
        result["server_mtime"] = server_path.stat().st_mtime
        result["server_hash"] = sha256_file(server_path)
    
    if result["local_exists"] and result["server_exists"]:
        result["same"] = result["local_hash"] == result["server_hash"]
        result["local_newer"] = result["local_mtime"] > result["server_mtime"]
        result["server_newer"] = result["server_mtime"] > result["local_mtime"]
    elif result["local_exists"]:
        result["local_newer"] = True  # 本地有，伺服器沒有，需要推送
    
    return result


def patch_file(local_path: Path, server_path: Path, dry_run: bool = False) -> Dict[str, Any]:
    """修補檔案（以本地為準）"""
    result = {
        "file": local_path.name,
        "action": "none",
        "success": False,
        "error": None
    }
    
    if not local_path.exists():
        result["action"] = "skip"
        result["error"] = "本地檔案不存在"
        return result
    
    comparison = compare_files(local_path, server_path)
    
    # 決定是否需要修補
    need_patch = False
    if not comparison["server_exists"]:
        result["action"] = "create"
        need_patch = True
    elif not comparison["same"]:
        if comparison["local_newer"] or not comparison["server_newer"]:
            result["action"] = "update"
            need_patch = True
        else:
            result["action"] = "skip"
            result["error"] = "伺服器端檔案較新，跳過修補"
    else:
        result["action"] = "skip"
        result["error"] = "檔案相同，無需修補"
    
    if need_patch and not dry_run:
        try:
            # 確保目標目錄存在
            server_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 原子複製
            import tempfile
            with tempfile.NamedTemporaryFile(
                delete=False,
                dir=str(server_path.parent),
                prefix=server_path.name + ".",
                suffix=".tmp"
            ) as tf:
                tmp_path = Path(tf.name)
            
            try:
                shutil.copy2(local_path, tmp_path)
                os.replace(str(tmp_path), str(server_path))
                result["success"] = True
            except Exception as e:
                if tmp_path.exists():
                    tmp_path.unlink()
                raise e
                
        except Exception as e:
            result["error"] = str(e)
            result["success"] = False
    elif need_patch and dry_run:
        result["success"] = True  # 模擬成功
    
    result["comparison"] = comparison
    return result


def get_sync_files(profile: str = "all") -> List[Path]:
    """獲取需要同步的檔案列表"""
    files = []
    
    if profile in ("all", "kb"):
        kb_files = [
            "wuchang_community_knowledge_index.json",
            "wuchang_community_context_compact.md",
        ]
        for f in kb_files:
            p = BASE_DIR / f
            if p.exists():
                files.append(p)
    
    if profile in ("all", "rules"):
        rule_files = [
            "AGENT_CONSTITUTION.md",
            "RISK_ACTION_SOP.md",
            "risk_gate.py",
            "safe_sync_push.py",
            "api_community_data.py",
        ]
        for f in rule_files:
            p = BASE_DIR / f
            if p.exists():
                files.append(p)
    
    return files


def compare_and_patch(profile: str = "all", server_dir: str = None, dry_run: bool = False) -> Dict[str, Any]:
    """比對並修補所有檔案"""
    print("【比對並修補檔案】")
    print(f"  配置檔: {profile}")
    print(f"  模式: {'模擬執行' if dry_run else '實際執行'}")
    print()
    
    # 獲取伺服器目錄
    if not server_dir:
        server_dir = os.getenv("WUCHANG_COPY_TO", "").strip()
        if not server_dir:
            print("  ✗ 未指定伺服器目錄")
            print("  請設定 WUCHANG_COPY_TO 環境變數或提供 --server-dir 參數")
            return {"ok": False, "error": "missing_server_dir"}
    
    server_path = Path(server_dir)
    if not server_path.exists():
        print(f"  ✗ 伺服器目錄不存在: {server_dir}")
        return {"ok": False, "error": "server_dir_not_exists"}
    
    print(f"  伺服器目錄: {server_dir}")
    print()
    
    # 獲取檔案列表
    local_files = get_sync_files(profile)
    
    if not local_files:
        print("  ✗ 未找到需要同步的檔案")
        return {"ok": False, "error": "no_files_found"}
    
    print(f"  找到 {len(local_files)} 個檔案")
    print()
    
    # 比對和修補
    results = []
    patched_count = 0
    skipped_count = 0
    error_count = 0
    
    for local_file in local_files:
        server_file = server_path / local_file.name
        
        print(f"【處理】{local_file.name}")
        
        # 比對
        comparison = compare_files(local_file, server_file)
        
        if comparison["local_exists"]:
            print(f"  本地: {comparison['local_size']} bytes, SHA256: {comparison['local_hash'][:16]}...")
        if comparison["server_exists"]:
            print(f"  伺服器: {comparison['server_size']} bytes, SHA256: {comparison['server_hash'][:16]}...")
        
        if comparison["same"]:
            print("  ✓ 檔案相同，無需修補")
            skipped_count += 1
        else:
            # 修補
            patch_result = patch_file(local_file, server_file, dry_run=dry_run)
            results.append(patch_result)
            
            if patch_result["success"]:
                print(f"  ✓ {patch_result['action']}: 已修補")
                patched_count += 1
            else:
                print(f"  ✗ {patch_result['action']}: 失敗 - {patch_result.get('error', '未知錯誤')}")
                error_count += 1
        
        print()
    
    # 生成報告
    report = {
        "ok": error_count == 0,
        "timestamp": __import__("time").strftime("%Y-%m-%dT%H:%M:%S%z"),
        "profile": profile,
        "server_dir": str(server_dir),
        "dry_run": dry_run,
        "total_files": len(local_files),
        "patched": patched_count,
        "skipped": skipped_count,
        "errors": error_count,
        "results": results
    }
    
    return report


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="以本地檔案進行比對修補")
    parser.add_argument("--profile", choices=["kb", "rules", "all"], default="all", help="同步配置檔")
    parser.add_argument("--server-dir", default=None, help="伺服器目錄（覆蓋環境變數）")
    parser.add_argument("--dry-run", action="store_true", help="模擬執行，不實際修補")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("以本地檔案進行比對修補")
    print("=" * 70)
    print()
    
    # 執行比對和修補
    report = compare_and_patch(
        profile=args.profile,
        server_dir=args.server_dir,
        dry_run=args.dry_run
    )
    
    if not report.get("ok"):
        print("=" * 70)
        print("【執行結果】")
        print(f"  ✗ 執行失敗: {report.get('error', '未知錯誤')}")
        print("=" * 70)
        return 1
    
    # 顯示摘要
    print("=" * 70)
    print("【執行摘要】")
    print("=" * 70)
    print(f"  總檔案數: {report['total_files']}")
    print(f"  已修補: {report['patched']}")
    print(f"  已跳過: {report['skipped']}")
    print(f"  錯誤: {report['errors']}")
    print()
    
    if report['patched'] > 0:
        print("【已修補的檔案】")
        for result in report['results']:
            if result.get('success') and result.get('action') != 'skip':
                print(f"  ✓ {result['file']} ({result['action']})")
        print()
    
    # 儲存報告
    report_file = BASE_DIR / "compare_patch_report.json"
    report_file.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"比對修補報告已儲存到: {report_file}")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
