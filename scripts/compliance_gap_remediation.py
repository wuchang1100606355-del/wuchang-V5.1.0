#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compliance_gap_remediation.py

合規缺口完善作業工具

功能：
- 自動修復技術基礎設施問題
- 補充缺失的聯絡資訊
- 建立合規網站頁面
- 安裝 Google Analytics 並配置轉換追蹤
- 生成合規完善報告
"""

import sys
import json
import os
import subprocess
import requests
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
COMPLIANCE_DATA_FILE = BASE_DIR / "compliance_data.json"
WEBSITE_CONTENT_DATA_FILE = BASE_DIR / "website_content_data.json"
INDEX_HTML_FILE = BASE_DIR / "index.html"
REMEDIATION_LOG_FILE = BASE_DIR / "compliance_remediation.log"
REMEDIATION_CONFIG_FILE = BASE_DIR / "compliance_remediation_config.json"

# 聯絡資訊（從 compliance_data.json 讀取或使用預設值）
CONTACT_INFO = {
    "phone": "0229866856",
    "email": "wuchang110006355@gmail.com",
    "admin_email": "admin@gmail.com",
    "organization_email": "admin@wuchang.life",
    "google_business_account": "admin@wuchang.life"
}


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌",
        "PROGRESS": "🔄"
    }
    icon = icons.get(level, "•")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{icon} [{timestamp}] [{level}] {message}"
    print(log_entry)
    
    try:
        with open(REMEDIATION_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{log_entry}\n")
    except:
        pass


def load_compliance_data() -> Dict[str, Any]:
    """載入合規資料"""
    if COMPLIANCE_DATA_FILE.exists():
        try:
            return json.loads(COMPLIANCE_DATA_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            log(f"載入合規資料失敗: {e}", "ERROR")
            return {}
    return {}


def load_website_content_data() -> Dict[str, Any]:
    """載入網站內容資料"""
    if WEBSITE_CONTENT_DATA_FILE.exists():
        try:
            return json.loads(WEBSITE_CONTENT_DATA_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            log(f"載入網站內容資料失敗: {e}", "ERROR")
            return {}
    return {}


def update_contact_info_in_compliance_data() -> bool:
    """更新合規資料中的聯絡資訊"""
    log("更新合規資料中的聯絡資訊", "PROGRESS")
    try:
        data = load_compliance_data()
        
        if "contact" not in data:
            data["contact"] = {}
        
        data["contact"].update({
            "phone": CONTACT_INFO["phone"],
            "email": CONTACT_INFO["email"],
            "admin_email": CONTACT_INFO["admin_email"],
            "organization_email": CONTACT_INFO["organization_email"],
            "google_business_account": CONTACT_INFO["google_business_account"]
        })
        
        COMPLIANCE_DATA_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        log("合規資料中的聯絡資訊已更新", "OK")
        return True
    except Exception as e:
        log(f"更新合規資料失敗: {e}", "ERROR")
        return False


def create_about_page() -> bool:
    """建立關於我們頁面"""
    log("建立關於我們頁面", "PROGRESS")
    try:
        compliance_data = load_compliance_data()
        website_data = load_website_content_data()
        
        about_html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>關於我們 - 五常社區發展協會</title>
    <link rel="stylesheet" href="/static/css/style.css">
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
                <p><strong>組織名稱：</strong>{compliance_data.get('organization', {}).get('name', '新北市三重區五常社區發展協會')}</p>
                <p><strong>成立宗旨：</strong>{compliance_data.get('mission', {}).get('vision', '促進社區發展、增進居民福祉')}</p>
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
                <p>{compliance_data.get('mission', {}).get('development_plan', '社區眾利閉環系統開發')}</p>
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
        <p>&copy; 2024 五常社區發展協會. All rights reserved.</p>
    </footer>
</body>
</html>"""
        
        about_file = BASE_DIR / "about.html"
        about_file.write_text(about_html, encoding="utf-8")
        log(f"關於我們頁面已建立: {about_file.name}", "OK")
        return True
    except Exception as e:
        log(f"建立關於我們頁面失敗: {e}", "ERROR")
        return False


