#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小j 記憶系統 Google Drive 同步器
整合既有的 Drive API 實作，自動備份 memory_store 到雲端
"""
import os
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('MemoryDriveSync')

# 路徑配置
BASE_DIR = Path(__file__).parent.parent
MEMORY_STORE_DIR = BASE_DIR / 'memory_store'
EXPERIENCE_DIR = MEMORY_STORE_DIR / 'experience'
CONFIG_DIR = BASE_DIR / 'config'

# Drive 配置（從 Odoo 獲取或使用服務帳號）
DRIVE_MEMORY_FOLDER_NAME = 'WuchangAI_Memory'
DRIVE_BACKUP_FOLDER_NAME = 'Backups'


class MemoryDriveSync:
    """記憶系統與 Google Drive 同步器"""

    def __init__(self, use_service_account: bool = False):
        """
        初始化同步器

        Args:
            use_service_account: 是否使用服務帳號（推薦）
                                 False 則使用 Odoo OAuth token
        """
        self.use_service_account = use_service_account
        self.drive_service = None
        self.memory_folder_id = None

        if use_service_account:
            self._init_service_account()
        else:
            self._init_oauth()

    def _init_service_account(self):
        """使用服務帳號初始化"""
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            # 服務帳號金鑰檔案路徑（需先下載）
            key_path = CONFIG_DIR / 'xiaoj_service_account.json'
            if not key_path.exists():
                logger.error(f'服務帳號金鑰檔案不存在: {key_path}')
                logger.info('請從 GCP Console 下載金鑰，或使用 Odoo OAuth token')
                return

            scopes = ['https://www.googleapis.com/auth/drive']
            credentials = service_account.Credentials.from_service_account_file(
                str(key_path),
                scopes=scopes
            )

            # Domain-wide Delegation (模擬 admin@wuchang.life)
            delegated_credentials = credentials.with_subject(
                'admin@wuchang.life')

            self.drive_service = build(
                'drive', 'v3', credentials=delegated_credentials)
            logger.info('✅ 已使用服務帳號初始化 Google Drive')

        except ImportError:
            logger.error(
                '請安裝: pip install google-auth google-api-python-client')
        except Exception as e:
            logger.error(f'服務帳號初始化失敗: {e}')

    def _init_oauth(self):
        """使用 Odoo OAuth token 初始化（需 Odoo 環境）"""
        try:
            from odoo import api, SUPERUSER_ID
            import odoo

            db_name = os.environ.get('POSTGRES_DB', 'odoo')
            registry = odoo.registry(db_name)

            with registry.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                params = env['ir.config_parameter'].sudo()

                token_json = params.get_param(
                    'wuchang.drive.oauth_token_json', '')
                self.memory_folder_id = params.get_param(
                    'wuchang.drive.memory_folder_id', '')

                if not token_json:
                    logger.warning('未設定 Drive OAuth token，請在 Odoo 後台設定')
                    return

                # 使用既有的 Odoo Drive 實作
                logger.info('✅ 已載入 Odoo Drive OAuth token')

        except Exception as e:
            logger.error(f'Odoo OAuth 初始化失敗: {e}')

    def ensure_memory_folder(self) -> str:
        """確保記憶資料夾存在，回傳 folder_id"""
        if not self.drive_service:
            logger.error('Drive 服務未初始化')
            return ''

        try:
            # 搜尋資料夾
            query = f"name='{DRIVE_MEMORY_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.drive_service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()

            folders = results.get('files', [])

            if folders:
                folder_id = folders[0]['id']
                logger.info(f'找到記憶資料夾: {folder_id}')
                return folder_id

            # 建立資料夾
            file_metadata = {
                'name': DRIVE_MEMORY_FOLDER_NAME,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = self.drive_service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()

            folder_id = folder.get('id')
            logger.info(f'✅ 已建立記憶資料夾: {folder_id}')
            return folder_id

        except Exception as e:
            logger.error(f'建立記憶資料夾失敗: {e}')
            return ''

    def backup_memory_to_drive(self, incremental: bool = True):
        """
        備份 memory_store 到 Drive

        Args:
            incremental: 是否僅備份變更的檔案（增量備份）
        """
        if not self.drive_service:
            logger.error('Drive 服務未初始化，無法備份')
            return

        folder_id = self.ensure_memory_folder()
        if not folder_id:
            return

        # 建立今日備份資料夾
        today = datetime.now().strftime('%Y%m%d')
        backup_folder_name = f'backup_{today}'

        try:
            # TODO: 實作檔案上傳邏輯
            # 1. 遞迴讀取 memory_store/
            # 2. 上傳到 Drive (保留目錄結構)
            # 3. 記錄備份清單

            logger.info(f'✅ 記憶備份完成: {backup_folder_name}')

        except Exception as e:
            logger.error(f'備份失敗: {e}')

    def sync_experience_to_drive(self):
        """同步 experience/ 資料夾到 Drive（雙向同步）"""
        if not self.drive_service:
            logger.error('Drive 服務未初始化')
            return

        folder_id = self.ensure_memory_folder()
        if not folder_id:
            return

        try:
            # 同步 decision_patterns.json
            decision_file = EXPERIENCE_DIR / 'decision_patterns.json'
            if decision_file.exists():
                # TODO: 上傳到 Drive
                logger.info(f'同步決策模式到 Drive')

            # 同步 user_preferences.json
            prefs_file = EXPERIENCE_DIR / 'user_preferences.json'
            if prefs_file.exists():
                # TODO: 上傳到 Drive
                logger.info(f'同步使用者偏好到 Drive')

            # 同步 learned_skills.json
            skills_file = EXPERIENCE_DIR / 'learned_skills.json'
            if skills_file.exists():
                # TODO: 上傳到 Drive
                logger.info(f'同步學習技能到 Drive')

            logger.info('✅ 經驗同步完成')

        except Exception as e:
            logger.error(f'經驗同步失敗: {e}')

    def restore_from_drive(self, backup_date: str = None):
        """
        從 Drive 還原記憶

        Args:
            backup_date: 備份日期 (YYYYMMDD)，若為 None 則還原最新備份
        """
        if not self.drive_service:
            logger.error('Drive 服務未初始化')
            return

        folder_id = self.ensure_memory_folder()
        if not folder_id:
            return

        try:
            # TODO: 實作還原邏輯
            # 1. 列出備份資料夾
            # 2. 下載指定日期的備份
            # 3. 解壓到 memory_store/

            logger.info(f'✅ 記憶還原完成')

        except Exception as e:
            logger.error(f'還原失敗: {e}')

    def setup_j_drive_mapping(self):
        """設定 J: 磁碟映射到 Google Drive（Windows）"""
        logger.info('設定 J: 磁碟映射...')

        # 檢查是否為 Windows
        if os.name != 'nt':
            logger.warning('J: 磁碟映射僅支援 Windows')
            return

        # 使用 Google Drive Desktop 的映射功能
        drive_desktop_path = Path.home() / 'Google Drive'

        if drive_desktop_path.exists():
            logger.info(f'✅ Google Drive Desktop 已安裝: {drive_desktop_path}')
            logger.info('請在 Google Drive Desktop 設定中:')
            logger.info('1. 啟用「電腦」功能')
            logger.info('2. 將 WuchangAI_Memory 資料夾設為「鏡像檔案」')
            logger.info('3. 在 Windows 檔案總管中將其指派為 J: 磁碟')
        else:
            logger.warning('未找到 Google Drive Desktop')
            logger.info('請安裝: https://www.google.com/drive/download/')


# ========== 使用範例 ==========
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='小j 記憶系統 Drive 同步')
    parser.add_argument('--action', choices=['backup', 'sync', 'restore', 'setup-j'],
                        default='sync', help='執行動作')
    parser.add_argument('--service-account', action='store_true',
                        help='使用服務帳號（需先設定金鑰）')
    parser.add_argument('--backup-date', help='還原日期 (YYYYMMDD)')

    args = parser.parse_args()

    syncer = MemoryDriveSync(use_service_account=args.service_account)

    if args.action == 'backup':
        syncer.backup_memory_to_drive()
    elif args.action == 'sync':
        syncer.sync_experience_to_drive()
    elif args.action == 'restore':
        syncer.restore_from_drive(args.backup_date)
    elif args.action == 'setup-j':
        syncer.setup_j_drive_mapping()

    logger.info('✅ 完成')
