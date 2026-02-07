"""
五常 AI - 本機 AI 節點服務
本機運行的輕量級 AI 服務，優先處理請求

支援多種本機 AI 後端：
- Ollama (推薦)
- OpenAI API (本機部署)
- 其他本機 LLM
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import aiohttp
import os

# 日誌配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 配置
LOCAL_AI_TYPE = os.getenv("LOCAL_AI_TYPE", "ollama")  # ollama, openai, custom
LOCAL_AI_HOST = os.getenv("LOCAL_AI_HOST", "http://localhost:11434")
LOCAL_AI_MODEL = os.getenv("LOCAL_AI_MODEL", "gemma2:2b")  # 輕量級模型
LOCAL_AI_TIMEOUT = int(os.getenv("LOCAL_AI_TIMEOUT", "30"))


class LocalAINode:
    """本機 AI 節點"""

    def __init__(self):
        self.ai_type = LOCAL_AI_TYPE
        self.host = LOCAL_AI_HOST
        self.model = LOCAL_AI_MODEL
        self.timeout = LOCAL_AI_TIMEOUT
        self.available = False
        self.chat_history = []

        logger.info(f"本機 AI 節點初始化: {self.ai_type} @ {self.host}")

    async def check_health(self) -> bool:
        """健康檢查"""
        try:
            async with aiohttp.ClientSession() as session:
                if self.ai_type == "ollama":
                    # Ollama 健康檢查
                    async with session.get(
                        f"{self.host}/api/tags",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            models = [m['name']
                                      for m in data.get('models', [])]
                            self.available = self.model in models
                            if self.available:
                                logger.info(f"✅ 本機 AI 節點可用: {self.model}")
                            else:
                                logger.warning(f"⚠️  模型 {self.model} 未安裝")
                            return self.available

                elif self.ai_type == "openai":
                    # OpenAI 相容 API 健康檢查
                    async with session.get(
                        f"{self.host}/v1/models",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        self.available = response.status == 200
                        return self.available

                else:
                    logger.warning(f"未知的 AI 類型: {self.ai_type}")
                    return False

        except Exception as e:
            logger.warning(f"本機 AI 節點不可用: {e}")
            self.available = False
            return False

    async def chat(self, message: str, system_prompt: str = None) -> Optional[str]:
        """發送聊天請求"""
        if not self.available:
            logger.warning("本機 AI 節點不可用，需要使用備援")
            return None

        try:
            async with aiohttp.ClientSession() as session:
                if self.ai_type == "ollama":
                    return await self._chat_ollama(session, message, system_prompt)
                elif self.ai_type == "openai":
                    return await self._chat_openai(session, message, system_prompt)
                else:
                    return None

        except asyncio.TimeoutError:
            logger.error("本機 AI 請求超時")
            return None
        except Exception as e:
            logger.error(f"本機 AI 請求失敗: {e}")
            return None

    async def _chat_ollama(self, session: aiohttp.ClientSession,
                           message: str, system_prompt: str = None) -> Optional[str]:
        """Ollama API 聊天"""
        # 構建訊息
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # 加入歷史對話（最近 5 輪）
        messages.extend(self.chat_history[-10:])
        messages.append({"role": "user", "content": message})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        async with session.post(
            f"{self.host}/api/chat",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as response:
            if response.status == 200:
                data = await response.json()
                assistant_message = data.get('message', {}).get('content', '')

                # 更新歷史
                self.chat_history.append({"role": "user", "content": message})
                self.chat_history.append(
                    {"role": "assistant", "content": assistant_message})

                return assistant_message
            else:
                logger.error(f"Ollama API 錯誤: {response.status}")
                return None

    async def _chat_openai(self, session: aiohttp.ClientSession,
                           message: str, system_prompt: str = None) -> Optional[str]:
        """OpenAI 相容 API 聊天"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.extend(self.chat_history[-10:])
        messages.append({"role": "user", "content": message})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7
        }

        headers = {
            "Content-Type": "application/json"
        }

        api_key = os.getenv("LOCAL_AI_API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        async with session.post(
            f"{self.host}/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as response:
            if response.status == 200:
                data = await response.json()
                assistant_message = data['choices'][0]['message']['content']

                self.chat_history.append({"role": "user", "content": message})
                self.chat_history.append(
                    {"role": "assistant", "content": assistant_message})

                return assistant_message
            else:
                logger.error(f"OpenAI API 錯誤: {response.status}")
                return None

    def reset_history(self):
        """重置對話歷史"""
        self.chat_history = []
        logger.info("本機 AI 對話歷史已重置")


# ============================================
# 測試本機 AI 節點
# ============================================

async def test_local_ai():
    """測試本機 AI 節點"""
    print("="*60)
    print("  🧪 測試本機 AI 節點")
    print("="*60)
    print()

    node = LocalAINode()

    # 健康檢查
    print("正在檢查健康狀態...")
    if await node.check_health():
        print(f"✅ 本機 AI 節點可用: {node.model}")
        print()

        # 測試對話
        system_prompt = "你是小j，一個友善的 AI 助手。使用繁體中文回答。"

        print("測試對話 1:")
        print("你: 你好")
        response = await node.chat("你好", system_prompt)
        if response:
            print(f"小j: {response}")
        else:
            print("❌ 對話失敗")
        print()

        print("測試對話 2:")
        print("你: 1+1等於多少？")
        response = await node.chat("1+1等於多少？")
        if response:
            print(f"小j: {response}")
        else:
            print("❌ 對話失敗")

    else:
        print("❌ 本機 AI 節點不可用")
        print()
        print("請確認:")
        print(f"  1. {node.ai_type} 服務已啟動")
        print(f"  2. 服務地址: {node.host}")
        print(f"  3. 模型已安裝: {node.model}")
        print()

        if node.ai_type == "ollama":
            print("Ollama 安裝指南:")
            print("  1. 下載: https://ollama.ai/")
            print("  2. 安裝後執行: ollama pull gemma2:2b")
            print("  3. 啟動服務: ollama serve")


if __name__ == "__main__":
    asyncio.run(test_local_ai())
