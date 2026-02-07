#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小j 混合推理路由器
本地 Ollama (快速/免費) + Vertex AI (強大/付費) 智慧調度
"""
import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Literal

# 嘗試導入相關庫
try:
    import requests
except ImportError:
    print('請安裝: pip install requests')
    requests = None

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
except ImportError:
    print('請安裝: pip install google-cloud-aiplatform')
    vertexai = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('InferenceRouter')

# 配置
PROJECT_ID = os.environ.get('GCP_PROJECT_ID', 'coffee-spark-ai-barista-b10b5')
LOCATION = os.environ.get('GCP_LOCATION', 'us-central1')
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
DEFAULT_LOCAL_MODEL = os.environ.get('LOCAL_MODEL', 'qwen2.5:7b')
DEFAULT_CLOUD_MODEL = os.environ.get('CLOUD_MODEL', 'gemini-2.0-flash-exp')

# 成本追蹤 (估算)
COST_PER_1K_TOKENS = {
    'local': 0.0,  # 本地免費
    'gemini-2.0-flash-exp': 0.0001,  # 每 1K token ~$0.0001
    'gemini-2.5-pro': 0.005,  # 每 1K token ~$0.005
}


class CostTracker:
    """成本追蹤器"""

    def __init__(self, log_path: str = 'memory_store/ai_usage_log.json'):
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

    def log_usage(self, model: str, tokens: int, cost: float, task_type: str):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'model': model,
            'tokens': tokens,
            'cost': cost,
            'task_type': task_type
        }
        try:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.warning(f'無法記錄成本: {e}')


class OllamaClient:
    """本地 Ollama 客戶端"""

    def __init__(self, host: str = OLLAMA_HOST, model: str = DEFAULT_LOCAL_MODEL):
        self.host = host
        self.model = model

    def is_available(self) -> bool:
        """檢查 Ollama 是否可用"""
        if not requests:
            return False
        try:
            resp = requests.get(f'{self.host}/api/tags', timeout=2)
            return resp.status_code == 200
        except:
            return False

    def generate(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> Dict[str, Any]:
        """生成回應"""
        if not requests:
            raise RuntimeError('requests 未安裝')

        payload = {
            'model': self.model,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': temperature,
                'num_predict': max_tokens
            }
        }

        start_time = time.time()
        try:
            resp = requests.post(
                f'{self.host}/api/generate', json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            latency = time.time() - start_time

            return {
                'text': data.get('response', ''),
                'model': self.model,
                'tokens': data.get('eval_count', 0) + data.get('prompt_eval_count', 0),
                'latency': latency,
                'source': 'local'
            }
        except Exception as e:
            logger.error(f'Ollama 生成失敗: {e}')
            raise


class VertexAIClient:
    """雲端 Vertex AI 客戶端"""

    def __init__(self, project_id: str = PROJECT_ID, location: str = LOCATION, model: str = DEFAULT_CLOUD_MODEL):
        self.project_id = project_id
        self.location = location
        self.model_name = model
        self.model = None

        if vertexai:
            try:
                vertexai.init(project=project_id, location=location)
                self.model = GenerativeModel(model)
                logger.info(f'Vertex AI 已連線: {model}')
            except Exception as e:
                logger.warning(f'Vertex AI 初始化失敗: {e}')

    def is_available(self) -> bool:
        return self.model is not None

    def generate(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> Dict[str, Any]:
        """生成回應"""
        if not self.model:
            raise RuntimeError('Vertex AI 未初始化')

        start_time = time.time()
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'max_output_tokens': max_tokens,
                    'temperature': temperature
                }
            )
            latency = time.time() - start_time
            text = response.text

            # 估算 token (粗略)
            tokens = len(text.split()) * 1.3  # 中文約 1.3 倍

            return {
                'text': text,
                'model': self.model_name,
                'tokens': int(tokens),
                'latency': latency,
                'source': 'vertex_ai'
            }
        except Exception as e:
            logger.error(f'Vertex AI 生成失敗: {e}')
            raise


class InferenceRouter:
    """推理路由器 - 智慧選擇本地或雲端"""

    def __init__(self):
        self.ollama = OllamaClient()
        self.vertex = VertexAIClient()
        self.cost_tracker = CostTracker()

        # 檢查可用性
        self.ollama_available = self.ollama.is_available()
        self.vertex_available = self.vertex.is_available()

        logger.info(f'本地 Ollama: {"✓" if self.ollama_available else "✗"}')
        logger.info(f'Vertex AI: {"✓" if self.vertex_available else "✗"}')

    def route(
        self,
        prompt: str,
        task_type: Literal['simple', 'complex', 'code',
                           'translation', 'reasoning', 'creative'] = 'simple',
        max_tokens: int = 2000,
        temperature: float = 0.7,
        force_cloud: bool = False
    ) -> Dict[str, Any]:
        """
        智慧路由決策

        Args:
            prompt: 使用者提示詞
            task_type: 任務類型
                - simple: 簡單問答 (本地優先)
                - complex: 複雜推理 (雲端優先)
                - code: 程式生成 (本地可)
                - translation: 翻譯 (本地可)
                - reasoning: 邏輯推理 (雲端優先)
                - creative: 創意寫作 (雲端優先)
            max_tokens: 最大輸出 token
            temperature: 溫度參數
            force_cloud: 強制使用雲端

        Returns:
            生成結果字典
        """
        # 決策邏輯
        use_cloud = force_cloud or task_type in [
            'complex', 'reasoning', 'creative']

        # 若雲端優先但不可用,降級到本地
        if use_cloud and not self.vertex_available:
            logger.warning('雲端不可用,降級到本地')
            use_cloud = False

        # 若本地優先但不可用,升級到雲端
        if not use_cloud and not self.ollama_available:
            logger.warning('本地不可用,升級到雲端')
            use_cloud = True

        # 執行推理
        try:
            if use_cloud:
                logger.info(f'路由到 Vertex AI (任務: {task_type})')
                result = self.vertex.generate(prompt, max_tokens, temperature)
            else:
                logger.info(f'路由到本地 Ollama (任務: {task_type})')
                result = self.ollama.generate(prompt, max_tokens, temperature)

            # 記錄成本
            cost = self._calculate_cost(result['model'], result['tokens'])
            self.cost_tracker.log_usage(
                result['model'], result['tokens'], cost, task_type)
            result['cost'] = cost

            return result

        except Exception as e:
            # 失敗時嘗試備用方案
            logger.error(f'推理失敗: {e}')
            if use_cloud and self.ollama_available:
                logger.info('雲端失敗,嘗試本地備援')
                result = self.ollama.generate(prompt, max_tokens, temperature)
                cost = 0.0
                self.cost_tracker.log_usage(
                    result['model'], result['tokens'], cost, task_type)
                result['cost'] = cost
                return result
            else:
                raise

    def _calculate_cost(self, model: str, tokens: int) -> float:
        """計算成本 (估算)"""
        rate = COST_PER_1K_TOKENS.get(
            model, COST_PER_1K_TOKENS.get('local', 0.0))
        return (tokens / 1000.0) * rate


# ========== 使用範例 ==========
if __name__ == '__main__':
    router = InferenceRouter()

    # 測試簡單任務 (本地)
    print('\n=== 測試 1: 簡單問答 (本地) ===')
    result = router.route(
        prompt='你好,我是哥哥。請簡單介紹自己。',
        task_type='simple'
    )
    print(f"回應: {result['text'][:100]}...")
    print(
        f"來源: {result['source']}, 延遲: {result['latency']:.2f}s, 成本: ${result['cost']:.6f}")

    # 測試複雜任務 (雲端)
    print('\n=== 測試 2: 複雜推理 (雲端) ===')
    result = router.route(
        prompt='請分析五常社區未來 5 年的數位轉型策略,包含技術選型、成本控制、社區參與三個維度。',
        task_type='reasoning'
    )
    print(f"回應: {result['text'][:200]}...")
    print(
        f"來源: {result['source']}, 延遲: {result['latency']:.2f}s, 成本: ${result['cost']:.6f}")

    print('\n✅ 測試完成。請查看 memory_store/ai_usage_log.json 查看成本記錄。')
