import paramiko
import sys
import time

HOST = '127.0.0.1'
PORT = 33891

CREDENTIALS = [
    ('wuchang', '97573469'),
    ('vboxuser', 'changeme'),
    ('osboxes', 'osboxes.org'),
    ('ubuntu', 'ubuntu'),
    ('odoo', 'odoo')
]

def test_ssh():
    for user, password in CREDENTIALS:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            print(f"Trying {user} / {password}...")
            client.connect(HOST, PORT, user, password, timeout=5)
            print(f"SUCCESS: Connected to Odoo-Entry-VM with user '{user}' and password '{password}'")
            stdin, stdout, stderr = client.exec_command('ls -la')
            print(stdout.read().decode())
            client.close()
            return
        except Exception as e:
            print(f"Failed with {user}: {e}")
        finally:
            client.close()

if __name__ == "__main__":
    test_ssh()