def create_mission_page() -> bool:
    """建立使命與活動頁面"""
    log("建立使命與活動頁面", "PROGRESS")
    try:
        compliance_data = load_compliance_data()
        
        mission_html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>使命與活動 - 五常社區發展協會</title>
    <link rel="stylesheet" href="/static/css/style.css">
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
                <p>{compliance_data.get('mission', {}).get('vision', '促進社區發展、增進居民福祉、推動社區營造、提升生活品質')}</p>
            </div>
            
            <div class="activities">
                <h2>主要活動</h2>
                <ul>
                    <li>社區發展計畫推動</li>
                    <li>數位化轉型輔導</li>
                    <li>社區 AI 服務開發</li>
                    <li>地方小商業振興</li>
                    <li>公民教育推廣</li>
                </ul>
            </div>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2024 五常社區發展協會. All rights reserved.</p>
    </footer>
</body>
</html>"""
        
        mission_file = BASE_DIR / "mission.html"
        mission_file.write_text(mission_html, encoding="utf-8")
        log(f"使命與活動頁面已建立: {mission_file.name}", "OK")
        return True
    except Exception as e:
        log(f"建立使命與活動頁面失敗: {e}", "ERROR")
        return False


def create_contact_page() -> bool:
    """建立聯絡我們頁面"""
    log("建立聯絡我們頁面", "PROGRESS")
    try:
        contact_html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>聯絡我們 - 五常社區發展協會</title>
    <link rel="stylesheet" href="/static/css/style.css">
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
                <p><strong>電話：</strong><a href="tel:{CONTACT_INFO['phone']}">{CONTACT_INFO['phone']}</a></p>
                <p><strong>電子郵件：</strong><a href="mailto:{CONTACT_INFO['email']}">{CONTACT_INFO['email']}</a></p>
                <p><strong>組織信箱：</strong><a href="mailto:{CONTACT_INFO['organization_email']}">{CONTACT_INFO['organization_email']}</a></p>
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
        <p>&copy; 2024 五常社區發展協會. All rights reserved.</p>
    </footer>
</body>
</html>"""
        
        contact_file = BASE_DIR / "contact.html"
        contact_file.write_text(contact_html, encoding="utf-8")
        log(f"聯絡我們頁面已建立: {contact_file.name}", "OK")
        return True
    except Exception as e:
        log(f"建立聯絡我們頁面失敗: {e}", "ERROR")
        return False


def update_index_html_with_contact_info() -> bool:
    """更新 index.html 中的聯絡資訊"""
    log("更新 index.html 中的聯絡資訊", "PROGRESS")
    try:
        if not INDEX_HTML_FILE.exists():
            log("index.html 不存在，跳過更新", "WARN")
            return False
        
        content = INDEX_HTML_FILE.read_text(encoding="utf-8")
        
        # 檢查是否已有聯絡資訊，如果沒有則添加
        if "0229866856" not in content:
            # 在適當位置添加聯絡資訊
            contact_section = f"""
    <!-- 聯絡資訊區塊 -->
    <section class="contact-section" id="contact" style="background: #f8f9fa; padding: 40px 20px; margin: 40px 0;">
        <div class="container" style="max-width: 1200px; margin: 0 auto;">
            <h2 style="text-align: center; color: #333; margin-bottom: 30px; font-size: 28px;">
                聯絡我們
            </h2>
            <div style="text-align: center;">
                <p style="font-size: 18px; margin: 10px 0;">
                    <strong>電話：</strong><a href="tel:{CONTACT_INFO['phone']}" style="color: #667eea;">{CONTACT_INFO['phone']}</a>
                </p>
                <p style="font-size: 18px; margin: 10px 0;">
                    <strong>電子郵件：</strong><a href="mailto:{CONTACT_INFO['email']}" style="color: #667eea;">{CONTACT_INFO['email']}</a>
                </p>
                <p style="font-size: 18px; margin: 10px 0;">
                    <strong>組織信箱：</strong><a href="mailto:{CONTACT_INFO['organization_email']}" style="color: #667eea;">{CONTACT_INFO['organization_email']}</a>
                </p>
            </div>
        </div>
    </section>
"""
            # 在 </body> 標籤前插入聯絡資訊區塊
            if "</body>" in content:
                content = content.replace("</body>", contact_section + "\n</body>")
                INDEX_HTML_FILE.write_text(content, encoding="utf-8")
                log("index.html 中的聯絡資訊已更新", "OK")
                return True
            else:
                log("無法找到 </body> 標籤", "WARN")
                return False
        else:
            log("index.html 中已有聯絡資訊", "OK")
            return True
    except Exception as e:
        log(f"更新 index.html 失敗: {e}", "ERROR")
        return False


