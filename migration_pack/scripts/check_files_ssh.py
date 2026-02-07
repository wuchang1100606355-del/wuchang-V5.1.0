import paramiko

HOST = 'localhost'
PORT = 33893
USER = 'o0930'
PASS = 'poiuY926926'

def list_files():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, PORT, USER, PASS, timeout=10)
        # Check directory listing
        cmd = 'dir C:\\Users\\o0930\\wuchang_project\\scripts'
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode('mbcs', errors='ignore')) # Use mbcs for Windows output
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_files()
