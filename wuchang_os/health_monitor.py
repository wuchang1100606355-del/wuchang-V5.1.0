import socket
import os
import sys
import psutil

def check_port(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            return s.connect_ex((host, port)) == 0
    except:
        return False

def check_vpn():
    try:
        interfaces = psutil.net_if_addrs()
        vpn_names = ['vpn', 'tun', 'tap', 'tailscale', 'wireguard']
        found = []
        for name in interfaces:
            if any(v in name.lower() for v in vpn_names):
                found.append(name)
        return found
    except Exception as e:
        return [f"Error checking VPN: {e}"]

print("=== System Health Check Report ===")
core_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'vm_fastapi_main_new.py')
print(f"Core File (vm_fastapi_main_new.py): {'EXISTS' if os.path.exists(core_path) else 'MISSING'}")
if os.path.exists(core_path):
    print(f"Core File Size: {os.path.getsize(core_path)} bytes")

print(f"Odoo Service (Port 8069): {'ONLINE' if check_port('localhost', 8069) else 'OFFLINE'}")

vpns = check_vpn()
if vpns:
    print(f"VPN Connection: ACTIVE ({', '.join(vpns)})")
else:
    print("VPN Connection: NOT DETECTED")

runner_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'double_j_1_to_8_runner.py')
print(f"1+8 Runner Script: {'EXISTS' if os.path.exists(runner_file) else 'MISSING'}")

print("=== End Report ===")
