#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
search_google_workspace_files.py

從 Google Workspace 組織空間中搜尋檔案

功能：
- 使用 Google Drive API 搜尋檔案
- 支援多種搜尋條件（檔名、類型、修改時間等）
- 顯示檔案詳細資訊
- 支援匯出搜尋結果
"""

import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError as e:
    print(f"❌ 缺少必要的 Google API 套件: {e}")
    print("請執行: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# Google Drive API 範圍
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# 認證檔案路徑
CREDENTIALS_FILE = BASE_DIR / "google_credentials.json"
TOKEN_FILE = BASE_DIR / "google_token.json"


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")


def authenticate_google_drive() -> Optional[object]:
    """認證 Google Drive API"""
    creds = None
    
    # 檢查是否有已儲存的 token
    if TOKEN_FILE.exists():
        try:
            with open(TOKEN_FILE, 'r', encoding='utf-8') as token:
                creds = Credentials.from_authorized_user_info(
                    json.load(token), SCOPES)
            log("已載入儲存的認證資訊", "OK")
        except Exception as e:
            log(f"載入認證資訊失敗: {e}", "WARN")
    
    # 如果沒有有效的認證，進行 OAuth 流程
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                log("已重新整理認證資訊", "OK")
            except Exception as e:
                log(f"重新整理認證資訊失敗: {e}", "ERROR")
                creds = None
        
        if not creds:
            if not CREDENTIALS_FILE.exists():
                log(f"認證檔案不存在: {CREDENTIALS_FILE}", "ERROR")
                log("請先建立 Google OAuth 2.0 認證檔案", "WARN")
                log("1. 前往 Google Cloud Console", "INFO")
                log("2. 建立 OAuth 2.0 憑證", "INFO")
                log("3. 下載憑證並儲存為 google_credentials.json", "INFO")
                return None
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_FILE), SCOPES)
                creds = flow.run_local_server(port=0)
                log("OAuth 認證成功", "OK")
            except Exception as e:
                log(f"OAuth 認證失敗: {e}", "ERROR")
                return None
        
        # 儲存認證資訊
        try:
            with open(TOKEN_FILE, 'w', encoding='utf-8') as token:
                token.write(creds.to_json())
            log("已儲存認證資訊", "OK")
        except Exception as e:
            log(f"儲存認證資訊失敗: {e}", "WARN")
    
    return creds


def build_search_query(
    name: Optional[str] = None,
    mime_type: Optional[str] = None,
    modified_after: Optional[datetime] = None,
    modified_before: Optional[datetime] = None,
    folder_id: Optional[str] = None,
    owner: Optional[str] = None,
    shared: Optional[bool] = None
) -> str:
    """建立搜尋查詢字串"""
    query_parts = []
    
    # 檔名搜尋
    if name:
        query_parts.append(f"name contains '{name}'")
    
    # MIME 類型
    if mime_type:
        query_parts.append(f"mimeType = '{mime_type}'")
    
    # 修改時間
    if modified_after:
        query_parts.append(f"modifiedTime >= '{modified_after.isoformat()}'")
    if modified_before:
        query_parts.append(f"modifiedTime <= '{modified_before.isoformat()}'")
    
    # 資料夾
    if folder_id:
        query_parts.append(f"'{folder_id}' in parents")
    
    # 擁有者
    if owner:
        query_parts.append(f"'{owner}' in owners")
    
    # 共享狀態
    if shared is not None:
        if shared:
            query_parts.append("sharedWithMe = true")
        else:
            query_parts.append("sharedWithMe = false")
    
    # 排除垃圾桶
    query_parts.append("trashed = false")
    
    return " and ".join(query_parts) if query_parts else "trashed = false"


def search_files(
    service: object,
    query: str,
    max_results: int = 100,
    fields: str = "nextPageToken, files(id, name, mimeType, modifiedTime, size, owners, webViewLink, shared)"
) -> List[Dict]:
    """搜尋檔案"""
    try:
        results = service.files().list(
            q=query,
            pageSize=min(max_results, 1000),
            fields=fields,
            orderBy="modifiedTime desc"
        ).execute()
        
        files = results.get('files', [])
        log(f"找到 {len(files)} 個檔案", "OK")
        return files
    
    except HttpError as error:
        log(f"搜尋檔案時發生錯誤: {error}", "ERROR")
        return []


def format_file_size(size_bytes: Optional[str]) -> str:
    """格式化檔案大小"""
    if not size_bytes:
        return "未知"
    
    try:
        size = int(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    except:
        return size_bytes


def format_datetime(dt_str: Optional[str]) -> str:
    """格式化日期時間"""
    if not dt_str:
        return "未知"
    
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return dt_str


def display_files(files: List[Dict]):
    """顯示檔案列表"""
    if not files:
        log("沒有找到符合條件的檔案", "WARN")
        return
    
    print("\n" + "=" * 100)
    print(f"找到 {len(files)} 個檔案")
    print("=" * 100)
    print()
    
    for i, file in enumerate(files, 1):
        print(f"【檔案 {i}】")
        print(f"  名稱: {file.get('name', '未知')}")
        print(f"  ID: {file.get('id', '未知')}")
        print(f"  類型: {file.get('mimeType', '未知')}")
        print(f"  大小: {format_file_size(file.get('size'))}")
        print(f"  修改時間: {format_datetime(file.get('modifiedTime'))}")
        
        owners = file.get('owners', [])
        if owners:
            owner_names = [o.get('displayName', o.get('emailAddress', '未知')) for o in owners]
            print(f"  擁有者: {', '.join(owner_names)}")
        
        print(f"  共享: {'是' if file.get('shared', False) else '否'}")
        
        web_link = file.get('webViewLink')
        if web_link:
            print(f"  連結: {web_link}")
        
        print()


def export_results(files: List[Dict], output_file: Path):
    """匯出搜尋結果"""
    try:
        results = {
            "搜尋時間": datetime.now().isoformat(),
            "檔案數量": len(files),
            "檔案列表": files
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        log(f"搜尋結果已匯出至: {output_file}", "OK")
    except Exception as e:
        log(f"匯出結果失敗: {e}", "ERROR")


def main():
    """主程式"""
    print("=" * 100)
    print("Google Workspace 檔案搜尋工具")
    print("=" * 100)
    print()
    
    # 認證
    log("正在認證 Google Drive API...", "INFO")
    creds = authenticate_google_drive()
    if not creds:
        log("認證失敗，無法繼續", "ERROR")
        return
    
    # 建立服務
    try:
        service = build('drive', 'v3', credentials=creds)
        log("Google Drive API 服務已建立", "OK")
    except Exception as e:
        log(f"建立服務失敗: {e}", "ERROR")
        return
    
    # 搜尋選項
    print("\n" + "-" * 100)
    print("搜尋選項")
    print("-" * 100)
    
    name = input("檔名關鍵字（留空跳過）: ").strip() or None
    mime_type = input("檔案類型（例如: application/pdf, image/jpeg，留空跳過）: ").strip() or None
    
    # 修改時間
    days_ago = input("修改時間：幾天內（留空跳過）: ").strip()
    modified_after = None
    if days_ago:
        try:
            days = int(days_ago)
            modified_after = datetime.now() - timedelta(days=days)
            log(f"搜尋 {days} 天內修改的檔案", "INFO")
        except ValueError:
            log("無效的天數，將跳過時間篩選", "WARN")
    
    # 資料夾 ID
    folder_id = input("資料夾 ID（留空搜尋全部）: ").strip() or None
    
    # 建立查詢
    query = build_search_query(
        name=name,
        mime_type=mime_type,
        modified_after=modified_after
    )
    
    log(f"搜尋查詢: {query}", "INFO")
    print()
    
    # 執行搜尋
    log("正在搜尋檔案...", "INFO")
    files = search_files(service, query, max_results=100)
    
    # 顯示結果
    display_files(files)
    
    # 匯出結果
    if files:
        export_choice = input("\n是否匯出搜尋結果？(y/n): ").strip().lower()
        if export_choice == 'y':
            output_file = BASE_DIR / "reports" / f"google_workspace_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            export_results(files, output_file)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程式已中斷")
        sys.exit(0)
    except Exception as e:
        log(f"發生未預期的錯誤: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)
