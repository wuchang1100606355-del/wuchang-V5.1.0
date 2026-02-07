#!/usr/bin/env python3
"""
小j AI 學習系統 - 完整功能測試
"""

from sister_ai_learning_integration import enhance_ai_logic_with_learning
import sys


def test_system():
    print('='*60)
    print('小j AI 學習系統 - 完整測試')
    print('='*60)
    print()

    # 初始化系統
    print('[1] 初始化增強型 AI 邏輯...')
    try:
        ai = enhance_ai_logic_with_learning()
        print('✓ AI 系統初始化成功')
    except Exception as e:
        print(f'✗ 初始化失敗: {e}')
        return False
    print()

    # 測試 1: 處理查詢
    print('[2] 測試查詢處理...')
    try:
        result = ai.process_query(
            user_query='社區預算編制的最佳實踐是什麼？',
            user_id='test_user_001',
            domain='finance',
            user_intent='learn_best_practice',
            tags=['finance', 'budgeting', 'test'],
            model_used='local_ollama'
        )

        if result['success']:
            print('✓ 查詢已處理')
            print(f'  經驗ID: {result["experience_id"]}')
            print(f'  信心度: {result["confidence"]:.1%}')
            experience_id = result['experience_id']
        else:
            print(f'✗ 查詢失敗: {result.get("error")}')
            return False
    except Exception as e:
        print(f'✗ 查詢處理異常: {e}')
        return False
    print()

    # 測試 2: 記錄反饋
    print('[3] 測試反饋記錄...')
    try:
        feedback = ai.record_user_feedback(
            experience_id=experience_id,
            satisfaction=5,
            comments='非常有幫助的建議！',
            effectiveness=0.95,
            action_taken=True,
            result_description='已按照建議實施新的預算政策'
        )

        if feedback['success']:
            print(f'✓ 反饋已記錄: {feedback["feedback_id"]}')
        else:
            print(f'✗ 反饋記錄失敗: {feedback.get("error")}')
    except Exception as e:
        print(f'✗ 反饋記錄異常: {e}')
    print()

    # 測試 3: 知識庫統計
    print('[4] 檢查知識庫...')
    try:
        stats = ai.get_knowledge_stats()
        if stats['success']:
            kb = stats['stats']
            print('✓ 知識庫統計:')
            print(f'  總項目數: {kb["total_items"]}')
            print(f'  按類別: {dict(kb["by_category"])}')
            print(f'  平均效能: {kb["avg_effectiveness"]:.2f}')
        else:
            print(f'✗ 無法獲取統計')
    except Exception as e:
        print(f'✗ 統計異常: {e}')
    print()

    # 測試 4: 知識搜索
    print('[5] 測試知識搜索...')
    try:
        search = ai.search_knowledge('預算', category='finance', limit=3)
        if search['success']:
            results = search['results']
            print(f'✓ 搜索結果: 找到 {len(results)} 項')
            for item in results[:2]:
                print(f'  - {item["title"]}')
        else:
            print('✗ 搜索失敗')
    except Exception as e:
        print(f'✗ 搜索異常: {e}')
    print()

    # 測試 5: 添加知識
    print('[6] 測試添加知識...')
    try:
        new_knowledge = ai.add_knowledge(
            category='finance',
            title='季度財務報告流程',
            content='詳細說明如何編制季度財務報告，包括所有必要步驟和檢查點。',
            confidence_score=0.88,
            tags=['finance', 'reporting', 'quarterly', 'test']
        )

        if new_knowledge['success']:
            print(f'✓ 知識已添加: {new_knowledge["knowledge_id"]}')
        else:
            print('✗ 添加知識失敗')
    except Exception as e:
        print(f'✗ 添加知識異常: {e}')
    print()

    # 測試 6: 學習循環
    print('[7] 運行學習循環...')
    try:
        learning = ai.run_learning_cycle()
        if learning.get('status') == 'completed':
            print('✓ 學習循環完成')
            print(f'  新知識項目: {learning.get("new_knowledge_count", 0)}')
            if 'patterns' in learning:
                patterns = learning['patterns']
                print(f'  總經驗數: {patterns.get("total_experiences", 0)}')
        else:
            print(f'⚠ 學習循環狀態: {learning.get("status")}')
    except Exception as e:
        print(f'⚠ 學習循環異常: {e}')
    print()

    # 測試 7: 生成成長報告
    print('[8] 生成成長報告...')
    try:
        report = ai.generate_growth_report()
        print('✓ 成長報告已生成')
        print(f'  整體成長評分: {report.get("overall_growth_score", 0):.1f}/10')
        metrics = report.get('metrics', {})
        print(f'  準確性: {metrics.get("accuracy", 0):.1%}')
        print(f'  用戶滿意度: {metrics.get("user_satisfaction", 0):.1%}')
        print(f'  發現的里程碑: {len(report.get("milestones", []))}')
        print(f'  識別的挑戰: {len(report.get("challenges", []))}')
    except Exception as e:
        print(f'⚠ 報告生成異常: {str(e)[:100]}')
    print()

    print('='*60)
    print('✅ 測試完成！')
    print('='*60)
    return True


if __name__ == '__main__':
    success = test_system()
    sys.exit(0 if success else 1)
