import os
import shutil
import datetime
import re
from cryptography.fernet import Fernet
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

# Configuration
SOURCE_DIR = r"J:\共用雲端硬碟\五常雲端空間"
TARGET_BASE = r"J:\共用雲端硬碟\五常雲端空間\時空"
EXPORT_DIR = os.path.join(TARGET_BASE, "EXPORT_DATA")
PDF_DIR = os.path.join(TARGET_BASE, "PDF_DOCS")
SECURE_DIR = os.path.join(TARGET_BASE, "SECURED_ARCHIVE")
KEYWORDS = ["時空", "Spacetime", "鏡像資訊", "捨棄硬碟", "三同步", "螺旋路徑", "江政隆", "F124771717"]
TIMESTAMP_BLOCK = """
---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: {}
---
"""

def setup_directories():
    for d in [TARGET_BASE, EXPORT_DIR, PDF_DIR, SECURE_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"Created directory: {d}")

def get_font_path():
    # Try common Chinese fonts
    candidates = [
        r"C:\Windows\Fonts\msjh.ttc",
        r"C:\Windows\Fonts\msjh.ttf",
        r"C:\Windows\Fonts\simsun.ttc",
        r"C:\Windows\Fonts\mingliu.ttc"
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

def generate_pdf(source_path, target_path):
    c = canvas.Canvas(target_path, pagesize=A4)
    width, height = A4
    
    # Register Font
    font_path = get_font_path()
    font_name = "Helvetica" # Fallback
    if font_path:
        try:
            pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
            font_name = 'ChineseFont'
        except Exception as e:
            print(f"Font loading error: {e}")

    c.setFont(font_name, 10)
    y_position = height - 20 * mm
    
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            # Simple word wrap (very basic)
            max_char = 50
            chunks = [line[i:i+max_char] for i in range(0, len(line), max_char)]
            for chunk in chunks:
                if y_position < 20 * mm:
                    c.showPage()
                    c.setFont(font_name, 10)
                    y_position = height - 20 * mm
                c.drawString(20 * mm, y_position, chunk)
                y_position -= 5 * mm
                
        c.save()
        print(f"Generated PDF: {target_path}")
    except Exception as e:
        print(f"Failed to generate PDF for {source_path}: {e}")

def encrypt_file(file_path, target_path, cipher_suite):
    with open(file_path, 'rb') as f:
        data = f.read()
    encrypted_data = cipher_suite.encrypt(data)
    with open(target_path, 'wb') as f:
        f.write(encrypted_data)
    print(f"Encrypted: {target_path}")

def scan_and_process():
    setup_directories()
    
    # Generate Key
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    with open(os.path.join(TARGET_BASE, "encryption_key.key"), "wb") as key_file:
        key_file.write(key)
    print(f"Encryption Key Saved to {os.path.join(TARGET_BASE, 'encryption_key.key')}")
    
    processed_files = []
    
    for root, dirs, files in os.walk(SOURCE_DIR):
        # Exclude Target Base to avoid recursion
        if TARGET_BASE in root:
            continue
            
        for file in files:
            if not file.endswith(('.md', '.py', '.json', '.txt')):
                continue
                
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                if any(k in content for k in KEYWORDS):
                    # Found!
                    rel_path = os.path.relpath(file_path, SOURCE_DIR)
                    target_file_path = os.path.join(EXPORT_DIR, rel_path)
                    
                    # Ensure subdir exists
                    os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
                    
                    # Add Timestamp
                    timestamp = TIMESTAMP_BLOCK.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    new_content = content + "\n" + timestamp
                    
                    # Write to Export
                    with open(target_file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Processed: {rel_path}")
                    
                    # Generate PDF (for MD only)
                    if file.endswith('.md'):
                        pdf_path = os.path.join(PDF_DIR, os.path.splitext(os.path.basename(file))[0] + ".pdf")
                        generate_pdf(target_file_path, pdf_path)
                        
                    # Encrypt
                    enc_path = os.path.join(SECURE_DIR, rel_path + ".enc")
                    os.makedirs(os.path.dirname(enc_path), exist_ok=True)
                    encrypt_file(target_file_path, enc_path, cipher_suite)
                    
                    processed_files.append(rel_path)
                    
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    with open(os.path.join(TARGET_BASE, "manifest.txt"), "w", encoding='utf-8') as f:
        f.write("\n".join(processed_files))

if __name__ == "__main__":
    scan_and_process()


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:36:54
---
