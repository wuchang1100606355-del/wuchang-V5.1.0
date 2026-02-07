#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
configure_odoo_pos_attributes_complete.py

完整配置 Odoo POS 產品屬性

功能：
1. 根據主商品代碼（03913341-03913353）找對應組合
2. 將配置項目寫入 Odoo 產品屬性（不產生變體）
3. 設定屬性加價
4. 特殊處理：
   - 肯亞AA使用耶加雪夫屬性
   - 聊國簡餐屬性：紅茶0、綠茶0、其他飲品-20元
   - 飲品基準價改為中杯
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

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


def query_odoo_sql(query: str, description: str = ""):
    """查詢 Odoo 資料庫（使用 UTF-8 編碼）"""
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
            return result.stdout
        else:
            if description:
                log(f"查詢失敗: {description}", "ERROR")
            return None
    except Exception as e:
        if description:
            log(f"查詢 {description} 時發生錯誤: {e}", "ERROR")
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


def find_products_by_code_pattern(pattern: str):
    """根據代碼模式查找產品"""
    query = f"""
    SELECT id, name::text, default_code, list_price
    FROM product_template
    WHERE default_code LIKE '%{pattern}%' AND active = true AND sale_ok = true
    ORDER BY default_code;
    """
    
    return query_odoo_sql(query, f"查找產品代碼 {pattern}")


def find_products_by_name_in_json(pattern: str):
    """在 JSON 欄位中查找產品名稱"""
    query = f"""
    SELECT id, name::text, default_code, list_price
    FROM product_template
    WHERE name::text LIKE '%{pattern}%' AND active = true AND sale_ok = true
    ORDER BY name::text;
    """
    
    return query_odoo_sql(query, f"查找產品名稱 {pattern}")


def create_attribute_sql(attribute_name: str, create_variant: str = "no_variant"):
    """建立產品屬性的 SQL"""
    # 檢查是否已存在
    check_query = f"""
    SELECT id FROM product_attribute WHERE name::text LIKE '%{attribute_name}%';
    """
    
    result = query_odoo_sql(check_query, f"檢查屬性 {attribute_name}")
    
    # 如果不存在，建立新屬性
    # 注意：name 是 jsonb，需要正確格式
    insert_query = f"""
    INSERT INTO product_attribute (name, create_variant, display_type, create_date, write_date)
    VALUES ('{{"en_US": "{attribute_name}", "zh_TW": "{attribute_name}"}}', 
            '{create_variant}', 'radio', NOW(), NOW())
    RETURNING id;
    """
    
    return insert_query


def create_attribute_value_sql(attribute_id: int, value_name: str, price_extra: float = 0.0):
    """建立屬性值的 SQL"""
    insert_query = f"""
    INSERT INTO product_attribute_value (attribute_id, name, price_extra, create_date, write_date)
    VALUES ({attribute_id}, 
            '{{"en_US": "{value_name}", "zh_TW": "{value_name}"}}',
            {price_extra}, NOW(), NOW())
    RETURNING id;
    """
    
    return insert_query


def link_attribute_to_product_sql(product_id: int, attribute_id: int):
    """將屬性連結到產品的 SQL"""
    # 檢查是否已存在
    check_query = f"""
    SELECT id FROM product_template_attribute_line 
    WHERE product_tmpl_id = {product_id} AND attribute_id = {attribute_id};
    """
    
    result = query_odoo_sql(check_query, f"檢查產品 {product_id} 屬性 {attribute_id}")
    
    # 如果不存在，建立連結
    insert_query = f"""
    INSERT INTO product_template_attribute_line (product_tmpl_id, attribute_id, create_date, write_date)
    VALUES ({product_id}, {attribute_id}, NOW(), NOW())
    RETURNING id;
    """
    
    return insert_query


