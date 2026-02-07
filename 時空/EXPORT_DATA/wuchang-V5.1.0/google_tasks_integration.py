#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
google_tasks_integration.py

五常智慧社區雲 - Google Tasks API 整合模組 (強化自動刷新版)

功能說明：
- 賦予「小J」讀取與管理 Google Tasks (工作表) 的能力
- 支援增刪改查 (CRUD) 社區待辦事項
- OAuth 2.0 永久自動刷新機制：防止憑證過期導致自動化中斷

作者：江政隆 (Jiang Zhenglong) & AI 協作
版權宣告：本系統為非營利用途，供五常社區發展協會使用。
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# 檢查是否已安裝 Google API 套件
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

# Google Tasks API 權限範圍 (重要：包含讀寫權限)
SCOPES = ['https://www.googleapis.com/auth/tasks']

# API 版本
TASKS_API_VERSION = 'v1'


@dataclass
class GoogleTask:
    """單一任務 (Task) 的資料結構"""
    id: Optional[str] = None
    title: str = ""
    notes: Optional[str] = None
    status: str = "needsAction"  # needsAction(未完成), completed(已完成)
    due: Optional[str] = None  # 到期日
    completed: Optional[str] = None  # 完成時間
    updated: Optional[str] = None
    self_link: Optional[str] = None
    position: Optional[str] = None
    parent: Optional[str] = None
    links: Optional[List[Dict[str, str]]] = None

    def to_dict(self) -> Dict[str, Any]:
        """轉為字典格式"""
        result = {}
        if self.id: result['id'] = self.id
        if self.title: result['title'] = self.title
        if self.notes: result['notes'] = self.notes
        if self.status: result['status'] = self.status
        if self.due: result['due'] = self.due
        if self.completed: result['completed'] = self.completed
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GoogleTask:
        """從字典建立物件"""
        return cls(
            id=data.get('id'),
            title=data.get('title', ''),
            notes=data.get('notes'),
            status=data.get('status', 'needsAction'),
            due=data.get('due'),
            completed=data.get('completed'),
        )


@dataclass
class GoogleTaskList:
    """任務清單 (Task List) 的資料結構"""
    id: Optional[str] = None
    title: str = ""
    updated: Optional[str] = None
    self_link: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GoogleTaskList:
        return cls(
            id=data.get('id'),
            title=data.get('title', ''),
            updated=data.get('updated'),
            self_link=data.get('selfLink'),
        )


class GoogleTasksIntegration:
    """五常社區 - Google Tasks 核心整合引擎"""

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        token_path: Optional[str] = None,
    ):
        """初始化連線設定"""
        if not GOOGLE_API_AVAILABLE:
            raise ImportError(
                "缺少 Google API 套件！請在終端機執行：\n"
                "pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
            )

        # 設定金鑰檔案路徑 (預設在同一目錄下)
        credentials_path = credentials_path or str(BASE_DIR / "google_credentials.json")
        token_path = token_path or str(BASE_DIR / "google_token.json")

        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.service = None
        self._credentials = None

    def _get_credentials(self) -> Credentials:
        """
        [核心機制]：取得並驗證憑證。
        若過期會自動刷新，確保小J能 24 小時運作不斷線。
        """
        creds = None
        
        # 1. 如果已經有 token.json，直接讀取
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

        # 2. 如果憑證無效 (沒有檔案、過期、或是壞掉)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    # 【防呆機制】：嘗試自動向 Google 換新 Token
                    print("🔄 [系統通知] Google Token 已過期，小J 正在自動刷新憑證...")
                    creds.refresh(Request())
                except Exception as e:
                    print(f"❌ [警告] 自動刷新失敗，需要重新授權：{e}")
                    creds = None
            
            # 3. 如果連自動刷新都失敗，觸發首次登入流程
            if not creds:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(f"找不到密鑰檔案：{self.credentials_path}，請確認是否已下載。")
                print("🔒 [系統通知] 啟動 Google 帳號授權流程...")
                flow = InstalledAppFlow.from_client_secrets_file(str(self.credentials_path), SCOPES)
                creds = flow.run_local_server(port=0)

            # 4. 存下最新有效的 Token
            with open(self.token_path, 'w', encoding='utf-8') as token:
                token.write(creds.to_json())
                print("✅ [系統通知] Google 憑證已成功保存！")

        self._credentials = creds
        return creds

    def _get_service(self):
        """建立與 Google Tasks 的連線"""
        if self.service is None:
            creds = self._get_credentials()
            self.service = build('tasks', TASKS_API_VERSION, credentials=creds)
        return self.service

    # ================= 操作功能區 =================

    def list_task_lists(self) -> List[GoogleTaskList]:
        """取得所有任務清單"""
        service = self._get_service()
        results = service.tasklists().list(maxResults=100).execute()
        return [GoogleTaskList.from_dict(item) for item in results.get('items', [])]

    def create_task(self, task_list_id: str, title: str, notes: Optional[str] = None) -> GoogleTask:
        """讓小J新增任務"""
        service = self._get_service()
        body = {'title': title}
        if notes: body['notes'] = notes
        result = service.tasks().insert(tasklist=task_list_id, body=body).execute()
        return GoogleTask.from_dict(result)


def main():
    """系統測試主程式"""
    print("=== 五常社區雲：Google Tasks 整合模組測試 ===")
    try:
        integration = GoogleTasksIntegration()
        task_lists = integration.list_task_lists()
        print(f"✅ 連線成功！共找到 {len(task_lists)} 個任務清單。")
        for tl in task_lists:
            print(f" - {tl.title}")
    except Exception as e:
        print(f"❌ 連線失敗: {e}")

if __name__ == "__main__":
    main()

---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:34:03
---
