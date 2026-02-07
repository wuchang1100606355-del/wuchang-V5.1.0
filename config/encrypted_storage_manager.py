#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
encrypted_storage_manager.py

加密儲存管理系統

功能：
- 加密處理記錄
- 支援地端外接儲存裝置
- 設備辨識
- 變動紀錄於硬編碼
- 啟用個資處理功能

合規聲明：
- 本系統除法律規範須依法揭露及政府公示資訊中公開揭露之外無可供識別之個資，應屬合規
- 可究責自然人個資使用需獲得明確授權
- 個資處理需加密儲存
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

BASE_DIR = Path(__file__).resolve().parent
STORAGE_CONFIG_PATH = BASE_DIR / "encrypted_storage_config.json"
DEVICE_REGISTRY_PATH = BASE_DIR / "device_registry.json"
CHANGE_LOG_PATH = BASE_DIR / "storage_change_log.jsonl"


@dataclass
class StorageDevice:
    """儲存裝置資訊"""
    device_id: str  # 設備識別碼（硬編碼）
    device_name: str  # 設備名稱
    device_type: str  # 設備類型（usb, external_drive, network_drive 等）
    mount_path: str  # 掛載路徑
    serial_number: Optional[str] = None  # 序號（不得公開揭露）
    capacity_bytes: Optional[int] = None  # 容量（不得公開揭露）
    registered_at: str = ""  # 註冊時間
    last_seen_at: str = ""  # 最後使用時間
    is_active: bool = True  # 是否啟用
    encryption_key_hash: Optional[str] = None  # 加密金鑰雜湊（不得公開揭露）
    notes: Optional[str] = None  # 備註（不得公開揭露）


@dataclass
class StorageChangeLog:
    """儲存變動記錄（硬編碼）"""
    timestamp: str  # 時間戳
    change_type: str  # 變動類型（device_added, device_removed, data_encrypted, data_decrypted, key_rotated 等）
    device_id: str  # 設備識別碼
    actor: str  # 操作者
    details: Dict[str, Any]  # 詳細資訊（不得公開揭露）
    hash: str  # 記錄雜湊值


