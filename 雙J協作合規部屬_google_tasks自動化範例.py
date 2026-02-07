from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 1. 設定 Google Tasks 權限範圍
SCOPES = ['https://www.googleapis.com/auth/tasks']

# 2. 取得認證
def get_credentials():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json', SCOPES)
    creds = flow.run_local_server(port=0)
    return creds

# 3. 建立 Google Tasks 服務
def get_service():
    creds = get_credentials()
    service = build('tasks', 'v1', credentials=creds)
    return service

# 4. 建立部屬合規任務清單
def create_tasklist(service, title):
    tasklist = service.tasklists().insert(body={'title': title}).execute()
    return tasklist['id']

# 5. 新增部屬任務
def add_task(service, tasklist_id, title, notes=None):
    task = {'title': title}
    if notes:
        task['notes'] = notes
    service.tasks().insert(tasklist=tasklist_id, body=task).execute()

if __name__ == '__main__':
    service = get_service()
    tasklist_id = create_tasklist(service, '雙J協作合規部屬')
    部屬步驟 = [
        ('DNS 設定', 'Cloudflare 託管、A/CNAME、Google 驗證'),
        ('SSL 憑證', 'Cloudflare SSL、Let’s Encrypt'),
        ('權限控管', 'API Key/JWT、管理員審核'),
        ('日誌管理', '自動日誌收集、Google Sheet 備份'),
        ('稽核與追蹤', 'Google Tasks 任務同步、雙J審核')
    ]
    for title, notes in 部屬步驟:
        add_task(service, tasklist_id, title, notes)
    print("部屬合規任務已自動建立！")
