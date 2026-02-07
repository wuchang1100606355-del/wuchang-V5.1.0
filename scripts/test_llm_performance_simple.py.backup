#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wuchang OS 本地 LLM 簡化性能測試
適用於 Ollama 未運行的情況，提供測試框架
"""

import sys
import os
import json
import time
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError

# 測試配置
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
TEST_MODELS = ['llama3.1', 'qwen2:0.5b', 'phi4', 'mistral']
SIMPLE_TEST_PROMPTS = [
    {'name': '問候', 'prompt': '你好，請簡單自我介紹。', 'system': '你是一個友善的助手。'},
    {'name': '翻譯', 'prompt': '請將「你好世界」翻譯成英文和日文。', 'system': '你是一個翻譯助手。'},
    {'name': '解釋', 'prompt': '用簡單的語言解釋什麼是人工智慧。', 'system': '你是一個教育工作者。'},
]

def check_ollama():
    """檢查 Ollama 是否可用"""
    print("檢查 Ollama 服務...")
    try:
        req = Request(f"{OLLAMA_HOST}/api/tags")
        req.add_header('User-Agent', 'Wuchang-LLM-Test/1.0')
        response = urlopen(req, timeout=5)
        if response.getcode() == 200:
            data = json.loads(response.read().decode('utf-8'))
            models = [m.get('name', '') for m in data.get('models', [])]
            print(f"  ✓ Ollama 可用 ({OLLAMA_HOST})")
            print(f"  ✓ 可用模型: {', '.join(models) if models else '無'}")
            return models
        return []
    except Exception as e:
        print(f"  ✗ Ollama 不可用: {type(e).__name__}")
        return []

def test_single_call(model, prompt, system=None):
    """單次測試調用"""
    try:
        url = f"{OLLAMA_HOST.rstrip('/')}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 256}
        }
        if system:
            payload["system"] = system
        
        req = Request(url, data=json.dumps(payload).encode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        
        start = time.time()
        response = urlopen(req, timeout=30)
        elapsed = time.time() - start
        
        if response.getcode() == 200:
            data = json.loads(response.read().decode('utf-8'))
            return {
                'success': True,
                'time': elapsed,
                'tokens': data.get('eval_count', 0),
                'response': data.get('response', '')[:100],
                'speed': data.get('eval_count', 0) / elapsed if elapsed > 0 else 0
            }
    except Exception as e:
        return {'success': False, 'error': str(e)[:80]}
    
    return {'success': False, 'error': 'Unknown'}

def main():
    print("=" * 70)
    print("  Wuchang OS - 本地 LLM 簡化性能測試")
    print("=" * 70)
    print()
    
    models = check_ollama()
    if not models:
        print("\n❌ Ollama 服務不可用")
        print("\n請執行以下命令啟動服務：")
        print("  docker-compose --profile ui up -d")
        print("  或")
        print("  scripts/auto_install_ai.ps1")
        return 1
    
    # 找到要測試的模型
    test_model = None
    for candidate in TEST_MODELS:
        for m in models:
            if candidate in m or m.startswith(candidate):
                test_model = m
                break
        if test_model:
            break
    
    if not test_model and models:
        test_model = models[0]
    
    if not test_model:
        print("\n❌ 沒有可用模型")
        return 1
    
    print(f"\n將測試模型: {test_model}")
    print(f"測試案例數: {len(SIMPLE_TEST_PROMPTS)}")
    print()
    
    results = []
    total_time = 0
    success_count = 0
    
    for i, test in enumerate(SIMPLE_TEST_PROMPTS, 1):
        print(f"[{i}/{len(SIMPLE_TEST_PROMPTS)}] {test['name']}: {test['prompt']}")
        
        result = test_single_call(test_model, test['prompt'], test.get('system'))
        
        if result['success']:
            print(f"  ✓ 成功 - 時間: {result['time']:.2f}s, 速度: {result['speed']:.1f} t/s")
            print(f"  響應: {result['response']}...")
            total_time += result['time']
            success_count += 1
        else:
            print(f"  ✗ 失敗: {result['error']}")
        
        results.append(result)
        print()
    
    if success_count > 0:
        print("=" * 70)
        print("測試摘要")
        print("=" * 70)
        print(f"模型: {test_model}")
        print(f"成功率: {success_count}/{len(SIMPLE_TEST_PROMPTS)} ({success_count/len(SIMPLE_TEST_PROMPTS)*100:.1f}%)")
        print(f"總時間: {total_time:.2f}s")
        print(f"平均時間: {total_time/success_count:.2f}s")
        print("=" * 70)
        return 0
    else:
        print("❌ 所有測試均失敗")
        return 1

if __name__ == '__main__':
    sys.exit(main())