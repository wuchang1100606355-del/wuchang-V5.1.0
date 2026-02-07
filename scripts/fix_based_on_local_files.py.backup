#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基於地端檔案進行系統修復
根據完整性檢查和架構報告進行自動修復
"""

import sys
import os
import json
import re
from datetime import datetime
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent

def print_header():
    """打印標題"""
    print("=" * 80)
    print("  Wuchang OS - 基於地端檔案進行系統修復")
    print("=" * 80)
    print()

def check_and_fix_versions():
    """檢查並修復版本號一致性"""
    print("[1/4] 檢查並修復版本號一致性...")
    print("-" * 80)
    
    modules = [
        'wuchang_core', 'wuchang_finance', 'wuchang_business', 'wuchang_volunteer',
        'wuchang_community_campaign', 'wuchang_web_portal', 'wuchang_design_system',
        'wuchang_ui_compliance', 'wuchang_property_toolkits', 'wuchang_award_coach',
        'wuchang_guardian', 'wuchang_life'
    ]
    
    target_version = '5.1.0'
    fixed_count = 0
    
    for module in modules:
        manifest_path = BASE_PATH / 'wuchang_os' / 'addons' / module / '__manifest__.py'
        if not manifest_path.exists():
            print(f"  ⚠ {module}: 模組不存在")
            continue
        
        try:
            content = manifest_path.read_text(encoding='utf-8')
            # 檢查版本號
            version_match = re.search(r"'version'\s*:\s*['\"]([^'\"]+)['\"]", content)
            if version_match:
                current_version = version_match.group(1)
                if current_version != target_version:
                    # 修復版本號
                    content = re.sub(
                        r"'version'\s*:\s*['\"][^'\"]+['\"]",
                        f"'version': '{target_version}'",
                        content
                    )
                    manifest_path.write_text(content, encoding='utf-8')
                    print(f"  ✓ {module}: {current_version} -> {target_version}")
                    fixed_count += 1
                else:
                    print(f"  ✓ {module}: {target_version} (已正確)")
            else:
                print(f"  ⚠ {module}: 未找到版本號")
        except Exception as e:
            print(f"  ✗ {module}: 修復失敗 - {e}")
    
    print(f"\n修復版本號: {fixed_count} 個模組")
    print()
    return fixed_count

def check_models_imports():
    """檢查模型導入完整性"""
    print("[2/4] 檢查模型導入完整性...")
    print("-" * 80)
    
    models_init_path = BASE_PATH / 'wuchang_os' / 'addons' / 'wuchang_core' / 'models' / '__init__.py'
    
    if not models_init_path.exists():
        print("  ✗ models/__init__.py 不存在")
        return False
    
    content = models_init_path.read_text(encoding='utf-8')
    
    # 檢查關鍵模型是否已導入
    required_models = [
        'volunteer', 'res_partner', 'res_users', 'finance', 'delivery', 'governance',
        'order', 'task', 'settings', 'menu',
        'pos_config_ext', 'pos_expense',
        'property_management',
        'sister_control', 'infrastructure', 'device_control', 'system_tools',
        'ai_logic', 'ai_memory', 'ai_prompt', 'ai_agent_new',
        'ai_event_listener', 'ai_guard', 'ai_index_mixin',
        'ai_perception_sensor', 'ai_property_expert',
        'collab_meeting', 'core_logic', 'jf_gateway', 'mail_bot'
    ]
    
    missing_models = []
    for model in required_models:
        if f"from . import {model}" not in content and f"import {model}" not in content:
            missing_models.append(model)
    
    if missing_models:
        print(f"  ⚠ 缺少 {len(missing_models)} 個模型導入: {', '.join(missing_models)}")
        return False
    else:
        print(f"  ✓ 所有 {len(required_models)} 個關鍵模型都已導入")
        return True
    
    print()

def check_security_files():
    """檢查安全配置文件"""
    print("[3/4] 檢查安全配置文件...")
    print("-" * 80)
    
    security_path = BASE_PATH / 'wuchang_os' / 'addons' / 'wuchang_core' / 'security' / 'ir.model.access.csv'
    
    if not security_path.exists():
        print("  ✗ ir.model.access.csv 不存在")
        return False
    
    content = security_path.read_text(encoding='utf-8')
    
    # 檢查是否有註釋掉的訪問規則
    commented_lines = [line for line in content.split('\n') if line.strip().startswith('#') and 'model_' in line]
    
    if commented_lines:
        print(f"  ⚠ 發現 {len(commented_lines)} 個註釋掉的訪問規則")
        for line in commented_lines[:5]:  # 只顯示前5個
            print(f"    - {line.strip()[:60]}...")
        return False
    else:
        print("  ✓ 安全配置文件正常")
        return True
    
    print()

def check_config_files():
    """檢查配置文件一致性"""
    print("[4/4] 檢查配置文件一致性...")
    print("-" * 80)
    
    configs = {
        'docker-compose.yml': BASE_PATH / 'docker-compose.yml',
        'docker-compose-ai.yml': BASE_PATH / 'docker-compose-ai.yml',
        'odoo.conf': BASE_PATH / 'config' / 'odoo.conf',
        'official_ai_identity.json': BASE_PATH / 'config' / 'official_ai_identity.json',
    }
    
    all_ok = True
    for name, path in configs.items():
        if path.exists():
            size = path.stat().st_size
            print(f"  ✓ {name}: 存在 ({size:,} bytes)")
        else:
            print(f"  ✗ {name}: 不存在")
            all_ok = False
    
    print()
    return all_ok

def generate_fix_report(results):
    """生成修復報告"""
    try:
        report_dir = BASE_PATH / 'logs'
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f'fix_report_{timestamp}.json'
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'base_path': str(BASE_PATH),
            'fixes_applied': results,
            'summary': {
                'version_fixes': results.get('versions_fixed', 0),
                'models_complete': results.get('models_complete', False),
                'security_ok': results.get('security_ok', False),
                'configs_ok': results.get('configs_ok', False)
            }
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 修復報告已保存至: {report_file}")
        return str(report_file)
    except Exception as e:
        print(f"⚠ 保存修復報告失敗: {e}")
        return None

def main():
    """主函數"""
    print_header()
    
    print(f"檢查路徑: {BASE_PATH}")
    print(f"修復時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # 執行修復
    versions_fixed = check_and_fix_versions()
    results['versions_fixed'] = versions_fixed
    
    models_complete = check_models_imports()
    results['models_complete'] = models_complete
    
    security_ok = check_security_files()
    results['security_ok'] = security_ok
    
    configs_ok = check_config_files()
    results['configs_ok'] = configs_ok
    
    # 生成報告
    report_file = generate_fix_report(results)
    
    # 總結
    print("=" * 80)
    print("修復結果總結")
    print("=" * 80)
    print()
    
    print(f"版本修復: {versions_fixed} 個模組")
    print(f"模型導入: {'✓ 完整' if models_complete else '✗ 不完整'}")
    print(f"安全配置: {'✓ 正常' if security_ok else '✗ 需要檢查'}")
    print(f"配置文件: {'✓ 完整' if configs_ok else '✗ 缺失'}")
    print()
    
    if versions_fixed == 0 and models_complete and security_ok and configs_ok:
        print("=" * 80)
        print("✅ 所有項目已修復或正常")
        print("=" * 80)
        return 0
    else:
        print("=" * 80)
        print("⚠️  部分項目需要進一步檢查")
        print("=" * 80)
        return 1

if __name__ == '__main__':
    sys.exit(main())
