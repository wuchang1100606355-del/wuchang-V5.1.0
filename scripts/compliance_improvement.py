#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compliance_improvement.py

現有可合規項目改善工具

功能：
- 修正頁面內容（填入正確的合規資料）
- 為所有頁面添加 Google Analytics 代碼
- 統一頁面樣式和導航結構
- 確保所有頁面包含完整的合規資訊
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
COMPLIANCE_DATA_FILE = BASE_DIR / "compliance_data.json"
INDEX_HTML_FILE = BASE_DIR / "index.html"
ABOUT_HTML_FILE = BASE_DIR / "about.html"
MISSION_HTML_FILE = BASE_DIR / "mission.html"
CONTACT_HTML_FILE = BASE_DIR / "contact.html"

# Google Analytics 代碼模板（待配置 ID）
GA4_CODE = """    <!-- Google Analytics 4 (GA4) - 請替換為實際的測量 ID -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-XXXXXXXXXX');
    </script>"""


def load_compliance_data() -> dict:
    """載入合規資料"""
    if COMPLIANCE_DATA_FILE.exists():
        try:
            return json.loads(COMPLIANCE_DATA_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"載入合規資料失敗: {e}")
            return {}
    return {}


def improve_about_html():
    """改善 about.html"""
    print("改善 about.html...")
    
    compliance_data = load_compliance_data()
    mission_data = compliance_data.get("mission", {})
    
    about_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="新北市三重區五常社區發展協會 - 關於我們">
    <title>關於我們 - 五常社區發展協會</title>
{GA4_CODE}
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Microsoft JhengHei', 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        nav {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            gap: 2rem;
        }}
        
        nav a {{
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: background 0.3s;
        }}
        
        nav a:hover, nav a.active {{
            background: rgba(255, 255, 255, 0.2);
        }}
        
        main {{
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 20px;
        }}
        
        .about-section {{
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #667eea;
            margin-bottom: 30px;
            font-size: 2.5rem;
        }}
        
        h2 {{
            color: #764ba2;
            margin: 30px 0 15px 0;
            font-size: 1.8rem;
        }}
        
        .organization-info, .core-values, .development-plan, .expected-goals {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        
        ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        ul li {{
            margin: 10px 0;
            padding-left: 25px;
            position: relative;
        }}
        
        ul li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: #667eea;
            font-weight: bold;
        }}
        
        footer {{
            background: #333;
            color: white;
            text-align: center;
            padding: 2rem;
            margin-top: 3rem;
        }}
        
        @media (max-width: 768px) {{
            nav {{
                flex-direction: column;
            }}
            
            .about-section {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <nav>
            <a href="/">首頁</a>
            <a href="/about.html" class="active">關於我們</a>
            <a href="/mission.html">使命與活動</a>
            <a href="/contact.html">聯絡我們</a>
        </nav>
    </header>
    
    <main>
        <section class="about-section">
            <h1>關於我們</h1>
            
            <div class="organization-info">
                <h2>組織資訊</h2>
                <p><strong>組織名稱：</strong>新北市三重區五常社區發展協會</p>
                <p><strong>成立宗旨：</strong>{mission_data.get('mission', '促進社區發展、增進居民福祉、推動社區營造、提升生活品質')}</p>
                <p><strong>服務範圍：</strong>新北市三重區（五常里、五順里、仁忠里）</p>
                <p><strong>認證狀態：</strong>Google for Nonprofits 已驗證 ✅</p>
            </div>
            
            <div class="core-values">
                <h2>核心價值</h2>
                <ul>
                    <li><strong>科技平權：</strong>讓科技服務每一個人</li>
                    <li><strong>數位普及：</strong>推動數位化轉型</li>
                </ul>
            </div>
            
            <div class="development-plan">
                <h2>發展計畫</h2>
                <p>社區眾利閉環系統開發</p>
                <p style="margin-top: 15px;">我們致力於開發一個整合式社區服務平台，透過科技創新推動社區發展，打造智慧社區生活圈。</p>
            </div>
            
            <div class="expected-goals">
                <h2>期望達成目標</h2>
                <ul>
                    <li>振興及保護地方小商業</li>
                    <li>增進居民社區認同</li>
                    <li>落實公民教育</li>
                    <li>開發社區 AI 服務</li>
                    <li>引流商業利潤投入公益</li>
                </ul>
            </div>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2026 新北市三重區五常社區發展協會 | Google for Nonprofits 認證組織</p>
        <p style="margin-top: 0.5rem; opacity: 0.8;">本網站使用 HTTPS 安全連線 | 所有資料處理遵循合規與可追溯原則</p>
    </footer>
</body>
</html>"""
    
    ABOUT_HTML_FILE.write_text(about_content, encoding="utf-8")
    print("✅ about.html 已改善")


def improve_mission_html():
    """改善 mission.html"""
    print("改善 mission.html...")
    
    compliance_data = load_compliance_data()
    mission_data = compliance_data.get("mission", {})
    main_activities = mission_data.get("main_activities", [])
    
    mission_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="新北市三重區五常社區發展協會 - 使命與活動">
    <title>使命與活動 - 五常社區發展協會</title>
{GA4_CODE}
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Microsoft JhengHei', 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        nav {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            gap: 2rem;
        }}
        
        nav a {{
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: background 0.3s;
        }}
        
        nav a:hover, nav a.active {{
            background: rgba(255, 255, 255, 0.2);
        }}
        
        main {{
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 20px;
        }}
        
        .mission-section {{
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #667eea;
            margin-bottom: 30px;
            font-size: 2.5rem;
        }}
        
        h2 {{
            color: #764ba2;
            margin: 30px 0 15px 0;
            font-size: 1.8rem;
        }}
        
        .mission, .activities {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        
        ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        ul li {{
            margin: 10px 0;
            padding-left: 25px;
            position: relative;
        }}
        
        ul li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: #667eea;
            font-weight: bold;
        }}
        
        footer {{
            background: #333;
            color: white;
            text-align: center;
            padding: 2rem;
            margin-top: 3rem;
        }}
        
        @media (max-width: 768px) {{
            nav {{
                flex-direction: column;
            }}
            
            .mission-section {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <nav>
            <a href="/">首頁</a>
            <a href="/about.html">關於我們</a>
            <a href="/mission.html" class="active">使命與活動</a>
            <a href="/contact.html">聯絡我們</a>
        </nav>
    </header>
    
    <main>
        <section class="mission-section">
            <h1>使命與活動</h1>
            
            <div class="mission">
                <h2>我們的使命</h2>
                <p>{mission_data.get('mission', '促進社區發展、增進居民福祉、推動社區營造、提升生活品質')}</p>
            </div>
            
            <div class="activities">
                <h2>主要活動</h2>
                <ul>
{chr(10).join([f'                    <li>{activity}</li>' for activity in main_activities[:8]])}
                </ul>
            </div>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2026 新北市三重區五常社區發展協會 | Google for Nonprofits 認證組織</p>
        <p style="margin-top: 0.5rem; opacity: 0.8;">本網站使用 HTTPS 安全連線 | 所有資料處理遵循合規與可追溯原則</p>
    </footer>
</body>
</html>"""
    
    MISSION_HTML_FILE.write_text(mission_content, encoding="utf-8")
    print("✅ mission.html 已改善")


def improve_contact_html():
    """改善 contact.html"""
    print("改善 contact.html...")
    
    compliance_data = load_compliance_data()
    contact_data = compliance_data.get("contact", {})
    
    contact_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="新北市三重區五常社區發展協會 - 聯絡我們">
    <title>聯絡我們 - 五常社區發展協會</title>
{GA4_CODE}
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Microsoft JhengHei', 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        nav {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            gap: 2rem;
        }}
        
        nav a {{
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: background 0.3s;
        }}
        
        nav a:hover, nav a.active {{
            background: rgba(255, 255, 255, 0.2);
        }}
        
        main {{
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 20px;
        }}
        
        .contact-section {{
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #667eea;
            margin-bottom: 30px;
            font-size: 2.5rem;
        }}
        
        h2 {{
            color: #764ba2;
            margin: 30px 0 15px 0;
            font-size: 1.8rem;
        }}
        
        .contact-info, .contact-form {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        
        .contact-info p {{
            margin: 15px 0;
            font-size: 1.1rem;
        }}
        
        .contact-info a {{
            color: #667eea;
            text-decoration: none;
            font-weight: bold;
        }}
        
        .contact-info a:hover {{
            text-decoration: underline;
        }}
        
        .form-group {{
            margin: 20px 0;
        }}
        
        .form-group label {{
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }}
        
        .form-group input,
        .form-group textarea {{
            width: 100%;
            padding: 10px;
            border: 2px solid #e9ecef;
            border-radius: 5px;
            font-size: 1rem;
            font-family: inherit;
        }}
        
        .form-group input:focus,
        .form-group textarea:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        button[type="submit"] {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        button[type="submit"]:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }}
        
        footer {{
            background: #333;
            color: white;
            text-align: center;
            padding: 2rem;
            margin-top: 3rem;
        }}
        
        @media (max-width: 768px) {{
            nav {{
                flex-direction: column;
            }}
            
            .contact-section {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <nav>
            <a href="/">首頁</a>
            <a href="/about.html">關於我們</a>
            <a href="/mission.html">使命與活動</a>
            <a href="/contact.html" class="active">聯絡我們</a>
        </nav>
    </header>
    
    <main>
        <section class="contact-section">
            <h1>聯絡我們</h1>
            
            <div class="contact-info">
                <h2>聯絡資訊</h2>
                <p><strong>電話：</strong><a href="tel:{contact_data.get('phone', '0229866856')}">{contact_data.get('phone', '0229866856')}</a></p>
                <p><strong>電子郵件：</strong><a href="mailto:{contact_data.get('email', 'wuchang110006355@gmail.com')}">{contact_data.get('email', 'wuchang110006355@gmail.com')}</a></p>
                <p><strong>組織信箱：</strong><a href="mailto:{contact_data.get('organization_email', 'admin@wuchang.life')}">{contact_data.get('organization_email', 'admin@wuchang.life')}</a></p>
                <p><strong>服務範圍：</strong>新北市三重區（五常里、五順里、仁忠里）</p>
            </div>
            
            <div class="contact-form">
                <h2>聯絡表單</h2>
                <form action="/api/contact" method="POST">
                    <div class="form-group">
                        <label for="name">姓名：</label>
                        <input type="text" id="name" name="name" required>
                    </div>
                    <div class="form-group">
                        <label for="email">電子郵件：</label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label for="message">訊息：</label>
                        <textarea id="message" name="message" rows="5" required></textarea>
                    </div>
                    <button type="submit">送出</button>
                </form>
            </div>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2026 新北市三重區五常社區發展協會 | Google for Nonprofits 認證組織</p>
        <p style="margin-top: 0.5rem; opacity: 0.8;">本網站使用 HTTPS 安全連線 | 所有資料處理遵循合規與可追溯原則</p>
    </footer>
</body>
</html>"""
    
    CONTACT_HTML_FILE.write_text(contact_content, encoding="utf-8")
    print("✅ contact.html 已改善")


def enable_ga4_in_index():
    """在 index.html 中啟用 Google Analytics（取消註解）"""
    print("啟用 index.html 中的 Google Analytics...")
    
    if not INDEX_HTML_FILE.exists():
        print("❌ index.html 不存在")
        return
    
    content = INDEX_HTML_FILE.read_text(encoding="utf-8")
    
    # 取消註解 Google Analytics 代碼
    if "<!-- <script async src=\"https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX\">" in content:
        content = content.replace(
            "    <!-- Google Analytics 4 (GA4) - 請替換為實際的測量 ID -->\n    <!-- <script async src=\"https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX\"></script>\n    <script>\n        window.dataLayer = window.dataLayer || [];\n        function gtag(){dataLayer.push(arguments);}\n        gtag('js', new Date());\n        gtag('config', 'G-XXXXXXXXXX');\n    </script> -->",
            GA4_CODE
        )
        INDEX_HTML_FILE.write_text(content, encoding="utf-8")
        print("✅ index.html 中的 Google Analytics 已啟用（待配置實際 ID）")
    else:
        print("ℹ️ index.html 中的 Google Analytics 代碼可能已經啟用或格式不同")


def main():
    """主函數"""
    print("="*60)
    print("現有可合規項目改善")
    print("="*60)
    print()
    
    # 改善頁面
    improve_about_html()
    improve_mission_html()
    improve_contact_html()
    
    # 啟用 Google Analytics
    enable_ga4_in_index()
    
    print()
    print("="*60)
    print("改善完成")
    print("="*60)
    print()
    print("📋 後續步驟：")
    print("1. 建立 Google Analytics 4 屬性")
    print("2. 取得 GA4 測量 ID（格式：G-XXXXXXXXXX）")
    print("3. 在所有 HTML 檔案中替換 G-XXXXXXXXXX 為實際的測量 ID")
    print("4. 配置轉換追蹤事件")
    print()
    print("📁 已改善的檔案：")
    print("  - about.html")
    print("  - mission.html")
    print("  - contact.html")
    print("  - index.html（Google Analytics 已啟用）")


if __name__ == "__main__":
    main()
