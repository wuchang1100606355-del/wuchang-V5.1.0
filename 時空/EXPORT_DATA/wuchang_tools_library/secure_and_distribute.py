import os
import shutil
import datetime
from cryptography.fernet import Fernet

# Configuration
SOURCE_ROOT = r"J:\共用雲端硬碟\五常雲端空間"
LOCAL_VAULT_DIR = os.path.join(SOURCE_ROOT, "LOCAL_SECURE_VAULT")
EXPORT_SOURCE_DIR = os.path.join(SOURCE_ROOT, "時空")
MEMORY_CARD_DRIVE = "E:"
MEMORY_CARD_TARGET = os.path.join(MEMORY_CARD_DRIVE, "\\時空")

TARGET_DIRS = ["INTELLIGENCE_CORE", "wuchang_tools_library"]
TARGET_EXTENSIONS = [".py", ".ps1", ".md", ".json", ".txt"]

def encrypt_file(file_path, target_path, cipher_suite):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        encrypted_data = cipher_suite.encrypt(data)
        with open(target_path, "wb") as f:
            f.write(encrypted_data)
        # print(f"Encrypted: {target_path}")
    except Exception as e:
        print(f"Error encrypting {file_path}: {e}")

def create_local_vault():
    print(f"Creating Local Secure Vault at {LOCAL_VAULT_DIR}...")
    if os.path.exists(LOCAL_VAULT_DIR):
        shutil.rmtree(LOCAL_VAULT_DIR)
    os.makedirs(LOCAL_VAULT_DIR)

    # Generate Encryption Key for Vault
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    with open(os.path.join(LOCAL_VAULT_DIR, "vault_key.key"), "wb") as key_file:
        key_file.write(key)
    
    print("Encryption key generated.")

    count = 0
    # Process Directories
    for folder in TARGET_DIRS:
        source_folder = os.path.join(SOURCE_ROOT, folder)
        if not os.path.exists(source_folder):
            continue
            
        for root, dirs, files in os.walk(source_folder):
            rel_path = os.path.relpath(root, SOURCE_ROOT)
            target_root = os.path.join(LOCAL_VAULT_DIR, rel_path)
            os.makedirs(target_root, exist_ok=True)
            
            for file in files:
                if any(file.endswith(ext) for ext in TARGET_EXTENSIONS):
                    source_file = os.path.join(root, file)
                    target_file = os.path.join(target_root, file + ".enc")
                    encrypt_file(source_file, target_file, cipher_suite)
                    count += 1
    
    # Process Root Files
    for file in os.listdir(SOURCE_ROOT):
        if os.path.isfile(os.path.join(SOURCE_ROOT, file)):
            if any(file.endswith(ext) for ext in TARGET_EXTENSIONS):
                source_file = os.path.join(SOURCE_ROOT, file)
                target_file = os.path.join(LOCAL_VAULT_DIR, file + ".enc")
                encrypt_file(source_file, target_file, cipher_suite)
                count += 1

    print(f"Local Vault created. {count} files encrypted and stored.")

def distribute_to_memory_card():
    print(f"Checking for memory card at {MEMORY_CARD_DRIVE}...")
    if os.path.exists(MEMORY_CARD_DRIVE):
        print(f"Memory card found. Copying to {MEMORY_CARD_TARGET}...")
        try:
            if os.path.exists(MEMORY_CARD_TARGET):
                shutil.rmtree(MEMORY_CARD_TARGET) # Clean overwrite
            shutil.copytree(EXPORT_SOURCE_DIR, MEMORY_CARD_TARGET)
            print("Successfully copied to Memory Card.")
        except Exception as e:
            print(f"Error copying to memory card: {e}")
    else:
        print(f"Drive {MEMORY_CARD_DRIVE} not found. Skipping memory card copy.")
        print(f"Please manually copy {EXPORT_SOURCE_DIR} to your memory card.")

if __name__ == "__main__":
    create_local_vault()
    distribute_to_memory_card()



---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:36:54
---
