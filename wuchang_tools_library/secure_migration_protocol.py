import os
import shutil
import time
import base64

# Configuration
SOURCE_DIR = os.getcwd()
TARGET_DRIVE = "E:\\時空\\專利"
KEYWORDS = ["時空", "Spacetime", "Rule", "規則", "INVENTION", "QUANTUM"]
SKIP_DIRS = [".git", ".vscode", "__pycache__", "wuchang_tools_library"] # Don not move tool library itself
EXTENSIONS = [".txt", ".md", ".py", ".ps1", ".json", ".html"]

def simple_encrypt(content_bytes):
    # Simple XOR encryption with a key
    key = b"WUCHANG_TE_SECRET_KEY_2026"
    encrypted = bytearray()
    for i, byte in enumerate(content_bytes):
        encrypted.append(byte ^ key[i % len(key)])
    return base64.b64encode(encrypted)

def scan_and_migrate():
    print(f"🔒 INITIATING SECURE MIGRATION PROTOCOL...")
    print(f"�� Source: {SOURCE_DIR}")
    print(f"💾 Target: {TARGET_DRIVE}")
    
    # Ensure target exists
    if not os.path.exists(TARGET_DRIVE):
        try:
            os.makedirs(TARGET_DRIVE)
            print(f"✅ Created target directory: {TARGET_DRIVE}")
        except Exception as e:
            print(f"❌ Failed to create target directory: {e}")
            print("⚠️  Switching to ENCRYPTION ONLY mode.")
            return

    moved_count = 0
    encrypted_count = 0
    
    for root, dirs, files in os.walk(SOURCE_DIR):
        # Skip forbidden directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # Check extension
            _, ext = os.path.splitext(file)
            if ext.lower() not in EXTENSIONS:
                continue
                
            # Check keywords in filename
            if any(k.lower() in file.lower() for k in KEYWORDS):
                print(f"\n🔍 Found Artifact: {file}")
                
                try:
                    # Attempt MOVE
                    dest_path = os.path.join(TARGET_DRIVE, file)
                    shutil.move(file_path, dest_path)
                    print(f"   ✅ MOVED to {dest_path}")
                    moved_count += 1
                except Exception as e:
                    print(f"   ⚠️  Move Failed: {e}")
                    print(f"   🔒 Initiating In-Place Encryption...")
                    
                    try:
                        # Attempt ENCRYPT
                        with open(file_path, "rb") as f:
                            content = f.read()
                        
                        encrypted_content = simple_encrypt(content)
                        
                        enc_file_path = file_path + ".wuchang_locked"
                        with open(enc_file_path, "wb") as f:
                            f.write(encrypted_content)
                            
                        os.remove(file_path) # Delete original
                        print(f"   ✅ ENCRYPTED: {enc_file_path}")
                        encrypted_count += 1
                    except Exception as enc_e:
                        print(f"   ❌ Encryption Failed: {enc_e}")

    print("\n==================================================")
    print(f"📊 MIGRATION SUMMARY")
    print(f"   - Moved to SD Card: {moved_count}")
    print(f"   - Encrypted Locally: {encrypted_count}")
    print("==================================================")

if __name__ == "__main__":
    scan_and_migrate()

