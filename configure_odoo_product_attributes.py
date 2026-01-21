#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
configure_odoo_product_attributes.py

配置 Odoo 產品屬性

功能：
1. 根據主商品代碼找對應的組合配置
2. 將配置項目寫入 Odoo 產品屬性
3. 設定屬性加價（不產生變體）
4. 處理特殊情況：
   - 肯亞AA使用耶加雪夫屬性
   - 聊國簡餐屬性改為：紅茶0、綠茶0、其他飲品-20元
   - 飲品基準價改為中杯
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


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
    print(f"{icon} [{level}] {message}")


def query_odoo(query: str, description: str = ""):
    """查詢 Odoo 資料庫"""
    try:
        result = subprocess.run(
            ["docker", "exec", "wuchangv510-db-1", "psql", "-U", "odoo", "-d", "admin",
             "-c", query],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            log(f"查詢失敗: {description}", "ERROR")
            return None
    except Exception as e:
        log(f"查詢時發生錯誤: {e}", "ERROR")
        return None


def load_merged_options():
    """載入合併後的選項資料"""
    json_file = BASE_DIR / "pos_options_merged.json"
    
    if not json_file.exists():
        log("合併後的選項資料不存在", "ERROR")
        return None
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log(f"讀取選項資料失敗: {e}", "ERROR")
        return None


def group_options_by_code(options_data: List[Dict]) -> Dict[str, Dict]:
    """根據題型代碼分組選項"""
    grouped = {}
    
    for item in options_data:
        code = item.get("題型代碼", "")
        if code not in grouped:
            grouped[code] = {
                "combination_name": item.get("題型選項組合名稱", ""),
                "categories": {}
            }
        
        category = item.get("類別", "")
        if category and category not in grouped[code]["categories"]:
            grouped[code]["categories"][category] = []
        
        if category:
            option_detail = {
                "detail": item.get("詳細選項", ""),
                "simple": item.get("簡化選項", ""),
                "value": item.get("數值", "0"),
                "type": item.get("選項類型", ""),
                "code": item.get("選項代碼", "")
            }
            grouped[code]["categories"][category].append(option_detail)
    
    return grouped


def find_product_by_code(default_code: str):
    """根據商品代碼查找產品"""
    query = f"""
    SELECT id, name, default_code, list_price, sale_ok, active
    FROM product_template
    WHERE default_code = '{default_code}' AND active = true;
    """
    
    result = query_odoo(query, f"查找產品 {default_code}")
    return result


def find_products_by_name_pattern(pattern: str):
    """根據名稱模式查找產品"""
    query = f"""
    SELECT id, name, default_code, list_price
    FROM product_template
    WHERE name LIKE '%{pattern}%' AND active = true AND sale_ok = true
    ORDER BY name;
    """
    
    result = query_odoo(query, f"查找產品 {pattern}")
    return result


def create_or_get_attribute(attribute_name: str):
    """建立或取得產品屬性"""
    # 先查詢是否已存在
    query = f"""
    SELECT id, name FROM product_attribute WHERE name = '{attribute_name}';
    """
    
    result = query_odoo(query, f"查詢屬性 {attribute_name}")
    
    # 如果不存在，建立新屬性
    # 注意：這裡需要通過 Odoo API 或直接操作資料庫
    # 為了安全，先查詢，建立操作需要確認
    
    return None


def configure_product_attributes():
    """配置產品屬性"""
    print("=" * 70)
    print("配置 Odoo 產品屬性")
    print("=" * 70)
    print()
    
    # 載入合併後的選項資料
    log("載入選項資料...", "PROGRESS")
    options_data = load_merged_options()
    
    if not options_data:
        log("無法載入選項資料", "ERROR")
        return 1
    
    log(f"載入 {len(options_data)} 筆選項資料", "OK")
    
    # 根據題型代碼分組
    log("分組選項資料...", "PROGRESS")
    grouped_options = group_options_by_code(options_data)
    
    log(f"找到 {len(grouped_options)} 個題型代碼組合", "OK")
    print()
    
    # 顯示分組結果
    print("=" * 70)
    print("【選項分組結果】")
    print("=" * 70)
    print()
    
    for code, data in sorted(grouped_options.items()):
        print(f"題型代碼: {code}")
        print(f"  組合名稱: {data['combination_name']}")
        print(f"  類別: {', '.join(data['categories'].keys())}")
        for category, options in data['categories'].items():
            print(f"    {category}: {len(options)} 個選項")
        print()
    
    # 查找特殊產品
    print("=" * 70)
    print("【查找特殊產品】")
    print("=" * 70)
    print()
    
    # 查找肯亞AA
    log("查找肯亞AA產品...", "PROGRESS")
    kenya_result = find_products_by_name_pattern("肯亞")
    if kenya_result:
        print(kenya_result)
    
    # 查找耶加雪夫
    log("查找耶加雪夫產品...", "PROGRESS")
    yirgacheffe_result = find_products_by_name_pattern("耶加")
    if yirgacheffe_result:
        print(yirgacheffe_result)
    
    # 查找聊國簡餐
    log("查找聊國簡餐產品...", "PROGRESS")
    liaoguo_result = find_products_by_name_pattern("聊國")
    if liaoguo_result:
        print(liaoguo_result)
    
    print()
    print("=" * 70)
    print("【配置說明】")
    print("=" * 70)
    print()
    
    print("需要執行的配置：")
    print()
    print("1. 根據主商品代碼（03913341-03913353）設定產品屬性")
    print("   - 將組合配置的項目寫入產品屬性")
    print("   - 設定屬性加價（不產生變體）")
    print()
    print("2. 特殊處理：")
    print("   - 肯亞AA：使用耶加雪夫的屬性配置")
    print("   - 聊國簡餐：屬性改為「紅茶0、綠茶0、其他飲品-20元」")
    print("   - 飲品基準價：非中杯的改為中杯為基準")
    print()
    print("3. 注意事項：")
    print("   - 屬性設定不產生變體（variant）")
    print("   - 屬性價格作為加價使用")
    print()
    
    return 0


def main():
    """主函數"""
    return configure_product_attributes()


if __name__ == "__main__":
    sys.exit(main())
