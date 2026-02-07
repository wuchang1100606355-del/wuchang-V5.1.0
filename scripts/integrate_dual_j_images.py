#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
integrate_dual_j_images.py

整合雙J形象圖片到系統中

功能：
- 搜尋現有的雙J形象圖片
- 將圖片整合到系統各處（首頁、UI、文檔等）
- 建立圖片使用索引
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def find_dual_j_images() -> Dict[str, List[Path]]:
    """搜尋雙J形象圖片"""
    print("🔍 搜尋雙J形象圖片...")
    
    images = {
        "little_j": [],
        "jules": [],
        "dual_j": [],
        "other": []
    }
    
    # 搜尋 static 目錄
    static_dir = BASE_DIR / "static"
    if static_dir.exists():
        # 搜尋地端小J圖片
        for pattern in ["little_j*.png", "little_j*.jpg", "little_j*.svg", "*小j*.png", "*小J*.png"]:
            for img_file in static_dir.rglob(pattern):
                if "little_j" in img_file.name.lower() or "小j" in img_file.name.lower():
                    images["little_j"].append(img_file)
        
        # 搜尋雲端小J圖片
        for pattern in ["jules*.png", "jules*.jpg", "jules*.svg", "*jules*.png", "*JULES*.png"]:
            for img_file in static_dir.rglob(pattern):
                if "jules" in img_file.name.lower():
                    images["jules"].append(img_file)
        
        # 搜尋雙J協作圖片
        for pattern in ["dual_j*.png", "dual_j*.jpg", "*雙j*.png", "*雙J*.png"]:
            for img_file in static_dir.rglob(pattern):
                if "dual" in img_file.name.lower() or "雙" in img_file.name.lower():
                    images["dual_j"].append(img_file)
    
    # 搜尋 images 目錄
    images_dir = BASE_DIR / "static" / "images"
    if images_dir.exists():
        for img_file in images_dir.rglob("*.png"):
            if "little_j" in img_file.name.lower() or "小j" in img_file.name.lower():
                images["little_j"].append(img_file)
            elif "jules" in img_file.name.lower():
                images["jules"].append(img_file)
            elif "dual" in img_file.name.lower() or "雙" in img_file.name.lower():
                images["dual_j"].append(img_file)
            else:
                images["other"].append(img_file)
    
    # 統計
    total = sum(len(v) for v in images.values())
    print(f"✅ 找到 {total} 張圖片：")
    print(f"   - 地端小J: {len(images['little_j'])} 張")
    print(f"   - 雲端小J: {len(images['jules'])} 張")
    print(f"   - 雙J協作: {len(images['dual_j'])} 張")
    print(f"   - 其他: {len(images['other'])} 張")
    print()
    
    return images


def create_image_index(images: Dict[str, List[Path]]) -> Dict[str, Any]:
    """建立圖片索引"""
    index = {
        "generated_at": datetime.now().isoformat(),
        "little_j": [],
        "jules": [],
        "dual_j": [],
        "usage_locations": {
            "homepage": [],
            "ui": [],
            "docs": []
        }
    }
    
    for img_file in images["little_j"]:
        index["little_j"].append({
            "file": str(img_file.relative_to(BASE_DIR)),
            "name": img_file.name,
            "size": img_file.stat().st_size if img_file.exists() else 0,
        })
    
    for img_file in images["jules"]:
        index["jules"].append({
            "file": str(img_file.relative_to(BASE_DIR)),
            "name": img_file.name,
            "size": img_file.stat().st_size if img_file.exists() else 0,
        })
    
    for img_file in images["dual_j"]:
        index["dual_j"].append({
            "file": str(img_file.relative_to(BASE_DIR)),
            "name": img_file.name,
            "size": img_file.stat().st_size if img_file.exists() else 0,
        })
    
    return index