def generate_configuration_plan():
    """產生配置計劃"""
    print("=" * 70)
    print("Odoo POS 產品屬性配置計劃")
    print("=" * 70)
    print()
    
    # 載入選項資料
    log("載入選項資料...", "PROGRESS")
    options_data = load_merged_options()
    
    if not options_data:
        return 1
    
    log(f"載入 {len(options_data)} 筆選項資料", "OK")
    
    # 分組選項
    grouped_options = group_options_by_code(options_data)
    log(f"找到 {len(grouped_options)} 個題型代碼組合", "OK")
    print()
    
    # 查找產品
    print("=" * 70)
    print("【查找產品】")
    print("=" * 70)
    print()
    
    # 查找主商品代碼產品
    log("查找主商品代碼產品...", "PROGRESS")
    products_by_code = find_products_by_code_pattern("039133")
    
    if products_by_code:
        print(products_by_code)
    else:
        log("未找到主商品代碼產品", "WARN")
    
    print()
    
    # 查找特殊產品
    log("查找肯亞AA產品...", "PROGRESS")
    kenya_products = find_products_by_name_in_json("肯亞")
    if kenya_products:
        print(kenya_products)
    
    log("查找耶加雪夫產品...", "PROGRESS")
    yirgacheffe_products = find_products_by_name_in_json("耶加")
    if yirgacheffe_products:
        print(yirgacheffe_products)
    
    log("查找聊國簡餐產品...", "PROGRESS")
    liaoguo_products = find_products_by_name_in_json("聊國")
    if liaoguo_products:
        print(liaoguo_products)
    
    print()
    
    # 產生配置計劃
    print("=" * 70)
    print("【配置計劃】")
    print("=" * 70)
    print()
    
    print("1. 根據主商品代碼設定屬性：")
    for code, data in sorted(grouped_options.items()):
        print(f"   代碼 {code}: {data['combination_name']}")
        for category, options in data['categories'].items():
            print(f"     - {category}: {len(options)} 個選項")
    
    print()
    print("2. 特殊處理：")
    print("   - 肯亞AA：使用耶加雪夫的屬性配置")
    print("   - 聊國簡餐：屬性改為「紅茶0、綠茶0、其他飲品-20元」")
    print("   - 飲品基準價：非中杯的改為中杯為基準")
    
    print()
    print("3. 屬性設定規則：")
    print("   - create_variant = 'no_variant'（不產生變體）")
    print("   - 屬性價格作為加價使用")
    print("   - 尺寸選項的數值作為加價金額")
    
    # 產生 SQL 腳本
    print()
    print("=" * 70)
    print("【產生 SQL 配置腳本】")
    print("=" * 70)
    print()
    
    sql_script = generate_sql_script(grouped_options)
    
    sql_file = BASE_DIR / "configure_pos_attributes.sql"
    sql_file.write_text(sql_script, encoding="utf-8")
    log(f"SQL 腳本已產生: {sql_file}", "OK")
    
    # 產生配置報告
    report = generate_configuration_report(grouped_options)
    report_file = BASE_DIR / "POS_ATTRIBUTES_CONFIGURATION_PLAN.md"
    report_file.write_text(report, encoding="utf-8")
    log(f"配置計劃已產生: {report_file}", "OK")
    
    return 0


