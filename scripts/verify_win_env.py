import paramiko
import sys

HOST = 'localhost'
PORT = 33893
USER = 'o0930'
PASS = 'poiuY926926'

def verify_env():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, PORT, USER, PASS, timeout=10)
        print("SSH Connected. Checking tools...")
        
        # Check Python
        stdin, stdout, stderr = client.exec_command('python --version')
        py_ver = stdout.read().decode().strip() or stderr.read().decode().strip()
        print(f"Python: {py_ver}")
        
        # Check Git
        stdin, stdout, stderr = client.exec_command('git --version')
        git_ver = stdout.read().decode().strip() or stderr.read().decode().strip()
        print(f"Git: {git_ver}")
        
        # Check Project Dir
        stdin, stdout, stderr = client.exec_command('dir C:\\Users\\o0930\\wuchang_project')
        dir_out = stdout.read().decode('mbcs', errors='ignore').strip() # Use mbcs for Windows CMD output
        if "wuchang_os" in dir_out:
            print("Project files found.")
        else:
            print("Project files verification failed (might be encoding issue or missing).")

        client.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    verify_env()
