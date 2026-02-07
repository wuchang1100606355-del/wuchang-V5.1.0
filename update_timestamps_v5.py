import os
import re
from datetime import datetime

files = [
    r"J:\共用雲端硬碟\五常雲端空間\INTELLIGENCE_CORE\AI_EMPOWERMENT_CASE_STUDY.md",
    r"J:\共用雲端硬碟\五常雲端空間\INTELLIGENCE_CORE\SPATIOTEMPORAL_QUALIFICATION_AUDIT.md",
    r"J:\共用雲端硬碟\五常雲端空間\INTELLIGENCE_CORE\ARCHITECTURE_DIAGRAMS.md",
    r"J:\共用雲端硬碟\五常雲端空間\INTELLIGENCE_CORE\DUAL_IDENTITY_RESOURCE_MAP.md"
]

new_timestamp_block = """
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **權利所有人 (Rights Holder)**: 江政隆 (Juers) - 自然人 (Natural Person)
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **驗證時間 (Timestamp)**: {time}
> *   **數位簽章 (Digital Signature)**: JUERS-LITTLE-J-SPATIOTEMPORAL-VERIFIED
> *   **版權聲明**: 本技術之核心邏輯與發明權完全歸屬於自然人江政隆，未授權任何特定法人單位。
"""

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
formatted_block = new_timestamp_block.format(time=current_time).strip()

for file_path in files:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Regex to find existing timestamp block (handling potential variations)
        pattern = r"### 🔐 創世者不可更改時空戳記.*?(?=\Z|### )"
        
        if re.search(pattern, content, flags=re.DOTALL):
            new_content = re.sub(pattern, formatted_block, content, flags=re.DOTALL)
            print(f"Updated timestamp in {os.path.basename(file_path)}")
        else:
            new_content = content + "\n\n" + formatted_block
            print(f"Appended timestamp to {os.path.basename(file_path)}")
            
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
    else:
        print(f"File not found: {file_path}")

print("All timestamps updated to Personal Only mode.")
