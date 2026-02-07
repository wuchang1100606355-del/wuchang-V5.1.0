import paramiko
from scp import SCPClient
import os
import sys
import socket

# Configuration
HOST = 'localhost'
PORT = 33893
CREDENTIALS = [
    ('admin@wuchang.life', 'poiuY926926'),
    ('admin', 'poiuY926926'),
    ('o0930', 'poiuY926926'),
    ('Administrator', 'poiuY926926'),
    ('wuchang', '97573469')
]
LOCAL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_ssh_client(user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, PORT, user, password,
                       timeout=10, banner_timeout=10)
        return client
    except Exception as e:
        print(f"Failed to connect with {user}: {e}")
        return None


def main():
    print(f"Attempting to deploy to Win-VM on {HOST}:{PORT}...")

    client = None
    username = None

    for user, pwd in CREDENTIALS:
        print(f"Trying {user}...")
        client = create_ssh_client(user, pwd)
        if client:
            username = user
            print(f"SUCCESS: Connected as {username}")
            break

    if not client:
        print("Could not connect with any credentials. Please check SSH service on Win-VM.")
        print("Suggested fix in Win-VM PowerShell: 'Start-Service sshd'")
        sys.exit(1)

    # Detect Remote OS and Home
    stdin, stdout, stderr = client.exec_command('echo %USERPROFILE%')
    remote_home = stdout.read().decode().strip()
    if not remote_home or '%' in remote_home:  # Fallback if not cmd
        stdin, stdout, stderr = client.exec_command('pwd')
        remote_home = stdout.read().decode().strip()
        print(f"Using pwd home: {remote_home}")
    else:
        print(f"Using USERPROFILE: {remote_home}")

    # Target Directory
    target_dir = f"{remote_home}\\wuchang_project"
    print(f"Targeting remote directory: {target_dir}")

    # Create Directory (PowerShell syntax)
    print("Creating remote directories...")
    client.exec_command(
        f'powershell -Command "New-Item -Path \'{target_dir}\' -ItemType Directory -Force"')

    # SCP Transfer
    print("Starting file transfer...")
    try:
        with SCPClient(client.get_transport()) as scp:
            # Transfer wuchang_os
            print("Uploading wuchang_os...")
            local_os_path = os.path.join(LOCAL_ROOT, 'wuchang_os')
            if os.path.exists(local_os_path):
                scp.put(local_os_path, recursive=True,
                        remote_path='wuchang_project')

            # Transfer scripts
            print("Uploading scripts...")
            local_scripts_path = os.path.join(LOCAL_ROOT, 'scripts')
            if os.path.exists(local_scripts_path):
                scp.put(local_scripts_path, recursive=True,
                        remote_path='wuchang_project')

            # Transfer config
            print("Uploading config...")
            local_config_path = os.path.join(LOCAL_ROOT, 'config')
            if os.path.exists(local_config_path):
                scp.put(local_config_path, recursive=True,
                        remote_path='wuchang_project')

            # Transfer root files
            files = ['docker-compose.yml', '.env', 'requirements.txt']
            for f in files:
                local_f = os.path.join(LOCAL_ROOT, f)
                if os.path.exists(local_f):
                    print(f"Uploading {f}...")
                    scp.put(local_f, remote_path='wuchang_project')

        print("Transfer Complete!")

        # Verify
        stdin, stdout, stderr = client.exec_command(f'dir "{target_dir}"')
        print("\nRemote Directory Listing:")
        print(stdout.read().decode())

    except Exception as e:
        print(f"Transfer failed: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
