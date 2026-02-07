# -*- coding: utf-8 -*-
import socket
import threading
from queue import Queue
import time

def port_scan(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.1)
        result = s.connect_ex((ip, port))
        if result == 0:
            return True
        s.close()
    except:
        pass
    return False

def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return 'Unknown'

def scan_host(ip):
    # Scan common ports to detect device type
    ports = [22, 80, 443, 8080, 5000, 8069]  # SSH, HTTP, HTTPS, Proxy, Flask, Odoo
    open_ports = []
    for port in ports:
        if port_scan(ip, port):
            open_ports.append(port)
    
    if open_ports or port_scan(ip, 62078):  # Check for iPhone/iPad sync port often open
        hostname = get_hostname(ip)
        print(f'Found device: {ip} ({hostname}) - Open ports: {open_ports}')
        return {'ip': ip, 'hostname': hostname, 'ports': open_ports}
    return None

def worker():
    while True:
        ip = q.get()
        scan_host(ip)
        q.task_done()

print('Starting LAN scan for 192.168.55.x...')
q = Queue()
for i in range(1, 255):
    ip = f'192.168.55.{i}'
    q.put(ip)

for t in range(50):
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()

q.join()
print('Scan complete.')
