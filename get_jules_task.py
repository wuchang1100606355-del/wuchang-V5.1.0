#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
get_jules_task.py

從 Google Tasks URL 獲取 JULES 的任務

使用方式：
  python get_jules_task.py "https://jules.google.com/task/2903235408856978280"
"""

import sys
import json
import requests
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
CONTROL_CENTER_URL = "http://127.0.0.1:8788"


def check_control_center():
    """檢查控制中心是否運行"""
    try:
        # 嘗試多個端點
        endpoints = [
            f"{CONTROL_CENTER_URL}/api/local/health",
            f"{CONTROL_CENTER_URL}/health",
            f"{CONTROL_CENTER_URL}/",
        ]
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=2)
                if response.status_code in [200, 404]:
                    return True
            except:
                continue
        return False
    except:
        return False


def get_task_from_api(task_url: str):
    """通過控制中心 API 獲取任務"""
    try:
        response = requests.post(
            f"{CONTROL_CENTER_URL}/api/google-tasks/tasks/from-url",
            json={"url": task_url},
            timeout=10
        )
        
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


def main():
    """主函數"""
    if len(sys.argv) < 2:
        task_url = "https://jules.google.com/task/2903235408856978280"
    else:
        task_url = sys.argv[1]
    
    print("=" * 70)
    print("從 Google Tasks 獲取 JULES 任務")
    print("=" * 70)
    print(f"任務 URL: {task_url}")
    print()
    
    # 檢查控制中心
    print("【步驟 1：檢查控制中心】")
    if check_control_center():
        print("✓ 控制中心運行中")
    else:
        print("✗ 控制中心未運行")
        print()
        print("請先啟動控制中心：")
        print("  python local_control_center.py")
        return
    print()
    
    # 嘗試獲取任務
    print("【步驟 2：獲取任務內容】")
    result = get_task_from_api(task_url)
    
    if result.get("ok"):
        print("✓ 任務獲取成功")
        print()
        print("【任務資訊】")
        task = result.get("task", {})
        print(f"  標題: {task.get('title', '無標題')}")
        print(f"  狀態: {task.get('status', '未知')}")
        if task.get('notes'):
            print(f"  備註: {task.get('notes')}")
        if task.get('due'):
            print(f"  到期: {task.get('due')}")
        if task.get('completed'):
            print(f"  完成時間: {task.get('completed')}")
        print()
        print("【完整資料】")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 儲存任務內容
        output_file = BASE_DIR / "jules_task_response.json"
        output_file.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print()
        print(f"✓ 任務內容已儲存到: {output_file}")
    else:
        print("✗ 任務獲取失敗")
        print(f"  錯誤: {result.get('error', '未知錯誤')}")
        print()
        
        if "OAuth" in str(result.get('error', '')) or "憑證" in str(result.get('error', '')):
            print("【解決方案】")
            print("需要設定 Google OAuth 憑證：")
            print("1. 參考 GOOGLE_TASKS_QUICK_SETUP.md")
            print("2. 從 Google Cloud Console 下載 OAuth 憑證")
            print("3. 儲存為 google_credentials.json")
            print("4. 執行授權流程")
        elif "無法連接" in str(result.get('error', '')):
            print("【解決方案】")
            print("請確認控制中心正在運行")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
