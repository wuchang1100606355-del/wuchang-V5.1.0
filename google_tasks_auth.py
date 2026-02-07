from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']  # 或 'https://www.googleapis.com/auth/tasks'

def main():
    creds = None
    if os.path.exists('token.json'):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('tasks', 'v1', credentials=creds)
    results = service.tasklists().list(maxResults=10).execute()
    items = results.get('items', [])

    if not items:
        print('No task lists found.')
    else:
        print('Task lists:')
        for item in items:
            print(u'{0} ({1})'.format(item['title'], item['id']))

if __name__ == '__main__':
    main()
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os

SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']  # 或 'https://www.googleapis.com/auth/tasks'

def main():
    creds = None
    # 友善提示：檢查 client_secret.json 是否存在
    if not os.path.exists('client_secret.json'):
        print('\n[錯誤] 找不到 client_secret.json！\n請確認檔案已放在本程式同一資料夾，且檔名正確。')
        print('（如有副檔名請移除，檔名必須完全為 client_secret.json）')
        input('請按 Enter 結束...')
        return

    if os.path.exists('token.json'):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w', encoding='utf-8') as token:
            token.write(creds.to_json())

    service = build('tasks', 'v1', credentials=creds)
    results = service.tasklists().list(maxResults=10).execute()
    items = results.get('items', [])

    if not items:
        print('No task lists found.')
    else:
        print('Task lists:')
        for item in items:
            print('{0} ({1})'.format(item['title'], item['id']))

    # 預留自動化擴充點
    # 例如：自動同步、定時備份、寫入資料庫等
    # 只要在這裡加功能即可

if __name__ == '__main__':
    main()
