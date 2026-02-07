#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 小 J 時空能力整合配置
將時空系統能力整合到 AI 小 J 中
支援從 Odoo 讀取專用金鑰
"""

import os
import sys
from pathlib import Path
from typing import Optional

# 添加時空系統路徑
SPATIOTEMPORAL_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SPATIOTEMPORAL_ROOT))

from core.spatiotemporal import SpatiotemporalSystem
from core.ai_agent import AIAgent
from applications.community_service import CommunityService

# 嘗試導入 Odoo 配置載入器
try:
    from odoo_integration.odoo_config_loader import get_odoo_config_loader
    ODOO_AVAILABLE = True
except ImportError:
    ODOO_AVAILABLE = False
    get_odoo_config_loader = None


class AIJSpatiotemporalIntegration:
    """AI 小 J 時空能力整合"""
    
    def __init__(self, odoo_env=None):
        """
        初始化整合
        
        Args:
            odoo_env: Odoo 環境（如果從 Odoo 內部調用）
        """
        self.odoo_env = odoo_env
        self.st_system = SpatiotemporalSystem()
        self.ai_agent = AIAgent(self.st_system)
        self.community_service = CommunityService(self.st_system, self.ai_agent)
        self.enabled = True
        
        # 載入配置（優先從 Odoo 讀取）
        self.config_loader = None
        self.cloud_compute_enabled = False
        self._load_config(odoo_env)
    
    def _load_config(self, odoo_env=None):
        """載入配置（優先從 Odoo 讀取）"""
        # 嘗試從 Odoo 讀取配置
        if ODOO_AVAILABLE and (odoo_env or self._try_get_odoo_env()):
            try:
                self.config_loader = get_odoo_config_loader(odoo_env or self._try_get_odoo_env())
                
                # 從 Odoo 讀取設定
                self.enabled = self.config_loader.is_spatiotemporal_enabled()
                self.cloud_compute_enabled = self.config_loader.is_cloud_compute_enabled()
                
                # 設定 API Key（AI 小 J 專用）
                openai_key = self.config_loader.get_openai_api_key()
                anthropic_key = self.config_loader.get_anthropic_api_key()
                google_key = self.config_loader.get_google_api_key()
                
                if openai_key:
                    os.environ['OPENAI_API_KEY'] = openai_key
                if anthropic_key:
                    os.environ['ANTHROPIC_API_KEY'] = anthropic_key
                if google_key:
                    os.environ['GOOGLE_API_KEY'] = google_key
                
                print("✓ 已從 Odoo 載入 AI 小 J 專用配置")
                
            except Exception as e:
                print(f"從 Odoo 載入配置失敗，使用環境變數: {e}")
                self._load_from_env()
        else:
            # 從環境變數讀取
            self._load_from_env()
    
    def _try_get_odoo_env(self):
        """嘗試取得 Odoo 環境"""
        # 如果從 Odoo 內部調用，可以通過特定方式取得環境
        # 這裡需要根據實際情況調整
        return None
    
    def _load_from_env(self):
        """從環境變數載入配置"""
        openai_key = os.getenv('OPENAI_API_KEY')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        google_key = os.getenv('GOOGLE_API_KEY')
        
        if openai_key or anthropic_key or google_key:
            self.cloud_compute_enabled = True
            print("✓ 已從環境變數載入雲端算力配置")
    
    def get_capabilities(self) -> dict:
        """取得 AI 小 J 的時空能力"""
        capabilities = {
            "spatiotemporal_system": {
                "enabled": self.enabled,
                "version": "1.0.0",
                "capabilities": [
                    "時空事件管理",
                    "時間空間建議",
                    "排程優化",
                    "活動模式分析",
                    "空間使用率預測",
                    "社區服務管理"
                ]
            },
            "cloud_compute": {
                "enabled": self.cloud_compute_enabled,
                "providers": {
                    "openai": bool(os.getenv('OPENAI_API_KEY')),
                    "anthropic": bool(os.getenv('ANTHROPIC_API_KEY')),
                    "google": bool(os.getenv('GOOGLE_API_KEY'))
                }
            },
            "config_source": "odoo" if self.config_loader else "environment"
        }
        
        # 如果從 Odoo 讀取，添加更多資訊
        if self.config_loader:
            odoo_config = self.config_loader.get_all_config()
            capabilities["odoo_config"] = odoo_config
        
        return capabilities
    
    def suggest_event(self, event_type: str, participants: int, duration_hours: float, **kwargs):
        """建議事件（AI 小 J 介面）"""
        return self.ai_agent.suggest_optimal_time_and_space(
            event_type=event_type,
            participants=participants,
            duration_hours=duration_hours,
            **kwargs
        )
    
    def schedule_event(self, title: str, event_type: str, participants: int, **kwargs):
        """排程事件（AI 小 J 介面）"""
        return self.community_service.schedule_community_event(
            title=title,
            event_type=event_type,
            participants=participants,
            **kwargs
        )
    
    def analyze_patterns(self, village_id: str = None, days: int = 30):
        """分析模式（AI 小 J 介面）"""
        return self.ai_agent.analyze_community_activity_patterns(
            village_id=village_id,
            days=days
        )


# 全域實例（供 AI 小 J 使用）
_ai_j_spatiotemporal_instance = None


def get_ai_j_spatiotemporal(odoo_env=None) -> AIJSpatiotemporalIntegration:
    """
    取得 AI 小 J 時空整合實例
    
    Args:
        odoo_env: Odoo 環境（如果從 Odoo 內部調用）
    
    Returns:
        AIJSpatiotemporalIntegration 實例
    """
    global _ai_j_spatiotemporal_instance
    
    if _ai_j_spatiotemporal_instance is None:
        _ai_j_spatiotemporal_instance = AIJSpatiotemporalIntegration(odoo_env)
    elif odoo_env and _ai_j_spatiotemporal_instance.odoo_env != odoo_env:
        # 如果提供了新的 Odoo 環境，重新建立實例
        _ai_j_spatiotemporal_instance = AIJSpatiotemporalIntegration(odoo_env)
    
    return _ai_j_spatiotemporal_instance
