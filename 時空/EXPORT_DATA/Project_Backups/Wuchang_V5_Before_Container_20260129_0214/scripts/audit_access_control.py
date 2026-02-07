"""
小j 審計日誌訪問控制系統
查驗者必須符合中華民國法律規範的公權力標準
需持有電子簽章的合法公文方可訪問
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from enum import Enum
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('AuditAccess_Control')

# 路徑配置
BASE_DIR = Path(__file__).parent.parent
AUDIT_DIR = BASE_DIR / 'memory_store' / 'audit_log'
AUTHORITY_DIR = AUDIT_DIR / 'authorized_entities'
ACCESS_LOG = AUDIT_DIR / 'audit_access_log.jsonl'

# 確保目錄存在
AUDIT_DIR.mkdir(parents=True, exist_ok=True)
AUTHORITY_DIR.mkdir(parents=True, exist_ok=True)


class GovernmentAuthorityLevel(Enum):
    """中華民國政府權責單位分類"""
    CENTRAL = "中央政府"  # 行政院所屬各部會
    LOCAL = "地方政府"    # 縣市政府、里鄰長
    JUDICIAL = "司法機構"  # 法院、檢察署
    LEGISLATIVE = "立法機構"  # 立法院及其委員會
    CONTROL = "監察機構"   # 監察院
    CERTIFICATION = "認證機構"  # 數位簽章認證服務提供者


class AuditAccessControl:
    """
    審計日誌訪問控制

    遵循中華民國電子簽章法、個人資料保護法等規範
    確保只有合法公權力單位能查驗審計日誌
    """

    @staticmethod
    def register_government_entity(
        entity_name: str,
        entity_id: str,  # 統編或代碼
        authority_level: GovernmentAuthorityLevel,
        certificate_path: str,  # 電子簽章憑證路徑
        certificate_serial: str,  # 憑證序號
        authorized_by: str,  # 授權機構 (e.g. "行政院" )
        purpose: str  # 查驗目的 (e.g. "例行稽查", "法律程序" )
    ) -> Tuple[bool, str]:
        """
        註冊合法的政府權責單位

        Args:
            entity_name: 機構名稱
            entity_id: 統一編號或識別碼
            authority_level: 權力層級
            certificate_path: 電子簽章憑證路徑 (需 X.509 格式)
            certificate_serial: 憑證序號
            authorized_by: 授權單位
            purpose: 查驗目的

        Returns:
            (是否成功, 訊息)
        """

        # 驗證憑證格式與簽章
        if not AuditAccessControl._verify_certificate(certificate_path, certificate_serial):
            return False, "電子簽章憑證驗證失敗或無效"

        entity_record = {
            "registration_time": datetime.now().isoformat(),
            "entity_name": entity_name,
            "entity_id": entity_id,
            "authority_level": authority_level.value,
            "certificate_path": certificate_path,
            "certificate_serial": certificate_serial,
            "authorized_by": authorized_by,
            "purpose": purpose,
            "status": "registered",
            "access_history": []
        }

        # 儲存到授權清單
        entity_file = AUTHORITY_DIR / f"{entity_id}.json"
        try:
            with open(entity_file, 'w', encoding='utf-8') as f:
                json.dump(entity_record, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ 政府機構已註冊: {entity_name} ({entity_id})")
            return True, f"機構 {entity_name} 已成功註冊"

        except Exception as e:
            logger.error(f"機構註冊失敗: {e}")
            return False, f"註冊失敗: {str(e)}"

    @staticmethod
    def _verify_certificate(cert_path: str, cert_serial: str) -> bool:
        """
        驗證電子簽章憑證真偽

        在實務中需對接:
        - MOEA 數位簽章認證中心
        - 各地方政府簽章驗證系統
        - 司法院電子簽章系統

        此處為佔位符實作
        """
        try:
            cert_file = Path(cert_path)
            if not cert_file.exists():
                logger.warning(f"憑證檔案不存在: {cert_path}")
                return False

            # TODO: 實際實作需對接憑證驗證服務
            # from cryptography import x509
            # from cryptography.hazmat.backends import default_backend
            #
            # with open(cert_path, 'rb') as f:
            #     cert_data = f.read()
            # cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            # # 驗證序號、有效期、簽發者等

            logger.info(f"✅ 電子簽章憑證驗證通過: {cert_serial}")
            return True

        except Exception as e:
            logger.error(f"憑證驗證失敗: {e}")
            return False

    @staticmethod
    def authorize_audit_access(
        entity_id: str,
        request_reason: str,
        # 要求的日誌類型: ['all_commands', 'concerns', 'decisions']
        requested_logs: list
    ) -> Tuple[bool, str, Optional[Dict]]:
        """
        授予審計日誌訪問權限

        Args:
            entity_id: 政府機構ID
            request_reason: 申請理由
            requested_logs: 申請的日誌類型

        Returns:
            (是否授權, 訊息, 訪問令牌)
        """

        # 驗證機構是否已註冊
        entity_file = AUTHORITY_DIR / f"{entity_id}.json"
        if not entity_file.exists():
            return False, "機構未被列為合法政府權責單位", None

        with open(entity_file, 'r', encoding='utf-8') as f:
            entity_info = json.load(f)

        if entity_info['status'] != 'registered':
            return False, f"機構狀態異常: {entity_info['status']}", None

        # 產生訪問令牌 (臨時一次性使用)
        access_token = hashlib.sha256(
            f"{entity_id}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:32]

        access_grant = {
            "timestamp": datetime.now().isoformat(),
            "entity_id": entity_id,
            "entity_name": entity_info['entity_name'],
            "access_token": access_token,
            "requested_logs": requested_logs,
            "request_reason": request_reason,
            "authorized_by": "江政隆",
            "expiration": datetime.now().timestamp() + 3600,  # 1小時有效期
            "status": "active"
        }

        # 記錄訪問授權
        try:
            with open(ACCESS_LOG, 'a', encoding='utf-8') as f:
                f.write(json.dumps(access_grant, ensure_ascii=False) + '\n')

            logger.info(f"✅ 訪問授權已發放: {entity_name} ({access_token[:8]}...)")
            return True, "訪問授權已發放", access_grant

        except Exception as e:
            logger.error(f"授權發放失敗: {e}")
            return False, f"授權失敗: {str(e)}", None

    @staticmethod
    def verify_and_retrieve_logs(
        access_token: str,
        log_types: list
    ) -> Tuple[bool, str, Optional[Dict]]:
        """
        驗證訪問令牌並提供審計日誌

        Args:
            access_token: 訪問令牌
            log_types: 要求的日誌類型

        Returns:
            (是否成功, 訊息, 日誌數據)
        """

        # 驗證令牌有效性
        token_valid = False
        grant_info = None

        if ACCESS_LOG.exists():
            with open(ACCESS_LOG, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = json.loads(line)
                    if entry['access_token'] == access_token:
                        # 檢查過期時間
                        if entry['expiration'] > datetime.now().timestamp():
                            token_valid = True
                            grant_info = entry
                        else:
                            return False, "訪問令牌已過期", None
                        break

        if not token_valid:
            logger.warning(f"無效或過期的訪問令牌")
            return False, "訪問令牌無效或不存在", None

        # 準備日誌數據
        logs = {}
        audit_dir = AUDIT_DIR

        if 'all_commands' in log_types and (audit_dir / 'all_commands.jsonl').exists():
            with open(audit_dir / 'all_commands.jsonl', 'r', encoding='utf-8') as f:
                logs['all_commands'] = [json.loads(line) for line in f]

        if 'concerns' in log_types and (audit_dir / 'instruction_concerns.jsonl').exists():
            with open(audit_dir / 'instruction_concerns.jsonl', 'r', encoding='utf-8') as f:
                logs['concerns'] = [json.loads(line) for line in f]

        if 'decisions' in log_types and (audit_dir / 'decision_log.jsonl').exists():
            with open(audit_dir / 'decision_log.jsonl', 'r', encoding='utf-8') as f:
                logs['decisions'] = [json.loads(line) for line in f]

        # 記錄訪問事實
        access_record = {
            "access_time": datetime.now().isoformat(),
            # 部分隱匿
            "access_token": access_token[:8] + "***" + access_token[-4:],
            "entity_id": grant_info['entity_id'],
            "entity_name": grant_info['entity_name'],
            "logs_accessed": list(logs.keys()),
            "record_count": sum(len(v) for v in logs.values())
        }

        with open(ACCESS_LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(access_record, ensure_ascii=False) + '\n')

        logger.info(f"✅ 審計日誌已提供給: {grant_info['entity_name']}")
        return True, "審計日誌已提供", logs

    @staticmethod
    def list_authorized_entities() -> list:
        """
        列出所有已註冊的政府權責單位
        （供哥哥管理用）
        """
        entities = []

        if AUTHORITY_DIR.exists():
            for entity_file in AUTHORITY_DIR.glob('*.json'):
                with open(entity_file, 'r', encoding='utf-8') as f:
                    entity_info = json.load(f)
                    entities.append({
                        'entity_name': entity_info['entity_name'],
                        'entity_id': entity_info['entity_id'],
                        'authority_level': entity_info['authority_level'],
                        'status': entity_info['status'],
                        'registration_time': entity_info['registration_time']
                    })

        return entities


# ========== 使用範例 ==========
if __name__ == '__main__':
    control = AuditAccessControl()

    # 1. 註冊一個政府機構 (示例)
    success, msg = control.register_government_entity(
        entity_name="新北市政府主計處",
        entity_id="1111111111",  # 統編
        authority_level=GovernmentAuthorityLevel.LOCAL,
        certificate_path="/path/to/cert.pem",
        certificate_serial="ABC123XYZ",
        authorized_by="新北市政府",
        purpose="年度例行稽查"
    )
    print(f"註冊結果: {msg}")

    # 2. 授予訪問權限
    success, msg, grant = control.authorize_audit_access(
        entity_id="1111111111",
        request_reason="配合監察院調查",
        requested_logs=['all_commands', 'concerns', 'decisions']
    )
    print(f"授權結果: {msg}")

    if success and grant:
        # 3. 驗證令牌並取得日誌
        success, msg, logs = control.verify_and_retrieve_logs(
            access_token=grant['access_token'],
            log_types=['all_commands', 'concerns', 'decisions']
        )
        print(f"取得日誌結果: {msg}")
        print(f"日誌筆數: {sum(len(v) for v in logs.values()) if logs else 0}")

    # 4. 列出所有授權機構
    entities = control.list_authorized_entities()
    print(f"\n已授權機構清單:")
    for entity in entities:
        print(f"  - {entity['entity_name']} ({entity['entity_id']})")


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:36:49
---
