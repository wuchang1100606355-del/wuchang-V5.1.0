# Odoo 服務預覽摘要

## 服務狀態

- **Odoo Web**: http://localhost:8069
- **服務狀態**: 運行中
- **檢查時間**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## 相關服務鏈接

### 主要服務
- **Odoo 主界面**: http://localhost:8069
- **Odoo 應用程式管理**: http://localhost:8069/web#action=base.open_module_tree
- **Odoo 設定**: http://localhost:8069/web#action=base.action_res_config_settings

### 其他服務（如果運行中）
- **Portainer**: http://localhost:9000
- **Uptime Kuma**: http://localhost:3001
- **Ollama**: http://localhost:11434
- **Open WebUI**: http://localhost:8080

## 當前修復狀態

### stock_sms 模組
- **模組狀態**: installed
- **模組版本**: 17.0.1.0
- **字段狀態**: stock_move_sms_validation 字段已存在於資料庫

### 注意事項
- 如果瀏覽器中仍出現 `stock_move_sms_validation` 字段錯誤，請：
  1. 刷新頁面（Ctrl+F5）
  2. 清除瀏覽器緩存
  3. 如果問題持續，進入 Odoo UI 升級 stock_sms 模組

## 合規聲明

✅ 符合 Google 非營利組織合規要求
