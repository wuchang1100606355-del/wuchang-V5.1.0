#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
authorized_administrators.py

本系統經授權之獨立管理權限自然人硬編碼記錄

合規聲明：
- 本系統經授權之獨立管理權限自然人不在隱私權保護規範內
- 此兩種自然人（本系統及AI程序設計之可究責自然人、本系統經授權之獨立管理權限自然人）除姓名外其餘不得公開揭露，但須紀錄於本系統之硬編碼
- 本檔案為硬編碼記錄，包含所有相關資訊以確保責任歸屬和系統管理
"""

from __future__ import annotations
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional, Dict, Any

# 注意：此檔案為硬編碼記錄，除姓名外其餘資訊不得公開揭露
# 但須記錄於本系統之硬編碼以確保責任歸屬和系統管理

BASE_DIR = Path(__file__).resolve().parent
AUTHORIZATION_RECORDS_PATH = BASE_DIR / "accountable_person_authorizations.json"


@dataclass
class PersonalDataAuthorization:
    """可究責自然人個資使用授權"""
    person_name: str  # 姓名（可公開）
    person_type: str  # 類型：system_designer 或 authorized_administrator
    authorization_scope: str  # 授權範圍（不得公開揭露）
    authorized_uses: List[str]  # 授權用途列表（不得公開揭露）
    granted_at: str  # 授權時間（ISO 格式）
    expires_at: Optional[str] = None  # 到期時間（ISO 格式，None 表示永久有效）
    revoked_at: Optional[str] = None  # 撤銷時間（ISO 格式，None 表示未撤銷）
    granted_by: Optional[str] = None  # 授權人（不得公開揭露）
    notes: Optional[str] = None  # 備註（不得公開揭露）
    
    def is_valid(self) -> bool:
        """檢查授權是否有效"""
        if self.revoked_at:
            return False
        if self.expires_at:
            try:
                expires_ts = time.mktime(time.strptime(self.expires_at, "%Y-%m-%dT%H:%M:%S%z"))
                if time.time() > expires_ts:
                    return False
            except Exception:
                pass
        return True


@dataclass
class AuthorizedAdministrator:
    """經授權之獨立管理權限自然人"""
    name: str  # 姓名（可公開）
    role: str  # 職務角色（不得公開揭露）
    contact_method: Optional[str] = None  # 聯絡方式（不得公開揭露）
    authorization_scope: Optional[str] = None  # 授權範圍（不得公開揭露）
    notes: Optional[str] = None  # 備註（不得公開揭露）


@dataclass
class SystemDesigner:
    """本系統及AI程序設計之可究責自然人"""
    name: str  # 姓名（可公開）
    role: str  # 職務角色（不得公開揭露）
    responsibility: Optional[str] = None  # 負責範圍（不得公開揭露）
    contact_method: Optional[str] = None  # 聯絡方式（不得公開揭露）
    notes: Optional[str] = None  # 備註（不得公開揭露）


# 硬編碼記錄：本系統經授權之獨立管理權限自然人
AUTHORIZED_ADMINISTRATORS: List[AuthorizedAdministrator] = [
    # 範例格式（請依實際情況填入）：
    # AuthorizedAdministrator(
    #     name="姓名（可公開）",
    #     role="職務角色（不得公開揭露）",
    #     contact_method="聯絡方式（不得公開揭露）",
    #     authorization_scope="授權範圍（不得公開揭露）",
    #     notes="備註（不得公開揭露）",
    # ),
]

# 硬編碼記錄：本系統及AI程序設計之可究責自然人
SYSTEM_DESIGNERS: List[SystemDesigner] = [
    # 範例格式（請依實際情況填入）：
    # SystemDesigner(
    #     name="姓名（可公開）",
    #     role="職務角色（不得公開揭露）",
    #     responsibility="負責範圍（不得公開揭露）",
    #     contact_method="聯絡方式（不得公開揭露）",
    #     notes="備註（不得公開揭露）",
    # ),
]


def get_authorized_administrators_names() -> List[str]:
    """
    獲取經授權之獨立管理權限自然人姓名列表（可公開）
    
    注意：僅返回姓名，其他資訊不得公開揭露
    """
    return [admin.name for admin in AUTHORIZED_ADMINISTRATORS]


def get_system_designers_names() -> List[str]:
    """
    獲取本系統及AI程序設計之可究責自然人姓名列表（可公開）
    
    注意：僅返回姓名，其他資訊不得公開揭露
    """
    return [designer.name for designer in SYSTEM_DESIGNERS]


def get_all_accountable_names() -> List[str]:
    """
    獲取所有可究責自然人姓名列表（可公開）
    
    包括：
    - 本系統及AI程序設計之可究責自然人
    - 本系統經授權之獨立管理權限自然人
    
    注意：僅返回姓名，其他資訊不得公開揭露
    """
    names = []
    names.extend(get_system_designers_names())
    names.extend(get_authorized_administrators_names())
    return list(set(names))  # 去重


# ===== 可究責自然人個資使用授權管理 =====

def _now_iso() -> str:
    """獲取當前時間 ISO 格式"""
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def load_authorizations() -> Dict[str, PersonalDataAuthorization]:
    """
    載入所有授權記錄
    
    返回：{person_name: PersonalDataAuthorization}
    """
    if not AUTHORIZATION_RECORDS_PATH.exists():
        return {}
    
    try:
        data = json.loads(AUTHORIZATION_RECORDS_PATH.read_text(encoding="utf-8"))
        authorizations = {}
        for name, auth_data in data.items():
            authorizations[name] = PersonalDataAuthorization(**auth_data)
        return authorizations
    except Exception:
        return {}


def save_authorizations(authorizations: Dict[str, PersonalDataAuthorization]) -> None:
    """
    儲存所有授權記錄
    
    注意：此檔案為硬編碼記錄，除姓名外其餘資訊不得公開揭露
    """
    AUTHORIZATION_RECORDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {name: asdict(auth) for name, auth in authorizations.items()}
    AUTHORIZATION_RECORDS_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def grant_authorization(
    person_name: str,
    person_type: str,
    authorization_scope: str,
    authorized_uses: List[str],
    expires_at: Optional[str] = None,
    granted_by: Optional[str] = None,
    notes: Optional[str] = None,
) -> PersonalDataAuthorization:
    """
    授予可究責自然人個資使用授權
    
    參數：
    - person_name: 姓名（可公開）
    - person_type: 類型（system_designer 或 authorized_administrator）
    - authorization_scope: 授權範圍（不得公開揭露）
    - authorized_uses: 授權用途列表（不得公開揭露）
    - expires_at: 到期時間（ISO 格式，None 表示永久有效）
    - granted_by: 授權人（不得公開揭露）
    - notes: 備註（不得公開揭露）
    """
    authorizations = load_authorizations()
    
    # 如果已存在授權，先撤銷舊的
    if person_name in authorizations:
        old_auth = authorizations[person_name]
        if old_auth.is_valid():
            old_auth.revoked_at = _now_iso()
    
    # 建立新授權
    new_auth = PersonalDataAuthorization(
        person_name=person_name,
        person_type=person_type,
        authorization_scope=authorization_scope,
        authorized_uses=authorized_uses,
        granted_at=_now_iso(),
        expires_at=expires_at,
        revoked_at=None,
        granted_by=granted_by,
        notes=notes,
    )
    
    authorizations[person_name] = new_auth
    save_authorizations(authorizations)
    
    return new_auth


def revoke_authorization(person_name: str) -> bool:
    """
    撤銷可究責自然人個資使用授權
    
    返回：是否成功撤銷
    """
    authorizations = load_authorizations()
    
    if person_name not in authorizations:
        return False
    
    auth = authorizations[person_name]
    if auth.revoked_at:
        return False  # 已經撤銷
    
    auth.revoked_at = _now_iso()
    save_authorizations(authorizations)
    
    return True


def get_authorization(person_name: str) -> Optional[PersonalDataAuthorization]:
    """
    獲取可究責自然人個資使用授權
    
    返回：授權記錄（如果存在且有效）
    """
    authorizations = load_authorizations()
    
    if person_name not in authorizations:
        return None
    
    auth = authorizations[person_name]
    if not auth.is_valid():
        return None
    
    return auth


def check_authorization(person_name: str, use_case: str) -> bool:
    """
    檢查可究責自然人是否授權特定用途
    
    參數：
    - person_name: 姓名
    - use_case: 用途（如 "hardcode_record", "system_audit", "compliance_report" 等）
    
    返回：是否授權
    """
    auth = get_authorization(person_name)
    if not auth:
        return False
    
    return use_case in auth.authorized_uses or "*" in auth.authorized_uses


def get_all_valid_authorizations() -> List[PersonalDataAuthorization]:
    """
    獲取所有有效的授權記錄
    
    返回：有效的授權記錄列表
    """
    authorizations = load_authorizations()
    return [auth for auth in authorizations.values() if auth.is_valid()]


def get_authorization_summary(person_name: str) -> Dict[str, Any]:
    """
    獲取可究責自然人授權摘要（僅包含可公開資訊）
    
    返回：授權摘要（僅包含姓名和授權狀態）
    """
    auth = get_authorization(person_name)
    
    if not auth:
        return {
            "person_name": person_name,
            "authorized": False,
            "status": "no_authorization",
        }
    
    return {
        "person_name": person_name,
        "authorized": True,
        "status": "active" if auth.is_valid() else "revoked_or_expired",
        "granted_at": auth.granted_at,
        "expires_at": auth.expires_at,
    }


# 硬編碼記錄驗證
def validate_hardcoded_records() -> dict:
    """
    驗證硬編碼記錄的完整性
    
    返回驗證結果，包含：
    - 是否有記錄
    - 記錄數量
    - 姓名是否完整
    """
    result = {
        "authorized_administrators_count": len(AUTHORIZED_ADMINISTRATORS),
        "system_designers_count": len(SYSTEM_DESIGNERS),
        "all_names": get_all_accountable_names(),
        "valid": True,
    }
    
    # 驗證所有記錄都有姓名
    for admin in AUTHORIZED_ADMINISTRATORS:
        if not admin.name or not admin.name.strip():
            result["valid"] = False
            result["error"] = "發現未填寫姓名的授權管理員記錄"
            break
    
    for designer in SYSTEM_DESIGNERS:
        if not designer.name or not designer.name.strip():
            result["valid"] = False
            result["error"] = "發現未填寫姓名的系統設計者記錄"
            break
    
    return result


# 授權記錄驗證
def validate_authorizations() -> dict:
    """
    驗證授權記錄的完整性
    
    返回驗證結果，包含：
    - 授權記錄數量
    - 有效授權數量
    - 過期授權數量
    - 已撤銷授權數量
    """
    authorizations = load_authorizations()
    valid_count = 0
    expired_count = 0
    revoked_count = 0
    
    for auth in authorizations.values():
        if auth.revoked_at:
            revoked_count += 1
        elif auth.expires_at:
            try:
                expires_ts = time.mktime(time.strptime(auth.expires_at, "%Y-%m-%dT%H:%M:%S%z"))
                if time.time() > expires_ts:
                    expired_count += 1
                else:
                    valid_count += 1
            except Exception:
                valid_count += 1
        else:
            valid_count += 1
    
    return {
        "total_count": len(authorizations),
        "valid_count": valid_count,
        "expired_count": expired_count,
        "revoked_count": revoked_count,
        "valid": True,
    }
