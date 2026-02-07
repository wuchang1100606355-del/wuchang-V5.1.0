#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wuchang OS - 本地 LLM vs 雲端 Gemini 性能比較測試
生成量化比較表格
"""

import sys
import os
import json
import time
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError
import subprocess

# 測試配置
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
TEST_MODELS = ['qwen2:0.5b', 'llama3.1']  # 本地模型
GEMINI_MODEL = 'gemini-1.5-flash'  # 雲端模型

TEST_PROMPTS = [
    {
        'name': '短問答',
        'prompt': '你好，請簡單介紹一下你自己。',
        'system': '你是一個友善的 AI 助手。'
    },
    {
        'name': '中長回答',
        'prompt': '請解釋一下什麼是社區自治，以及它在現代社會中的重要性。請用三個要點說明。',
        'system': '你是一個專業的社區治理顧問。'
    },
    {
        'name': '創意任務',
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
    print("  Wuchang OS - 本地 LLM vs 雲端 Gemini 性能比較測試")
    print("=" * 80)
    print()

def check_ollama():
    """檢查 Ollama 是否可用"""
    try:
        req = Request(f"{OLLAMA_HOST}/api/tags")
        req.add_header('User-Agent', 'Wuchang-LLM-Compare/1.0')
        response = urlopen(req, timeout=10)
        if response.getcode() == 200:
            data = json.loads(response.read().decode('utf-8'))
            models = [m.get('name', '') for m in data.get('models', [])]
            return models
        return []
    except Exception as e:
        print(f"    Ollama 檢查錯誤: {type(e).__name__}")
        return []

def check_gemini():
    """檢查 Gemini API 是否可用"""
    try:
        # 檢查配置文件
        config_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'config', 'official_ai_identity.json'
        )
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 檢查是否有 API key 配置
                return True
        return False
    except Exception:
        return False

def call_ollama(model, prompt, system=None, timeout=30):
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
        if system:
            payload["system"] = system
        
        req = Request(url, data=json.dumps(payload).encode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        
        start_time = time.time()
        response = urlopen(req, timeout=timeout)
        elapsed_time = time.time() - start_time
        
        if response.getcode() == 200:
            data = json.loads(response.read().decode('utf-8'))
            response_text = data.get('response', '')
            tokens = data.get('eval_count', 0)
            
            return {
                'success': True,
                'response': response_text,
                'elapsed_time': elapsed_time,
                'tokens': tokens,
                'tokens_per_sec': tokens / elapsed_time if elapsed_time > 0 else 0,
                'response_length': len(response_text),
                'cost': 0  # 本地模型免費
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)[:100],
            'elapsed_time': 0,
            'cost': 0
        }
    
    return {
        'success': False,
        'error': 'Unknown',
        'elapsed_time': 0,
        'cost': 0
    }

def call_gemini(prompt, system=None, timeout=30):
    """調用 Gemini API"""
    try:
        # 嘗試使用 Vertex AI 或直接使用 Google API
        config_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'config', 'official_ai_identity.json'
        )
        
        # 檢查是否有 API key
        api_key = None
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                api_key = config.get('google_api_key') or os.environ.get('GOOGLE_API_KEY')
        
        if not api_key:
            # 嘗試從環境變量或 Odoo 配置獲取
            api_key = os.environ.get('GOOGLE_API_KEY')
        
        if not api_key:
            return {
                'success': False,
                'error': 'API key not found',
                'elapsed_time': 0,
                'cost': 0
            }
        
        # 構建請求
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{prompt}"
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 512
            }
        }
        
        req = Request(url, data=json.dumps(payload).encode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        
        start_time = time.time()
        response = urlopen(req, timeout=timeout)
        elapsed_time = time.time() - start_time
        
        if response.getcode() == 200:
            data = json.loads(response.read().decode('utf-8'))
            response_text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            usage = data.get('usageMetadata', {})
            input_tokens = usage.get('promptTokenCount', 0)
            output_tokens = usage.get('candidatesTokenCount', 0)
            total_tokens = usage.get('totalTokenCount', 0)
            
            # 估算成本（Gemini 1.5 Flash 定價約 $0.075/$0.30 per 1M tokens）
            input_cost = (input_tokens / 1_000_000) * 0.075
            output_cost = (output_tokens / 1_000_000) * 0.30
            total_cost = input_cost + output_cost
            
            return {
                'success': True,
                'response': response_text,
                'elapsed_time': elapsed_time,
                'tokens': output_tokens,
                'tokens_per_sec': output_tokens / elapsed_time if elapsed_time > 0 else 0,
                'response_length': len(response_text),
                'total_tokens': total_tokens,
                'input_tokens': input_tokens,
                'cost': total_cost
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)[:100],
            'elapsed_time': 0,
            'cost': 0
        }
    
    return {
        'success': False,
        'error': 'Unknown',
        'elapsed_time': 0,
        'cost': 0
    }

def run_model_test(name, model_func, test_cases):
    """測試模型"""
    print(f"\n測試: {name}")
    print("-" * 80)
    
    results = []
    total_time = 0
    total_cost = 0
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"[{i}/{len(test_cases)}] {test_case['name']}: ", end='', flush=True)
        
        result = model_func(
            test_case['prompt'],
            test_case.get('system')
        )
        
        if result['success']:
            print(f"✓ ({result['elapsed_time']:.2f}s, {result['tokens_per_sec']:.1f} t/s)")
            results.append({
                'test_case': test_case['name'],
                **result
            })
            total_time += result['elapsed_time']
            total_cost += result.get('cost', 0)
            success_count += 1
        else:
            print(f"✗ ({result.get('error', 'Failed')})")
            results.append({
                'test_case': test_case['name'],
                **result
            })
        
        time.sleep(0.5)  # 避免請求過快
    
    return {
        'name': name,
        'results': results,
        'summary': {
            'total_tests': len(test_cases),
            'successful_tests': success_count,
            'success_rate': success_count / len(test_cases) * 100 if test_cases else 0,
            'total_time': total_time,
            'avg_response_time': total_time / success_count if success_count > 0 else 0,
            'avg_tokens_per_sec': sum(r.get('tokens_per_sec', 0) for r in results if r.get('success')) / success_count if success_count > 0 else 0,
            'total_cost': total_cost
        }
    }

def generate_comparison_table(all_results):
    """生成比較表格"""
    print("\n" + "=" * 80)
    print("性能比較表")
    print("=" * 80)
    print()
    
    # 表頭
    print(f"{'指標':<20} {'本地模型':<30} {'雲端 Gemini':<30}")
    print("-" * 80)
    
    # 提取數據
    local_results = [r for r in all_results if '本地' in r['name'] or 'Ollama' in r['name']]
    gemini_results = [r for r in all_results if 'Gemini' in r['name'] or '雲端' in r['name']]
    
    if not local_results or not gemini_results:
        print("⚠ 缺少比較數據")
        return
    
    local = local_results[0]  # 取第一個本地模型
    gemini = gemini_results[0]
    
    # 比較指標
    comparisons = [
        ('成功率', f"{local['summary']['success_rate']:.1f}%", f"{gemini['summary']['success_rate']:.1f}%"),
        ('平均響應時間', f"{local['summary']['avg_response_time']:.2f}s", f"{gemini['summary']['avg_response_time']:.2f}s"),
        ('平均生成速度', f"{local['summary']['avg_tokens_per_sec']:.1f} t/s", f"{gemini['summary']['avg_tokens_per_sec']:.1f} t/s"),
        ('總成本', f"$0.00 (免費)", f"${gemini['summary']['total_cost']:.4f}"),
        ('總響應時間', f"{local['summary']['total_time']:.2f}s", f"{gemini['summary']['total_time']:.2f}s"),
    ]
    
    for metric, local_val, gemini_val in comparisons:
        print(f"{metric:<20} {local_val:<30} {gemini_val:<30}")
    
    print()
    
    # 詳細比較
    print("=" * 80)
    print("詳細測試結果")
    print("=" * 80)
    print()
    
    print(f"{'測試案例':<20} {'本地模型':<15} {'Gemini':<15} {'優勢':<15}")
    print("-" * 80)
    
    # 對每個測試案例進行比較
    for i, test_case in enumerate(TEST_PROMPTS):
        local_result = local['results'][i] if i < len(local['results']) else None
        gemini_result = gemini['results'][i] if i < len(gemini['results']) else None
        
        if local_result and gemini_result:
            local_time = local_result['elapsed_time'] if local_result['success'] else float('inf')
            gemini_time = gemini_result['elapsed_time'] if gemini_result['success'] else float('inf')
            
            if local_time < gemini_time:
                advantage = "本地更快"
            elif gemini_time < local_time:
                advantage = "Gemini 更快"
            else:
                advantage = "相當"
            
            local_str = f"{local_time:.2f}s" if local_result['success'] else "失敗"
            gemini_str = f"{gemini_time:.2f}s" if gemini_result['success'] else "失敗"
            
            print(f"{test_case['name']:<20} {local_str:<15} {gemini_str:<15} {advantage:<15}")
    
    print()

def save_results(all_results):
    """保存結果"""
    try:
        workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        results_dir = os.path.join(workspace_path, 'logs')
        os.makedirs(results_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = os.path.join(results_dir, f'llm_comparison_{timestamp}.json')
        
        output = {
            'timestamp': datetime.now().isoformat(),
            'test_config': {
                'ollama_host': OLLAMA_HOST,
                'gemini_model': GEMINI_MODEL,
                'test_cases': len(TEST_PROMPTS)
            },
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
    
    # 檢查服務可用性
    print("檢查服務可用性...")
    ollama_models = check_ollama()
    gemini_available = check_gemini()
    
    print(f"  Ollama: {'可用' if ollama_models else '不可用'}")
    if ollama_models:
        print(f"    可用模型: {', '.join(ollama_models)}")
    
    print(f"  Gemini: {'可用' if gemini_available else '不可用 (需要 API key)'}")
    print()
    
    if not ollama_models and not gemini_available:
        print("❌ 沒有可用的測試服務")
        return 1
    
    # 確定要測試的模型
    models_to_test = []
    
    # 本地模型
    if ollama_models:
        for test_model in TEST_MODELS:
            for available in ollama_models:
                if test_model in available or available.startswith(test_model):
                    models_to_test.append({
                        'name': f'本地 {test_model}',
                        'func': lambda p, s, m=available: call_ollama(m, p, s)
                    })
                    break
    
    # 雲端 Gemini
    if gemini_available:
        models_to_test.append({
            'name': '雲端 Gemini',
            'func': call_gemini
        })
    
    if not models_to_test:
        print("❌ 沒有可測試的模型")
        return 1
    
    print(f"將測試以下模型: {', '.join(m['name'] for m in models_to_test)}")
    print(f"測試案例數: {len(TEST_PROMPTS)}")
    print()
    
    print("開始測試...")
    print()
    
    # 執行測試
    all_results = []
    for model_config in models_to_test:
        result = run_model_test(model_config['name'], model_config['func'], TEST_PROMPTS)
        all_results.append(result)
    
    # 生成比較表
    if len(all_results) >= 2:
        generate_comparison_table(all_results)
    
    # 保存結果
    save_results(all_results)
    
    print()
    print("=" * 80)
    print("✅ 比較測試完成")
    print("=" * 80)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())