# POS 模擬器 500 錯誤修復指南

## 🚨 問題描述

訪問 `http://localhost:8069/pos_simulator` 時返回 **500 內部伺服器錯誤**。

### 錯誤訊息
```
ValueError: External ID not found in the system: wuchang_core.pos_simulator_page
```

## 🔍 問題根源

**視圖模板未在資料庫中註冊**

- `pos_simulator.xml` 文件存在
- 但未在 `__manifest__.py` 的 `data` 列表中
- 導致視圖沒有被載入到資料庫

## ✅ 已執行的修復

### 1. 修復 manifest 配置

已將 `'views/pos_simulator.xml'` 添加到 `wuchang_core/__manifest__.py` 的 `data` 列表中。

**修改位置**：
```python
'views/property_views.xml',
'views/pos_simulator.xml',  # ← 新增
```

## 🔧 下一步：升級模組

### 方法 1：在 Odoo 界面中升級（推薦）

1. **訪問 Odoo**
   - 打開 http://localhost:8069
   - 使用管理員帳號登入

2. **進入應用程式管理**
   - 點擊左上角 **九宮格圖標** (應用程式選單)
   - 選擇 **應用程式** (Apps)

3. **移除過濾器**
   - 在搜索框上方，點擊 **「已安裝」** 過濾器標籤上的 **X** 圖標

4. **搜索並升級模組**
   - 在搜索框中輸入：`wuchang_core`
   - 找到 **Wuchang Core** 模組
   - 點擊 **「升級」** (Upgrade) 按鈕
   - 等待升級完成（通常需要 10-30 秒）

5. **驗證修復**
   - 訪問 http://localhost:8069/pos_simulator
   - 應該可以正常顯示 POS 模擬器頁面

### 方法 2：通過命令行升級（如果方法 1 失敗）

```powershell
# 注意：需要正確的資料庫連接參數
docker-compose exec -T wuchang-web odoo -d admin -u wuchang_core --stop-after-init --db_host=db --db_user=odoo --db_password=odoo
```

然後重啟服務：
```powershell
docker-compose restart wuchang-web
```

## 📋 驗證步驟

升級完成後，驗證視圖是否已載入：

```powershell
docker-compose exec -T db psql -U odoo -d admin -c "SELECT id, name, type, key FROM ir_ui_view WHERE key = 'wuchang_core.pos_simulator_page';"
```

應該返回一行記錄。

## 🎯 POS 模擬器功能

升級成功後，POS 模擬器將提供：

- ✅ 山水風格 POS 界面
- ✅ 3D 樓層圖（桌位管理）
- ✅ AI 功能（研發新品、殺價、點餐解析、題詩）
- ✅ 語音輸入
- ✅ 客戶管理（檔案、習慣、標籤）

## 📝 相關配置

POS 模擬器需要以下配置參數（可選）：

- `wuchang.gemini_api_key` - Gemini API 金鑰（用於 AI 功能）
- `wuchang.llm_base_url` - LLM 服務 URL（用於地端 AI）
- `wuchang.pos.menu_json` - 菜單 JSON 數據
- `wuchang.store.default` - 預設店舖名稱

## ✅ 合規聲明

符合 Google 非營利組織合規要求

---

## 📝 最後更新

- **修復時間**: 2026-01-07 22:53
- **修復內容**: 將 `pos_simulator.xml` 添加到 manifest data 列表
- **待執行**: 升級 wuchang_core 模組