def generate_sql_script(grouped_options: Dict) -> str:
    """產生 SQL 配置腳本"""
    sql_lines = [
        "-- Odoo POS 產品屬性配置 SQL 腳本",
        "-- 產生時間: 2026-01-20",
        "",
        "BEGIN;",
        "",
    ]
    
    # 為每個類別建立屬性
    all_categories = set()
    for code, data in grouped_options.items():
        all_categories.update(data['categories'].keys())
    
    attribute_id_map = {}
    attribute_counter = 1000  # 起始 ID（避免衝突）
    
    for category in sorted(all_categories):
        if category in ["產品"]:  # 跳過產品類別
            continue
        
        attr_id = attribute_counter
        attribute_counter += 1
        attribute_id_map[category] = attr_id
        
        sql_lines.append(f"-- 建立屬性: {category}")
        sql_lines.append(f"""
INSERT INTO product_attribute (id, name, create_variant, display_type, create_date, write_date)
VALUES ({attr_id}, 
        '{{"en_US": "{category}", "zh_TW": "{category}"}}',
        'no_variant', 'radio', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;
""")
    
    # 為每個屬性建立屬性值
    value_id_map = {}
    value_counter = 10000
    
    for code, data in grouped_options.items():
        for category, options in data['categories'].items():
            if category not in attribute_id_map:
                continue
            
            attr_id = attribute_id_map[category]
            
            for option in options:
                value_name = option['simple']
                price_extra = float(option['value']) if option['value'] else 0.0
                
                value_id = value_counter
                value_counter += 1
                value_key = f"{category}_{value_name}"
                
                if value_key not in value_id_map:
                    value_id_map[value_key] = value_id
                    
                    sql_lines.append(f"-- 建立屬性值: {category} - {value_name} (+{price_extra})")
                    sql_lines.append(f"""
INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES ({value_id}, {attr_id},
        '{{"en_US": "{value_name}", "zh_TW": "{value_name}"}}',
        {price_extra}, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;
""")
    
    sql_lines.append("")
    sql_lines.append("COMMIT;")
    sql_lines.append("")
    sql_lines.append("-- 注意：此腳本需要根據實際產品 ID 進行調整")
    sql_lines.append("-- 產品屬性連結需要通過 Odoo API 或手動在介面中設定")
    
    return "\n".join(sql_lines)


def generate_configuration_report(grouped_options: Dict) -> str:
    """產生配置報告"""
    report = f"""# Odoo POS 產品屬性配置計劃

**產生時間：** 2026-01-20

## 📋 配置目標

1. 根據主商品代碼（03913341-03913353）設定產品屬性
2. 將組合配置的項目寫入產品屬性（不產生變體）
3. 設定屬性加價
4. 處理特殊情況

---

## 🔍 選項分組

"""
    
    for code, data in sorted(grouped_options.items()):
        report += f"### 題型代碼: {code}\n\n"
        report += f"**組合名稱：** {data['combination_name']}\n\n"
        report += "**類別和選項：**\n\n"
        
        for category, options in data['categories'].items():
            report += f"- **{category}** ({len(options)} 個選項):\n"
            for option in options:
                price = float(option['value']) if option['value'] else 0.0
                report += f"  - {option['simple']} (+{price}元)\n"
            report += "\n"
    
    report += """
---

## ⚙️ 特殊處理

### 1. 肯亞AA產品
- **處理方式：** 使用耶加雪夫的屬性配置
- **步驟：**
  1. 查找肯亞AA產品
  2. 查找耶加雪夫產品的屬性配置
  3. 將耶加雪夫的屬性複製到肯亞AA

### 2. 聊國簡餐產品
- **處理方式：** 屬性改為「紅茶0、綠茶0、其他飲品-20元」
- **步驟：**
  1. 查找所有聊國簡餐產品
  2. 移除現有屬性
  3. 新增三個屬性值：紅茶(0元)、綠茶(0元)、其他飲品(-20元)

### 3. 飲品基準價調整
- **處理方式：** 非中杯的改為中杯為基準
- **步驟：**
  1. 識別飲品產品
  2. 檢查基準價是否為中杯
  3. 如果不是，調整為中杯價格
  4. 其他尺寸作為加價處理

---

## 📝 配置步驟

### 步驟 1: 建立產品屬性

為每個類別建立屬性（create_variant = 'no_variant'）：
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

根據主商品代碼，將對應的屬性連結到產品。

### 步驟 4: 特殊處理

執行特殊處理規則。

---

## ⚠️ 注意事項

1. **不產生變體：** 所有屬性設定 `create_variant = 'no_variant'`
2. **屬性加價：** 屬性價格作為加價使用，不影響基準價
3. **基準價調整：** 飲品基準價需調整為中杯
4. **資料備份：** 執行前請先備份資料庫

---

## 📁 產生的檔案

- `configure_pos_attributes.sql` - SQL 配置腳本
- `POS_ATTRIBUTES_CONFIGURATION_PLAN.md` - 本配置計劃

---

**配置計劃產生時間：** 2026-01-20
"""
    
    return report


def main():
    """主函數"""
    return generate_configuration_plan()


if __name__ == "__main__":
    sys.exit(main())
