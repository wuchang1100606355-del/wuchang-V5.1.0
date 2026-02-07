import paramiko
import time

HOST = 'localhost'
PORT = 33893
USER = 'o0930'
PASS = 'poiuY926926'

def check_ssh():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Connecting to {HOST}:{PORT}...")
        client.connect(HOST, PORT, USER, PASS, timeout=10)
        print("SSH Connected successfully.")
        
        # Check if the script exists
        stdin, stdout, stderr = client.exec_command('Test-Path "C:\\Users\\o0930\\wuchang_project\\scripts\\Deploy-Win-Odoo-Native.ps1"')
        result = stdout.read().decode().strip()
        print(f"Script exists: {result}")
        
        client.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check_ssh()
