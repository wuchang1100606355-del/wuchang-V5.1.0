#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_from_google_task.py

從 Google Tasks 獲取任務內容並覆蓋本地檔案

使用方式：
  python sync_from_google_task.py "https://jules.google.com/task/9554046612705221251" [target_file]
"""

import sys
import json
from pathlib import Path
from dataclasses import asdict

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def get_task_from_url(task_url: str):
    """從 URL 獲取任務"""
    try:
        from google_tasks_integration import get_google_tasks_integration
        
        print("正在連接到 Google Tasks API...")
        integration = get_google_tasks_integration()
        
        print("正在搜尋任務...")
        task = integration.get_task_by_url(task_url)
        
        if task:
            return task
        else:
            print("❌ 無法找到任務")
            return None
            
    except FileNotFoundError as e:
        print("❌ 錯誤：找不到 OAuth 憑證檔案")
        print("請從 Google Cloud Console 下載 OAuth 2.0 憑證並儲存為 google_credentials.json")
        print(f"詳細錯誤: {e}")
        return None
        
    except ImportError as e:
        print("❌ 錯誤：Google API Client Library 未安裝")
        print("請執行：pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        print(f"詳細錯誤: {e}")
        return None
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return None


def parse_task_content(task):
    """解析任務內容"""
    # 任務的 notes 欄位可能包含 JSON 或配置資訊
    notes = task.notes or ""
    title = task.title or ""
    
    # 嘗試解析 JSON
    try:
        if notes.strip().startswith("{") or notes.strip().startswith("["):
            content = json.loads(notes)
            return content, "json"
    except:
        pass
    
    # 如果 notes 是純文字，返回文字內容
    if notes:
        return notes, "text"
    
    # 如果沒有 notes，返回標題
    return title, "text"


def save_to_file(content, target_file: Path, content_type: str):
    """儲存內容到檔案"""
    try:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        if content_type == "json":
            # 儲存為 JSON
            target_file.write_text(
                json.dumps(content, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        else:
            # 儲存為文字
            target_file.write_text(str(content), encoding="utf-8")
        
        print(f"✓ 已覆蓋本地檔案: {target_file}")
        return True
    except Exception as e:
        print(f"✗ 儲存失敗: {e}")
        return False


def main():
    """主函數"""
    if len(sys.argv) < 2:
        print("使用方式: python sync_from_google_task.py <task_url> [target_file]")
        print("範例: python sync_from_google_task.py \"https://jules.google.com/task/9554046612705221251\" config.json")
        sys.exit(1)
    
    task_url = sys.argv[1]
    target_file_str = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("=" * 70)
    print("從 Google Tasks 同步並覆蓋本地檔案")
    print("=" * 70)
    print(f"任務 URL: {task_url}")
    print()
    
    # 獲取任務
    task = get_task_from_url(task_url)
    if not task:
        sys.exit(1)
    
    print()
    print("【任務資訊】")
    print(f"  標題: {task.title}")
    print(f"  狀態: {task.status}")
    if task.notes:
        print(f"  備註長度: {len(task.notes)} 字元")
    print()
    
    # 解析任務內容
    content, content_type = parse_task_content(task)
    
    # 決定目標檔案
    if target_file_str:
        target_file = Path(target_file_str).resolve()
    else:
        # 根據內容類型決定預設檔名
        if content_type == "json":
            target_file = BASE_DIR / "google_task_sync.json"
        else:
            target_file = BASE_DIR / "google_task_sync.txt"
    
    print("【同步資訊】")
    print(f"  內容類型: {content_type}")
    print(f"  目標檔案: {target_file}")
    print()
    
    # 確認覆蓋
    if target_file.exists():
        print(f"⚠️  警告：檔案 {target_file} 已存在，將被覆蓋")
        print()
    
    # 儲存內容
    if save_to_file(content, target_file, content_type):
        print()
        print("【同步完成】")
        print(f"  任務內容已成功覆蓋到: {target_file}")
        
        # 顯示內容預覽
        if content_type == "json":
            print()
            print("【內容預覽】")
            print(json.dumps(content, ensure_ascii=False, indent=2)[:500])
            if len(json.dumps(content, ensure_ascii=False)) > 500:
                print("... (內容已截斷)")
        else:
            print()
            print("【內容預覽】")
            print(str(content)[:500])
            if len(str(content)) > 500:
                print("... (內容已截斷)")
    else:
        sys.exit(1)
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
