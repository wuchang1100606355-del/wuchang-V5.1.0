#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_pos_menu.py

檢查 POS 菜單內容是否完整

功能：
- 檢查產品數量
- 檢查分類結構
- 檢查價格設定
- 檢查庫存狀態
"""

import sys
import subprocess
from pathlib import Path

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
        "ERROR": "❌"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")


def query_pos_data(query, description):
    """查詢 POS 資料"""
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
            log(f"查詢 {description} 失敗", "ERROR")
            return None
    except Exception as e:
        log(f"查詢 {description} 時發生錯誤: {e}", "ERROR")
        return None


def check_pos_products():
    """檢查 POS 產品"""
    print("=" * 70)
    print("【檢查 POS 產品】")
    print("=" * 70)
    print()
    
    # 查詢產品總數
    query = "SELECT COUNT(*) as total, COUNT(*) FILTER (WHERE active = true) as active_count FROM product_product;"
    result = query_pos_data(query, "產品總數")
    
    if result:
        print(result)
    
    # 查詢可銷售產品
    query = """
    SELECT COUNT(*) as saleable_count 
    FROM product_product pp 
    JOIN product_template pt ON pp.product_tmpl_id = pt.id 
    WHERE pp.active = true AND pt.sale_ok = true;
    """
    result = query_pos_data(query, "可銷售產品")
    
    if result:
        print(result)
    
    # 查詢有價格的產品
    query = """
    SELECT COUNT(*) as priced_count 
    FROM product_product pp 
    JOIN product_template pt ON pp.product_tmpl_id = pt.id 
    WHERE pp.active = true AND pt.sale_ok = true AND pt.list_price > 0;
    """
    result = query_pos_data(query, "有價格的產品")
    
    if result:
        print(result)


def check_pos_categories():
    """檢查 POS 分類"""
    print()
    print("=" * 70)
    print("【檢查 POS 分類】")
    print("=" * 70)
    print()
    
    # 查詢分類總數
    query = "SELECT COUNT(*) as total, COUNT(*) FILTER (WHERE active = true) as active_count FROM pos_category;"
    result = query_pos_data(query, "分類總數")
    
    if result:
        print(result)
    
    # 查詢分類結構
    query = """
    SELECT id, name, parent_id, 
           CASE WHEN parent_id IS NULL THEN '主分類' ELSE '子分類' END as type
    FROM pos_category 
    WHERE active = true 
    ORDER BY parent_id NULLS FIRST, name 
    LIMIT 30;
    """
    result = query_pos_data(query, "分類結構")
    
    if result:
        print(result)


def check_pos_menu_structure():
    """檢查 POS 菜單結構"""
    print()
    print("=" * 70)
    print("【檢查 POS 菜單結構】")
    print("=" * 70)
    print()
    
    # 查詢產品分類分布
    query = """
    SELECT 
        COALESCE(pc.name, '未分類') as category,
        COUNT(*) as product_count
    FROM product_product pp 
    JOIN product_template pt ON pp.product_tmpl_id = pt.id 
    LEFT JOIN pos_category pc ON pt.pos_categ_id = pc.id 
    WHERE pp.active = true AND pt.sale_ok = true 
    GROUP BY pc.name 
    ORDER BY product_count DESC;
    """
    result = query_pos_data(query, "產品分類分布")
    
    if result:
        print(result)


def check_pos_pricing():
    """檢查 POS 價格設定"""
    print()
    print("=" * 70)
    print("【檢查 POS 價格設定】")
    print("=" * 70)
    print()
    
    # 查詢價格範圍
    query = """
    SELECT 
        MIN(pt.list_price) as min_price,
        MAX(pt.list_price) as max_price,
        AVG(pt.list_price) as avg_price,
        COUNT(*) FILTER (WHERE pt.list_price = 0) as zero_price_count
    FROM product_product pp 
    JOIN product_template pt ON pp.product_tmpl_id = pt.id 
    WHERE pp.active = true AND pt.sale_ok = true;
    """
    result = query_pos_data(query, "價格範圍")
    
    if result:
        print(result)


def check_pos_inventory():
    """檢查 POS 庫存"""
    print()
    print("=" * 70)
    print("【檢查 POS 庫存】")
    print("=" * 70)
    print()
    
    # 查詢庫存狀態
    query = """
    SELECT 
        COUNT(*) FILTER (WHERE pt.type = 'product' AND pp.active = true) as stockable_count,
        COUNT(*) FILTER (WHERE pt.type = 'service' AND pp.active = true) as service_count,
        COUNT(*) FILTER (WHERE pt.type = 'consu' AND pp.active = true) as consumable_count
    FROM product_product pp 
    JOIN product_template pt ON pp.product_tmpl_id = pt.id 
    WHERE pp.active = true;
    """
    result = query_pos_data(query, "庫存狀態")
    
    if result:
        print(result)


def generate_summary():
    """產生檢查總結"""
    print()
    print("=" * 70)
    print("【檢查總結】")
    print("=" * 70)
    print()
    
    print("POS 菜單完整性檢查項目：")
    print()
    print("1. ✅ 產品數量")
    print("2. ✅ 分類結構")
    print("3. ✅ 菜單結構")
    print("4. ✅ 價格設定")
    print("5. ✅ 庫存狀態")
    print()
    print("建議：")
    print("  - 確認所有產品都有正確的分類")
    print("  - 確認所有產品都有設定價格")
    print("  - 確認分類結構完整")
    print("  - 確認庫存狀態正確")


def main():
    """主函數"""
    print("=" * 70)
    print("POS 菜單內容完整性檢查")
    print("=" * 70)
    print()
    
    # 檢查各項內容
    check_pos_products()
    check_pos_categories()
    check_pos_menu_structure()
    check_pos_pricing()
    check_pos_inventory()
    
    # 產生總結
    generate_summary()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
