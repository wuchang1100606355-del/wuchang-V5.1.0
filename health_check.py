#!/usr/bin/env python3
"""
小j AI 學習系統 - 快速健康檢查
"""

import sys
from pathlib import Path


def check_files():
    print("\n" + "="*60)
    print("  小j AI 學習系統 - 快速健康檢查")
    print("="*60 + "\n")

    files = [
        ("核心模組", [
            "sister_learning_engine.py",
            "sister_growth_dashboard.py",
            "sister_ai_learning_integration.py",
            "initialize_learning_system.py"
        ]),
        ("文檔", [
            "docs/AI_LEARNING_FRAMEWORK.md",
            "docs/AI_LEARNING_IMPLEMENTATION_GUIDE.md",
            "docs/QUICK_REFERENCE_CARD.md"
        ]),
        ("配置", [
            "config/ai_learning_config.json"
        ]),
        ("測試", [
            "test_learning_system.py"
        ]),
        ("報告", [
            "AI_LEARNING_SYSTEM_COMPLETION_REPORT.md",
            "TEST_RESULTS_REPORT.md",
            "SYSTEM_READY_STATUS.md",
            "FINAL_DELIVERY_CHECKLIST.md"
        ])
    ]

    total = 0
    found = 0

    for category, file_list in files:
        print(f"\n📁 {category}:")
        for file in file_list:
            total += 1
            path = Path(file)
            if path.exists():
                size = path.stat().st_size
                print(f"  ✓ {file} ({size:,} bytes)")
                found += 1
            else:
                print(f"  ✗ {file} (缺失)")

    print("\n" + "-"*60)
    print(f"\n交付物完整性: {found}/{total} ({100*found//total}%)")

    if found == total:
        print("\n✅ 所有文件已就緒！")
        print("\n🚀 快速開始:")
        print("  1. python initialize_learning_system.py")
        print("  2. python test_learning_system.py")
        print("  3. 查看 docs/QUICK_REFERENCE_CARD.md")
        return True
    else:
        print(f"\n⚠️  缺失 {total - found} 個文件")
        return False


def check_imports():
    print("\n" + "-"*60)
    print("\n🔍 檢查模組導入...")

    try:
        from sister_learning_engine import create_learning_system
        print("  ✓ sister_learning_engine 導入成功")
    except ImportError as e:
        print(f"  ✗ sister_learning_engine 導入失敗: {e}")
        return False

    try:
        from sister_growth_dashboard import create_evaluation_system
        print("  ✓ sister_growth_dashboard 導入成功")
    except ImportError as e:
        print(f"  ✗ sister_growth_dashboard 導入失敗: {e}")
        return False

    try:
        from sister_ai_learning_integration import enhance_ai_logic_with_learning
        print("  ✓ sister_ai_learning_integration 導入成功")
    except ImportError as e:
        print(f"  ✗ sister_ai_learning_integration 導入失敗: {e}")
        return False

    print("\n✅ 所有模組導入成功！")
    return True


def check_directories():
    print("\n" + "-"*60)
    print("\n📂 檢查數據目錄...")

    dirs = [
        "memory_store",
        "memory_store/experiences",
        "memory_store/knowledge",
        "memory_store/feedback",
        "memory_store/evaluations",
        "memory_store/learning_logs",
        "memory_store/growth_metrics",
        "memory_store/dashboards"
    ]

    all_exist = True
    for dir in dirs:
        if Path(dir).exists():
            print(f"  ✓ {dir}")
        else:
            print(f"  ✗ {dir} (不存在)")
            all_exist = False

    if all_exist:
        print("\n✅ 所有數據目錄已就緒！")
    else:
        print("\n⚠️  某些目錄缺失，運行 initialize_learning_system.py 來創建")

    return all_exist


def main():
    print("\n" + "="*60)
    print("  小j AI 學習系統 - 健康檢查")
    print("="*60)

    # Check 1: Files
    files_ok = check_files()

    # Check 2: Imports
    imports_ok = check_imports()

    # Check 3: Directories
    dirs_ok = check_directories()

    # Summary
    print("\n" + "="*60)
    print("  檢查總結")
    print("="*60)

    print(f"\n交付物文件:  {'✓ 通過' if files_ok else '✗ 失敗'}")
    print(f"模組導入:    {'✓ 通過' if imports_ok else '✗ 失敗'}")
    print(f"數據目錄:    {'✓ 通過' if dirs_ok else '✗ 失敗'}")

    if files_ok and imports_ok:
        print("\n" + "="*60)
        print("  ✅ 系統健康檢查通過！")
        print("="*60)
        print("\n系統已準備就緒。您可以:")
        print("  1. 運行初始化: python initialize_learning_system.py")
        print("  2. 運行測試: python test_learning_system.py")
        print("  3. 開始使用: 查看 docs/QUICK_REFERENCE_CARD.md")
        return 0
    else:
        print("\n" + "="*60)
        print("  ⚠️  系統檢查發現問題")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
