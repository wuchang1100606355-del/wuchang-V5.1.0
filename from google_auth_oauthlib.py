from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']  # 或 'https://www.googleapis.com/auth/tasks'
flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret.json', SCOPES)
auth_url, _ = flow.authorization_url(prompt='consent')

print("請在瀏覽器開啟此連結授權：", auth_url)