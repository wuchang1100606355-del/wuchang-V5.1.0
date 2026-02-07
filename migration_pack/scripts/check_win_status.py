import paramiko
import sys

HOST = 'localhost'
PORT = 33893
USER = 'o0930'
PASS = 'poiuY926926'

def check_status():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=10)
        
        # Check running processes
        print("Checking running processes on Win-VM...")
        stdin, stdout, stderr = ssh.exec_command("powershell \"Get-Process | Where-Object {$_.ProcessName -match 'choco|python|git|postgres|node'} | Select-Object ProcessName, Id, CPU\"")
        processes = stdout.read().decode('utf-8', errors='ignore')
        
        if processes.strip():
            print(f"Active installation processes found:\n{processes}")
        else:
            print("No specific installation processes found via PowerShell.")

        # Check directory progress
        print("Checking installation directories...")
        stdin, stdout, stderr = ssh.exec_command("dir C:\\Users\\o0930\\odoo")
        output = stdout.read().decode('utf-8', errors='ignore')
        if "File Not Found" not in output and "Volume" in output:
             print("Odoo directory exists (Git clone started/finished).")
        else:
             print("Odoo directory not found yet.")

            
        ssh.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check_status()
