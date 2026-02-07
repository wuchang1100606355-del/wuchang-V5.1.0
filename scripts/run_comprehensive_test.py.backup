#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wuchang OS - 綜合測試腳本
進行系統完整性、服務狀態和功能測試
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

BASE_PATH = Path(__file__).parent.parent

def print_header():
    """打印標題"""
    print("=" * 80)
    print("  Wuchang OS V5.1.0 - 綜合系統測試")
    print("=" * 80)
    print()

def test_file_integrity():
    """測試檔案完整性"""
    print("[1/5] 測試檔案完整性...")
    print("-" * 80)
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(BASE_PATH / 'scripts' / 'check_file_integrity.py')],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("  ✓ 檔案完整性檢查通過")
            
            # 提取完整性百分比
            if '100.0%' in result.stdout or '100%' in result.stdout:
                print("  ✓ 完整性: 100%")
                return True
            else:
                print("  ⚠ 完整性未達 100%")
                return False
        else:
            print("  ✗ 檔案完整性檢查失敗")
            return False
    except Exception as e:
        print(f"  ✗ 測試失敗: {e}")
        return False
    
    print()

def test_docker_services():
    """測試 Docker 服務"""
    print("[2/5] 測試 Docker 服務...")
    print("-" * 80)
    
    services = {
        'Odoo': 'http://localhost:8069/web/health',
        'Ollama': 'http://localhost:11434/api/tags',
        'Open WebUI': 'http://localhost:8080',
    }
    
    results = {}
    
    for service_name, url in services.items():
        try:
            req = Request(url)
            req.add_header('User-Agent', 'Wuchang-Test/1.0')
            response = urlopen(req, timeout=5)
            if response.getcode() in [200, 301, 302]:
                print(f"  ✓ {service_name}: 運行中 ({url})")
                results[service_name] = True
            else:
                print(f"  ⚠ {service_name}: 響應異常 (HTTP {response.getcode()})")
                results[service_name] = False
        except (URLError, OSError) as e:
            print(f"  ✗ {service_name}: 不可用 ({type(e).__name__})")
            results[service_name] = False
    
    print()
    
    success_count = sum(1 for v in results.values() if v)
    return success_count, len(services)

def test_ollama_models():
    """測試 Ollama 模型"""
    print("[3/5] 測試 Ollama 模型...")
    print("-" * 80)
    
    try:
        req = Request('http://localhost:11434/api/tags')
        req.add_header('User-Agent', 'Wuchang-Test/1.0')
        response = urlopen(req, timeout=5)
        if response.getcode() == 200:
            data = json.loads(response.read().decode('utf-8'))
            models = data.get('models', [])
            model_names = [m.get('name', '') for m in models]
            
            if model_names:
                print(f"  ✓ Ollama 可用")
                print(f"  ✓ 可用模型: {', '.join(model_names)}")
                print(f"  ✓ 模型數量: {len(model_names)}")
                return True, len(model_names)
            else:
                print("  ⚠ Ollama 可用但無模型")
                return False, 0
        else:
            print(f"  ✗ Ollama 響應異常 (HTTP {response.getcode()})")
            return False, 0
    except (URLError, OSError) as e:
        print(f"  ✗ Ollama 不可用: {type(e).__name__}")
        return False, 0
    
    print()

