import paramiko
import sys
import time
import socket

HOST = 'localhost'
PORT = 33893
USERS = ['o0930', 'wuchang01\\o0930', 'o0930913993o@yahoo.com', 'admin@wuchang.life', 'admin', 'User', 'Administrator', 'wuchang']
PASSWORDS = ['poiuY926926@', 'poiuY926926', '97573469', 'poiuY926', '123456', 'password']

def is_port_open(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((host, port))
        s.close()
        return True
    except:
        return False

def test_auth(user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, PORT, user, password, timeout=10, banner_timeout=20)
        print(f"SUCCESS: Connected to Win-VM with user '{user}' and password '{password}'")
        client.close()
        return True
    except paramiko.AuthenticationException:
        pass
    except Exception as e:
        print(f"Error checking {user}:{password} -> {e}")
    return False

if __name__ == "__main__":
    print(f"Checking if Win-VM SSH port {PORT} is open...")
    if not is_port_open(HOST, PORT):
        print("Port 33893 is NOT open. OpenSSH Server might not be running or firewall blocked.")
        sys.exit(1)
    
    print(f"Port {PORT} is open. Testing credentials...")
    for user in USERS:
        for pwd in PASSWORDS:
            print(f"Trying {user} / {pwd}...", end='\r')
            if test_auth(user, pwd):
                print(f"\nFOUND MATCH: User: '{user}', Password: '{pwd}'")
                sys.exit(0)
    
    print("\nAll attempts failed. Please ask user for credentials.")
    sys.exit(1)
