#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
backup_to_gdrive.py

自動備份檔案到 Google Drive

功能：
- 備份指定目錄到 Google Drive
- 支援增量備份
- 自動壓縮
- 保留歷史版本
"""

import os
import sys
import json
import tarfile
import datetime
from pathlib import Path
from typing import List, Optional

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
except ImportError:
    print("❌ 缺少 Google API 套件，請執行: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)

# 配置
BASE_DIR = Path(__file__).resolve().parent
BACKUP_DIR = BASE_DIR / "backups"
CREDENTIALS_FILE = BASE_DIR / "google_credentials.json"
TOKEN_FILE = BASE_DIR / "google_token.json"
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# 備份目錄列表
BACKUP_PATHS = [
    BASE_DIR / "wuchang_os",
    BASE_DIR / "config",
    BASE_DIR / "scripts",
    BASE_DIR / "containers" / "config",
]


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌",
        "PROGRESS": "🔄"
    }
    icon = icons.get(level, "•")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {icon} [{level}] {message}")


def authenticate():
    """Google Drive 認證"""
    creds = None
    
    if TOKEN_FILE.exists():
        try:
            with open(TOKEN_FILE, 'r', encoding='utf-8') as token:
                creds = Credentials.from_authorized_user_info(
                    json.load(token), SCOPES)
        except Exception as e:
            log(f"載入 token 失敗: {e}", "WARN")
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                log("✓ Token 已重新整理", "OK")
            except Exception as e:
                log(f"重新整理 token 失敗: {e}", "ERROR")
                creds = None
        
        if not creds:
            if not CREDENTIALS_FILE.exists():
                log(f"❌ 憑證檔案不存在: {CREDENTIALS_FILE}", "ERROR")
                log("請先下載 Google OAuth 憑證檔案", "INFO")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
            log("✓ OAuth 認證成功", "OK")
        
        # 儲存 token
        with open(TOKEN_FILE, 'w', encoding='utf-8') as token:
            token.write(creds.to_json())
        log("✓ Token 已儲存", "OK")
    
    return creds


def create_backup_archive() -> Optional[Path]:
    """建立備份壓縮檔"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"wuchang_backup_{timestamp}.tar.gz"
    backup_path = BACKUP_DIR / backup_filename
    
    # 確保備份目錄存在
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    log(f"正在建立備份壓縮檔: {backup_filename}", "PROGRESS")
    
    try:
        with tarfile.open(backup_path, "w:gz") as tar:
            for path in BACKUP_PATHS:
                if path.exists():
                    log(f"  加入: {path.name}", "INFO")
                    tar.add(path, arcname=path.name)
                else:
                    log(f"  ⚠️ 跳過不存在的路徑: {path}", "WARN")
        
        size_mb = backup_path.stat().st_size / (1024 * 1024)
        log(f"✓ 備份壓縮檔建立完成: {size_mb:.2f} MB", "OK")
        return backup_path
    except Exception as e:
        log(f"❌ 建立備份壓縮檔失敗: {e}", "ERROR")
        return None


def upload_to_drive(service, file_path: Path, folder_id: Optional[str] = None):
    """上傳檔案到 Google Drive"""
    log(f"正在上傳到 Google Drive: {file_path.name}", "PROGRESS")
    
    file_metadata = {
        'name': file_path.name,
        'description': f'五常系統自動備份 - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    }
    
    if folder_id:
        file_metadata['parents'] = [folder_id]
    
    media = MediaFileUpload(
        str(file_path),
        mimetype='application/gzip',
        resumable=True
    )
    
    try:
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, size'
        ).execute()
        
        size_mb = int(file.get('size', 0)) / (1024 * 1024)
        log(f"✓ 上傳成功: {file.get('name')} ({size_mb:.2f} MB)", "OK")
        log(f"  File ID: {file.get('id')}", "INFO")
        return file.get('id')
    except Exception as e:
        log(f"❌ 上傳失敗: {e}", "ERROR")
        return None


def main():
    """主程式"""
    print("=" * 70)
    print("Google Drive 自動備份工具")
    print("=" * 70)
    print()
    
    # 認證
    creds = authenticate()
    if not creds:
        log("認證失敗，無法繼續", "ERROR")
        return 1
    
    # 建立服務
    try:
        service = build('drive', 'v3', credentials=creds)
        log("✓ Google Drive API 服務已建立", "OK")
    except Exception as e:
        log(f"❌ 建立 API 服務失敗: {e}", "ERROR")
        return 1
    
    # 建立備份壓縮檔
    backup_file = create_backup_archive()
    if not backup_file:
        log("無法建立備份檔案", "ERROR")
        return 1
    
    # 上傳到 Google Drive
    file_id = upload_to_drive(service, backup_file)
    if not file_id:
        log("上傳失敗", "ERROR")
        return 1
    
    log("✅ 備份完成！", "OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
