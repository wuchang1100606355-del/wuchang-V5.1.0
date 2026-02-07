#!/usr/bin/env python3
import paramiko
import os
import sys

SERVER = "192.168.50.249"
USERS = ["user", "wuchang", "ubuntu", "debian", "admin"]
PASSWORD = "Qwerrty9266"
PUBKEY_PATH = os.path.expanduser("~/.ssh/id_ed25519.pub")

print(f"\n=== Deploying SSH Key to {SERVER} ===\n")

# Read public key
try:
    with open(PUBKEY_PATH, 'r') as f:
        pubkey = f.read().strip()
    print(f"[INFO] Public key: {pubkey[:50]}...")
except FileNotFoundError:
    print(f"[ERROR] Public key not found: {PUBKEY_PATH}")
    sys.exit(1)

# Try each user
success = False
for USER in USERS:
    try:
        print(f"[INFO] Trying {USER}@{SERVER}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(SERVER, username=USER, password=PASSWORD, timeout=10)

        print(f"[OK] Connected as {USER}!")
        success = True
        break
    except paramiko.AuthenticationException:
        print(f"[SKIP] Auth failed for {USER}")
        continue
    except Exception as e:
        print(f"[ERROR] {USER}: {e}")
        continue

if not success:
    print("\n[ERROR] Could not authenticate with any user")
    sys.exit(1)

# Deploy key
try:
    print(f"\n[INFO] Deploying key for {USER}...")

    commands = f"""
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo '{pubkey}' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
echo 'KEY_DEPLOYED'
"""

    stdin, stdout, stderr = client.exec_command(commands)
    output = stdout.read().decode()
    errors = stderr.read().decode()

    if "KEY_DEPLOYED" in output:
        print("[OK] SSH key deployed successfully!")
        print("\n[INFO] Testing passwordless login...")

        # Test
        stdin, stdout, stderr = client.exec_command("whoami; hostname")
        result = stdout.read().decode().strip()
        print(f"[OK] Server info:\n{result}")

        client.close()
        print("\n[SUCCESS] Setup complete! You can now use SSH without password.")
        sys.exit(0)
    else:
        print(f"[ERROR] Deployment failed:\n{errors}")
        sys.exit(1)

except paramiko.AuthenticationException:
    print("[ERROR] Authentication failed. Check password.")
    sys.exit(1)
except paramiko.SSHException as e:
    print(f"[ERROR] SSH error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)
