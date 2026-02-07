import paramiko
import time

def check_router():
    host = "192.168.50.1"
    user = "coffeeboss"
    password = "977349"
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {host}...")
        client.connect(host, username=user, password=password)
        
        commands = [
            "nvram get lan_domain",
            "nvram get wan_domain",
            "nvram get ddns_hostname_x",
            "cat /etc/hosts",
            "route"
        ]
        
        for cmd in commands:
            print(f"\n--- Executing: {cmd} ---")
            stdin, stdout, stderr = client.exec_command(cmd)
            print(stdout.read().decode().strip())
            err = stderr.read().decode().strip()
            if err:
                print(f"Error: {err}")
                
        client.close()
        print("\nDone.")
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check_router()
