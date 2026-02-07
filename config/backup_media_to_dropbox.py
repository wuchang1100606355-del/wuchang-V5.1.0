#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
backup_media_to_dropbox.py

將專案中的影片和照片打包並上傳到 Dropbox，然後建立捷徑
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

# 設定 UTF-8 編碼
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent

# 媒體檔案副檔名
MEDIA_EXTENSIONS = {
    # 影片
    '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.3gp',
    # 圖片
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.heic', '.heif', '.webp', '.svg'
}

# 排除目錄
EXCLUDE_DIRS = {'node_modules', '.git', '__pycache__', '.venv', 'venv', 'env', 'dist', 'build'}

# 使用統一的雲端同步配置（改為五常雲端空間）
try:
    from cloud_sync_config import ensure_wuchang_cloud_path, get_sync_directories
    CLOUD_BACKUP = ensure_wuchang_cloud_path()
    sync_dirs = get_sync_directories()
    # 使用五常雲端空間的備份目錄
    CLOUD_TARGET = sync_dirs.get("backups", CLOUD_BACKUP / "backups") / "媒體檔案備份"
except ImportError:
    # 回退到舊配置（Dropbox）
    CLOUD_BACKUP = Path(os.path.expanduser("~")) / "Dropbox" / "五常系統備份"
    CLOUD_TARGET = CLOUD_BACKUP / "媒體檔案備份"

CLOUD_TARGET.mkdir(parents=True, exist_ok=True)


def find_media_files(base_dir: Path) -> list[Path]:
    """找出所有媒體檔案"""
    media_files = []
    
    for root, dirs, files in os.walk(base_dir):
        # 排除不需要的目錄
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        root_path = Path(root)
        
        for file in files:
            file_path = root_path / file
            if file_path.suffix.lower() in MEDIA_EXTENSIONS:
                # 排除備份檔案本身
                if 'backup' not in file_path.name.lower() and 'media_files_' not in file_path.name:
                    media_files.append(file_path)
    
    return media_files


def create_zip_archive(files: list[Path], output_path: Path) -> bool:
    """
    建立 ZIP 壓縮檔（直接寫入雲端）
    
    注意：壓縮檔直接寫入雲端，不保留本機副本
    """
    try:
        # 確保輸出目錄存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files:
                # 計算相對路徑
                try:
                    arcname = file_path.relative_to(BASE_DIR)
                    zipf.write(file_path, arcname)
                    print(f"已加入: {arcname}")
                except Exception as e:
                    print(f"⚠️ 無法加入 {file_path}: {e}")
        
        file_size = output_path.stat().st_size / (1024 * 1024)  # MB
        print(f"\n✅ 壓縮檔已建立於雲端: {output_path.name}")
        print(f"   檔案大小: {file_size:.2f} MB")
        print(f"   位置: {output_path}")
        print(f"   注意: 備份僅存於雲端，本機不保留副本")
        return True
    except Exception as e:
        print(f"❌ 建立壓縮檔失敗: {e}")
        return False


def copy_to_cloud(zip_path: Path) -> Path:
    """
    複製到雲端（如果 ZIP 不在雲端）
    
    注意：如果 ZIP 已經在雲端，則不需要複製
    """
    # 檢查 ZIP 是否已經在雲端目錄
    try:
        from cloud_sync_config import validate_cloud_path
        if validate_cloud_path(zip_path):
            print(f"✅ ZIP 檔案已在雲端: {zip_path}")
            return zip_path
    except ImportError:
        pass
    
    # 如果不在雲端，複製到雲端
    try:
        target_path = CLOUD_TARGET / zip_path.name
        
        print(f"\n正在複製到雲端...")
        print(f"  來源: {zip_path}")
        print(f"  目標: {target_path}")
        
        shutil.copy2(zip_path, target_path)
        
        # 刪除本機副本
        try:
            zip_path.unlink()
            print(f"✅ 已刪除本機副本: {zip_path}")
        except Exception as e:
            print(f"⚠️ 無法刪除本機副本: {e}")
        
        print(f"✅ 已複製到雲端: {target_path}")
        return target_path
    except Exception as e:
        print(f"❌ 複製到雲端失敗: {e}")
        return None


