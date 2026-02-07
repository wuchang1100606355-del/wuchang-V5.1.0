import paramiko
import os
from scp import SCPClient
import sys
import time

# Configuration
HOST = 'localhost'
PORT = 33891
PASSWORD = sys.argv[1] if len(sys.argv) > 1 else '97573469'
LOCAL_ROOT = r'C:\wuchang V5.0.0'


def create_ssh_client(username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, PORT, username, password)
        return client
    except Exception as e:
        print(f"Failed to connect with {username}: {e}")
        return None


def main():
    print(f"Connecting to {HOST}:{PORT}...")

    usernames = [
        'wuchang',
        'chiang',
        'chiangchenglung',
        'chiang-cheng-lung',
        'chiang_cheng_lung',
        'cheng',
        'lung',
        'admin',
        'user',
        'ubuntu'
    ]

    client = None
    username = None

    for u in usernames:
        print(f"Trying username: '{u}'...")
        client = create_ssh_client(u, PASSWORD)
        if client:
            username = u
            break

    if not client:
        print("Could not connect. Please check credentials.")
        return

    remote_home = f'/home/{username}'
    if username == 'root':
        remote_home = '/root'

    print(f"Connected successfully as {username}! Home: {remote_home}")

    # Create directories
    dirs = ['wuchang_os', 'scripts', 'config',
            'backups', 'downloads', 'memory_store']
    for d in dirs:
        stdin, stdout, stderr = client.exec_command(
            f'mkdir -p {remote_home}/{d}')
        stdout.channel.recv_exit_status()

    # SCP Transfer
    print("Starting file transfer...")
    try:
        with SCPClient(client.get_transport()) as scp:
            # Transfer directories
            print("Uploading wuchang_os...")
            scp.put(os.path.join(LOCAL_ROOT, 'wuchang_os'),
                    recursive=True, remote_path=remote_home)
            print("Uploading scripts...")
            scp.put(os.path.join(LOCAL_ROOT, 'scripts'),
                    recursive=True, remote_path=remote_home)
            print("Uploading config...")
            if os.path.exists(os.path.join(LOCAL_ROOT, 'config')):
                scp.put(os.path.join(LOCAL_ROOT, 'config'),
                        recursive=True, remote_path=remote_home)

            # Transfer individual files
            files = ['docker-compose.yml', '.env',
                     'Dockerfile', 'requirements.txt']
            for f in files:
                local_path = os.path.join(LOCAL_ROOT, f)
                if os.path.exists(local_path):
                    print(f"Uploading {f}...")
                    scp.put(local_path, remote_path=remote_home)
    except Exception as e:
        print(f"File transfer failed: {e}")
        # Continue anyway to try setup

    print("File transfer complete.")

    # Setup VM
    print("Setting up VM environment (Docker & Compose)...")

    setup_commands = [
        'sudo apt-get update',
        'sudo apt-get install -y docker.io docker-compose',
        'sudo usermod -aG docker $USER',
        'sudo systemctl enable docker',
        'sudo systemctl start docker'
    ]

    for cmd in setup_commands:
        print(f"Running: {cmd}")
        full_cmd = f'echo {PASSWORD} | sudo -S {cmd}'
        stdin, stdout, stderr = client.exec_command(full_cmd)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            err = stderr.read().decode()
            if "Could not get lock" in err:
                print("Waiting for apt lock...")
                time.sleep(10)
                stdin, stdout, stderr = client.exec_command(
                    full_cmd)  # Retry once
            else:
                print(f"Error executing {cmd}: {err}")
        else:
            print(f"Success: {cmd}")

    # Launch Docker Compose
    print("Launching Odoo stack...")
    # We use nohup to let it run after disconnect, but we want to see if it starts.
    # Build might take time.
    launch_cmd = f'echo {PASSWORD} | sudo -S docker-compose up -d --build'
    print(f"Running: {launch_cmd}")
    stdin, stdout, stderr = client.exec_command(
        f'cd {remote_home} && {launch_cmd}')

    # Stream output for a bit
    while not stdout.channel.exit_status_ready():
        if stdout.channel.recv_ready():
            sys.stdout.write(stdout.channel.recv(1024).decode())
        if stderr.channel.recv_ready():
            sys.stderr.write(stderr.channel.recv(1024).decode())

    print("\n\nOdoo stack launch command finished.")
    print(f"You can check status with: ssh {username}@localhost -p {PORT}")

    client.close()


if __name__ == '__main__':
    main()
