#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_pos_attributes_configuration.py

執行 Odoo POS 產品屬性配置

功能：
1. 根據主商品代碼設定產品屬性
2. 處理特殊情況
3. 調整飲品基準價
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


def execute_sql(query: str, description: str = ""):
    """執行 SQL 查詢"""
    try:
        result = subprocess.run(
            ["docker", "exec", "wuchangv510-db-1", "psql", "-U", "odoo", "-d", "admin",
             "-c", query],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)


def get_yirgacheffe_attributes():
    """取得耶加雪夫的屬性配置"""
    query = """
    SELECT 
        pa.id as attribute_id,
        pa.name::text as attribute_name,
        pav.id as value_id,
        pav.name::text as value_name,
        pav.default_extra_price as price_extra
    FROM product_template pt
    JOIN product_template_attribute_line ptal ON pt.id = ptal.product_tmpl_id
    JOIN product_attribute pa ON ptal.attribute_id = pa.id
    JOIN product_template_attribute_value ptav ON ptal.id = ptav.attribute_line_id
    JOIN product_attribute_value pav ON ptav.product_attribute_value_id = pav.id
    WHERE pt.name::text LIKE '%耶加%' AND pt.active = true
    LIMIT 50;
    """
    
    success, result = execute_sql(query, "查詢耶加雪夫屬性")
    return result if success else None


def configure_kenya_aa_with_yirgacheffe_attributes():
    """配置肯亞AA使用耶加雪夫屬性"""
    print("=" * 70)
    print("【配置肯亞AA使用耶加雪夫屬性】")
    print("=" * 70)
    print()
    
    # 查找肯亞AA產品
    query = """
    SELECT id, name::text, default_code, list_price
    FROM product_template
    WHERE name::text LIKE '%肯亞AA%' AND active = true AND sale_ok = true;
    """
    
    success, result = execute_sql(query, "查找肯亞AA產品")
    if not success:
        log("無法查找肯亞AA產品", "ERROR")
        return False
    
    print(result)
    
    # 查找耶加雪夫屬性
    yirgacheffe_attrs = get_yirgacheffe_attributes()
    if yirgacheffe_attrs:
        print("耶加雪夫屬性配置：")
        print(yirgacheffe_attrs)
    else:
        log("未找到耶加雪夫屬性配置", "WARN")
        log("需要先為耶加雪夫設定屬性", "INFO")
    
    log("肯亞AA屬性配置需要通過 Odoo 介面或 API 執行", "INFO")
    return True


def configure_liaoguo_meal_attributes():
    """配置聊國簡餐屬性"""
    print()
    print("=" * 70)
    print("【配置聊國簡餐屬性】")
    print("=" * 70)
    print()
    
    # 查找聊國簡餐產品
    query = """
    SELECT pt.id, pt.name::text, pt.default_code, pt.list_price, pc.name::text as category
    FROM product_template pt
    LEFT JOIN pos_category pc ON pt.categ_id = pc.id
    WHERE pt.active = true AND pt.sale_ok = true
    AND (pc.name::text LIKE '%簡餐%' OR pt.name::text LIKE '%簡餐%' OR pc.name::text LIKE '%聊國%');
    """
    
    success, result = execute_sql(query, "查找聊國簡餐產品")
    if success and result.strip():
        print(result)
        log("找到聊國簡餐產品", "OK")
    else:
        log("未找到聊國簡餐產品，可能需要調整查詢條件", "WARN")
    
    print()
    log("聊國簡餐屬性配置：", "INFO")
    print("  需要設定三個屬性值：")
    print("  - 紅茶 (加價: 0元)")
    print("  - 綠茶 (加價: 0元)")
    print("  - 其他飲品 (加價: -20元)")
    
    return True


def adjust_beverage_base_price():
    """調整飲品基準價為中杯"""
    print()
    print("=" * 70)
    print("【調整飲品基準價為中杯】")
    print("=" * 70)
    print()
    
    log("需要識別飲品產品並檢查基準價", "INFO")
    log("如果基準價不是中杯，需要調整為中杯價格", "INFO")
    log("其他尺寸作為屬性加價處理", "INFO")
    
    return True


