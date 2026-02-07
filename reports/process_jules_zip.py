#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
process_jules_zip.py

處理從 Google Tasks 下載的 ZIP 檔案

使用方式：
  python process_jules_zip.py "jules_session_9554046612705221251_wuchang-file-sync-9554046612705221251 (1).zip"
"""

import sys
import zipfile
import json
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def extract_zip(zip_path: Path, extract_to: Path = None):
    """解壓縮 ZIP 檔案"""
    if extract_to is None:
        extract_to = zip_path.parent / zip_path.stem
    
    print(f"正在解壓縮: {zip_path.name}")
    print(f"目標目錄: {extract_to}")
    print()
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 列出所有檔案
            file_list = zip_ref.namelist()
            print(f"【檔案清單】共 {len(file_list)} 個檔案")
            for f in file_list:
                print(f"  - {f}")
            print()
            
            # 解壓縮
            extract_to.mkdir(parents=True, exist_ok=True)
            zip_ref.extractall(extract_to)
            
            print(f"✓ 解壓縮完成")
            print(f"  解壓縮到: {extract_to}")
            print()
            
            return extract_to, file_list
    except Exception as e:
        print(f"✗ 解壓縮失敗: {e}")
        return None, []


def process_extracted_files(extract_dir: Path, file_list: list):
    """處理解壓縮後的檔案"""
    print("【處理檔案】")
    print()
    
    # 尋找 JSON 檔案
    json_files = [f for f in file_list if f.endswith('.json')]
    if json_files:
        print("找到 JSON 檔案:")
        for json_file in json_files:
            json_path = extract_dir / json_file
            if json_path.exists():
                try:
                    content = json.loads(json_path.read_text(encoding="utf-8"))
                    print(f"  - {json_file}")
                    print(f"    內容預覽: {json.dumps(content, ensure_ascii=False, indent=2)[:300]}")
                    if len(json.dumps(content, ensure_ascii=False)) > 300:
                        print("    ... (內容已截斷)")
                    print()
                    
                    # 如果是配置檔案，可以覆蓋本地檔案
                    if "config" in json_file.lower() or "sync" in json_file.lower():
                        print(f"  → 檢測到配置/同步檔案，可以覆蓋本地配置")
                except Exception as e:
                    print(f"  - {json_file} (解析失敗: {e})")
        print()
    
    # 尋找文字檔案
    text_files = [f for f in file_list if f.endswith(('.txt', '.md', '.jsonl'))]
    if text_files:
        print("找到文字檔案:")
        for text_file in text_files:
            text_path = extract_dir / json_file
            if text_path.exists():
                content = text_path.read_text(encoding="utf-8")
                print(f"  - {text_file}")
                print(f"    內容長度: {len(content)} 字元")
                print(f"    內容預覽: {content[:200]}")
                if len(content) > 200:
                    print("    ... (內容已截斷)")
                print()
    
    return extract_dir


def sync_to_local(extract_dir: Path, file_list: list):
    """同步到本地檔案"""
    print("【同步到本地】")
    print()
    
    # 尋找需要同步的檔案
    sync_candidates = []
    for f in file_list:
        if f.endswith('.json'):
            # 檢查是否為配置檔案
            if any(keyword in f.lower() for keyword in ['config', 'sync', 'env', 'settings']):
                sync_candidates.append(f)
    
    if not sync_candidates:
        print("未找到可同步的配置檔案")
        return
    
    print("找到可同步的檔案:")
    for candidate in sync_candidates:
        print(f"  - {candidate}")
    print()
    
    # 詢問是否同步
    print("是否要覆蓋本地檔案？")
    print("（此操作會覆蓋現有檔案，請確認）")
    print()
    
    # 這裡可以添加實際的同步邏輯
    # 例如：將 JSON 檔案複製到專案根目錄


def main():
    """主函數"""
    if len(sys.argv) < 2:
        print("使用方式: python process_jules_zip.py <zip_file>")
        print("範例: python process_jules_zip.py \"jules_session_9554046612705221251_wuchang-file-sync-9554046612705221251 (1).zip\"")
        sys.exit(1)
    
    zip_file_str = sys.argv[1]
    zip_path = Path(zip_file_str)
    
    if not zip_path.is_absolute():
        zip_path = BASE_DIR / zip_path
    
    print("=" * 70)
    print("處理 Google Tasks ZIP 檔案")
    print("=" * 70)
    print(f"ZIP 檔案: {zip_path}")
    print()
    
    # 檢查檔案是否存在
    if not zip_path.exists():
        print(f"✗ 檔案不存在: {zip_path}")
        print()
        print("請確認檔案路徑，或將檔案放置在專案根目錄")
        sys.exit(1)
    
    print(f"✓ 檔案存在")
    print(f"  檔案大小: {zip_path.stat().st_size / 1024:.2f} KB")
    print()
    
    # 解壓縮
    extract_dir, file_list = extract_zip(zip_path)
    if not extract_dir:
        sys.exit(1)
    
    # 處理檔案
    process_extracted_files(extract_dir, file_list)
    
    # 同步到本地（可選）
    # sync_to_local(extract_dir, file_list)
    
    print("=" * 70)
    print()
    print("【下一步】")
    print(f"解壓縮的檔案位於: {extract_dir}")
    print("請檢查檔案內容，確認需要同步的配置")


if __name__ == "__main__":
    main()
