import paramiko
import sys
import time

HOST = 'localhost'
PORT = 33893
USER = 'o0930'
PASS = 'poiuY926926'

def install_odoo_remote():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=10)
        print("SSH Connected. Starting installation...")
        
        # We use Start-Process to run in background and redirect output
        # But for simplicity, we can just run it directly. 
        # However, standard SSH exec_command waits for completion if we read stdout.
        # Given the script might take long, we want to see output.
        
        # Let's run it and stream output.
        stdin, stdout, stderr = ssh.exec_command(r'powershell -ExecutionPolicy Bypass -File C:\Users\o0930\wuchang_project\scripts\Deploy-Win-Odoo-Native.ps1')
        
        # Stream output
        while True:
            line = stdout.readline()
            if not line:
                break
            print(line.strip())
            
        # Check stderr
        err = stderr.read().decode('utf-8')
        if err:
            print(f"Errors:\n{err}")
            
        ssh.close()
    except Exception as e:
        print(f"Remote execution failed: {e}")

if __name__ == "__main__":
    install_odoo_remote()
