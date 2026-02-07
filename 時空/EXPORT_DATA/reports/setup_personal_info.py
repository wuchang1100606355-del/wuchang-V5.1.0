#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直接寫入個人資訊，撤銷驗證機制"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

from personal_ai_binding import create_personal_binding, get_mac_address
from datetime import datetime

def main():
    # 取得 MAC 地址
    mac = get_mac_address()
    
    # 直接建立個人 AI 綁定（使用江政隆的資訊）
    binding = create_personal_binding(
        personal_name="江政隆",
        personal_id="chiang_cheng_lung_001",
        password="wuchang2026",
        email="",
        phone="",
        notes="協會總幹事，最高權限使用者",
        mac_address=mac
    )
    
    print("=" * 60)
    print("✅ 個人資訊已直接寫入系統")
    print("=" * 60)
    print(f"姓名: {binding['personal_name']}")
    print(f"身份 ID: {binding['personal_id']}")
    print(f"MAC 地址: {binding['mac_address']}")
    print(f"最高權限: {binding['highest_authority']}")
    print(f"建立時間: {binding['created_at']}")
    print("=" * 60)
    print("\n✅ 驗證機制已撤銷，UI 可直接訪問")

if __name__ == "__main__":
    main()


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:04:46
---
