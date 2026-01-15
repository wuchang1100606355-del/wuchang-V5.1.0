"""
更新小 J 頭像腳本
支持使用白色頭髮圖片
"""

import os
import sys
import io
import base64
from pathlib import Path

# 設置 UTF-8 編碼
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def create_avatar_placeholder():
    """創建頭像佔位符說明"""
    static_dir = Path('static')
    static_dir.mkdir(exist_ok=True)
    
    readme_path = static_dir / 'README_AVATAR.md'
    readme_content = """# 小 J 頭像圖片說明

## 文件位置
將白色頭髮的頭像圖片放在此目錄，命名為：
- `little_j_white_hair.png` (推薦)
- `little_j_white_hair.jpg`
- `little_j_white_hair.svg`

## 圖片要求
- **格式**: PNG (透明背景最佳), JPG, SVG
- **尺寸**: 至少 256x256 像素
- **背景**: 透明背景 PNG 效果最佳
- **風格**: 白色頭髮角色頭像

## 使用方式
1. 將圖片文件放入 `static/` 目錄
2. 命名為 `little_j_white_hair.png`
3. 刷新頁面，小 J 浮動圖示會自動使用新頭像

## 備用方案
如果圖片不存在，系統會自動使用 🤖 emoji 作為備用顯示。
"""
    
    readme_path.write_text(readme_content, encoding='utf-8')
    print("[OK] 已創建頭像說明文件: static/README_AVATAR.md")

def check_avatar_exists():
    """檢查頭像文件是否存在"""
    static_dir = Path('static')
    possible_names = [
        'little_j_white_hair.png',
        'little_j_white_hair.jpg',
        'little_j_white_hair.svg',
        'little_j_white_hair.gif'
    ]
    
    for name in possible_names:
        path = static_dir / name
        if path.exists():
            print(f"[OK] 找到頭像文件: {path}")
            return str(path)
    
    print("[WARN] 未找到頭像文件，將使用 emoji 備用顯示")
    print("   請將白色頭髮圖片放入 static/ 目錄，命名為 little_j_white_hair.png")
    return None

if __name__ == "__main__":
    print("=" * 60)
    print("小 J 頭像檢查工具")
    print("=" * 60)
    
    create_avatar_placeholder()
    check_avatar_exists()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
