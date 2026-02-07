#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
評估安裝報告是否適合套用
"""

import sys
from pathlib import Path
from datetime import datetime
import json

WORKSPACE_PATH = Path(__file__).parent.parent
REPORTS_PATH = WORKSPACE_PATH / 'reports'

def read_report(file_path: Path):
    """讀取報告檔案"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return None

def evaluate_report(report_name: str, content: str):
    """評估單個報告"""
    evaluation = {
        'report_name': report_name,
        'suitable': False,
        'reasons': [],
        'warnings': [],
        'recommendations': []
    }
    
    # 檢查關鍵字
    content_lower = content.lower()
    
    # 檢查是否為完成狀態
    if any(keyword in content_lower for keyword in ['complete', '完成', 'success', '成功', 'ready', '就緒']):
        evaluation['suitable'] = True
        evaluation['reasons'].append('報告顯示安裝已完成或就緒')
    
    # 檢查是否有錯誤
    if any(keyword in content_lower for keyword in ['error', '錯誤', 'fail', '失敗', 'issue', '問題']):
        evaluation['warnings'].append('報告中包含錯誤或問題')
        evaluation['suitable'] = False
    
    # 檢查是否有待辦事項
    if any(keyword in content_lower for keyword in ['todo', '待辦', 'pending', 'pending', '需要', 'required']):
        evaluation['warnings'].append('報告中包含待辦事項')
    
    # 檢查時間戳記
    if '2026-01' in content or '2026/01' in content:
        evaluation['reasons'].append('報告為近期產生（2026年1月）')
    
    # 檢查 Docker 相關
    if 'docker' in content_lower:
        evaluation['recommendations'].append('需要確認 Docker 環境是否就緒')
    
    # 檢查資料庫相關
    if any(keyword in content_lower for keyword in ['database', '資料庫', 'postgres', 'odoo']):
        evaluation['recommendations'].append('需要確認資料庫狀態')
    
    return evaluation

def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("  📊 安裝報告評估工具")
    print("=" * 60)
    
    # 關鍵報告檔案
    key_reports = [
        'DEPLOYMENT_HISTORY_SUMMARY.md',
        'AUTO_SETUP_READY.md',
        'MODULE_INSTALLATION_COMPLETE.md',
        'ODOO_MODULE_INSTALLATION_EXPLANATION.md',
        'SYSTEM_HEALTH_REPORT.md',
        'CUSTOM_MODULES_STATUS.md'
    ]
    
    evaluations = []
    
    for report_name in key_reports:
        report_path = REPORTS_PATH / report_name
        if report_path.exists():
            print(f"\n📄 評估報告: {report_name}")
            content = read_report(report_path)
            if content:
                evaluation = evaluate_report(report_name, content)
                evaluations.append(evaluation)
                
                # 顯示評估結果
                status = "✅ 適合套用" if evaluation['suitable'] else "⚠️ 需要檢查"
                print(f"  狀態: {status}")
                
                if evaluation['reasons']:
                    print("  理由:")
                    for reason in evaluation['reasons']:
                        print(f"    • {reason}")
                
                if evaluation['warnings']:
                    print("  警告:")
                    for warning in evaluation['warnings']:
                        print(f"    ⚠️ {warning}")
                
                if evaluation['recommendations']:
                    print("  建議:")
                    for rec in evaluation['recommendations']:
                        print(f"    💡 {rec}")
            else:
                print(f"  ❌ 無法讀取報告")
        else:
            print(f"\n📄 {report_name}: ❌ 檔案不存在")
    
    # 總結
    print("\n" + "=" * 60)
    print("  📋 評估總結")
    print("=" * 60)
    
    suitable_count = sum(1 for e in evaluations if e['suitable'])
    total_count = len(evaluations)
    
    print(f"\n評估報告數量: {total_count}")
    print(f"適合套用: {suitable_count}")
    print(f"需要檢查: {total_count - suitable_count}")
    
    if suitable_count > 0:
        print("\n✅ 可以考慮套用的報告:")
        for eval in evaluations:
            if eval['suitable']:
                print(f"  • {eval['report_name']}")
    
    if total_count - suitable_count > 0:
        print("\n⚠️ 需要進一步檢查的報告:")
        for eval in evaluations:
            if not eval['suitable']:
                print(f"  • {eval['report_name']}")
                if eval['warnings']:
                    for warning in eval['warnings']:
                        print(f"    - {warning}")
    
    # 儲存評估結果
    output_file = REPORTS_PATH / f'installation_report_evaluation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'evaluation_time': datetime.now().isoformat(),
            'evaluations': evaluations,
            'summary': {
                'total': total_count,
                'suitable': suitable_count,
                'needs_review': total_count - suitable_count
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 評估結果已儲存至: {output_file}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
