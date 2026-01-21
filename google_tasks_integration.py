#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
google_tasks_integration.py

Google Tasks API 整合模組

功能：
- 讀取 Google Tasks 任務
- 建立/更新/刪除任務
- 管理任務列表
- OAuth 2.0 認證管理

環境變數：
- WUCHANG_GOOGLE_CLIENT_ID：Google OAuth Client ID
- WUCHANG_GOOGLE_CLIENT_SECRET：Google OAuth Client Secret
- WUCHANG_GOOGLE_CREDENTIALS_PATH：OAuth 憑證儲存路徑（預設：./google_credentials.json）
- WUCHANG_GOOGLE_TOKEN_PATH：Access Token 儲存路徑（預設：./google_token.json）

合規聲明：
- 本系統已完成 Google for Nonprofits 驗證
- 所有 API 操作均遵循 Google API 使用規範
- 不儲存任何個資（可究責自然人除外）
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

BASE_DIR = Path(__file__).resolve().parent

# Google Tasks API 範圍
SCOPES = ['https://www.googleapis.com/auth/tasks']

# API 版本
TASKS_API_VERSION = 'v1'


@dataclass
class GoogleTask:
    """Google Task 資料結構"""
    id: Optional[str] = None
    title: str = ""
    notes: Optional[str] = None
    status: str = "needsAction"  # needsAction, completed
    due: Optional[str] = None  # RFC3339 格式
    completed: Optional[str] = None  # RFC3339 格式
    updated: Optional[str] = None
    self_link: Optional[str] = None
    position: Optional[str] = None
    parent: Optional[str] = None
    links: Optional[List[Dict[str, str]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        result = {}
        if self.id:
            result['id'] = self.id
        if self.title:
            result['title'] = self.title
        if self.notes:
            result['notes'] = self.notes
        if self.status:
            result['status'] = self.status
        if self.due:
            result['due'] = self.due
        if self.completed:
            result['completed'] = self.completed
        if self.updated:
            result['updated'] = self.updated
        if self.self_link:
            result['selfLink'] = self.self_link
        if self.position:
            result['position'] = self.position
        if self.parent:
            result['parent'] = self.parent
        if self.links:
            result['links'] = self.links
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GoogleTask:
        """從字典建立"""
        return cls(
            id=data.get('id'),
            title=data.get('title', ''),
            notes=data.get('notes'),
            status=data.get('status', 'needsAction'),
            due=data.get('due'),
            completed=data.get('completed'),
            updated=data.get('updated'),
            self_link=data.get('selfLink'),
            position=data.get('position'),
            parent=data.get('parent'),
            links=data.get('links'),
        )


@dataclass
class GoogleTaskList:
    """Google Task List 資料結構"""
    id: Optional[str] = None
    title: str = ""
    updated: Optional[str] = None
    self_link: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        result = {}
        if self.id:
            result['id'] = self.id
        if self.title:
            result['title'] = self.title
        if self.updated:
            result['updated'] = self.updated
        if self.self_link:
            result['selfLink'] = self.self_link
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GoogleTaskList:
        """從字典建立"""
        return cls(
            id=data.get('id'),
            title=data.get('title', ''),
            updated=data.get('updated'),
            self_link=data.get('selfLink'),
        )


class GoogleTasksIntegration:
    """Google Tasks API 整合類別"""
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        credentials_path: Optional[str] = None,
        token_path: Optional[str] = None,
    ):
        """
        初始化 Google Tasks 整合
        
        參數：
        - client_id: Google OAuth Client ID
        - client_secret: Google OAuth Client Secret
        - credentials_path: OAuth 憑證檔案路徑
        - token_path: Access Token 儲存路徑
        """
        if not GOOGLE_API_AVAILABLE:
            raise ImportError(
                "Google API Client Library 未安裝。請執行：pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
            )
        
        self.client_id = client_id or os.getenv("WUCHANG_GOOGLE_CLIENT_ID", "").strip()
        self.client_secret = client_secret or os.getenv("WUCHANG_GOOGLE_CLIENT_SECRET", "").strip()
        
        credentials_path = credentials_path or os.getenv(
            "WUCHANG_GOOGLE_CREDENTIALS_PATH",
            str(BASE_DIR / "google_credentials.json")
        )
        token_path = token_path or os.getenv(
            "WUCHANG_GOOGLE_TOKEN_PATH",
            str(BASE_DIR / "google_token.json")
        )
        
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        
        self.service = None
        self._credentials = None
    
    def _get_credentials(self) -> Credentials:
        """獲取或刷新 OAuth 憑證"""
        # 如果已有憑證且有效，直接返回
        if self._credentials and self._credentials.valid:
            return self._credentials
        
        # 嘗試從檔案載入 token
        if self.token_path.exists():
            try:
                self._credentials = Credentials.from_authorized_user_file(
                    str(self.token_path), SCOPES
                )
                if self._credentials.valid:
                    return self._credentials
                # Token 過期，嘗試刷新
                if self._credentials.expired and self._credentials.refresh_token:
                    self._credentials.refresh(Request())
                    self._save_token()
                    return self._credentials
            except Exception as e:
                print(f"載入 token 失敗: {e}")
        
        # 需要重新授權
        if not self.credentials_path.exists():
            raise FileNotFoundError(
                f"找不到 OAuth 憑證檔案: {self.credentials_path}\n"
                "請從 Google Cloud Console 下載 OAuth 2.0 憑證並儲存為 google_credentials.json"
            )
        
        # 執行 OAuth 流程
        flow = InstalledAppFlow.from_client_secrets_file(
            str(self.credentials_path), SCOPES
        )
        self._credentials = flow.run_local_server(port=0)
        self._save_token()
        return self._credentials
    
    def _save_token(self):
        """儲存 token 到檔案"""
        if self._credentials:
            with open(self.token_path, 'w', encoding='utf-8') as f:
                f.write(self._credentials.to_json())
    
    def _get_service(self):
        """獲取 Google Tasks API 服務實例"""
        if self.service is None:
            creds = self._get_credentials()
            self.service = build('tasks', TASKS_API_VERSION, credentials=creds)
        return self.service
    
    def list_task_lists(self) -> List[GoogleTaskList]:
        """列出所有任務列表"""
        try:
            service = self._get_service()
            results = service.tasklists().list(maxResults=100).execute()
            items = results.get('items', [])
            return [GoogleTaskList.from_dict(item) for item in items]
        except HttpError as e:
            raise Exception(f"列出任務列表失敗: {e}")
    
    def get_task_list(self, task_list_id: str) -> GoogleTaskList:
        """獲取特定任務列表"""
        try:
            service = self._get_service()
            result = service.tasklists().get(tasklist=task_list_id).execute()
            return GoogleTaskList.from_dict(result)
        except HttpError as e:
            raise Exception(f"獲取任務列表失敗: {e}")
    
    def create_task_list(self, title: str) -> GoogleTaskList:
        """建立新任務列表"""
        try:
            service = self._get_service()
            result = service.tasklists().insert(body={'title': title}).execute()
            return GoogleTaskList.from_dict(result)
        except HttpError as e:
            raise Exception(f"建立任務列表失敗: {e}")
    
    def list_tasks(self, task_list_id: str, show_completed: bool = False) -> List[GoogleTask]:
        """列出任務列表中的所有任務"""
        try:
            service = self._get_service()
            results = service.tasks().list(
                tasklist=task_list_id,
                showCompleted=show_completed,
                maxResults=100
            ).execute()
            items = results.get('items', [])
            return [GoogleTask.from_dict(item) for item in items]
        except HttpError as e:
            raise Exception(f"列出任務失敗: {e}")
    
    def get_task(self, task_list_id: str, task_id: str) -> GoogleTask:
        """獲取特定任務"""
        try:
            service = self._get_service()
            result = service.tasks().get(
                tasklist=task_list_id,
                task=task_id
            ).execute()
            return GoogleTask.from_dict(result)
        except HttpError as e:
            raise Exception(f"獲取任務失敗: {e}")
    
    def create_task(
        self,
        task_list_id: str,
        title: str,
        notes: Optional[str] = None,
        due: Optional[str] = None,
        parent: Optional[str] = None,
    ) -> GoogleTask:
        """建立新任務"""
        try:
            service = self._get_service()
            body = {'title': title}
            if notes:
                body['notes'] = notes
            if due:
                body['due'] = due
            if parent:
                body['parent'] = parent
            
            result = service.tasks().insert(
                tasklist=task_list_id,
                body=body
            ).execute()
            return GoogleTask.from_dict(result)
        except HttpError as e:
            raise Exception(f"建立任務失敗: {e}")
    
    def update_task(
        self,
        task_list_id: str,
        task_id: str,
        title: Optional[str] = None,
        notes: Optional[str] = None,
        status: Optional[str] = None,
        due: Optional[str] = None,
    ) -> GoogleTask:
        """更新任務"""
        try:
            service = self._get_service()
            # 先獲取現有任務
            existing = service.tasks().get(
                tasklist=task_list_id,
                task=task_id
            ).execute()
            
            # 更新欄位
            if title is not None:
                existing['title'] = title
            if notes is not None:
                existing['notes'] = notes
            if status is not None:
                existing['status'] = status
            if due is not None:
                existing['due'] = due
            
            result = service.tasks().update(
                tasklist=task_list_id,
                task=task_id,
                body=existing
            ).execute()
            return GoogleTask.from_dict(result)
        except HttpError as e:
            raise Exception(f"更新任務失敗: {e}")
    
    def delete_task(self, task_list_id: str, task_id: str) -> bool:
        """刪除任務"""
        try:
            service = self._get_service()
            service.tasks().delete(
                tasklist=task_list_id,
                task=task_id
            ).execute()
            return True
        except HttpError as e:
            raise Exception(f"刪除任務失敗: {e}")
    
    def complete_task(self, task_list_id: str, task_id: str) -> GoogleTask:
        """標記任務為完成"""
        return self.update_task(
            task_list_id=task_list_id,
            task_id=task_id,
            status='completed'
        )
    
    def get_task_by_url(self, task_url: str) -> Optional[GoogleTask]:
        """
        從 Google Tasks URL 獲取任務
        
        支援格式：
        - https://jules.google.com/task/{task_id}
        - https://tasks.google.com/embed/list/{task_list_id}/{task_id}
        """
        try:
            # 解析 URL 獲取 task_id
            task_id = None
            task_list_id = None
            
            if 'jules.google.com/task/' in task_url:
                task_id = task_url.split('jules.google.com/task/')[-1].split('?')[0].split('#')[0]
            elif 'tasks.google.com/embed/list/' in task_url:
                parts = task_url.split('tasks.google.com/embed/list/')[-1].split('/')
                if len(parts) >= 2:
                    task_list_id = parts[0]
                    task_id = parts[1].split('?')[0].split('#')[0]
            
            if not task_id:
                return None
            
            # 如果沒有 task_list_id，需要搜尋所有列表
            if not task_list_id:
                task_lists = self.list_task_lists()
                for task_list in task_lists:
                    try:
                        task = self.get_task(task_list.id, task_id)
                        return task
                    except Exception:
                        continue
                return None
            else:
                return self.get_task(task_list_id, task_id)
        except Exception as e:
            raise Exception(f"從 URL 獲取任務失敗: {e}")


# 全局實例
_google_tasks_integration: Optional[GoogleTasksIntegration] = None


def get_google_tasks_integration() -> GoogleTasksIntegration:
    """獲取 Google Tasks 整合實例"""
    global _google_tasks_integration
    if _google_tasks_integration is None:
        _google_tasks_integration = GoogleTasksIntegration()
    return _google_tasks_integration


def main():
    """測試主函數"""
    if not GOOGLE_API_AVAILABLE:
        print("錯誤：Google API Client Library 未安裝")
        print("請執行：pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return
    
    try:
        integration = get_google_tasks_integration()
        
        # 列出任務列表
        print("任務列表：")
        task_lists = integration.list_task_lists()
        for task_list in task_lists:
            print(f"  - {task_list.title} (ID: {task_list.id})")
        
        # 如果有任務列表，列出第一個列表的任務
        if task_lists:
            first_list = task_lists[0]
            print(f"\n任務列表 '{first_list.title}' 的任務：")
            tasks = integration.list_tasks(first_list.id)
            for task in tasks:
                status = "✓" if task.status == "completed" else "○"
                print(f"  {status} {task.title}")
                if task.notes:
                    print(f"     備註: {task.notes}")
                if task.due:
                    print(f"     到期: {task.due}")
    except Exception as e:
        print(f"錯誤: {e}")


if __name__ == "__main__":
    main()
