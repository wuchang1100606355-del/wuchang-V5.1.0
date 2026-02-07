#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
personal_ai_binding.py

個人身份驗證與最高權限 AI 綁定系統
"""

import sys
import json
import hashlib
import uuid
import platform
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# 設定 UTF-8 編碼
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
PERSONAL_BINDING_FILE = BASE_DIR / "personal_ai_binding.json"
VERIFICATION_FILE = BASE_DIR / "personal_verification.json"
INTERNAL_ID_RECORDS_FILE = BASE_DIR / "internal_id_records.json"
INTERNAL_ID_RECORDS_FILE = BASE_DIR / "internal_id_records.json"


def get_mac_address() -> str:
    """取得本機 MAC 地址（唯一識別碼）"""
    try:
        # 方法 1: 使用 uuid.getnode()（跨平台）
        mac = uuid.getnode()
        if mac != uuid.getnode():  # 如果返回的是隨機值，嘗試其他方法
            # 方法 2: Windows
            if platform.system() == "Windows":
                import subprocess
                result = subprocess.run(
                    ["getmac", "/fo", "csv", "/nh"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if line and ',' in line:
                            mac_str = line.split(',')[0].strip().replace('-', ':').replace('"', '')
                            if mac_str and mac_str != "N/A":
                                return mac_str
        else:
            # 將整數 MAC 轉換為標準格式
            mac_hex = ':'.join(['{:02x}'.format((mac >> ele) & 0xff) for ele in range(0, 8*6, 8)][::-1])
            return mac_hex
        
        # 方法 3: 使用網路介面（備用）
        import socket
        hostname = socket.gethostname()
        # 這不是真正的 MAC，但可以作為備用唯一識別碼
        return f"{hostname}_{uuid.getnode():012x}"
    except Exception as e:
        # 最後備用：使用機器 ID
        try:
            import subprocess
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["wmic", "csproduct", "get", "uuid"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    uuid_line = [l.strip() for l in result.stdout.split('\n') if l.strip() and l.strip() != "UUID"]
                    if uuid_line:
                        return uuid_line[0]
        except:
            pass
        # 最終備用：使用 hostname + 隨機 ID
        return f"{socket.gethostname()}_{uuid.uuid4().hex[:12]}"


def load_personal_binding() -> Dict[str, Any]:
    """載入個人 AI 綁定設定"""
    if PERSONAL_BINDING_FILE.exists():
        try:
            return json.loads(PERSONAL_BINDING_FILE.read_text(encoding="utf-8"))
        except:
            return {}
    return {}


def save_personal_binding(binding: Dict[str, Any]):
    """儲存個人 AI 綁定設定"""
    binding["last_updated"] = datetime.now().isoformat()
    PERSONAL_BINDING_FILE.write_text(
        json.dumps(binding, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def load_verification() -> Dict[str, Any]:
    """載入驗證資料"""
    if VERIFICATION_FILE.exists():
        try:
            return json.loads(VERIFICATION_FILE.read_text(encoding="utf-8"))
        except:
            return {}
    return {}


def save_verification(verification: Dict[str, Any]):
    """儲存驗證資料"""
    verification["last_updated"] = datetime.now().isoformat()
    VERIFICATION_FILE.write_text(
        json.dumps(verification, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def hash_password(password: str) -> str:
    """雜湊密碼"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """驗證密碼"""
    return hash_password(password) == hashed


def create_personal_binding(
    personal_name: str,
    personal_id: str,
    password: str,
    email: str = "",
    phone: str = "",
    notes: str = "",
    mac_address: str = None
) -> Dict[str, Any]:
    """建立個人 AI 綁定（需要本機唯一碼驗證）"""
    # 取得本機 MAC 地址
    if not mac_address:
        mac_address = get_mac_address()
    
    binding = {
        "personal_name": personal_name,
        "personal_id": personal_id,
        "password_hash": hash_password(password),
        "email": email,
        "phone": phone,
        "notes": notes,
        "mac_address": mac_address,  # 本機唯一碼
        "highest_authority": True,
        "ai_binding": {
            "local_j": True,
            "cloud_j": True,
            "binding_date": datetime.now().isoformat()
        },
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }
    
    save_personal_binding(binding)
    return binding


def load_internal_id_records() -> Dict[str, Any]:
    """載入內部身份證檔案"""
    if INTERNAL_ID_RECORDS_FILE.exists():
        try:
            return json.loads(INTERNAL_ID_RECORDS_FILE.read_text(encoding="utf-8"))
        except:
            return {}
    return {}


def find_id_record_by_name(name: str) -> Optional[Dict[str, Any]]:
    """根據姓名查找身份證記錄"""
    records_data = load_internal_id_records()
    records = records_data.get("records", [])
    
    for record in records:
        if record.get("name") == name:
            return record
    return None


def verify_biometric_against_id(
    name: str,
    id_number: str = None,
    biometric_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """對照生物特徵與內部身份證檔案"""
    # 查找身份證記錄
    id_record = find_id_record_by_name(name)
    
    if not id_record:
        return {
            "verified": False,
            "error": "身份證記錄不存在",
            "message": f"找不到 {name} 的身份證記錄"
        }
    
    # 驗證身份證號碼（如果提供）
    if id_number and id_record.get("id_number") != id_number:
        return {
            "verified": False,
            "error": "身份證號碼不匹配",
            "message": "身份證號碼與記錄不符"
        }
    
    # 生物特徵驗證（這裡可以加入更複雜的比對邏輯）
    # 目前先做基本驗證
    if biometric_data:
        # 可以加入人臉識別、指紋等驗證邏輯
        # 目前先標記為已驗證
        biometric_verified = True
    else:
        biometric_verified = False
    
    return {
        "verified": True,
        "id_record": {
            "name": id_record.get("name", ""),
            "id_number": id_record.get("id_number", ""),
            "role": id_record.get("role", ""),
            "organization": id_record.get("organization", "")
        },
        "biometric_verified": biometric_verified,
        "message": "身份證對照成功"
    }


def update_verification(
    personal_id: str,
    verification_data: Dict[str, Any]
) -> Dict[str, Any]:
    """更新驗證資料"""
    verification = load_verification()
    
    verification[personal_id] = {
        **verification_data,
        "verified_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }
    
    save_verification(verification)
    return verification[personal_id]


def get_accountability_from_personal_binding() -> Dict[str, Any]:
    """從個人綁定取得可究責對象資訊"""
    binding = load_personal_binding()
    if not binding:
        return {
            "design_responsibility": {"natural_person": {}, "legal_entity": {}},
            "usage_responsibility": {"natural_person": {}, "legal_entity": {}}
        }
    
    # 從內部身份證記錄取得完整資訊
    id_record = find_id_record_by_name(binding.get("personal_name", ""))
    
    # 建立自然人資訊
    natural_person = {
        "name": binding.get("personal_name", ""),
        "id_number": id_record.get("id_number", "") if id_record else "",
        "role": id_record.get("role", "") if id_record else "",
        "email": binding.get("email", ""),
        "phone": binding.get("phone", ""),
        "verified": True,
        "verification_source": "personal_ai_binding"
    }
    
    # 建立法人資訊（從身份證記錄中的組織）
    legal_entity = {}
    if id_record and id_record.get("organization"):
        legal_entity = {
            "name": id_record.get("organization", ""),
            "role": id_record.get("role", ""),  # 例如：總幹事
            "verified": True,
            "verification_source": "internal_id_records"
        }
    
    return {
        "design_responsibility": {
            "natural_person": natural_person,
            "legal_entity": legal_entity
        },
        "usage_responsibility": {
            "natural_person": natural_person,
            "legal_entity": legal_entity
        }
    }


def verify_personal_identity(
    personal_id: str,
    password: str,
    mac_address: str = None
) -> bool:
    """驗證個人身份（需要本機唯一碼驗證）"""
    binding = load_personal_binding()
    
    if not binding:
        return False
    
    if binding.get("personal_id") != personal_id:
        return False
    
    if not verify_password(password, binding.get("password_hash", "")):
        return False
    
    # 驗證本機唯一碼（MAC 地址）
    if not mac_address:
        mac_address = get_mac_address()
    
    stored_mac = binding.get("mac_address", "")
    if stored_mac and stored_mac != mac_address:
        return False  # MAC 地址不匹配，不是同一台機器
    
    return True


def get_highest_authority_status() -> Dict[str, Any]:
    """取得最高權限狀態"""
    binding = load_personal_binding()
    current_mac = get_mac_address()
    
    if not binding:
        return {
            "bound": False,
            "message": "尚未綁定個人身份",
            "current_mac": current_mac
        }
    
    stored_mac = binding.get("mac_address", "")
    mac_match = (stored_mac == current_mac) if stored_mac else False
    
    # 取得可究責對象資訊
    accountability = get_accountability_from_personal_binding()
    
    return {
        "bound": True,
        "personal_name": binding.get("personal_name", ""),
        "personal_id": binding.get("personal_id", ""),
        "highest_authority": binding.get("highest_authority", False),
        "ai_binding": binding.get("ai_binding", {}),
        "mac_address": stored_mac,
        "current_mac": current_mac,
        "mac_match": mac_match,
        "created_at": binding.get("created_at", ""),
        "last_updated": binding.get("last_updated", ""),
        "accountability": accountability
    }


if __name__ == "__main__":
    print("=" * 70)
    print("個人 AI 綁定系統")
    print("=" * 70)
    print()
    
    status = get_highest_authority_status()
    
    if status["bound"]:
        print("✅ 已綁定個人身份")
        print(f"   姓名: {status.get('personal_name', '')}")
        print(f"   身份 ID: {status.get('personal_id', '')}")
        print(f"   最高權限: {'是' if status.get('highest_authority') else '否'}")
        print(f"   AI 綁定: {status.get('ai_binding', {})}")
    else:
        print("❌ 尚未綁定個人身份")
        print()
        print("使用方式：")
        print("  1. 在 UI 中填寫個人驗證資料")
        print("  2. 系統會自動建立最高權限 AI 綁定")
    
    print()
    print("=" * 70)
