#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速測試腳本
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def test_imports():
    """測試模組導入"""
    print("測試模組導入...")
    try:
        from local_control_center import BASE_DIR as CC_BASE
        print("  ✓ local_control_center 可導入")
    except Exception as e:
        print(f"  ✗ local_control_center 導入失敗: {e}")
    
    try:
        from google_tasks_integration import get_google_tasks_integration
        print("  ✓ google_tasks_integration 可導入")
    except Exception as e:
        print(f"  ✗ google_tasks_integration 導入失敗: {e}")

if __name__ == "__main__":
    test_imports()
