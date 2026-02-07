import paramiko
import time

TARGET_IP = "192.168.50.249"
PORT = 22
PASSWORD = "Qwerty926"
USERNAMES = ["root", "admin", "odoo", "user", "ubuntu"]

def try_ssh_login(username):
    print(f"🔐 Trying login as '{username}'...")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(TARGET_IP, port=PORT, username=username, password=PASSWORD, timeout=5, banner_timeout=5)
        
        print(f"✅ Login SUCCESSFUL with user: {username}")
        
        # Run a simple command
        stdin, stdout, stderr = client.exec_command('whoami && uname -a')
        print(f"   Output: {stdout.read().decode().strip()}")
        
        client.close()
        return True
    except paramiko.AuthenticationException:
        print(f"❌ Authentication failed for user: {username}")
    except Exception as e:
        print(f"⚠️ Connection error: {e}")
    
    return False

print(f"🚀 Attempting SSH Login to {TARGET_IP}")

success = False
for user in USERNAMES:
    if try_ssh_login(user):
        success = True
        break

if not success:
    print("\n❌ All login attempts failed.")
else:
    print("\n🎉 Access verified.")