def integrate_to_homepage(images: Dict[str, List[Path]], index_file: Path):
    """整合雙J形象到首頁"""
    print("🌐 整合雙J形象到首頁...")
    
    homepage_file = BASE_DIR / "index.html"
    if not homepage_file.exists():
        print("⚠️  首頁檔案不存在")
        return False
    
    # 讀取首頁內容
    homepage_content = homepage_file.read_text(encoding="utf-8")
    
    # 檢查是否已有雙J形象區塊
    if "dual-j-section" in homepage_content or "雙J" in homepage_content:
        print("✅ 首頁已包含雙J形象區塊")
        return True
    
    # 選擇要使用的圖片
    little_j_img = images["little_j"][0] if images["little_j"] else None
    jules_img = images["jules"][0] if images["jules"] else None
    dual_j_img = images["dual_j"][0] if images["dual_j"] else None
    
    # 建立雙J形象區塊 HTML
    dual_j_section = """
    <!-- 雙J協作系統 -->
    <section id="dual-j" class="section" style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 60px 20px;">
        <div class="container">
            <h2 class="section-title">雙J協作系統</h2>
            <p style="text-align: center; color: var(--text-light); font-size: 1.1rem; margin-bottom: 40px;">
                地端小J與雲端小J (JULES) 協作，共同維護和管理系統
            </p>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 30px; margin-top: 40px;">
                <!-- 地端小J -->
                <div class="service-card" style="background: var(--white); padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); text-align: center;">
                    <div style="margin-bottom: 20px;">
                        <img src="/static/images/dual_j/little_j_avatar.png" 
                             alt="地端小J" 
                             onerror="this.style.display='none'; this.nextElementSibling.style.display='block';"
                             style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; margin: 0 auto; display: block;">
                        <div style="display: none; font-size: 64px; margin: 20px 0;">🤖</div>
                    </div>
                    <h3 style="color: var(--primary-color); margin: 15px 0 10px 0;">地端小J</h3>
                    <p style="color: var(--text-light); font-size: 0.9rem; margin-bottom: 15px;">本地 LLM 助理</p>
                    <ul style="list-style: none; padding: 0; text-align: left; color: var(--text-light); font-size: 0.85rem;">
                        <li style="margin: 8px 0;">✓ 持續監控容器狀態</li>
                        <li style="margin: 8px 0;">✓ 進行工作討論和分析</li>
                        <li style="margin: 8px 0;">✓ 建立任務給 JULES</li>
                        <li style="margin: 8px 0;">✓ 路由器管理</li>
                    </ul>
                </div>
                
                <!-- 雲端小J (JULES) -->
                <div class="service-card" style="background: var(--white); padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); text-align: center;">
                    <div style="margin-bottom: 20px;">
                        <img src="/static/images/dual_j/jules_avatar.png" 
                             alt="雲端小J (JULES)" 
                             onerror="this.style.display='none'; this.nextElementSibling.style.display='block';"
                             style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; margin: 0 auto; display: block;">
                        <div style="display: none; font-size: 64px; margin: 20px 0;">☁️</div>
                    </div>
                    <h3 style="color: var(--primary-color); margin: 15px 0 10px 0;">雲端小J (JULES)</h3>
                    <p style="color: var(--text-light); font-size: 0.9rem; margin-bottom: 15px;">雲端 LLM 執行者</p>
                    <ul style="list-style: none; padding: 0; text-align: left; color: var(--text-light); font-size: 0.85rem;">
                        <li style="margin: 8px 0;">✓ 執行任務和修復</li>
                        <li style="margin: 8px 0;">✓ 應用定義的人格設定</li>
                        <li style="margin: 8px 0;">✓ 回報任務狀態</li>
                        <li style="margin: 8px 0;">✓ 系統優化建議</li>
                    </ul>
                </div>
                
                <!-- 雙J協作 -->
                <div class="service-card" style="background: var(--white); padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); text-align: center;">
                    <div style="margin-bottom: 20px;">
                        <img src="/static/images/dual_j/dual_j_collaboration.png" 
                             alt="雙J協作" 
                             onerror="this.style.display='none'; this.nextElementSibling.style.display='block';"
                             style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; margin: 0 auto; display: block;">
                        <div style="display: none; font-size: 64px; margin: 20px 0;">🤝</div>
                    </div>
                    <h3 style="color: var(--primary-color); margin: 15px 0 10px 0;">雙J協作</h3>
                    <p style="color: var(--text-light); font-size: 0.9rem; margin-bottom: 15px;">協作夥伴關係</p>
                    <ul style="list-style: none; padding: 0; text-align: left; color: var(--text-light); font-size: 0.85rem;">
                        <li style="margin: 8px 0;">✓ 地端監控 + 雲端執行</li>
                        <li style="margin: 8px 0;">✓ 自動化協作流程</li>
                        <li style="margin: 8px 0;">✓ 持續優化系統</li>
                        <li style="margin: 8px 0;">✓ 工作日誌記錄</li>
                    </ul>
                </div>
            </div>
        </div>
    </section>
    """
    
    # 插入到資金來源區塊之前
    if "<!-- 資金來源 -->" in homepage_content:
        homepage_content = homepage_content.replace(
            "<!-- 資金來源 -->",
            dual_j_section + "\n    <!-- 資金來源 -->"
        )
    elif "<!-- 頁尾 -->" in homepage_content:
        homepage_content = homepage_content.replace(
            "<!-- 頁尾 -->",
            dual_j_section + "\n    <!-- 頁尾 -->"
        )
    else:
        # 如果找不到插入點，在聯絡我們區塊之後插入
        if "</section>" in homepage_content:
            sections = homepage_content.split("</section>")
            if len(sections) > 1:
                homepage_content = sections[0] + "</section>" + dual_j_section + "".join(sections[1:])
    
    # 更新導航列
    if '<li><a href="#contact">聯絡我們</a></li>' in homepage_content:
        homepage_content = homepage_content.replace(
            '<li><a href="#contact">聯絡我們</a></li>',
            '<li><a href="#contact">聯絡我們</a></li>\n                <li><a href="#dual-j">雙J協作</a></li>'
        )
    
    # 寫回檔案
    homepage_file.write_text(homepage_content, encoding="utf-8")
    print("✅ 已整合雙J形象到首頁")
    return True


def main():
    """主函數"""
    print("=" * 70)
    print("雙J形象圖片整合工具")
    print("=" * 70)
    print()
    
    # 1. 搜尋現有圖片
    images = find_dual_j_images()
    
    # 2. 建立圖片索引
    index = create_image_index(images)
    
    # 3. 儲存索引
    index_file = BASE_DIR / "static" / "images" / "dual_j_images_index.json"
    index_file.parent.mkdir(parents=True, exist_ok=True)
    index_file.write_text(
        json.dumps(index, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"📋 圖片索引已儲存至: {index_file.relative_to(BASE_DIR)}")
    print()
    
    # 4. 整合到首頁
    if images["little_j"] or images["jules"] or images["dual_j"]:
        integrate_to_homepage(images, index_file)
    else:
        print("⚠️  未找到雙J形象圖片，請先執行 generate_dual_j_images.py 生成圖片")
        print()
        print("💡 提示：")
        print("1. 執行 python generate_dual_j_images.py 生成雙J形象圖片")
        print("2. 或手動將圖片放入 static/images/dual_j/ 目錄")
        print("   - little_j_avatar.png (地端小J)")
        print("   - jules_avatar.png (雲端小J)")
        print("   - dual_j_collaboration.png (雙J協作)")
    
    print()
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
