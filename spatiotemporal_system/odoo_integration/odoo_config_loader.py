#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo 配置載入器
從 Odoo 系統參數讀取 AI 小 J 專用金鑰和設定
"""

import os
import sys
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class OdooConfigLoader:
    """Odoo 配置載入器"""
    
    def __init__(self, odoo_env=None):
        """
        初始化 Odoo 配置載入器
        
        Args:
            odoo_env: Odoo 環境（如果從 Odoo 內部調用）
        """
        self.odoo_env = odoo_env
        self._cache = {}
    
    def get_param(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        從 Odoo 系統參數取得值
        
        Args:
            key: 參數鍵
            default: 預設值
        
        Returns:
            參數值
        """
        # 如果有 Odoo 環境，直接查詢
        if self.odoo_env:
            try:
                param = self.odoo_env['ir.config_parameter'].sudo().get_param(key, default)
                return param
            except Exception as e:
                logger.warning(f"從 Odoo 讀取參數失敗 {key}: {e}")
                return default
        
        # 否則從環境變數讀取（用於外部調用）
        env_key = key.upper().replace('.', '_')
        return os.getenv(env_key, default)
    
    def get_openai_api_key(self) -> Optional[str]:
        """取得 OpenAI API Key (AI 小 J 專用)"""
        return self.get_param('ai.j.openai.api.key')
    
    def get_anthropic_api_key(self) -> Optional[str]:
        """取得 Anthropic API Key (AI 小 J 專用)"""
        return self.get_param('ai.j.anthropic.api.key')
    
    def get_google_api_key(self) -> Optional[str]:
        """取得 Google API Key (AI 小 J 專用)"""
        return self.get_param('ai.j.google.api.key')
    
    def is_spatiotemporal_enabled(self) -> bool:
        """檢查時空系統是否啟用"""
        value = self.get_param('spatiotemporal.system.enabled', 'False')
        return value.lower() in ('true', '1', 'yes')
    
    def is_cloud_compute_enabled(self) -> bool:
        """檢查雲端算力是否啟用"""
        value = self.get_param('ai.j.cloud.compute.enabled', 'False')
        return value.lower() in ('true', '1', 'yes')
    
    def get_authorization_level(self) -> str:
        """取得授權等級"""
        return self.get_param('ai.j.spatiotemporal.authorization', 'none')
    
    def get_system_path(self) -> Optional[str]:
        """取得時空系統路徑"""
        return self.get_param('spatiotemporal.system.path')
    
    def get_capabilities(self) -> list:
        """取得能力清單"""
        value = self.get_param('ai.j.spatiotemporal.capabilities', '')
        return [c.strip() for c in value.split(',') if c.strip()]
    
    def get_all_config(self) -> Dict[str, Any]:
        """取得所有配置"""
        return {
            "spatiotemporal_enabled": self.is_spatiotemporal_enabled(),
            "cloud_compute_enabled": self.is_cloud_compute_enabled(),
            "authorization_level": self.get_authorization_level(),
            "system_path": self.get_system_path(),
            "capabilities": self.get_capabilities(),
            "api_keys": {
                "openai": bool(self.get_openai_api_key()),
                "anthropic": bool(self.get_anthropic_api_key()),
                "google": bool(self.get_google_api_key())
            }
        }


# 在 Odoo 環境中使用
def get_odoo_config_loader(odoo_env=None) -> OdooConfigLoader:
    """
    取得 Odoo 配置載入器
    
    Args:
        odoo_env: Odoo 環境
    
    Returns:
        OdooConfigLoader 實例
    """
    return OdooConfigLoader(odoo_env)


# 範例：在 Odoo 模型中使用
"""
from odoo import models, api
from spatiotemporal_system.odoo_integration.odoo_config_loader import get_odoo_config_loader

class MyModel(models.Model):
    _name = 'my.model'
    
    @api.model
    def use_spatiotemporal(self):
        # 取得配置載入器
        config = get_odoo_config_loader(self.env)
        
        # 取得 API Key
        openai_key = config.get_openai_api_key()
        
        # 檢查是否啟用
        if config.is_spatiotemporal_enabled():
            # 使用時空系統
            pass
"""