def add_google_analytics_to_html(html_file: Path, ga_id: str = None) -> bool:
    """在 HTML 檔案中添加 Google Analytics"""
    log(f"在 {html_file.name} 中添加 Google Analytics", "PROGRESS")
    try:
        if not html_file.exists():
            log(f"{html_file.name} 不存在", "WARN")
            return False
        
        content = html_file.read_text(encoding="utf-8")
        
        # 檢查是否已有 Google Analytics
        if "gtag" in content.lower() or "google-analytics" in content.lower():
            log(f"{html_file.name} 中已有 Google Analytics", "OK")
            return True
        
        # Google Analytics 4 代碼
        if ga_id:
            ga_code = f"""
    <!-- Google Analytics 4 -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{ga_id}');
    </script>
"""
        else:
            # 使用預設的 GA4 代碼（需要後續配置）
            ga_code = """
    <!-- Google Analytics 4 (需要配置 GA4 ID) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-XXXXXXXXXX');
    </script>
"""
        
        # 在 </head> 標籤前插入 Google Analytics
        if "</head>" in content:
            content = content.replace("</head>", ga_code + "\n</head>")
            html_file.write_text(content, encoding="utf-8")
            log(f"{html_file.name} 中的 Google Analytics 已添加", "OK")
            return True
        else:
            log(f"無法找到 </head> 標籤在 {html_file.name}", "WARN")
            return False
    except Exception as e:
        log(f"添加 Google Analytics 失敗: {e}", "ERROR")
        return False


def create_ga4_setup_guide() -> bool:
    """建立 Google Analytics 4 設定指南"""
    log("建立 Google Analytics 4 設定指南", "PROGRESS")
    try:
        guide_content = """# Google Analytics 4 設定指南

## 步驟 1: 建立 GA4 屬性

1. 前往 [Google Analytics](https://analytics.google.com/)
2. 建立新的 GA4 屬性
3. 取得測量 ID（格式：G-XXXXXXXXXX）

## 步驟 2: 更新 HTML 檔案

在以下檔案中更新 Google Analytics ID：
- `index.html`
- `about.html`
- `mission.html`
- `contact.html`

將 `G-XXXXXXXXXX` 替換為您的實際 GA4 測量 ID。

## 步驟 3: 配置轉換事件

在 Google Analytics 中設定轉換事件：
1. 前往「管理」>「事件」
2. 標記重要事件為「轉換」
3. 建議的轉換事件：
   - 聯絡表單提交
   - 頁面瀏覽（關鍵頁面）
   - 下載（如有提供下載）

## 步驟 4: 驗證安裝

1. 使用 [Google Tag Assistant](https://tagassistant.google.com/) 驗證
2. 在 GA4 中查看即時報表確認資料接收

## 注意事項

- 確保符合 GDPR 和隱私權政策
- 考慮添加 Cookie 同意橫幅
- 定期檢查轉換追蹤是否正常運作
"""
        
        guide_file = BASE_DIR / "GA4_SETUP_GUIDE.md"
        guide_file.write_text(guide_content, encoding="utf-8")
        log(f"Google Analytics 4 設定指南已建立: {guide_file.name}", "OK")
        return True
    except Exception as e:
        log(f"建立設定指南失敗: {e}", "ERROR")
        return False