class EncryptedStorageManager:
    """加密儲存管理器"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or STORAGE_CONFIG_PATH
        self.device_registry_path = DEVICE_REGISTRY_PATH
        self.change_log_path = CHANGE_LOG_PATH
        self.devices: Dict[str, StorageDevice] = {}
        self.encryption_keys: Dict[str, bytes] = {}  # 記憶體中的加密金鑰
        self._load_config()
        self._load_device_registry()
    
    def _load_config(self) -> None:
        """載入配置"""
        if self.config_path.exists():
            try:
                data = json.loads(self.config_path.read_text(encoding="utf-8"))
                # 載入配置（不包含敏感資訊）
            except Exception:
                pass
    
    def _load_device_registry(self) -> None:
        """載入設備註冊表"""
        if self.device_registry_path.exists():
            try:
                data = json.loads(self.device_registry_path.read_text(encoding="utf-8"))
                for device_id, device_data in data.items():
                    self.devices[device_id] = StorageDevice(**device_data)
            except Exception:
                pass
    
    def _save_device_registry(self) -> None:
        """儲存設備註冊表"""
        data = {device_id: asdict(device) for device_id, device in self.devices.items()}
        self.device_registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.device_registry_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    
    def _log_change(self, change_type: str, device_id: str, actor: str, details: Dict[str, Any]) -> None:
        """記錄變動（硬編碼）"""
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        log_entry = StorageChangeLog(
            timestamp=timestamp,
            change_type=change_type,
            device_id=device_id,
            actor=actor,
            details=details,
            hash="",  # 將在下面計算
        )
        
        # 計算雜湊值
        log_data = json.dumps(asdict(log_entry), ensure_ascii=False, sort_keys=True)
        log_entry.hash = hashlib.sha256(log_data.encode("utf-8")).hexdigest()
        
        # 寫入變動記錄（硬編碼）
        log_line = json.dumps(asdict(log_entry), ensure_ascii=False)
        self.change_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.change_log_path, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    
    def detect_external_devices(self) -> List[Dict[str, Any]]:
        """偵測外接儲存裝置"""
        devices = []
        
        if platform.system() == "Windows":
            try:
                # Windows: 使用 wmic 查詢磁碟機
                result = subprocess.run(
                    ["wmic", "logicaldisk", "get", "deviceid,drivetype,volumename,size,filesystem"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                lines = result.stdout.strip().split("\n")[1:]  # 跳過標題行
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        device_id = parts[0]
                        drive_type = parts[1] if len(parts) > 1 else "0"
                        # DriveType: 2=可移除, 3=固定, 4=網路, 5=CD-ROM
                        if drive_type in ("2", "3", "4"):  # 可移除、固定、網路
                            devices.append({
                                "device_id": device_id,
                                "drive_type": drive_type,
                                "mount_path": device_id,
                            })
            except Exception:
                pass
        elif platform.system() == "Linux":
            try:
                # Linux: 檢查 /dev/disk/by-id 或 /mnt, /media
                result = subprocess.run(
                    ["lsblk", "-o", "NAME,TYPE,MOUNTPOINT,SIZE", "-J"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    import json
                    data = json.loads(result.stdout)
                    for blockdev in data.get("blockdevices", []):
                        if blockdev.get("type") in ("disk", "part"):
                            mountpoint = blockdev.get("mountpoint", "")
                            if mountpoint and ("/media" in mountpoint or "/mnt" in mountpoint):
                                devices.append({
                                    "device_id": blockdev.get("name", ""),
                                    "mount_path": mountpoint,
                                })
            except Exception:
                pass
        
        return devices
    
    def register_device(
        self,
        device_id: str,
        device_name: str,
        device_type: str,
        mount_path: str,
        serial_number: Optional[str] = None,
        capacity_bytes: Optional[int] = None,
        actor: str = "system",
        notes: Optional[str] = None,
    ) -> StorageDevice:
        """註冊儲存裝置"""
        now = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        
        device = StorageDevice(
            device_id=device_id,
            device_name=device_name,
            device_type=device_type,
            mount_path=mount_path,
            serial_number=serial_number,
            capacity_bytes=capacity_bytes,
            registered_at=now,
            last_seen_at=now,
            is_active=True,
            notes=notes,
        )
        
        self.devices[device_id] = device
        self._save_device_registry()
        
        # 記錄變動（硬編碼）
        self._log_change(
            change_type="device_added",
            device_id=device_id,
            actor=actor,
            details={
                "device_name": device_name,
                "device_type": device_type,
                "mount_path": mount_path,
            },
        )
        
        return device
    
    def generate_encryption_key(self, device_id: str, password: Optional[str] = None) -> bytes:
        """產生加密金鑰"""
        if password is None:
            # 使用設備識別碼和系統資訊產生金鑰
            key_material = f"{device_id}:{platform.node()}:{time.time()}".encode("utf-8")
        else:
            key_material = password.encode("utf-8")
        
        # 使用 PBKDF2 產生金鑰
        salt = b"wuchang_encryption_salt"  # 固定 salt（實際應用中應使用隨機 salt）
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(key_material))
        
        # 儲存金鑰雜湊
        key_hash = hashlib.sha256(key).hexdigest()
        if device_id in self.devices:
            self.devices[device_id].encryption_key_hash = key_hash
            self._save_device_registry()
        
        # 儲存在記憶體中
        self.encryption_keys[device_id] = key
        
        return key
    
    def encrypt_data(self, data: bytes, device_id: str) -> bytes:
        """加密資料"""
        if device_id not in self.encryption_keys:
            raise ValueError(f"設備 {device_id} 未註冊或金鑰未產生")
        
        key = self.encryption_keys[device_id]
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data)
        
        # 記錄變動（硬編碼）
        self._log_change(
            change_type="data_encrypted",
            device_id=device_id,
            actor="system",
            details={
                "data_size": len(data),
                "encrypted_size": len(encrypted),
            },
        )
        
        return encrypted
    
    def decrypt_data(self, encrypted_data: bytes, device_id: str) -> bytes:
        """解密資料"""
        if device_id not in self.encryption_keys:
            raise ValueError(f"設備 {device_id} 未註冊或金鑰未產生")
        
        key = self.encryption_keys[device_id]
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted_data)
        
        # 記錄變動（硬編碼）
        self._log_change(
            change_type="data_decrypted",
            device_id=device_id,
            actor="system",
            details={
                "encrypted_size": len(encrypted_data),
                "decrypted_size": len(decrypted),
            },
        )
        
        return decrypted
    
    def save_encrypted_to_device(
        self,
        data: Dict[str, Any],
        device_id: str,
        filename: str,
        actor: str = "system",
    ) -> Path:
        """儲存加密資料到外接裝置"""
        if device_id not in self.devices:
            raise ValueError(f"設備 {device_id} 未註冊")
        
        device = self.devices[device_id]
        if not device.is_active:
            raise ValueError(f"設備 {device_id} 未啟用")
        
        # 檢查掛載路徑是否存在
        mount_path = Path(device.mount_path)
        if not mount_path.exists():
            raise ValueError(f"掛載路徑不存在: {device.mount_path}")
        
        # 確保有加密金鑰
        if device_id not in self.encryption_keys:
            self.generate_encryption_key(device_id)
        
        # 加密資料
        data_json = json.dumps(data, ensure_ascii=False).encode("utf-8")
        encrypted_data = self.encrypt_data(data_json, device_id)
        
        # 儲存到外接裝置
        target_path = mount_path / filename
        target_path.write_bytes(encrypted_data)
        
        # 更新最後使用時間
        device.last_seen_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        self._save_device_registry()
        
        # 記錄變動（硬編碼）
        self._log_change(
            change_type="data_saved_to_device",
            device_id=device_id,
            actor=actor,
            details={
                "filename": filename,
                "file_size": len(encrypted_data),
                "target_path": str(target_path),
            },
        )
        
        return target_path
    
    def load_encrypted_from_device(
        self,
        device_id: str,
        filename: str,
        actor: str = "system",
    ) -> Dict[str, Any]:
        """從外接裝置載入加密資料"""
        if device_id not in self.devices:
            raise ValueError(f"設備 {device_id} 未註冊")
        
        device = self.devices[device_id]
        if not device.is_active:
            raise ValueError(f"設備 {device_id} 未啟用")
        
        # 檢查掛載路徑是否存在
        mount_path = Path(device.mount_path)
        if not mount_path.exists():
            raise ValueError(f"掛載路徑不存在: {device.mount_path}")
        
        # 確保有加密金鑰
        if device_id not in self.encryption_keys:
            self.generate_encryption_key(device_id)
        
        # 從外接裝置讀取
        source_path = mount_path / filename
        if not source_path.exists():
            raise FileNotFoundError(f"檔案不存在: {source_path}")
        
        encrypted_data = source_path.read_bytes()
        
        # 解密資料
        decrypted_data = self.decrypt_data(encrypted_data, device_id)
        data = json.loads(decrypted_data.decode("utf-8"))
        
        # 更新最後使用時間
        device.last_seen_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        self._save_device_registry()
        
        # 記錄變動（硬編碼）
        self._log_change(
            change_type="data_loaded_from_device",
            device_id=device_id,
            actor=actor,
            details={
                "filename": filename,
                "file_size": len(encrypted_data),
                "source_path": str(source_path),
            },
        )
        
        return data
    
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """獲取設備資訊（僅可公開資訊）"""
        if device_id not in self.devices:
            return None
        
        device = self.devices[device_id]
        return {
            "device_id": device.device_id,
            "device_name": device.device_name,
            "device_type": device.device_type,
            "mount_path": device.mount_path,
            "registered_at": device.registered_at,
            "last_seen_at": device.last_seen_at,
            "is_active": device.is_active,
        }
    
    def list_devices(self) -> List[Dict[str, Any]]:
        """列出所有設備（僅可公開資訊）"""
        return [self.get_device_info(device_id) for device_id in self.devices.keys()]


# 全局實例
_storage_manager: Optional[EncryptedStorageManager] = None


def get_storage_manager() -> EncryptedStorageManager:
    """獲取儲存管理器實例"""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = EncryptedStorageManager()
    return _storage_manager
