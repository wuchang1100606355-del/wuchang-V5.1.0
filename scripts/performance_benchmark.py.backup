#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 效能測試與比較腳本
測試 qwen2:0.5b、Gemini 2.5 和 GT5 的效能指標
"""

import sys
import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Any

# 測試配置
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://ollama:11434')
TEST_MODELS = {
    'qwen2:0.5b': {
        'type': 'local',
        'provider': 'ollama',
        'url': f'{OLLAMA_HOST}/api/generate'
    },
    'gemini-2.5-flash': {
        'type': 'cloud',
        'provider': 'google',
        'model_name': 'gemini-2.5-flash-preview-09-2025'
    },
    'gemini-2.5-pro': {
        'type': 'cloud',
        'provider': 'google',
        'model_name': 'gemini-2.5-pro'
    },
    'gt5': {
        'type': 'cloud',
        'provider': 'openai',  # 假設 GT5 可能是 GPT-5 的簡稱
        'model_name': 'gpt-5'  # 需要確認實際模型名稱
    }
}

# 測試案例
TEST_PROMPTS = [
    {
        'name': '短問答',
        'prompt': '你好，請簡單介紹一下你自己。',
        'system': '你是一個友善的 AI 助手。',
        'expected_length': (20, 200)
    },
    {
        'name': '中長回答',
        'prompt': '請解釋一下什麼是社區自治，以及它在現代社會中的重要性。請用三個要點說明。',
        'system': '你是一個專業的社區治理顧問。',
        'expected_length': (100, 500)
    },
    {
        'name': '創意任務',
        'prompt': '你是一家咖啡店的 AI 助手。請為顧客創建一份包含早餐、午餐、下午茶和晚餐的菜單。每類至少包含 3 個項目，並包含價格。',
        'system': '你是一個創意豐富的餐廳顧問。',
        'expected_length': (150, 800)
    },
    {
        'name': '代碼生成',
        'prompt': '用 Python 寫一個函數，計算列表中所有偶數的平方和。',
        'system': '你是一個專業的程式設計師。',
        'expected_length': (50, 300)
    },
    {
        'name': '翻譯任務',
        'prompt': '請將以下文字翻譯成英文和日文：五常社區致力於建立一個和諧共融的居住環境。',
        'system': '你是一個專業的翻譯助手。',
        'expected_length': (50, 200)
    },
    {
        'name': '複雜推理',
        'prompt': '如果今天下雨，小明就不去公園。如果小明去公園，他就會遇到小華。今天小明沒有遇到小華。請問今天下雨了嗎？請說明推理過程。',
        'system': '你是一個邏輯推理專家。',
        'expected_length': (100, 400)
    }
]

def print_header():
    """打印標題"""
    print("=" * 80)
    print("  LLM 效能測試與比較")
    print("=" * 80)
    print(f"  測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  測試案例數: {len(TEST_PROMPTS)}")
    print("=" * 80)
    print()

def check_ollama():
    """檢查 Ollama 是否可用"""
    try:
        response = requests.get(f'{OLLAMA_HOST}/api/tags', timeout=5)
        if response.status_code == 200:
            models = [m.get('name', '') for m in response.json().get('models', [])]
            return models
        return []
    except Exception as e:
        print(f"  ⚠ Ollama 檢查失敗: {e}")
        return []

def get_google_api_key():
    """獲取 Google API Key"""
    # 嘗試從多個來源獲取
    api_key = os.environ.get('GOOGLE_API_KEY')
    if api_key:
        return api_key
    
    # 嘗試從 Odoo 配置獲取
    try:
        workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_file = os.path.join(workspace_path, 'config', 'official_ai_identity.json')
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                api_key = config.get('google_api_key')
                if api_key:
                    return api_key
    except Exception:
        pass
    
    return None

def call_ollama(model_name: str, prompt: str, system: str = None, timeout: int = 60) -> Dict[str, Any]:
    """調用 Ollama API"""
    try:
        url = TEST_MODELS[model_name]['url']
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 512
            }
        }
        if system:
            payload["system"] = system
        
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=timeout)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            eval_count = data.get('eval_count', 0)
            prompt_eval_count = data.get('prompt_eval_count', 0)
            total_duration = data.get('total_duration', elapsed_time * 1_000_000_000) / 1_000_000_000
            
            return {
                'success': True,
                'response': response_text,
                'elapsed_time': elapsed_time,
                'response_time': total_duration,
                'tokens': eval_count,
                'input_tokens': prompt_eval_count,
                'total_tokens': prompt_eval_count + eval_count,
                'tokens_per_sec': eval_count / total_duration if total_duration > 0 else 0,
                'response_length': len(response_text),
                'cost': 0.0  # 本地模型免費
            }
        else:
            return {
                'success': False,
                'error': f'HTTP {response.status_code}',
                'elapsed_time': elapsed_time,
                'cost': 0.0
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)[:100],
            'elapsed_time': 0,
            'cost': 0.0
        }

def call_gemini(model_config: Dict, prompt: str, system: str = None, timeout: int = 60) -> Dict[str, Any]:
    """調用 Gemini API"""
    api_key = get_google_api_key()
    if not api_key:
        return {
            'success': False,
            'error': 'API key not found',
            'elapsed_time': 0,
            'cost': 0.0
        }
    
    try:
        model_name = model_config['model_name']
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{prompt}"
        
        # 使用 Google Generative AI API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 512
            }
        }
        
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=timeout)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            candidates = data.get('candidates', [])
            if candidates:
                response_text = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            else:
                response_text = ''
            
            usage = data.get('usageMetadata', {})
            input_tokens = usage.get('promptTokenCount', 0)
            output_tokens = usage.get('candidatesTokenCount', 0)
            total_tokens = usage.get('totalTokenCount', 0)
            
            # Gemini 2.5 定價（估算）
            # Flash: $0.075/$0.30 per 1M tokens
            # Pro: $1.25/$5.00 per 1M tokens
            if 'flash' in model_name.lower():
                input_cost_per_m = 0.075
                output_cost_per_m = 0.30
            else:
                input_cost_per_m = 1.25
                output_cost_per_m = 5.00
            
            input_cost = (input_tokens / 1_000_000) * input_cost_per_m
            output_cost = (output_tokens / 1_000_000) * output_cost_per_m
            total_cost = input_cost + output_cost
            
            return {
                'success': True,
                'response': response_text,
                'elapsed_time': elapsed_time,
                'response_time': elapsed_time,
                'tokens': output_tokens,
                'input_tokens': input_tokens,
                'total_tokens': total_tokens,
                'tokens_per_sec': output_tokens / elapsed_time if elapsed_time > 0 else 0,
                'response_length': len(response_text),
                'cost': total_cost
            }
        else:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
            return {
                'success': False,
                'error': error_msg[:100],
                'elapsed_time': elapsed_time,
                'cost': 0.0
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)[:100],
            'elapsed_time': 0,
            'cost': 0.0
        }

def test_model(model_name: str, test_cases: List[Dict]) -> Dict[str, Any]:
    """測試單個模型"""
    print(f"\n{'=' * 80}")
    print(f"測試模型: {model_name}")
    print(f"{'=' * 80}\n")
    
    model_config = TEST_MODELS.get(model_name)
    if not model_config:
        print(f"  ✗ 未知模型: {model_name}")
        return None
    
    results = []
    total_time = 0.0
    total_cost = 0.0
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"[{i}/{len(test_cases)}] {test_case['name']}: ", end='', flush=True)
        
        # 根據模型類型選擇調用方法
        if model_config['type'] == 'local':
            result = call_ollama(model_name, test_case['prompt'], test_case.get('system'))
        elif model_config['provider'] == 'google':
            result = call_gemini(model_config, test_case['prompt'], test_case.get('system'))
        else:
            result = {
                'success': False,
                'error': f"Unsupported provider: {model_config['provider']}",
                'elapsed_time': 0,
                'cost': 0.0
            }
        
        if result['success']:
            print(f"✓ ({result['elapsed_time']:.2f}s, {result.get('tokens_per_sec', 0):.1f} t/s)")
            if result.get('cost', 0) > 0:
                print(f"  成本: ${result['cost']:.6f}")
            print(f"  回應長度: {result.get('response_length', 0)} 字符")
            print(f"  回應預覽: {result.get('response', '')[:80]}...")
            
            total_time += result['elapsed_time']
            total_cost += result.get('cost', 0)
            success_count += 1
        else:
            print(f"✗ 失敗: {result.get('error', 'Unknown error')}")
        
        results.append({
            'test_case': test_case['name'],
            **result
        })
        
        time.sleep(0.5)  # 避免請求過快
    
    summary = {
        'model_name': model_name,
        'total_tests': len(test_cases),
        'successful_tests': success_count,
        'success_rate': (success_count / len(test_cases) * 100) if test_cases else 0,
        'total_time': total_time,
        'avg_response_time': total_time / success_count if success_count > 0 else 0,
        'total_cost': total_cost,
        'avg_tokens_per_sec': sum(r.get('tokens_per_sec', 0) for r in results if r.get('success')) / success_count if success_count > 0 else 0,
        'results': results
    }
    
    print(f"\n摘要:")
    print(f"  成功率: {summary['success_rate']:.1f}% ({success_count}/{len(test_cases)})")
    print(f"  總時間: {total_time:.2f}s")
    print(f"  平均響應時間: {summary['avg_response_time']:.2f}s")
    print(f"  平均生成速度: {summary['avg_tokens_per_sec']:.1f} tokens/s")
    if total_cost > 0:
        print(f"  總成本: ${total_cost:.6f}")
    else:
        print(f"  總成本: 免費")
    
    return summary

def generate_comparison_table(all_results: List[Dict[str, Any]]):
    """生成比較表格"""
    print("\n" + "=" * 80)
    print("效能比較表")
    print("=" * 80)
    print()
    
    if not all_results:
        print("⚠ 沒有測試結果")
        return
    
    # 表頭
    print(f"{'指標':<25} " + " ".join(f"{r['model_name']:<20}" for r in all_results))
    print("-" * 80)
    
    # 提取比較指標
    metrics = [
        ('成功率 (%)', lambda r: f"{r['success_rate']:.1f}%"),
        ('平均響應時間 (s)', lambda r: f"{r['avg_response_time']:.2f}s"),
        ('總響應時間 (s)', lambda r: f"{r['total_time']:.2f}s"),
        ('平均生成速度 (t/s)', lambda r: f"{r['avg_tokens_per_sec']:.1f}"),
        ('總成本 ($)', lambda r: f"${r['total_cost']:.6f}" if r['total_cost'] > 0 else "免費"),
    ]
    
    for metric_name, metric_func in metrics:
        values = []
        for result in all_results:
            value = metric_func(result)
            values.append(value)
        print(f"{metric_name:<25} " + " ".join(f"{v:<20}" for v in values))
    
    print()
    print("=" * 80)
    print("詳細測試結果比較")
    print("=" * 80)
    print()
    
    # 對每個測試案例進行比較
    print(f"{'測試案例':<20} " + " ".join(f"{r['model_name']:<20}" for r in all_results))
    print("-" * 80)
    
    for i, test_case in enumerate(TEST_PROMPTS):
        row = [test_case['name']]
        for result in all_results:
            if i < len(result['results']):
                test_result = result['results'][i]
                if test_result.get('success'):
                    time_str = f"{test_result['elapsed_time']:.2f}s"
                    row.append(time_str)
                else:
                    row.append("失敗")
            else:
                row.append("N/A")
        print(" ".join(f"{item:<20}" for item in row))

def save_results(all_results: List[Dict[str, Any]], output_file: str = None):
    """保存測試結果"""
    try:
        # 使用 /tmp 目錄（容器內可寫）
        results_dir = '/tmp/llm_benchmark_results'
        os.makedirs(results_dir, exist_ok=True)
        
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(results_dir, f'llm_performance_benchmark_{timestamp}.json')
        
        output = {
            'timestamp': datetime.now().isoformat(),
            'test_config': {
                'ollama_host': OLLAMA_HOST,
                'test_cases': len(TEST_PROMPTS)
            },
            'results': all_results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 測試結果已保存至: {output_file}")
        return output_file
    except Exception as e:
        print(f"⚠ 保存測試結果失敗: {e}")
        return None

def main():
    """主函數"""
    print_header()
    
    # 檢查可用服務
    print("檢查服務可用性...")
    ollama_models = check_ollama()
    google_api_key = get_google_api_key()
    
    print(f"  Ollama: {'可用' if ollama_models else '不可用'}")
    if ollama_models:
        print(f"    可用模型: {', '.join(ollama_models)}")
    
    print(f"  Google API: {'可用' if google_api_key else '不可用 (需要 API key)'}")
    print()
    
    # 確定要測試的模型
    models_to_test = []
    
    # 測試 qwen2:0.5b（本地）
    if ollama_models and 'qwen2:0.5b' in ollama_models:
        models_to_test.append('qwen2:0.5b')
    elif ollama_models:
        # 如果沒有 qwen2:0.5b，嘗試找其他 qwen 模型
        qwen_models = [m for m in ollama_models if 'qwen' in m.lower()]
        if qwen_models:
            models_to_test.append(qwen_models[0])
    
    # 測試 Gemini 2.5（如果有 API key）
    if google_api_key:
        models_to_test.append('gemini-2.5-flash')
        # 如果測試 Pro 版本，取消下面註釋
        # models_to_test.append('gemini-2.5-pro')
    
    # GT5 暫時跳過（需要確認模型名稱和 API 配置）
    # if has_gt5_access():
    #     models_to_test.append('gt5')
    
    if not models_to_test:
        print("❌ 沒有可測試的模型")
        return 1
    
    print(f"將測試以下模型: {', '.join(models_to_test)}")
    print()
    
    # 執行測試
    all_results = []
    for model_name in models_to_test:
        result = test_model(model_name, TEST_PROMPTS)
        if result:
            all_results.append(result)
        time.sleep(1)  # 測試間隔
    
    # 生成比較表
    if len(all_results) > 1:
        generate_comparison_table(all_results)
    
    # 保存結果
    save_results(all_results)
    
    print()
    print("=" * 80)
    print("✅ 效能測試完成")
    print("=" * 80)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