def test_odoo_modules():
    """測試 Odoo 模組"""
    print("[4/5] 測試 Odoo 模組...")
    print("-" * 80)
    
    try:
        # 檢查 Odoo 服務是否運行
        req = Request('http://localhost:8069/web/health')
        req.add_header('User-Agent', 'Wuchang-Test/1.0')
        response = urlopen(req, timeout=5)
        
        if response.getcode() == 200:
            print("  ✓ Odoo 服務運行中")
            
            # 檢查模組目錄
            modules_path = BASE_PATH / 'wuchang_os' / 'addons'
            if modules_path.exists():
                modules = [d.name for d in modules_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
                wuchang_modules = [m for m in modules if m.startswith('wuchang_')]
                
                print(f"  ✓ 找到 {len(wuchang_modules)} 個 Wuchang 模組")
                print(f"    模組: {', '.join(wuchang_modules[:5])}" + ("..." if len(wuchang_modules) > 5 else ""))
                return True, len(wuchang_modules)
            else:
                print("  ✗ 模組目錄不存在")
                return False, 0
        else:
            print(f"  ⚠ Odoo 響應異常 (HTTP {response.getcode()})")
            return False, 0
    except (URLError, OSError) as e:
        print(f"  ✗ Odoo 不可用: {type(e).__name__}")
        return False, 0
    
    print()

def test_system_config():
    """測試系統配置"""
    print("[5/5] 測試系統配置...")
    print("-" * 80)
    
    configs = {
        'docker-compose.yml': BASE_PATH / 'docker-compose.yml',
        'docker-compose-ai.yml': BASE_PATH / 'docker-compose-ai.yml',
        'odoo.conf': BASE_PATH / 'config' / 'odoo.conf',
        'ai_identity.json': BASE_PATH / 'config' / 'official_ai_identity.json',
    }
    
    results = {}
    
    for name, path in configs.items():
        if path.exists():
            size = path.stat().st_size
            print(f"  ✓ {name}: 存在 ({size:,} bytes)")
            results[name] = True
        else:
            print(f"  ✗ {name}: 不存在")
            results[name] = False
    
    print()
    
    success_count = sum(1 for v in results.values() if v)
    return success_count, len(configs)

def generate_test_report(results):
    """生成測試報告"""
    try:
        report_dir = BASE_PATH / 'logs'
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f'comprehensive_test_{timestamp}.json'
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'base_path': str(BASE_PATH),
            'test_results': results,
            'summary': {
                'total_tests': 5,
                'passed_tests': sum(1 for r in results.values() if isinstance(r, dict) and r.get('passed', False)),
                'overall_status': 'PASS' if all(r.get('passed', False) for r in results.values() if isinstance(r, dict)) else 'PARTIAL'
            }
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 測試報告已保存至: {report_file}")
        return str(report_file)
    except Exception as e:
        print(f"⚠ 保存測試報告失敗: {e}")
        return None

def main():
    """主函數"""
    print_header()
    
    print(f"測試路徑: {BASE_PATH}")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # 執行測試
    file_integrity = test_file_integrity()
    results['file_integrity'] = {'passed': file_integrity, 'name': '檔案完整性'}
    
    service_count, service_total = test_docker_services()
    results['docker_services'] = {
        'passed': service_count >= service_total - 1,  # 允許1個服務未運行
        'count': service_count,
        'total': service_total,
        'name': 'Docker 服務'
    }
    
    ollama_ok, model_count = test_ollama_models()
    results['ollama_models'] = {
        'passed': ollama_ok,
        'model_count': model_count,
        'name': 'Ollama 模型'
    }
    
    odoo_ok, module_count = test_odoo_modules()
    results['odoo_modules'] = {
        'passed': odoo_ok,
        'module_count': module_count,
        'name': 'Odoo 模組'
    }
    
    config_count, config_total = test_system_config()
    results['system_config'] = {
        'passed': config_count == config_total,
        'count': config_count,
        'total': config_total,
        'name': '系統配置'
    }
    
    # 生成報告
    report_file = generate_test_report(results)
    
    # 總結
    print("=" * 80)
    print("測試結果總結")
    print("=" * 80)
    print()
    
    passed_count = sum(1 for r in results.values() if isinstance(r, dict) and r.get('passed', False))
    total_count = len(results)
    
    for test_name, result in results.items():
        if isinstance(result, dict):
            status = "✓" if result.get('passed', False) else "✗"
            name = result.get('name', test_name)
            
            if 'count' in result:
                print(f"  {status} {name}: {result['count']}/{result['total']}")
            elif 'model_count' in result:
                print(f"  {status} {name}: {result['model_count']} 個模型")
            elif 'module_count' in result:
                print(f"  {status} {name}: {result['module_count']} 個模組")
            else:
                print(f"  {status} {name}")
    
    print()
    print(f"通過: {passed_count}/{total_count} 項測試")
    print()
    
    if passed_count == total_count:
        print("=" * 80)
        print("✅ 所有測試通過")
        print("=" * 80)
        return 0
    elif passed_count >= total_count - 1:
        print("=" * 80)
        print("⚠️  大部分測試通過")
        print("=" * 80)
        return 0
    else:
        print("=" * 80)
        print("❌ 部分測試失敗")
        print("=" * 80)
        return 1

if __name__ == '__main__':
    sys.exit(main())
