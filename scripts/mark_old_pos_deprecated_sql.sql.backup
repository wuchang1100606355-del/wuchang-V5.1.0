-- 標記原 POS 設備為即將汰換
-- 用途：將舊的 POS 設備標記為即將汰換，v3_mix_edla_gl 為主要 POS
-- 執行方式：在 Odoo 中執行 SQL（技術功能 → 資料庫結構 → 執行 SQL）

-- 1. 將 v3_mix_edla_gl 標記為主要 POS 設備
UPDATE wuchang_infrastructure_device
SET 
    is_primary = true,
    status = 'online',
    note = COALESCE(note, '') || '，主要 POS 設備（v3_mix_edla_gl），原 POS 設備即將汰換'
WHERE device_type = 'pos' 
  AND (name = 'v3_mix_edla_gl' OR ip_address = '192.168.50.86');

-- 2. 將其他 POS 設備標記為即將汰換
UPDATE wuchang_infrastructure_device
SET 
    status = 'deprecated',
    is_primary = false,
    note = COALESCE(note, '') || '，已被 v3_mix_edla_gl 取代，即將汰換'
WHERE device_type = 'pos' 
  AND name != 'v3_mix_edla_gl' 
  AND ip_address != '192.168.50.86'
  AND status != 'deprecated';

-- 3. 驗證結果
SELECT 
    id,
    name,
    ip_address,
    device_type,
    status,
    is_primary,
    note
FROM wuchang_infrastructure_device
WHERE device_type = 'pos'
ORDER BY is_primary DESC, status;
