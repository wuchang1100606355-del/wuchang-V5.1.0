import socket

TARGET_IP = "192.168.50.249"
PORT = 22

print(f"🔍 Checking {TARGET_IP}:{PORT} for OpenSSH Server...")

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3.0)
    s.connect((TARGET_IP, PORT))
    
    # Receive banner
    banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
    
    print(f"✅ TCP Connection successful")
    print(f"🧩 Service Banner: {banner}")
    
    if "OpenSSH" in banner:
        print("🎉 MATCH CONFIRMED: OpenSSH Server detected!")
    else:
        print("⚠️ Service detected but banner does not explicitly state 'OpenSSH'")
        
    s.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
