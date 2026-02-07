import paramiko
import time
import socket

# Configuration
HOST = 'localhost'
PORT = 33891
CREDENTIALS = [
    ('wuchang', '97573469'),
    ('ubuntu', 'ubuntu'),
    ('ubuntu', ''),
    ('admin', 'admin'),
    ('admin', 'password'),
    ('root', 'root'),
    ('user', 'user'),
    ('user', 'password'),
    ('vagrant', 'vagrant'),
    ('osboxes', 'osboxes.org'),
    ('vboxuser', 'changeme'),
    ('odoo', 'odoo'),
    ('wuchang', 'wuchang'),
    ('wuchang', 'poiuY926926'),
    ('admin', 'poiuY926926')
]

def is_port_open(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((host, port))
        s.close()
        return True
    except:
        return False

def check_ssh(user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Trying {user} / {password} ...")
        client.connect(HOST, PORT, user, password, timeout=5, banner_timeout=5)
        print(f"SUCCESS! Connected with {user} / {password}")
        client.close()
        return True
    except paramiko.AuthenticationException:
        print("Authentication failed.")
        return False
    except Exception as e:
        print(f"Connection error: {e}")
        return False

def main():
    print(f"Checking {HOST}:{PORT}...")
    
    if not is_port_open(HOST, PORT):
        print("Port is closed. Is the VM running and forwarding set?")
        return

    print("Port is open. Attempting SSH Brute-force...")
    
    for user, pwd in CREDENTIALS:
        if check_ssh(user, pwd):
            print(f"\nFOUND CREDENTIALS: {user} / {pwd}")
            return
            
    print("\nAll attempts failed.")

if __name__ == '__main__':
    main()