def generate_implementation_guide():
    """產生實作指南"""
    print()
    print("=" * 70)
    print("【實作指南】")
    print("=" * 70)
    print()
    
    guide = """
## Odoo POS 產品屬性配置實作指南

### 步驟 1: 建立產品屬性

1. 登入 Odoo: http://localhost:8069
2. 前往：銷售點 > 配置 > 產品屬性
3. 建立以下屬性（設定 create_variant = '不建立變體'）：
   - 尺寸
   - 溫度
   - 甜度
   - 加口味
   - 口味選擇

### 步驟 2: 建立屬性值

為每個屬性建立對應的屬性值，並設定加價：
- 尺寸：S(0元)、M(+15元)、L(+45元) 等
- 溫度：去冰(0元)、少冰(0元)、正常冰(0元)、溫(0元)、熱(0元)
- 甜度：無糖(0元)、正常糖(0元)、少糖(0元)、半糖(0元)
- 加口味：焦糖(+10元)、香草(+10元) 等

### 步驟 3: 連結屬性到產品

根據主商品代碼（03913341-03913353），將對應的屬性連結到產品。

### 步驟 4: 特殊處理

#### 肯亞AA產品
1. 查找肯亞AA產品
2. 查找耶加雪夫產品的屬性配置
3. 將相同的屬性連結到肯亞AA產品

#### 聊國簡餐產品
1. 查找所有聊國簡餐產品
2. 建立「飲品選擇」屬性（不產生變體）
3. 新增三個屬性值：
   - 紅茶 (加價: 0元)
   - 綠茶 (加價: 0元)
   - 其他飲品 (加價: -20元)
4. 將屬性連結到聊國簡餐產品

#### 飲品基準價調整
1. 識別飲品產品
2. 檢查基準價是否為中杯價格
3. 如果不是，調整基準價為中杯價格
4. 其他尺寸（小杯、大杯）作為屬性加價處理

### 步驟 5: 驗證

1. 在 POS 介面測試產品屬性
2. 確認屬性加價正確
3. 確認不產生變體
4. 確認特殊處理正確

---

## ⚠️ 注意事項

1. **備份資料庫**：執行前請先備份
2. **不產生變體**：所有屬性必須設定為不產生變體
3. **屬性加價**：屬性價格作為加價使用
4. **基準價調整**：飲品基準價需調整為中杯

---

## 📁 相關檔案

- `configure_pos_attributes.sql` - SQL 配置腳本（參考用）
- `POS_ATTRIBUTES_CONFIGURATION_PLAN.md` - 配置計劃
- `pos_options_merged.json` - 合併後的選項資料

"""
    
    print(guide)
    
    guide_file = BASE_DIR / "POS_ATTRIBUTES_IMPLEMENTATION_GUIDE.md"
    guide_file.write_text(guide, encoding="utf-8")
    log(f"實作指南已產生: {guide_file}", "OK")
    
    return guide


def main():
    """主函數"""
    print("=" * 70)
    print("Odoo POS 產品屬性配置執行")
    print("=" * 70)
    print()
    
    # 配置肯亞AA
    configure_kenya_aa_with_yirgacheffe_attributes()
    
    # 配置聊國簡餐
    configure_liaoguo_meal_attributes()
    
    # 調整飲品基準價
    adjust_beverage_base_price()
    
    # 產生實作指南
    generate_implementation_guide()
    
    print()
    print("=" * 70)
    print("【總結】")
    print("=" * 70)
    print()
    
    log("配置計劃已產生", "OK")
    print()
    print("下一步：")
    print("  1. 查看 POS_ATTRIBUTES_CONFIGURATION_PLAN.md")
    print("  2. 查看 POS_ATTRIBUTES_IMPLEMENTATION_GUIDE.md")
    print("  3. 通過 Odoo 介面執行配置")
    print("  4. 或使用 Odoo XML-RPC API 自動化配置")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