def generate_remediation_report(results: Dict[str, Any]) -> str:
    """生成合規完善報告"""
    report = []
    report.append("# 合規缺口完善作業報告")
    report.append(f"\n生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    report.append("## 執行結果摘要")
    
    # 聯絡資訊更新
    report.append("\n### 聯絡資訊更新")
    if results.get("contact_info_updated", False):
        report.append("✅ 合規資料中的聯絡資訊已更新")
        report.append(f"   - 電話: {CONTACT_INFO['phone']}")
        report.append(f"   - 電子郵件: {CONTACT_INFO['email']}")
    else:
        report.append("❌ 聯絡資訊更新失敗")
    
    # 網站頁面建立
    report.append("\n### 網站頁面建立")
    if results.get("about_page_created", False):
        report.append("✅ 關於我們頁面已建立 (about.html)")
    else:
        report.append("❌ 關於我們頁面建立失敗")
    
    if results.get("mission_page_created", False):
        report.append("✅ 使命與活動頁面已建立 (mission.html)")
    else:
        report.append("❌ 使命與活動頁面建立失敗")
    
    if results.get("contact_page_created", False):
        report.append("✅ 聯絡我們頁面已建立 (contact.html)")
    else:
        report.append("❌ 聯絡我們頁面建立失敗")
    
    if results.get("index_html_updated", False):
        report.append("✅ index.html 中的聯絡資訊已更新")
    else:
        report.append("❌ index.html 更新失敗")
    
    # Google Analytics
    report.append("\n### Google Analytics 配置")
    if results.get("ga_added_to_index", False):
        report.append("✅ index.html 中已添加 Google Analytics 代碼")
    else:
        report.append("❌ index.html 中添加 Google Analytics 失敗")
    
    if results.get("ga_setup_guide_created", False):
        report.append("✅ Google Analytics 4 設定指南已建立 (GA4_SETUP_GUIDE.md)")
    else:
        report.append("❌ Google Analytics 設定指南建立失敗")
    
    # 待辦事項
    report.append("\n## 待辦事項")
    report.append("\n### P0 - 立即處理")
    report.append("1. **配置 Google Analytics 4 測量 ID**")
    report.append("   - 參考 GA4_SETUP_GUIDE.md")
    report.append("   - 更新所有 HTML 檔案中的 GA4 ID")
    
    report.append("\n2. **技術基礎設施檢查**")
    report.append("   - 確認 HTTPS/SSL 證書配置")
    report.append("   - 確認 DNS 記錄正確")
    report.append("   - 確認網站可訪問性")
    
    report.append("\n### P1 - 高優先級")
    report.append("1. **配置轉換追蹤**")
    report.append("   - 在 Google Analytics 中設定轉換事件")
    report.append("   - 測試轉換追蹤是否正常運作")
    
    report.append("\n2. **網站內容優化**")
    report.append("   - 確保所有頁面內容完整")
    report.append("   - 添加組織資訊披露")
    
    return "\n".join(report)


def main():
    """主函數"""
    log("開始合規缺口完善作業", "PROGRESS")
    
    results = {
        "contact_info_updated": False,
        "about_page_created": False,
        "mission_page_created": False,
        "contact_page_created": False,
        "index_html_updated": False,
        "ga_added_to_index": False,
        "ga_setup_guide_created": False
    }
    
    # 1. 更新聯絡資訊
    results["contact_info_updated"] = update_contact_info_in_compliance_data()
    
    # 2. 建立網站頁面
    results["about_page_created"] = create_about_page()
    results["mission_page_created"] = create_mission_page()
    results["contact_page_created"] = create_contact_page()
    
    # 3. 更新 index.html
    results["index_html_updated"] = update_index_html_with_contact_info()
    
    # 4. 添加 Google Analytics
    results["ga_added_to_index"] = add_google_analytics_to_html(INDEX_HTML_FILE)
    
    # 5. 建立 GA4 設定指南
    results["ga_setup_guide_created"] = create_ga4_setup_guide()
    
    # 生成報告
    report = generate_remediation_report(results)
    report_file = BASE_DIR / f"compliance_remediation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_file.write_text(report, encoding="utf-8")
    log(f"報告已儲存: {report_file.name}", "OK")
    
    # 儲存配置
    config = {
        "last_remediation": datetime.now().isoformat(),
        "results": results,
        "contact_info": CONTACT_INFO
    }
    REMEDIATION_CONFIG_FILE.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    print("\n" + "="*60)
    print(report)
    print("="*60)
    
    log("合規缺口完善作業完成", "OK")


if __name__ == "__main__":
    main()
