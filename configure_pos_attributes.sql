-- Odoo POS 產品屬性配置 SQL 腳本
-- 產生時間: 2026-01-20

BEGIN;

-- 建立屬性: 加口味

INSERT INTO product_attribute (id, name, create_variant, display_type, create_date, write_date)
VALUES (1000, 
        '{"en_US": "加口味", "zh_TW": "加口味"}',
        'no_variant', 'radio', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性: 口味選擇

INSERT INTO product_attribute (id, name, create_variant, display_type, create_date, write_date)
VALUES (1001, 
        '{"en_US": "口味選擇", "zh_TW": "口味選擇"}',
        'no_variant', 'radio', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性: 尺寸

INSERT INTO product_attribute (id, name, create_variant, display_type, create_date, write_date)
VALUES (1002, 
        '{"en_US": "尺寸", "zh_TW": "尺寸"}',
        'no_variant', 'radio', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性: 溫度

INSERT INTO product_attribute (id, name, create_variant, display_type, create_date, write_date)
VALUES (1003, 
        '{"en_US": "溫度", "zh_TW": "溫度"}',
        'no_variant', 'radio', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性: 甜度

INSERT INTO product_attribute (id, name, create_variant, display_type, create_date, write_date)
VALUES (1004, 
        '{"en_US": "甜度", "zh_TW": "甜度"}',
        'no_variant', 'radio', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 尺寸 - S (+0.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10000, 1002,
        '{"en_US": "S", "zh_TW": "S"}',
        0.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 尺寸 - M (+15.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10001, 1002,
        '{"en_US": "M", "zh_TW": "M"}',
        15.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 尺寸 - L (+45.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10002, 1002,
        '{"en_US": "L", "zh_TW": "L"}',
        45.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 溫度 - 去冰 (+0.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10003, 1003,
        '{"en_US": "去冰", "zh_TW": "去冰"}',
        0.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 溫度 - 少冰 (+0.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10004, 1003,
        '{"en_US": "少冰", "zh_TW": "少冰"}',
        0.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 溫度 - 正常冰 (+0.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10005, 1003,
        '{"en_US": "正常冰", "zh_TW": "正常冰"}',
        0.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 溫度 - 溫 (+0.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10006, 1003,
        '{"en_US": "溫", "zh_TW": "溫"}',
        0.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 溫度 - 熱 (+0.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10007, 1003,
        '{"en_US": "熱", "zh_TW": "熱"}',
        0.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 甜度 - 無糖 (+0.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10008, 1004,
        '{"en_US": "無糖", "zh_TW": "無糖"}',
        0.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 甜度 - 正常糖 (+0.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10009, 1004,
        '{"en_US": "正常糖", "zh_TW": "正常糖"}',
        0.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 甜度 - 少糖 (+0.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10010, 1004,
        '{"en_US": "少糖", "zh_TW": "少糖"}',
        0.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 甜度 - 半糖 (+0.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10011, 1004,
        '{"en_US": "半糖", "zh_TW": "半糖"}',
        0.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 口味選擇 - 花生 (+0.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10081, 1001,
        '{"en_US": "花生", "zh_TW": "花生"}',
        0.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 口味選擇 - 巧克力 (+0.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10082, 1001,
        '{"en_US": "巧克力", "zh_TW": "巧克力"}',
        0.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 口味選擇 - 奶油 (+0.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10083, 1001,
        '{"en_US": "奶油", "zh_TW": "奶油"}',
        0.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 口味選擇 - 辣味 (+0.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10084, 1001,
        '{"en_US": "辣味", "zh_TW": "辣味"}',
        0.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 加口味 - 焦糖 (+10.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10089, 1000,
        '{"en_US": "焦糖", "zh_TW": "焦糖"}',
        10.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 加口味 - 香草 (+10.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10090, 1000,
        '{"en_US": "香草", "zh_TW": "香草"}',
        10.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 加口味 - 愛爾蘭 (+10.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10091, 1000,
        '{"en_US": "愛爾蘭", "zh_TW": "愛爾蘭"}',
        10.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 加口味 - 榛果 (+10.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10092, 1000,
        '{"en_US": "榛果", "zh_TW": "榛果"}',
        10.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 加口味 - 黑糖 (+10.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10093, 1000,
        '{"en_US": "黑糖", "zh_TW": "黑糖"}',
        10.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 建立屬性值: 加口味 - 交錯 (+15.0)

INSERT INTO product_attribute_value (id, attribute_id, name, price_extra, create_date, write_date)
VALUES (10094, 1000,
        '{"en_US": "交錯", "zh_TW": "交錯"}',
        15.0, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;


COMMIT;

-- 注意：此腳本需要根據實際產品 ID 進行調整
-- 產品屬性連結需要通過 Odoo API 或手動在介面中設定