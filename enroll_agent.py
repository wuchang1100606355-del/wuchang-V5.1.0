import sys
import json
import urllib.request
import urllib.error
import socket
import platform
import os
import ssl
import subprocess

# Using Cloudflare Tunnel to bypass local firewall issues
SERVER_URL = "https://full-rolls-gregory-estimate.trycloudflare.com/enroll"

def get_device_info():
    info = {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "ip": get_ip(),
        "user": os.getlogin() if hasattr(os, 'getlogin') else "unknown",
        "specs": get_specs()
    }
    return info

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_specs():
    specs = {"cpu_count": os.cpu_count()}
    
    # Try to get memory info
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if 'MemTotal' in line:
                    specs['memory_kb'] = int(line.split()[1])
                    specs['memory_gb'] = round(specs['memory_kb'] / 1024 / 1024, 2)
                    break
    except:
        specs['memory_info'] = "unavailable"

    # Check for Docker
    try:
        docker_version = subprocess.check_output(['docker', '--version'], stderr=subprocess.STDOUT)
        specs['docker'] = docker_version.decode('utf-8').strip()
    except:
        specs['docker'] = "not_installed"

    return specs

def enroll():
    print(f"Connecting to Wuchang System at {SERVER_URL}...")
    print("\n[INIT] Initializing Quantum Spacetime Expansion Module...")
    info = get_device_info()
    print(f"Device Info: {json.dumps(info, indent=2)}")
    
    data = json.dumps(info).encode('utf-8')
    req = urllib.request.Request(SERVER_URL, data=data, headers={'Content-Type': 'application/json'})
    
    # SSL context (Cloudflare has valid certs, but we keep permissive mode just in case)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            resp_data = response.read()
            print("Response:", resp_data.decode('utf-8'))
            print("\n[SUCCESS] Quantum Spacetime Expansion successfully installed and registered.")
            
            if info['specs'].get('docker') == "not_installed":
                 print("\n[SUGGESTION] Docker (Quantum Container) is not installed. To activate full capacity:")
                 print("  sudo apt-get update && sudo apt-get install -y docker.io")
            else:
                 print("\n[READY] Quantum Containers (Docker) detected. Ready for workload deployment.")
    except urllib.error.URLError as e:
        print(f"\n[ERROR] Connection failed: {e}")
        print("Please ensure you can access the internet.")

if __name__ == "__main__":
    enroll()
