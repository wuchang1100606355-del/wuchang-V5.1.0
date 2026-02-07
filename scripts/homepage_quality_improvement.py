#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
homepage_quality_improvement.py

首頁品質提升工具

功能：
- SEO 優化
- 效能優化
- 無障礙檢查
- 響應式測試
- 分析工具整合
"""

import sys
import json
import re
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


def optimize_seo(html_content: str, compliance_data: Dict[str, Any]) -> str:
    """SEO 優化"""
    print("🔍 進行 SEO 優化...")
    
    org_info = compliance_data.get("organization", {})
    mission = compliance_data.get("mission", {})
    contact = compliance_data.get("contact", {})
    
    # 建立結構化資料 (Schema.org)
    structured_data = {
        "@context": "https://schema.org",
        "@type": "NGO",
        "name": org_info.get("name", ""),
        "alternateName": org_info.get("name_en", ""),
        "url": contact.get("website", ""),
        "logo": f"{contact.get('website', '')}/static/images/logo.png",
        "description": mission.get("mission", ""),
        "address": {
            "@type": "PostalAddress",
            "addressLocality": contact.get("address", {}).get("district", ""),
            "addressRegion": contact.get("address", {}).get("city", ""),
            "addressCountry": contact.get("address", {}).get("country", "")
        },
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": contact.get("phone", ""),
            "email": contact.get("email", ""),
            "contactType": "customer service"
        },
        "sameAs": [
            contact.get("website", "")
        ]
    }
    
    # 插入結構化資料
    structured_data_script = f"""
    <script type="application/ld+json">
    {json.dumps(structured_data, ensure_ascii=False, indent=2)}
    </script>
    """
    
    # 優化 Meta 標籤
    meta_tags = f"""
    <!-- SEO Meta Tags -->
    <meta name="description" content="{mission.get('mission', '')[:160]}">
    <meta name="keywords" content="五常社區,社區發展,智慧社區,幸福幣,社區服務,三重區,非營利組織">
    <meta name="author" content="{org_info.get('name', '')}">
    <meta name="robots" content="index, follow">
    <meta name="language" content="zh-TW">
    <meta name="geo.region" content="TW-NWT">
    <meta name="geo.placename" content="新北市三重區">
    
    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="{org_info.get('name', '')} - wuchang.life">
    <meta property="og:description" content="{mission.get('mission', '')[:200]}">
    <meta property="og:url" content="{contact.get('website', '')}">
    <meta property="og:site_name" content="{org_info.get('name', '')}">
    <meta property="og:locale" content="zh_TW">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{org_info.get('name', '')} - wuchang.life">
    <meta name="twitter:description" content="{mission.get('mission', '')[:200]}">
    """
    
    # 插入到 <head> 中
    if "<head>" in html_content:
        html_content = html_content.replace(
            "</head>",
            meta_tags + structured_data_script + "\n    </head>"
        )
    
    print("✅ SEO 優化完成")
    return html_content


def optimize_performance(html_content: str) -> str:
    """效能優化"""
    print("⚡ 進行效能優化...")
    
    optimizations = []
    
    # 1. 圖片延遲載入
    if 'src=' in html_content and 'loading=' not in html_content:
        html_content = re.sub(
            r'<img([^>]*?)src=([^>]*?)>',
            r'<img\1src=\2 loading="lazy">',
            html_content
        )
        optimizations.append("✓ 圖片延遲載入已啟用")
    
    # 2. 預載入關鍵資源
    preload_links = """
    <!-- Preload Critical Resources -->
    <link rel="preload" href="/static/css/main.css" as="style">
    <link rel="preload" href="/static/js/main.js" as="script">
    """
    
    if "<head>" in html_content and "preload" not in html_content:
        html_content = html_content.replace(
            "</head>",
            preload_links + "\n    </head>"
        )
        optimizations.append("✓ 關鍵資源預載入已啟用")
    
    # 3. DNS 預取
    dns_prefetch = """
    <!-- DNS Prefetch -->
    <link rel="dns-prefetch" href="https://www.google.com">
    <link rel="dns-prefetch" href="https://www.google-analytics.com">
    """
    
    if "<head>" in html_content and "dns-prefetch" not in html_content:
        html_content = html_content.replace(
            "</head>",
            dns_prefetch + "\n    </head>"
        )
        optimizations.append("✓ DNS 預取已啟用")
    
    if optimizations:
        print("✅ 效能優化完成：")
        for opt in optimizations:
            print(f"   {opt}")
    else:
        print("✅ 效能優化檢查完成（無需優化）")
    
    return html_content


def check_accessibility(html_content: str) -> Dict[str, Any]:
    """無障礙檢查"""
    print("♿ 進行無障礙檢查...")
    
    issues = []
    warnings = []
    
    # 1. 檢查 alt 屬性
    img_tags = re.findall(r'<img[^>]*>', html_content)
    for img in img_tags:
        if 'alt=' not in img:
            issues.append("圖片缺少 alt 屬性")
    
    # 2. 檢查標題結構
    if '<h1>' not in html_content:
        warnings.append("缺少 H1 標題")
    
    # 3. 檢查語言屬性
    if 'lang=' not in html_content and 'lang="' not in html_content:
        issues.append("缺少 lang 屬性")
    
    # 4. 檢查表單標籤
    input_tags = re.findall(r'<input[^>]*>', html_content)
    for inp in input_tags:
        if 'type=' in inp and 'label' not in html_content:
            warnings.append("表單輸入可能缺少標籤")
    
    result = {
        "issues": issues,
        "warnings": warnings,
        "score": max(0, 100 - len(issues) * 10 - len(warnings) * 5)
    }
    
    if issues:
        print(f"❌ 發現 {len(issues)} 個問題：")
        for issue in issues:
            print(f"   - {issue}")
    
    if warnings:
        print(f"⚠️  發現 {len(warnings)} 個警告：")
        for warning in warnings:
            print(f"   - {warning}")
    
    if not issues and not warnings:
        print("✅ 無障礙檢查通過")
    
    print(f"📊 無障礙分數: {result['score']}/100")
    
    return result


def integrate_google_analytics(html_content: str, ga_measurement_id: str = None) -> str:
    """整合 Google Analytics"""
    print("📊 整合 Google Analytics...")
    
    if not ga_measurement_id:
        ga_measurement_id = "G-XXXXXXXXXX"  # 預設值，需要替換
    
    ga_code = f"""
    <!-- Google Analytics 4 (GA4) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={ga_measurement_id}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{ga_measurement_id}', {{
            'page_title': document.title,
            'page_location': window.location.href
        }});
        
        // 轉換追蹤
        function trackConversion(eventName, eventData) {{
            gtag('event', eventName, eventData);
        }}
    </script>
    """
    
    # 檢查是否已有 GA
    if "googletagmanager.com/gtag/js" in html_content:
        print("✅ Google Analytics 已存在")
        return html_content
    
    # 插入到 <head> 中
    if "</head>" in html_content:
        html_content = html_content.replace(
            "</head>",
            ga_code + "\n    </head>"
        )
        print("✅ Google Analytics 已整合")
        if ga_measurement_id == "G-XXXXXXXXXX":
            print("⚠️  請將 G-XXXXXXXXXX 替換為實際的測量 ID")
    else:
        print("⚠️  找不到 </head> 標籤，無法插入 Google Analytics")
    
    return html_content


def main():
    """主函數"""
    print("=" * 70)
    print("首頁品質提升工具")
    print("=" * 70)
    print()
    
    # 1. 載入首頁 HTML
    homepage_file = BASE_DIR / "index.html"
    if not homepage_file.exists():
        print("❌ 找不到首頁檔案（index.html）")
        return 1
    
    print("📄 載入首頁 HTML...")
    html_content = homepage_file.read_text(encoding="utf-8")
    print("✅ 首頁 HTML 已載入")
    print()
    
    # 2. 載入合規資料
    compliance_file = BASE_DIR / "compliance_data.json"
    compliance_data = {}
    if compliance_file.exists():
        compliance_data = json.loads(compliance_file.read_text(encoding="utf-8"))
        print("✅ 合規資料已載入")
    else:
        print("⚠️  找不到合規資料檔案")
    print()
    
    # 3. SEO 優化
    print("=" * 70)
    html_content = optimize_seo(html_content, compliance_data)
    print()
    
    # 4. 效能優化
    print("=" * 70)
    html_content = optimize_performance(html_content)
    print()
    
    # 5. 無障礙檢查
    print("=" * 70)
    accessibility_result = check_accessibility(html_content)
    print()
    
    # 6. Google Analytics 整合
    print("=" * 70)
    html_content = integrate_google_analytics(html_content)
    print()
    
    # 7. 儲存優化後的 HTML
    output_file = BASE_DIR / "index_optimized.html"
    output_file.write_text(html_content, encoding="utf-8")
    print("=" * 70)
    print("✅ 優化完成")
    print("=" * 70)
    print()
    print(f"📁 優化後的檔案: {output_file.name}")
    print()
    print("💡 下一步：")
    print("1. 檢查 index_optimized.html")
    print("2. 如果滿意，可以替換 index.html")
    print("3. 設定 Google Analytics 測量 ID")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
