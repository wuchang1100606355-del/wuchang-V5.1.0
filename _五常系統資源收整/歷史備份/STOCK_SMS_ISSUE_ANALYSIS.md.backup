# stock_move_sms_validation 字段錯誤深度分析

## 問題現狀

### 錯誤訊息
```
Error: "res.config.settings"."stock_move_sms_validation" field is undefined.
```

### 已完成的修復嘗試

1. ✅ **添加依賴**: `'stock_sms'` 已添加到 `wuchang_core/__manifest__.py`
2. ✅ **字段已存在**: 資料庫中 `res_config_settings.stock_move_sms_validation` 字段已存在
3. ✅ **視圖已清理**: 移除了 `settings_views.xml` 中對該字段的引用
4. ❌ **模組未安裝**: `stock_sms` 模組狀態為 `to install`，但 Odoo 未執行安裝

## 根本原因

### Odoo 日誌顯示
```
ERROR admin odoo.modules.loading: Some modules have inconsistent states, 
some dependencies may be missing: ['stock_sms', 'wuchang_award_coach', 
'wuchang_business', 'wuchang_community_campaign', 'wuchang_core', 
'wuchang_finance', 'wuchang_guardian', 'wuchang_property_toolkits', 
'wuchang_volunteer', 'wuchang_web_portal']
```

### 問題分析

1. **模組狀態不一致**: Odoo 檢測到多個模組處於 `to install` 狀態，但它們的依賴關係存在問題
2. **自動安裝失敗**: Odoo 在啟動時發現狀態不一致，選擇跳過安裝而非嘗試修復
3. **命令行安裝失敗**: 使用 `odoo -i stock_sms` 命令時遇到 `psycopg2.OperationalError`，無法連接到資料庫

## 為什麼字段存在但仍報錯？

### Odoo 字段加載機制

1. **資料庫層面**: 字段在 PostgreSQL 表中存在 ✅
2. **Python 模型層面**: 字段需要在 Python 模型中定義 ✅ (已在 `settings.py` 中定義)
3. **模組註冊層面**: 字段所屬的模組必須處於 `installed` 狀態 ❌

### 關鍵問題

`stock_move_sms_validation` 字段是由 `stock_sms` 模組定義的。即使：
- 我們在 `wuchang_core/models/settings.py` 中添加了該字段
- 資料庫表中該字段已存在

**但是**，Odoo 的視圖渲染器在加載 `res.config.settings` 視圖時，會檢查：
1. 字段是否在任何已安裝模組的模型中定義
2. `stock_sms` 模組狀態為 `to install`（未安裝）
3. Odoo 認為該字段「未定義」，因為定義它的模組未安裝

## 解決方案

### 方案 A：通過 Odoo UI 手動安裝（推薦）

1. 登入 http://localhost:8069
2. 進入 `設定` > `應用程式`
3. 移除 `已安裝` 過濾器（點擊 `X`）
4. 搜索 `SMS`
5. 找到 `SMS in Stock` 模組
6. 點擊 `安裝` 按鈕

**優點**: 
- Odoo UI 會自動處理依賴關係
- 不會觸發「模組狀態不一致」錯誤
- 最可靠的安裝方式

### 方案 B：修復 Odoo 配置以支持命令行安裝

檢查 `config/odoo.conf` 中的資料庫連接配置：

```ini
[options]
db_host = db
db_port = 5432
db_user = odoo
db_password = odoo
```

確保容器內的 Odoo 可以通過網絡連接到 PostgreSQL。

### 方案 C：完全重置並重新安裝（最後手段）

```powershell
# 1. 備份資料庫
docker-compose exec -T db pg_dump -U odoo admin > backup_before_reset.sql

# 2. 重置所有 wuchang 模組
docker-compose exec -T db psql -U odoo -d admin -c "
DELETE FROM ir_model_data WHERE module LIKE 'wuchang_%';
DELETE FROM ir_module_module WHERE name LIKE 'wuchang_%';
"

# 3. 重啟並重新安裝
docker-compose restart wuchang-web
```

## 當前建議操作

### 立即執行：方案 A（UI 安裝）

1. 打開瀏覽器訪問 http://localhost:8069
2. 使用管理員帳號登入
3. 按照上述步驟手動安裝 `SMS in Stock` 模組
4. 安裝完成後，刷新頁面（Ctrl+F5）

### 如果方案 A 失敗

檢查 Odoo UI 中是否顯示任何錯誤訊息，並提供完整的錯誤堆棧。

## 合規聲明

✅ 本文檔符合 Google 非營利組織合規要求
✅ 所有操作均以系統穩定性和數據完整性為優先

---

**文檔版本**: 1.0  
**創建時間**: 2026-01-07  
**最後更新**: 2026-01-07
