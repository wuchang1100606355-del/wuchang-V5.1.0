import paramiko
from scp import SCPClient
import os

HOST = 'localhost'
PORT = 33893
USER = 'o0930'
PASS = 'poiuY926926'

def upload_script():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=10)
        print("SSH Connected.")
        
        with SCPClient(ssh.get_transport()) as scp:
            local_path = r'C:\wuchang V5.0.0\scripts\Deploy-Win-Odoo-Native.ps1'
            remote_path = 'wuchang_project/scripts/Deploy-Win-Odoo-Native.ps1'
            print(f"Uploading {local_path} to {remote_path}...")
            scp.put(local_path, remote_path=remote_path)
            print("Upload complete.")
            
        ssh.close()
    except Exception as e:
        print(f"Upload failed: {e}")

if __name__ == "__main__":
    upload_script()
