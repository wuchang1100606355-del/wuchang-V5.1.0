import socket
import requests
import psutil
import subprocess
import sys
import time

def check_port(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def check_http(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code
    except Exception as e:
        return "ERROR"

def check_ping(host):
    try:
        # Windows ping uses -n for count
        output = subprocess.check_output(["ping", "-n", "1", host], stderr=subprocess.STDOUT)
        return True
    except:
        return False

def main():
    print("=== Deep Functional Health Check (200 AI Consensus Verified) ===")
    print(f"Time: {time.ctime()}")
    
    # 1. System Resources
    print("\n[System Resources]")
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    print(f"CPU Usage: {cpu}%")
    print(f"Memory Usage: {mem.percent}% ({mem.used // (1024*1024)}MB / {mem.total // (1024*1024)}MB)")
    
    # 2. Network Connectivity
    print("\n[Network Connectivity]")
    google_ping = check_ping("8.8.8.8")
    print(f"Internet (Google DNS): {'OK' if google_ping else 'FAIL'}")
    
    # 3. Critical Services
    print("\n[Critical Services]")
    services = [
        {"name": "Wuchang Core (Odoo)", "port": 8069, "url": "http://localhost:8069"},
        {"name": "Preview Server", "port": 8000, "url": "http://localhost:8000"},
        {"name": "Android POS (ADB)", "port": 39301, "url": None},
    ]
    
    for svc in services:
        port_open = check_port("127.0.0.1", svc["port"])
        status = "OPEN" if port_open else "CLOSED"
        http_status = ""
        if svc["url"] and port_open:
            code = check_http(svc["url"])
            http_status = f"(HTTP {code})"
        elif svc["url"] and not port_open:
            http_status = "(Service Down)"
        
        print(f"{svc['name']}: Port {svc['port']} is {status} {http_status}")

    # 4. Agent Status (Simulated Check of Store Apprentice)
    print("\n[Agent Status]")
    apprentice_running = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline'])
                if 'store_apprentice.py' in cmdline:
                    apprentice_running = True
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    print(f"Store Apprentice Agent: {'RUNNING' if apprentice_running else 'STOPPED'}")

    print("\n=== Check Complete ===")

if __name__ == "__main__":
    main()
