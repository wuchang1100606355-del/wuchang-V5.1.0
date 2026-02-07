-- v3_mix_edla_gl Android POS 設備納管 SQL 腳本
-- 用途：直接在 Odoo 資料庫中納管設備（當 API 無法訪問時使用）
-- 執行方式：在 Odoo 中執行此 SQL（技術功能 → 資料庫結構 → 執行 SQL）

-- 檢查設備是否已存在
SELECT id, name, ip_address, status 
FROM wuchang_infrastructure_device 
WHERE ip_address = '192.168.50.86' OR name = 'v3_mix_edla_gl';

-- 如果設備不存在，執行以下 INSERT
-- 如果設備已存在，執行 UPDATE（見下方）

-- INSERT 新設備（如果不存在）
INSERT INTO wuchang_infrastructure_device 
(name, ip_address, mac_address, device_type, status, last_seen, note, create_date, write_date, create_uid, write_uid)
VALUES (
    'v3_mix_edla_gl',
    '192.168.50.86',
    '',  -- MAC 地址（如果知道請填入）
    'pos',
    'online',
    NOW(),
    'Android 13 POS 設備，IP: 192.168.50.86:41895，開發者模式: 已開啟，USB/GPU/WiFi 偵錯: 已開啟，納管時間: 2025-01-07',
    NOW(),
    NOW(),
    2,  -- create_uid (通常是 admin 的 ID，根據實際調整)
    2   -- write_uid (通常是 admin 的 ID，根據實際調整)
)
ON CONFLICT DO NOTHING;

-- UPDATE 現有設備（如果已存在）
UPDATE wuchang_infrastructure_device 
SET 
    name = 'v3_mix_edla_gl',
    ip_address = '192.168.50.86',
    device_type = 'pos',
    status = 'online',
    last_seen = NOW(),
    note = 'Android 13 POS 設備，IP: 192.168.50.86:41895，開發者模式: 已開啟，USB/GPU/WiFi 偵錯: 已開啟，更新時間: ' || TO_CHAR(NOW(), 'YYYY-MM-DD HH24:MI:SS'),
    write_date = NOW(),
    write_uid = 2
WHERE ip_address = '192.168.50.86' OR name = 'v3_mix_edla_gl';

-- 驗證納管結果
SELECT id, name, ip_address, device_type, status, last_seen, note
FROM wuchang_infrastructure_device 
WHERE ip_address = '192.168.50.86' OR name = 'v3_mix_edla_gl';