def create_shortcut(original_files: list[Path], zip_path: Path, cloud_path: Path):
    """建立捷徑和說明文件"""
    shortcut_content = f"""# 媒體檔案備份說明

## 備份時間
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 備份檔案
- **壓縮檔名稱**: {zip_path.name}
- **雲端位置**: {cloud_path}
- **檔案大小**: {zip_path.stat().st_size / (1024 * 1024):.2f} MB

## 包含的媒體檔案 ({len(original_files)} 個)

"""
    
    for i, file_path in enumerate(original_files, 1):
        try:
            rel_path = file_path.relative_to(BASE_DIR)
            file_size = file_path.stat().st_size / (1024 * 1024)  # MB
            shortcut_content += f"{i}. `{rel_path}` ({file_size:.2f} MB)\n"
        except:
            shortcut_content += f"{i}. `{file_path}`\n"
    
    shortcut_content += f"""

## 使用說明

1. **開啟雲端檔案**: 直接點擊五常雲端空間中的壓縮檔
2. **下載**: 使用 Google Drive 桌面應用程式同步，或透過網頁下載
3. **解壓縮**: 解壓縮後可取得所有原始媒體檔案

## 雲端路徑

```
{cloud_path}
```

## 注意事項

- 此備份僅包含專案目錄中的媒體檔案
- **備份僅存於雲端，本機不保留副本**
- 原始檔案仍保留在專案中
- 如需還原，請從雲端下載並解壓縮

---
*此文件由 backup_media_to_dropbox.py 自動生成*
"""
    
    shortcut_file = BASE_DIR / "媒體檔案備份說明.md"
    shortcut_file.write_text(shortcut_content, encoding="utf-8")
    
    print(f"\n✅ 已建立捷徑說明: {shortcut_file}")
    
    # 建立 Windows 捷徑（.lnk）
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(BASE_DIR / "媒體檔案備份.lnk"))
        shortcut.Targetpath = str(cloud_path.parent)
        shortcut.Description = "媒體檔案雲端備份資料夾（五常雲端空間）"
        shortcut.save()
        print(f"✅ 已建立 Windows 捷徑: 媒體檔案備份.lnk")
    except ImportError:
        print("⚠️ 無法建立 Windows 捷徑（需要 pywin32 模組）")
    except Exception as e:
        print(f"⚠️ 建立 Windows 捷徑失敗: {e}")


def main():
    """主函數"""
    print("=" * 60)
    print("媒體檔案備份到雲端（五常雲端空間）")
    print("=" * 60)
    print()
    print(f"雲端備份路徑: {CLOUD_TARGET}")
    print("注意: 備份直接寫入雲端，本機不保留副本")
    print()
    
    # 1. 找出所有媒體檔案
    print("正在搜尋媒體檔案...")
    media_files = find_media_files(BASE_DIR)
    
    if not media_files:
        print("⚠️ 沒有找到任何媒體檔案")
        return
    
    print(f"✅ 找到 {len(media_files)} 個媒體檔案\n")
    
    # 計算總大小
    total_size = sum(f.stat().st_size for f in media_files) / (1024 * 1024 * 1024)  # GB
    print(f"總大小: {total_size:.2f} GB\n")
    
    # 2. 建立壓縮檔（直接寫入雲端）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"media_files_{timestamp}.zip"
    # 直接寫入雲端，不經過本機
    zip_path = CLOUD_TARGET / zip_name
    
    print("正在建立壓縮檔（直接寫入雲端）...")
    if not create_zip_archive(media_files, zip_path):
        return
    
    # 3. 確認雲端路徑（ZIP 已在雲端，無需複製）
    cloud_path = copy_to_cloud(zip_path)
    if not cloud_path:
        print("⚠️ 警告: 無法確認雲端路徑")
        cloud_path = zip_path
    
    # 4. 建立捷徑（指向雲端檔案）
    create_shortcut(media_files, zip_path, cloud_path)
    
    print("\n" + "=" * 60)
    print("✅ 備份完成！")
    print("=" * 60)
    print(f"\n📁 雲端位置: {cloud_path}")
    print(f"📄 說明文件: 媒體檔案備份說明.md")
    print(f"🔗 捷徑: 媒體檔案備份.lnk (如果可用)")
    print(f"\n⚠️  注意: 備份僅存於雲端，本機不保留副本")


if __name__ == "__main__":
    main()
