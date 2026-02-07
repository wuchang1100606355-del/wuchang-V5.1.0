#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pii_storage_manager.py

個資儲存管理器（啟用個資處理功能）

功能：
- 啟用個資處理功能
- 使用加密儲存管理系統
- 支援外接儲存裝置
- 設備辨識與變動記錄

合規聲明：
- 本系統除法律規範須依法揭露及政府公示資訊中公開揭露之外無可供識別之個資，應屬合規
- 可究責自然人個資使用需獲得明確授權
- 個資處理需加密儲存
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional

from encrypted_storage_manager import get_storage_manager
from authorized_administrators import check_authorization

BASE_DIR = Path(__file__).resolve().parent


class PIIStorageManager:
    """個資儲存管理器"""
    
    def __init__(self):
        self.storage_manager = get_storage_manager()
        self.default_device_id = os.getenv("WUCHANG_PII_STORAGE_DEVICE", "").strip()
    
    def _check_authorization(self, person_name: str, use_case: str) -> bool:
        """檢查授權"""
        return check_authorization(person_name, use_case)
    
    def save_pii(
        self,
        person_name: str,
        pii_data: Dict[str, Any],
        device_id: Optional[str] = None,
        actor: str = "system",
    ) -> Path:
        """
        儲存個資（加密）
        
        參數：
        - person_name: 可究責自然人姓名
        - pii_data: 個資資料
        - device_id: 儲存裝置 ID（None 使用預設裝置）
        - actor: 操作者
        
        返回：儲存路徑
        """
        # 檢查授權
        if not self._check_authorization(person_name, "hardcode_record"):
            raise PermissionError(f"{person_name} 未授權個資使用")
        
        # 使用預設裝置或指定裝置
        target_device_id = device_id or self.default_device_id
        if not target_device_id:
            raise ValueError("未指定儲存裝置，請設定 WUCHANG_PII_STORAGE_DEVICE 或提供 device_id")
        
        # 準備儲存資料
        storage_data = {
            "person_name": person_name,
            "pii_data": pii_data,
            "stored_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "actor": actor,
        }
        
        # 儲存到加密外接裝置
        filename = f"pii_{person_name}_{int(time.time())}.encrypted"
        return self.storage_manager.save_encrypted_to_device(
            data=storage_data,
            device_id=target_device_id,
            filename=filename,
            actor=actor,
        )
    
    def load_pii(
        self,
        person_name: str,
        device_id: Optional[str] = None,
        filename: Optional[str] = None,
        actor: str = "system",
    ) -> Dict[str, Any]:
        """
        載入個資（解密）
        
        參數：
        - person_name: 可究責自然人姓名
        - device_id: 儲存裝置 ID（None 使用預設裝置）
        - filename: 檔案名稱（None 自動尋找最新檔案）
        - actor: 操作者
        
        返回：個資資料
        """
        # 檢查授權
        if not self._check_authorization(person_name, "hardcode_record"):
            raise PermissionError(f"{person_name} 未授權個資使用")
        
        # 使用預設裝置或指定裝置
        target_device_id = device_id or self.default_device_id
        if not target_device_id:
            raise ValueError("未指定儲存裝置，請設定 WUCHANG_PII_STORAGE_DEVICE 或提供 device_id")
        
        # 如果未指定檔案名稱，尋找最新檔案
        if filename is None:
            device = self.storage_manager.devices.get(target_device_id)
            if not device:
                raise ValueError(f"設備 {target_device_id} 未註冊")
            
            mount_path = Path(device.mount_path)
            # 尋找該人員的最新檔案
            pattern = f"pii_{person_name}_*.encrypted"
            files = list(mount_path.glob(pattern))
            if not files:
                raise FileNotFoundError(f"找不到 {person_name} 的個資檔案")
            
            filename = max(files, key=lambda p: p.stat().st_mtime).name
        
        # 從加密外接裝置載入
        data = self.storage_manager.load_encrypted_from_device(
            device_id=target_device_id,
            filename=filename,
            actor=actor,
        )
        
        return data.get("pii_data", {})


# 全局實例
_pii_storage_manager: Optional[PIIStorageManager] = None


def get_pii_storage_manager() -> PIIStorageManager:
    """獲取個資儲存管理器實例"""
    global _pii_storage_manager
    if _pii_storage_manager is None:
        _pii_storage_manager = PIIStorageManager()
    return _pii_storage_manager
