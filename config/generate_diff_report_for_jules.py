#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_diff_report_for_jules.py

生成檔案差異報告供上傳 JULES

功能：
- 比對本地和伺服器端檔案
- 生成機器可讀的差異報告
- 格式化為適合 Google Tasks 的內容
"""

import sys
import json
import os
import time
from pathlib import Path
from typing import Dict, Any, List

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def generate_jules_report() -> Dict[str, Any]:
    """生成 JULES 報告"""
    # 使用智能比對工具獲取結果
    try:
        from compare_files_smart import compare_file_list, find_accessible_server_path
        from safe_sync_push import DEFAULT_FILES, RULE_FILES
    except ImportError as e:
        return {
            "error": f"無法導入必要模組: {e}",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")
        }
    
    server_path = find_accessible_server_path()
    
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "local_dir": str(BASE_DIR),
        "server_dir": str(server_path) if server_path else None,
        "server_accessible": server_path is not None and server_path.exists(),
        "profiles": {}
    }
    
    # 比對 kb profile
    kb_results = compare_file_list(DEFAULT_FILES, server_path)
    report["profiles"]["kb"] = {
        "files": DEFAULT_FILES,
        "summary": kb_results["summary"],
        "details": []
    }
    
    for file_info in kb_results["files"]:
        detail = {
            "filename": file_info["filename"],
            "status": file_info["status"],
            "local": {
                "exists": file_info.get("local", {}).get("exists", False),
                "size": file_info.get("local", {}).get("size", 0),
                "mtime": file_info.get("local", {}).get("mtime_iso", ""),
                "sha256": file_info.get("local", {}).get("sha256", "")[:32] if file_info.get("local", {}).get("sha256") else ""
            },
            "server": {
                "exists": file_info.get("server", {}).get("exists", False) if server_path else False,
                "size": file_info.get("server", {}).get("size", 0) if server_path else 0,
                "mtime": file_info.get("server", {}).get("mtime_iso", "") if server_path else "",
                "sha256": file_info.get("server", {}).get("sha256", "")[:32] if server_path and file_info.get("server", {}).get("sha256") else ""
            }
        }
        report["profiles"]["kb"]["details"].append(detail)
    
    # 比對 rules profile
    rules_results = compare_file_list(RULE_FILES, server_path)
    report["profiles"]["rules"] = {
        "files": RULE_FILES,
        "summary": rules_results["summary"],
        "details": []
    }
    
    for file_info in rules_results["files"]:
        detail = {
            "filename": file_info["filename"],
            "status": file_info["status"],
            "local": {
                "exists": file_info.get("local", {}).get("exists", False),
                "size": file_info.get("local", {}).get("size", 0),
                "mtime": file_info.get("local", {}).get("mtime_iso", ""),
                "sha256": file_info.get("local", {}).get("sha256", "")[:32] if file_info.get("local", {}).get("sha256") else ""
            },
            "server": {
                "exists": file_info.get("server", {}).get("exists", False) if server_path else False,
                "size": file_info.get("server", {}).get("size", 0) if server_path else 0,
                "mtime": file_info.get("server", {}).get("mtime_iso", "") if server_path else "",
                "sha256": file_info.get("server", {}).get("sha256", "")[:32] if server_path and file_info.get("server", {}).get("sha256") else ""
            }
        }
        report["profiles"]["rules"]["details"].append(detail)
    
    return report


def format_for_google_tasks(report: Dict[str, Any]) -> str:
    """格式化為 Google Tasks 格式"""
    lines = []
    
    lines.append("# 檔案比對差異報告")
    lines.append("")
    lines.append(f"**生成時間**: {report['timestamp']}")
    lines.append(f"**本地目錄**: {report['local_dir']}")
    lines.append(f"**伺服器目錄**: {report['server_dir'] or '不可訪問'}")
    lines.append(f"**伺服器可訪問**: {'是' if report['server_accessible'] else '否'}")
    lines.append("")
    
    # 摘要
    lines.append("## 比對摘要")
    lines.append("")
    
    total_files = 0
    only_local = 0
    only_server = 0
    different = 0
    same = 0
    
    for profile_name, profile_data in report["profiles"].items():
        summary = profile_data["summary"]
        total_files += summary.get("total", 0)
        only_local += summary.get("only_local", 0)
        only_server += summary.get("only_server", 0)
        different += summary.get("different", 0)
        same += summary.get("same", 0)
    
    lines.append(f"- **總檔案數**: {total_files}")
    if report["server_accessible"]:
        lines.append(f"- **僅本地有**: {only_local}")
        lines.append(f"- **僅伺服器有**: {only_server}")
        lines.append(f"- **內容不同**: {different}")
        lines.append(f"- **內容相同**: {same}")
    else:
        lines.append(f"- **本地存在**: {only_local + different + same}")
        lines.append("- **伺服器不可訪問，無法完整比對**")
    lines.append("")
    
    # 詳細資訊
    for profile_name, profile_data in report["profiles"].items():
        lines.append(f"## {profile_name.upper()} Profile")
        lines.append("")
        
        summary = profile_data["summary"]
        lines.append(f"### 摘要")
        lines.append(f"- 總檔案數: {summary.get('total', 0)}")
        if report["server_accessible"]:
            lines.append(f"- 僅本地有: {summary.get('only_local', 0)}")
            lines.append(f"- 僅伺服器有: {summary.get('only_server', 0)}")
            lines.append(f"- 內容不同: {summary.get('different', 0)}")
            lines.append(f"- 內容相同: {summary.get('same', 0)}")
        else:
            lines.append(f"- 本地存在: {summary.get('only_local', 0) + summary.get('different', 0) + summary.get('same', 0)}")
        lines.append("")
        
        lines.append("### 檔案詳情")
        lines.append("")
        
        for detail in profile_data["details"]:
            filename = detail["filename"]
            status = detail["status"]
            local = detail["local"]
            server = detail["server"]
            
            lines.append(f"#### {filename}")
            lines.append("")
            lines.append(f"**狀態**: {status}")
            lines.append("")
            
            if local["exists"]:
                lines.append("**本地**:")
                lines.append(f"- 存在: 是")
                lines.append(f"- 大小: {local['size']} bytes")
                lines.append(f"- 修改時間: {local['mtime']}")
                if local["sha256"]:
                    lines.append(f"- SHA256: {local['sha256']}...")
            else:
                lines.append("**本地**: 不存在")
            
            lines.append("")
            
            if report["server_accessible"]:
                if server["exists"]:
                    lines.append("**伺服器**:")
                    lines.append(f"- 存在: 是")
                    lines.append(f"- 大小: {server['size']} bytes")
                    lines.append(f"- 修改時間: {server['mtime']}")
                    if server["sha256"]:
                        lines.append(f"- SHA256: {server['sha256']}...")
                else:
                    lines.append("**伺服器**: 不存在")
            else:
                lines.append("**伺服器**: 不可訪問")
            
            lines.append("")
            
            # 如果是不同，顯示差異提示
            if status == "different":
                lines.append("⚠️ **需要同步**: 本地和伺服器端內容不同")
                lines.append("")
            
            lines.append("---")
            lines.append("")
    
    # 行動建議
    lines.append("## 建議行動")
    lines.append("")
    
    if not report["server_accessible"]:
        lines.append("1. **修復網路連接**")
        lines.append("   - 執行: `python fix_network_share_issues.py`")
        lines.append("   - 檢查 VPN 連接狀態")
        lines.append("   - 確認伺服器共享路徑正確")
        lines.append("")
    
    if different > 0:
        lines.append("2. **同步差異檔案**")
        lines.append("   - 執行: `python smart_sync.py --profile all`")
        lines.append("   - 或執行: `python patch_from_local.py --profile all`")
        lines.append("")
    
    if only_local > 0:
        lines.append("3. **推送僅本地存在的檔案**")
        lines.append("   - 執行: `python safe_sync_push.py --profile all`")
        lines.append("")
    
    if only_server > 0:
        lines.append("4. **拉取僅伺服器存在的檔案**")
        lines.append("   - 執行: `python smart_sync.py --profile all --direction local`")
        lines.append("")
    
    return "\n".join(lines)


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="生成檔案差異報告供上傳 JULES")
    parser.add_argument("--format", choices=["json", "markdown", "both"], default="both", help="輸出格式")
    parser.add_argument("--output", default=None, help="輸出檔案路徑（預設自動生成）")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("生成檔案差異報告（供 JULES）")
    print("=" * 70)
    print()
    
    print("正在比對檔案...")
    report = generate_jules_report()
    
    if "error" in report:
        print(f"錯誤: {report['error']}")
        return 1
    
    # 生成輸出檔案
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    if args.format in ("json", "both"):
        json_file = args.output or BASE_DIR / f"file_diff_report_{timestamp}.json"
        json_file.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"✓ JSON 報告已儲存: {json_file}")
        print()
    
    if args.format in ("markdown", "both"):
        markdown_content = format_for_google_tasks(report)
        markdown_file = args.output or BASE_DIR / f"file_diff_report_{timestamp}.md"
        markdown_file.write_text(markdown_content, encoding="utf-8")
        print(f"✓ Markdown 報告已儲存: {markdown_file}")
        print()
        
        # 同時輸出到控制台（方便複製）
        print("=" * 70)
        print("Markdown 報告內容（可複製到 Google Tasks）")
        print("=" * 70)
        print()
        print(markdown_content)
        print()
        print("=" * 70)
    
    print("【完成】")
    print()
    print("報告已生成，可以上傳到 JULES (Google Tasks)")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
