#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全讀取 JULES 記憶庫的輔助函數
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent
MEMORY_BANK_FILE = BASE_DIR / "jules_memory_bank.json"


def load_memory_bank() -> Dict[str, Any]:
    """安全載入記憶庫，支援多種鍵名格式"""
    if not MEMORY_BANK_FILE.exists():
        return {}
    
    try:
        memory_bank = json.loads(MEMORY_BANK_FILE.read_text(encoding="utf-8"))
        
        # 標準化鍵名（支援中英文鍵名）
        if "system_architecture" in memory_bank:
            arch = memory_bank["system_architecture"]
            # 如果使用 container_architecture，也提供 容器架構 別名
            if "container_architecture" in arch and "容器架構" not in arch:
                arch["容器架構"] = arch["container_architecture"]
        
        return memory_bank
    except Exception as e:
        print(f"讀取記憶庫失敗: {e}")
        return {}


def get_partnership_info(memory_bank: Dict[str, Any]) -> Dict[str, Any]:
    """取得夥伴關係資訊"""
    partnership = memory_bank.get("partnership", {})
    
    return {
        "地端小j": partnership.get("地端小j", {}),
        "雲端小j": partnership.get("雲端小j", {}),
        "協作模式": partnership.get("協作模式", {}),
        "信任關係": partnership.get("信任關係", {})
    }


def get_container_architecture(memory_bank: Dict[str, Any]) -> Dict[str, Any]:
    """取得容器架構資訊（支援多種鍵名）"""
    arch = memory_bank.get("system_architecture", {})
    
    # 嘗試多種可能的鍵名
    container_arch = (
        arch.get("容器架構") or 
        arch.get("container_architecture") or 
        {}
    )
    
    return container_arch


if __name__ == "__main__":
    memory_bank = load_memory_bank()
    
    print("記憶庫讀取測試：")
    print(f"  版本: {memory_bank.get('version', '未知')}")
    print(f"  最後更新: {memory_bank.get('last_updated', '未知')}")
    
    partnership = get_partnership_info(memory_bank)
    print(f"  地端小 j: {partnership.get('地端小j', {}).get('身份', '未知')}")
    print(f"  雲端小 j: {partnership.get('雲端小j', {}).get('身份', '未知')}")
    
    container_arch = get_container_architecture(memory_bank)
    print(f"  標準容器數量: {container_arch.get('標準容器數量', '未知')}")
