import base64
import time
from email.mime.text import MIMEText
from typing import Callable

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SERVICE_ACCOUNT_FILE = "config/gcp-sa.json"
IMPERSONATE_USER = None  # set to user email if using domain-wide delegation
SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/gmail.send",
]


def retry(fn: Callable, *args, retries: int = 3, backoff: int = 1, **kwargs):
    for i in range(retries):
        try:
            return fn(*args, **kwargs)
        except HttpError:
            if i == retries - 1:
                raise
            time.sleep(backoff * (2 ** i))


def get_creds():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    if IMPERSONATE_USER:
        creds = creds.with_subject(IMPERSONATE_USER)
    return creds


def test_drive(creds):
    svc = build("drive", "v3", credentials=creds)
    resp = retry(svc.files().list, pageSize=10, fields="files(id,name)")
    files = resp.get("files", [])
    print("Drive OK, first 10:")
    for f in files:
        print(f" - {f['name']} ({f['id']})")


def test_sheets(creds):
    svc = build("sheets", "v4", credentials=creds)
    sheet = retry(
        svc.spreadsheets().create, body={"properties": {
            "title": "API Test Sheet"}}
    )
    sid = sheet["spreadsheetId"]
    retry(
        svc.spreadsheets().values().append,
        spreadsheetId=sid,
        range="A1",
        valueInputOption="RAW",
        body={"values": [["hello", "world", "test"]]},
    )
    print(f"Sheets OK, created and wrote {sid}")
    return sid


def test_gmail(creds, to_email: str):
    svc = build("gmail", "v1", credentials=creds)
    msg = MIMEText("This is a Gmail API test mail from service account.")
    msg["to"] = to_email
    msg["from"] = to_email if IMPERSONATE_USER is None else IMPERSONATE_USER
    msg["subject"] = "Gmail API test"
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    retry(svc.users().messages().send, userId="me", body={"raw": raw})
    print(f"Gmail OK, sent to {to_email}")


if __name__ == "__main__":
    creds = get_creds()
    test_drive(creds)
    sid = test_sheets(creds)
    test_gmail(creds, to_email="your_email@example.com")
    print("== DONE: Drive/Sheets/Gmail test ==")
