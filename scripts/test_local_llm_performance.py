#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wuchang OS 本地 LLM 模型性能測試
測試 Ollama 本地模型的響應時間、吞吐量和質量
"""

import sys
import os
import json
import time
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError
from http.client import HTTPResponse

# 測試配置
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
TEST_MODELS = ['llama3.1', 'qwen2:0.5b', 'phi4', 'mistral']  # 要測試的模型列表
TEST_PROMPTS = [
    {
        'name': '短提示',
        'prompt': '你好，請簡單介紹一下你自己。',
        'system': '你是一個友善的 AI 助手。'
    },
    {
        'name': '中長提示',
        'prompt': '請解釋一下什麼是社區自治，以及它在現代社會中的重要性。請用三個要點說明。',
        'system': '你是一個專業的社區治理顧問。'
    },
    {
        'name': '複雜任務',
        'prompt': '你是一家咖啡店的 AI 助手。請為顧客創建一份包含早餐、午餐、下午茶和晚餐的菜單。每類至少包含 3 個項目，並包含價格。',
        'system': '你是一個創意豐富的餐廳顧問。'
    },
    {
        'name': '代碼生成',
        'prompt': '用 Python 寫一個函數，計算列表中所有偶數的平方和。',
        'system': '你是一個專業的程式設計師。'
    },
    {
        'name': '翻譯任務',
        'prompt': '請將以下文字翻譯成英文和日文：五常社區致力於建立一個和諧共融的居住環境。',
        'system': '你是一個專業的翻譯助手。'
    }
]

def print_header():
    """打印標題"""
    print("=" * 80)
    print("     Wuchang OS - 本地 LLM 模型性能測試")
    print("=" * 80)
    print()

def check_ollama_available():
    """檢查 Ollama 是否可用"""
    print("檢查 Ollama 服務...")
    try:
        req = Request(f"{OLLAMA_HOST}/api/tags")
        req.add_header('User-Agent', 'Wuchang-LLM-PerfTest/1.0')
        response = urlopen(req, timeout=5)
        if response.getcode() == 200:
            data = json.loads(response.read().decode('utf-8'))
            models = [m.get('name', '') for m in data.get('models', [])]
            print(f"  ✓ Ollama 服務正在運行 ({OLLAMA_HOST})")
            print(f"  ✓ 可用模型：{', '.join(models) if models else '無'}")
            return models
        else:
            print(f"  ✗ Ollama 響應異常 (HTTP {response.getcode()})")
            return []
    except (URLError, OSError) as e:
        print(f"  ✗ Ollama 服務不可用: {e}")
        print(f"  提示：請先啟動 Ollama 服務")
        print(f"  - Docker: docker-compose --profile ui up -d")
        print(f"  - 或運行: scripts/auto_install_ai.ps1")
        return []

def test_model_available(models, model_name):
    """檢查模型是否可用"""
    if not models:
        return False
    
    # 檢查完整匹配或部分匹配
    for m in models:
        if model_name in m or m.startswith(model_name):
            return True
    return False

def call_ollama(model, prompt, system_prompt=None, timeout=30):
    """調用 Ollama API"""
    try:
        url = f"{OLLAMA_HOST.rstrip('/')}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 512
            }
        }
        if system_prompt:
            payload["system"] = system_prompt
        
        req = Request(url, data=json.dumps(payload).encode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        req.add_header('User-Agent', 'Wuchang-LLM-PerfTest/1.0')
        
        start_time = time.time()
        response = urlopen(req, timeout=timeout)
        elapsed_time = time.time() - start_time
        
        if response.getcode() == 200:
            data = json.loads(response.read().decode('utf-8'))
            response_text = data.get('response', '')
            tokens = data.get('eval_count', 0)  # 生成的 token 數量
            
            # 計算 token 生成速度 (tokens/second)
            tokens_per_sec = tokens / elapsed_time if elapsed_time > 0 else 0
            
            return {
                'success': True,
                'response': response_text,
                'elapsed_time': elapsed_time,
                'tokens': tokens,
                'tokens_per_sec': tokens_per_sec,
                'response_length': len(response_text)
            }
        else:
            return {
                'success': False,
                'error': f"HTTP {response.getcode()}",
                'elapsed_time': elapsed_time
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)[:100],
            'elapsed_time': 0
        }

def test_model(model_name, available_models):
    """測試單個模型的性能"""
    print(f"\n{'='*80}")
    print(f"測試模型: {model_name}")
    print(f"{'='*80}")
    
    # 檢查模型是否可用
    if not test_model_available(available_models, model_name):
        print(f"  ⚠ 模型 '{model_name}' 不可用，跳過測試")
        return None
    
    print(f"  ✓ 模型可用，開始測試...")
    print()
    
    results = {
        'model': model_name,
        'tests': [],
        'summary': {
            'total_tests': 0,
            'successful_tests': 0,
            'failed_tests': 0,
            'total_time': 0,
            'avg_response_time': 0,
            'avg_tokens_per_sec': 0,
            'total_tokens': 0
        }
    }
    
    # 對每個測試提示進行測試
    for i, test_case in enumerate(TEST_PROMPTS, 1):
        print(f"[{i}/{len(TEST_PROMPTS)}] 測試: {test_case['name']}")
        print(f"  提示: {test_case['prompt'][:50]}...")
        
        result = call_ollama(
            model_name,
            test_case['prompt'],
            test_case.get('system')
        )
        
        if result['success']:
            print(f"  ✓ 成功")
            print(f"  - 響應時間: {result['elapsed_time']:.2f}s")
            print(f"  - 生成 Token 數: {result['tokens']}")
            print(f"  - Token/秒: {result['tokens_per_sec']:.2f}")
            print(f"  - 響應長度: {result['response_length']} 字元")
            print(f"  - 響應預覽: {result['response'][:100]}...")
            
            results['summary']['successful_tests'] += 1
            results['summary']['total_time'] += result['elapsed_time']
            results['summary']['total_tokens'] += result['tokens']
            if result['tokens_per_sec'] > 0:
                results['summary']['avg_tokens_per_sec'] += result['tokens_per_sec']
        else:
            print(f"  ✗ 失敗: {result.get('error', 'Unknown error')}")
            results['summary']['failed_tests'] += 1
        
        results['summary']['total_tests'] += 1
        results['tests'].append({
            'test_case': test_case['name'],
            **result
        })
        print()
    
    # 計算平均值
    if results['summary']['successful_tests'] > 0:
        results['summary']['avg_response_time'] = results['summary']['total_time'] / results['summary']['successful_tests']
        results['summary']['avg_tokens_per_sec'] = results['summary']['avg_tokens_per_sec'] / results['summary']['successful_tests']
    
    return results

def print_summary(all_results):
    """打印測試摘要"""
    print("\n" + "=" * 80)
    print("測試結果摘要")
    print("=" * 80)
    print()
    
    # 表格標題
    print(f"{'模型':<20} {'成功率':<12} {'平均響應時間':<16} {'平均速度':<16} {'總 Token':<12}")
    print("-" * 80)
    
    for result in all_results:
        if result:
            model = result['model']
            success_rate = (result['summary']['successful_tests'] / result['summary']['total_tests'] * 100) if result['summary']['total_tests'] > 0 else 0
            avg_time = result['summary']['avg_response_time']
            avg_speed = result['summary']['avg_tokens_per_sec']
            total_tokens = result['summary']['total_tokens']
            
            print(f"{model:<20} {success_rate:>6.1f}%     {avg_time:>8.2f}s       {avg_speed:>10.2f} t/s   {total_tokens:>10}")
    
    print()

def save_results(all_results):
    """保存測試結果到文件"""
    try:
        workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        results_dir = os.path.join(workspace_path, 'logs')
        os.makedirs(results_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = os.path.join(results_dir, f'llm_performance_test_{timestamp}.json')
        
        output = {
            'timestamp': datetime.now().isoformat(),
            'ollama_host': OLLAMA_HOST,
            'results': all_results
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 測試結果已保存至: {results_file}")
        return results_file
    except Exception as e:
        print(f"⚠ 保存測試結果失敗: {e}")
        return None

def main():
    """主函數"""
    print_header()
    
    # 檢查 Ollama 服務
    available_models = check_ollama_available()
    if not available_models:
        print("\n❌ 無法繼續測試：Ollama 服務不可用")
        return 1
    
    print()
    
    # 過濾可用的測試模型
    models_to_test = [m for m in TEST_MODELS if test_model_available(available_models, m)]
    
    if not models_to_test:
        print("⚠ 沒有找到可測試的模型")
        print(f"可用模型: {', '.join(available_models)}")
        print(f"測試模型: {', '.join(TEST_MODELS)}")
        
        # 嘗試測試第一個可用模型
        if available_models:
            print(f"\n將測試第一個可用模型: {available_models[0]}")
            models_to_test = [available_models[0]]
        else:
            return 1
    
    print(f"將測試以下模型: {', '.join(models_to_test)}")
    print(f"每個模型將執行 {len(TEST_PROMPTS)} 個測試案例")
    print()
    
    print("開始測試...")
    print()
    
    # 執行測試
    all_results = []
    for model in models_to_test:
        result = test_model(model, available_models)
        if result:
            all_results.append(result)
    
    # 打印摘要
    print_summary(all_results)
    
    # 保存結果
    save_results(all_results)
    
    print()
    print("=" * 80)
    print("✅ 性能測試完成")
    print("=" * 80)
    print()
    
    # 推薦最佳模型
    if all_results:
        best_model = min(
            [r for r in all_results if r['summary']['successful_tests'] > 0],
            key=lambda x: x['summary']['avg_response_time']
        )
        print(f"💡 推薦：最快的模型是 '{best_model['model']}'")
        print(f"   - 平均響應時間: {best_model['summary']['avg_response_time']:.2f}s")
        print(f"   - 平均生成速度: {best_model['summary']['avg_tokens_per_sec']:.2f} tokens/s")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())