#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
read_workspace_status.py

讀取工作區狀態

功能：
- 讀取工作區對齊狀態
- 檢查工作區配置
- 顯示工作區目錄結構
- 生成工作區狀態報告
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


def read_workspace_alignment():
    """讀取工作區對齊狀態"""
    try:
        from workspace_alignment_check import main as alignment_check
        return alignment_check()
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "timestamp": __import__("time").strftime("%Y-%m-%dT%H:%M:%S%z")
        }


def read_workspace_from_api():
    """從 API 讀取工作區狀態"""
    try:
        import requests
        response = requests.get("http://127.0.0.1:8788/api/workspace/alignment", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "ok": False,
                "error": f"API 回應錯誤: {response.status_code}",
                "response": response.text[:500]
            }
    except requests.exceptions.ConnectionError:
        return {
            "ok": False,
            "error": "無法連接到控制中心",
            "hint": "請確認控制中心正在運行"
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }


def display_workspace_status(status: dict):
    """顯示工作區狀態"""
    print("=" * 70)
    print("工作區狀態報告")
    print("=" * 70)
    print(f"檢查時間: {status.get('timestamp', '未知')}")
    print()
    
    if not status.get("ok"):
        print("⚠️  工作區配置不完整")
        if status.get("error"):
            print(f"錯誤: {status['error']}")
        print()
    
    # 顯示檢查結果
    print("【工作區配置檢查】")
    checks = status.get("checks", [])
    for check in checks:
        name = check.get("name", "")
        ok = check.get("ok", False)
        path = check.get("path", "")
        env = check.get("env", "")
        note = check.get("note", "")
        
        status_icon = "✓" if ok else "✗"
        print(f"  {status_icon} {name}")
        if path:
            print(f"     路徑: {path}")
        if env:
            print(f"     環境變數: {env}")
        if note:
            print(f"     備註: {note}")
        print()
    
    # 顯示警告
    warnings = status.get("warnings", [])
    if warnings:
        print("【警告】")
        for warning in warnings:
            print(f"  ⚠️  {warning}")
        print()
    
    # 顯示缺少的項目
    missing = status.get("missing", [])
    if missing:
        print("【缺少的項目】")
        for item in missing:
            print(f"  - {item}")
        print()
    
    # 顯示建議的 PowerShell 指令
    suggested = status.get("suggested_powershell", [])
    if suggested:
        print("【建議的環境變數設定（PowerShell）】")
        for cmd in suggested:
            print(f"  {cmd}")
        print()


def main():
    """主函數"""
    print("=" * 70)
    print("讀取工作區狀態")
    print("=" * 70)
    print()
    
    # 嘗試從 API 讀取
    print("【方式 1：從控制中心 API 讀取】")
    api_status = read_workspace_from_api()
    
    if api_status.get("ok") is not False and "error" not in api_status:
        print("✓ 從 API 讀取成功")
        display_workspace_status(api_status)
        
        # 儲存報告
        report_file = BASE_DIR / "workspace_status_report.json"
        report_file.write_text(
            json.dumps(api_status, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"工作區狀態報告已儲存到: {report_file}")
        return
    
    print("⚠️  API 讀取失敗，使用本地檢查")
    print()
    
    # 使用本地檢查
    print("【方式 2：本地工作區對齊檢查】")
    local_status = read_workspace_alignment()
    display_workspace_status(local_status)
    
    # 儲存報告
    report_file = BASE_DIR / "workspace_status_report.json"
    report_file.write_text(
        json.dumps(local_status, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"工作區狀態報告已儲存到: {report_file}")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
