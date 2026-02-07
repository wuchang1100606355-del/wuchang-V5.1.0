#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試時空系統部署
驗證所有功能是否正常運作
"""

import sys
from pathlib import Path

# 添加路徑
SPATIOTEMPORAL_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SPATIOTEMPORAL_ROOT))

def test_imports():
    """測試模組導入"""
    print("=" * 50)
    print("測試模組導入...")
    print("=" * 50)
    
    try:
        from core.spatiotemporal import SpatiotemporalSystem
        print("✓ SpatiotemporalSystem 導入成功")
    except Exception as e:
        print(f"✗ SpatiotemporalSystem 導入失敗: {e}")
        return False
    
    try:
        from core.ai_agent import AIAgent
        print("✓ AIAgent 導入成功")
    except Exception as e:
        print(f"✗ AIAgent 導入失敗: {e}")
        return False
    
    try:
        from applications.community_service import CommunityService
        print("✓ CommunityService 導入成功")
    except Exception as e:
        print(f"✗ CommunityService 導入失敗: {e}")
        return False
    
    try:
        from config.ai_j_integration import get_ai_j_spatiotemporal
        print("✓ AI J 整合模組導入成功")
    except Exception as e:
        print(f"✗ AI J 整合模組導入失敗: {e}")
        return False
    
    return True


def test_functionality():
    """測試功能"""
    print("\n" + "=" * 50)
    print("測試功能...")
    print("=" * 50)
    
    try:
        from core.spatiotemporal import SpatiotemporalSystem
        from core.ai_agent import AIAgent
        from datetime import datetime
        
        # 初始化
        st_system = SpatiotemporalSystem()
        ai_j = AIAgent(st_system)
        print("✓ 系統初始化成功")
        
        # 測試建議功能
        suggestions = ai_j.suggest_optimal_time_and_space(
            event_type="meeting",
            participants=10,
            duration_hours=2
        )
        print(f"✓ 建議功能測試成功: {len(suggestions.get('suggestions', []))} 個建議")
        
        # 測試事件建立
        event = st_system.create_spatiotemporal_event(
            title="測試活動",
            start_time=datetime(2026, 1, 20, 14, 0),
            end_time=datetime(2026, 1, 20, 16, 0),
            location="五常里活動中心",
            village_id="wuchang_li"
        )
        print(f"✓ 事件建立成功: {event.title}")
        
        return True
        
    except Exception as e:
        print(f"✗ 功能測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_j_integration():
    """測試 AI 小 J 整合"""
    print("\n" + "=" * 50)
    print("測試 AI 小 J 整合...")
    print("=" * 50)
    
    try:
        from config.ai_j_integration import get_ai_j_spatiotemporal
        
        st_integration = get_ai_j_spatiotemporal()
        print("✓ AI J 整合實例建立成功")
        
        # 查看能力
        capabilities = st_integration.get_capabilities()
        print(f"✓ 能力查詢成功:")
        print(f"  - 時空系統: {capabilities['spatiotemporal_system']['enabled']}")
        print(f"  - 雲端算力: {capabilities['cloud_compute']['enabled']}")
        
        # 測試建議
        suggestions = st_integration.suggest_event(
            event_type="meeting",
            participants=5,
            duration_hours=1
        )
        print(f"✓ 建議功能測試成功")
        
        return True
        
    except Exception as e:
        print(f"✗ AI J 整合測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cloud_compute():
    """測試雲端算力（如果已設定）"""
    print("\n" + "=" * 50)
    print("測試雲端算力...")
    print("=" * 50)
    
    import os
    
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    
    if openai_key:
        print("✓ OpenAI API Key 已設定")
    else:
        print("⚠ OpenAI API Key 未設定")
    
    if anthropic_key:
        print("✓ Anthropic API Key 已設定")
    else:
        print("⚠ Anthropic API Key 未設定")
    
    if google_key:
        print("✓ Google API Key 已設定")
    else:
        print("⚠ Google API Key 未設定")
    
    if not (openai_key or anthropic_key or google_key):
        print("⚠ 未設定任何雲端算力 API Key")
        print("  如需使用雲端算力，請設定環境變數")


def main():
    """主測試流程"""
    print("\n" + "=" * 50)
    print("時空系統部署測試")
    print("=" * 50 + "\n")
    
    results = []
    
    # 測試導入
    results.append(("模組導入", test_imports()))
    
    # 測試功能
    if results[-1][1]:
        results.append(("功能測試", test_functionality()))
        results.append(("AI J 整合", test_ai_j_integration()))
    
    # 測試雲端算力
    test_cloud_compute()
    
    # 總結
    print("\n" + "=" * 50)
    print("測試總結")
    print("=" * 50)
    
    for name, result in results:
        status = "✓ 通過" if result else "✗ 失敗"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✓ 所有測試通過！時空系統已成功部署。")
    else:
        print("\n✗ 部分測試失敗，請檢查錯誤訊息。")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
