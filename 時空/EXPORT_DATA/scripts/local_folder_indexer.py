# 地端檔案夾自動化分析與索引腳本
# 功能：
# 1. 遍歷指定地端檔案夾，遞迴分析所有檔案與子資料夾
# 2. 建立完整目錄結構索引（含檔案名稱、路徑、大小、修改時間、雜湊值）
# 3. 將索引結果存為 JSON，並自動推送到時空系統指定目錄
# 4. 支援無人職守自動化執行

import os
import json
import hashlib
import time
from datetime import datetime

# 設定地端檔案夾路徑與索引輸出路徑
LOCAL_ROOT = r'j:/共用雲端硬碟/五常雲端空間/local_storage/data'
INDEX_OUTPUT = r'j:/共用雲端硬碟/五常雲端空間/local_storage/xiaoj_index/index.json'

# 遞迴建立目錄索引
def build_index(root_path):
    index = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            try:
                stat = os.stat(fpath)
                with open(fpath, 'rb') as f:
                    file_hash = hashlib.md5(f.read(4096)).hexdigest()
                index.append({
                    'name': fname,
                    'path': fpath,
                    'size': stat.st_size,
                    'mtime': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'hash': file_hash
                })
            except Exception as e:
                index.append({
                    'name': fname,
                    'path': fpath,
                    'error': str(e)
                })
    return index

if __name__ == "__main__":
    print(f"[小J] 開始分析地端檔案夾：{LOCAL_ROOT}")
    index = build_index(LOCAL_ROOT)
    print(f"[小J] 共索引 {len(index)} 個檔案。正在儲存索引...")
    os.makedirs(os.path.dirname(INDEX_OUTPUT), exist_ok=True)
    with open(INDEX_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"[小J] 索引已儲存：{INDEX_OUTPUT}")
    # TODO: 自動推送到時空系統（可呼叫API或複製到指定資料夾）
    print("[小J] 地端檔案夾索引流程完成。")


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:05:12
---
