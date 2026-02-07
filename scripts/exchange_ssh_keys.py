import os
import paramiko
import socket
from pathlib import Path

# Configuration
TARGET_IP = "192.168.50.249"
TARGET_PORT = 22
PASSWORD = "Qwerty926"
USERS_TO_TRY = ["root", "admin", "wuchang", "ubuntu", "pi"]
LOCAL_USER = "wuchang"
LOCAL_USER_HOME = r"C:\Users\wuchang"
SSH_DIR = os.path.join(LOCAL_USER_HOME, ".ssh")
ID_RSA = os.path.join(SSH_DIR, "id_rsa")
ID_RSA_PUB = os.path.join(SSH_DIR, "id_rsa.pub")
AUTHORIZED_KEYS = os.path.join(SSH_DIR, "authorized_keys")

def setup_local_keys():
    print(f"🔧 Setting up SSH keys for local user '{LOCAL_USER}'...")
    
    if not os.path.exists(SSH_DIR):
        try:
            os.makedirs(SSH_DIR)
            print(f"   ✅ Created directory: {SSH_DIR}")
        except Exception as e:
            print(f"   ❌ Failed to create directory: {e}")
            return None

    if not os.path.exists(ID_RSA):
        print("   🔑 Generating new RSA key pair...")
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file(ID_RSA)
        with open(ID_RSA_PUB, "w") as f:
            f.write(f"{key.get_name()} {key.get_base64()} {LOCAL_USER}@{socket.gethostname()}")
        print("   ✅ Key pair generated.")
    else:
        print("   ℹ️  Key pair already exists.")

    # Ensure authorized_keys exists
    if not os.path.exists(AUTHORIZED_KEYS):
        with open(AUTHORIZED_KEYS, "w") as f:
            f.write("")
        print("   ✅ authorized_keys file created.")

    # Read public key
    with open(ID_RSA_PUB, "r") as f:
        pub_key = f.read().strip()
    
    return pub_key

def push_key_to_server(pub_key):
    print(f"\n🚀 Attempting to push public key to {TARGET_IP}...")
    
    for user in USERS_TO_TRY:
        print(f"   🔐 Trying login as '{user}'...")
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(TARGET_IP, port=TARGET_PORT, username=user, password=PASSWORD, timeout=5)
            
            print(f"   ✅ Login SUCCESSFUL as '{user}'!")
            
            # Create .ssh dir and add key
            cmd = f"mkdir -p ~/.ssh && echo '{pub_key}' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && chmod 700 ~/.ssh"
            stdin, stdout, stderr = client.exec_command(cmd)
            
            exit_status = stdout.channel.recv_exit_status()
            if exit_status == 0:
                print(f"   🎉 Public key successfully added to {user}@{TARGET_IP}")
                
                # Optionally: Get Server's public key (simple way: generate one if missing and cat it)
                print("   🔄 Attempting to retrieve Server's public key...")
                gen_cmd = "ssh-keygen -t rsa -N '' -f ~/.ssh/id_rsa -q 2>/dev/null; cat ~/.ssh/id_rsa.pub"
                stdin, stdout, stderr = client.exec_command(gen_cmd)
                server_pub_key = stdout.read().decode().strip()
                
                if server_pub_key and "ssh-rsa" in server_pub_key:
                    print(f"   📥 Received Server's public key.")
                    # Add to local authorized_keys
                    with open(AUTHORIZED_KEYS, "a") as f:
                        f.write(f"\n{server_pub_key}")
                    print(f"   ✅ Server's key added to local authorized_keys.")
                else:
                    print("   ⚠️  Could not retrieve Server's public key.")
                
            else:
                print(f"   ❌ Failed to add key: {stderr.read().decode()}")
            
            client.close()
            return True
            
        except Exception as e:
            print(f"   ⚠️  Failed: {e}")
            
    return False

def main():
    pub_key = setup_local_keys()
    if not pub_key:
        print("❌ Failed to setup local keys.")
        return

    print(f"\n📜 Local Public Key ({LOCAL_USER}):")
    print(f"{pub_key}")
    print("\n---------------------------------------------------")
    
    if push_key_to_server(pub_key):
        print("\n✅ Key Exchange Completed Successfully!")
    else:
        print("\n❌ Automatic Key Exchange Failed (Could not log in to Server).")
        print("👉 Please manually add the above Public Key to the Server's authorized_keys.")

if __name__ == "__main__":
    main()
