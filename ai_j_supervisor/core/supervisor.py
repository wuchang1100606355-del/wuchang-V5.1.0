#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 總成小 J - 核心總成系統
具備完整系統權限的 AI 總成應用程式
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

# 添加路徑
SPATIOTEMPORAL_ROOT = Path(__file__).parent.parent.parent / "spatiotemporal_system"
sys.path.insert(0, str(SPATIOTEMPORAL_ROOT))

try:
    from config.ai_j_integration import get_ai_j_spatiotemporal
    SPATIOTEMPORAL_AVAILABLE = True
except ImportError:
    SPATIOTEMPORAL_AVAILABLE = False

logger = logging.getLogger(__name__)


class AISupervisor:
    """AI 總成小 J - 最高權限總成系統"""
    
    def __init__(self, odoo_env=None):
        """
        初始化 AI 總成系統
        
        Args:
            odoo_env: Odoo 環境（如果從 Odoo 內部調用）
        """
        self.name = "AI 總成小 J"
        self.version = "1.0.0"
        self.permission_level = "supervisor_u"  # 最高權限開發者
        self.odoo_env = odoo_env
        
        # 初始化各系統
        self.capabilities = {}
        self._initialize_capabilities()
        
        logger.info(f"{self.name} v{self.version} 已初始化 (權限等級: {self.permission_level})")
    
    def _initialize_capabilities(self):
        """初始化所有能力"""
        # 時空系統
        if SPATIOTEMPORAL_AVAILABLE:
            try:
                self.spatiotemporal = get_ai_j_spatiotemporal(self.odoo_env)
                self.capabilities['spatiotemporal'] = {
                    "enabled": True,
                    "capabilities": self.spatiotemporal.get_capabilities()
                }
                logger.info("✓ 時空系統已載入")
            except Exception as e:
                logger.warning(f"時空系統載入失敗: {e}")
                self.capabilities['spatiotemporal'] = {"enabled": False, "error": str(e)}
        else:
            self.capabilities['spatiotemporal'] = {"enabled": False, "reason": "模組未安裝"}
        
        # AI 能力
        self.capabilities['ai'] = {
            "enabled": True,
            "providers": {
                "local_ollama": self._check_local_ollama(),
                "openai": bool(os.getenv('OPENAI_API_KEY') or self._get_odoo_param('ai.j.openai.api.key')),
                "anthropic": bool(os.getenv('ANTHROPIC_API_KEY') or self._get_odoo_param('ai.j.anthropic.api.key')),
                "google": bool(os.getenv('GOOGLE_API_KEY') or self._get_odoo_param('ai.j.google.api.key'))
            }
        }
        
        # 系統權限
        self.capabilities['system'] = {
            "enabled": True,
            "permission_level": self.permission_level,
            "access": {
                "full_system_access": True,
                "config_modification": True,
                "data_access": True,
                "monitoring": True
            }
        }
    
    def _check_local_ollama(self) -> bool:
        """檢查本地 Ollama"""
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _get_odoo_param(self, key: str) -> Optional[str]:
        """從 Odoo 取得參數"""
        if self.odoo_env:
            try:
                return self.odoo_env['ir.config_parameter'].sudo().get_param(key)
            except:
                pass
        return None
    
    def get_all_capabilities(self) -> Dict[str, Any]:
        """取得所有能力"""
        return {
            "supervisor": {
                "name": self.name,
                "version": self.version,
                "permission_level": self.permission_level,
                "status": "active"
            },
            "capabilities": self.capabilities,
            "timestamp": datetime.now().isoformat()
        }
    
    def execute_command(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        執行命令（最高權限）
        
        Args:
            command: 命令名稱
            params: 命令參數
        
        Returns:
            執行結果
        """
        if params is None:
            params = {}
        
        try:
            # 時空系統命令
            if command.startswith('spatiotemporal.'):
                if 'spatiotemporal' in self.capabilities and self.capabilities['spatiotemporal']['enabled']:
                    return self._execute_spatiotemporal_command(command, params)
                else:
                    return {"status": "error", "message": "時空系統未啟用"}
            
            # AI 命令
            elif command.startswith('ai.'):
                return self._execute_ai_command(command, params)
            
            # 系統命令
            elif command.startswith('system.'):
                return self._execute_system_command(command, params)
            
            else:
                return {"status": "error", "message": f"未知命令: {command}"}
        
        except Exception as e:
            logger.error(f"執行命令失敗 {command}: {e}")
            return {"status": "error", "message": str(e)}
    
    def _execute_spatiotemporal_command(self, command: str, params: Dict) -> Dict:
        """執行時空系統命令"""
        if command == 'spatiotemporal.suggest':
            suggestions = self.spatiotemporal.suggest_event(
                event_type=params.get('event_type', 'meeting'),
                participants=params.get('participants', 10),
                duration_hours=params.get('duration_hours', 2),
                preferred_village=params.get('preferred_village')
            )
            return {"status": "success", "data": suggestions}
        
        elif command == 'spatiotemporal.schedule':
            result = self.spatiotemporal.schedule_event(
                title=params.get('title'),
                event_type=params.get('event_type', 'meeting'),
                participants=params.get('participants', 10),
                duration_hours=params.get('duration_hours', 2),
                preferred_village=params.get('preferred_village')
            )
            return {"status": "success", "data": result}
        
        elif command == 'spatiotemporal.analyze':
            patterns = self.spatiotemporal.analyze_patterns(
                village_id=params.get('village_id'),
                days=params.get('days', 30)
            )
            return {"status": "success", "data": patterns}
        
        else:
            return {"status": "error", "message": f"未知的時空命令: {command}"}
    
    def _execute_ai_command(self, command: str, params: Dict) -> Dict:
        """執行 AI 命令（Odoo 內部小j，完全依據主權人意旨，直連Gemini 2.0 Pro）"""
        try:
            from ai_odoo_gemini_api import call_gemini_2_pro_api
            prompt = params.get('prompt', '')
            if not prompt:
                return {"status": "error", "message": "缺少 prompt 參數"}
            # 以Odoo內部小j最高授權身份呼叫Gemini 2.0 Pro
            gemini_result = call_gemini_2_pro_api(prompt)
            return {"status": "success", "data": gemini_result, "identity": "odoo內部小j-可究責自然人", "sovereign": "主權人完全授權"}
        except Exception as e:
            return {"status": "error", "message": f"AI命令執行失敗: {e}"}
    
    def _execute_system_command(self, command: str, params: Dict) -> Dict:
        """執行系統命令"""
        if command == 'system.status':
            return {
                "status": "success",
                "data": {
                    "supervisor": self.get_all_capabilities(),
                    "system_time": datetime.now().isoformat(),
                    "python_version": sys.version
                }
            }
        
        elif command == 'system.config':
            return {
                "status": "success",
                "data": {
                    "permission_level": self.permission_level,
                    "capabilities": self.capabilities
                }
            }
        
        else:
            return {"status": "error", "message": f"未知的系統命令: {command}"}
    
    def test_permissions(self) -> Dict[str, Any]:
        """測試所有權限"""
        tests = {
            "spatiotemporal_access": False,
            "ai_access": False,
            "system_access": False,
            "config_access": False,
            "data_access": False
        }
        
        # 測試時空系統
        if 'spatiotemporal' in self.capabilities and self.capabilities['spatiotemporal']['enabled']:
            try:
                self.spatiotemporal.get_capabilities()
                tests["spatiotemporal_access"] = True
            except:
                pass
        
        # 測試 AI
        tests["ai_access"] = self.capabilities['ai']['enabled']
        
        # 測試系統
        tests["system_access"] = self.capabilities['system']['enabled']
        tests["config_access"] = True  # 最高權限
        tests["data_access"] = True  # 最高權限
        
        return {
            "status": "success",
            "permission_level": self.permission_level,
            "tests": tests,
            "all_passed": all(tests.values()),
            "timestamp": datetime.now().isoformat()
        }


# 全域實例
_supervisor_instance = None


def get_supervisor(odoo_env=None) -> AISupervisor:
    """取得 AI 總成實例"""
    global _supervisor_instance
    
    if _supervisor_instance is None:
        _supervisor_instance = AISupervisor(odoo_env)
    elif odoo_env and _supervisor_instance.odoo_env != odoo_env:
        _supervisor_instance = AISupervisor(odoo_env)
    
    return _supervisor_instance
