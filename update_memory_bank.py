#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_memory_bank.py

更新 JULES 記憶庫（由兩小 j 共同編寫）
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 設定 UTF-8 編碼
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
MEMORY_BANK_FILE = BASE_DIR / "jules_memory_bank.json"


def load_memory_bank():
    """載入記憶庫"""
    if MEMORY_BANK_FILE.exists():
        try:
            return json.loads(MEMORY_BANK_FILE.read_text(encoding="utf-8"))
        except:
            return {}
    return {}


def save_memory_bank(memory_bank: dict, updated_by: str = "地端小 j + JULES"):
    """儲存記憶庫"""
    memory_bank["last_updated"] = datetime.now().isoformat()
    memory_bank["updated_by"] = updated_by
    
    # 備份舊版本
    if MEMORY_BANK_FILE.exists():
        backup_file = BASE_DIR / f"jules_memory_bank_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            MEMORY_BANK_FILE.rename(backup_file)
            print(f"已備份舊版本到: {backup_file.name}")
        except:
            pass
    
    # 儲存新版本
    MEMORY_BANK_FILE.write_text(
        json.dumps(memory_bank, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"✅ 記憶庫已更新")
    print(f"   更新時間: {memory_bank['last_updated']}")
    print(f"   更新者: {updated_by}")


def update_system_architecture(memory_bank: dict, updates: dict):
    """更新系統架構描述"""
    if "system_architecture" not in memory_bank:
        memory_bank["system_architecture"] = {}
    
    architecture = memory_bank["system_architecture"]
    
    # 更新各個部分
    for key, value in updates.items():
        architecture[key] = value
    
    architecture["last_updated"] = datetime.now().isoformat()
    architecture["last_updated_by"] = "地端小 j + JULES"
    
    return memory_bank


def main():
    """主函數"""
    print("=" * 70)
    print("更新 JULES 記憶庫")
    print("=" * 70)
    print()
    
    memory_bank = load_memory_bank()
    
    if not memory_bank:
        print("❌ 記憶庫檔案不存在或無法讀取")
        print("請確認 jules_memory_bank.json 存在")
        return
    
    print("當前記憶庫版本:", memory_bank.get("version", "未知"))
    print("最後更新:", memory_bank.get("last_updated", "未知"))
    print("更新者:", memory_bank.get("updated_by", "未知"))
    print()
    
    print("記憶庫內容摘要：")
    print()
    
    # 顯示夥伴關係
    partnership = memory_bank.get("partnership", {})
    if partnership:
        print("【夥伴關係】")
        print(f"  地端小 j: {partnership.get('地端小j', {}).get('身份', '')}")
        print(f"  雲端小 j: {partnership.get('雲端小j', {}).get('身份', '')}")
        print()
    
    # 顯示系統架構
    architecture = memory_bank.get("system_architecture", {})
    if architecture:
        container_arch = architecture.get("容器架構", {})
        print("【系統架構】")
        print(f"  標準容器數量: {container_arch.get('標準容器數量', 0)}")
        print()
    
    print("=" * 70)
    print("如需更新記憶庫，請編輯 jules_memory_bank.json")
    print("或使用此腳本進行程式化更新")
    print("=" * 70)


if __name__ == "__main__":
    main()
