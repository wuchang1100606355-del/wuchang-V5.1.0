# 五常 AI 系統遷移 - 完整檢查清單

```
═══════════════════════════════════════════════════════════════════════════
  五常AI系統 v5.1.0 → 伺服器遷移 (192.168.50.84 → 192.168.50.249)
═══════════════════════════════════════════════════════════════════════════
```

## 📋 遷移前準備 (0-1 天)

### 基礎檢查

-   [ ] 驗證當前系統版本: `docker --version`
-   [ ] 檢查磁盤空間: `Get-Volume | Format-Table`
-   [ ] 驗證 Git 狀態: `git status`
-   [ ] 備份重要文件到外部存儲
-   [ ] 記錄當前 Odoo 配置
-   [ ] 導出用戶數據和設置
-   [ ] 驗證 GCP 服務帳戶密鑰可用

### 網絡驗證

-   [ ] Ping 伺服器: `ping 192.168.50.249`
-   [ ] 測試 SSH 連接: `ssh admin@192.168.50.249 "echo OK"`
-   [ ] 檢查防火牆設置
-   [ ] 驗證網絡帶寬 (推薦: 100Mbps+)
-   [ ] 測試網絡穩定性 (ping 5 分鐘)
-   [ ] 記錄伺服器管理員聯繫方式

### 系統文檔

-   [ ] 閱讀 `MIGRATION_PLAN_SERVER_DEPLOYMENT.md`
-   [ ] 閱讀 `MIGRATION_QUICK_START.md`
-   [ ] 檢查所有腳本檔案權限
-   [ ] 驗證 PowerShell 執行策略: `Get-ExecutionPolicy`
-   [ ] 準備遷移日誌存儲位置

---

## 🚀 遷移執行 (1-2 天)

### 步驟 1: 伺服器環境準備

```powershell
# 時間: 30分鐘
# 目標: 準備伺服器基礎環境
```

-   [ ] SSH 連接伺服器確認可用
-   [ ] 將 `server_init.sh` 上傳到伺服器
-   [ ] 執行伺服器初始化腳本
    ```bash
    ssh admin@192.168.50.249 "bash server_init.sh"
    ```
-   [ ] 驗證 Docker 安裝: `docker --version`
-   [ ] 驗證 NFS 配置: `exportfs -v`
-   [ ] 驗證 Samba 配置: `testparm`
-   [ ] 驗證防火牆規則: `ufw status`
-   [ ] 檢查磁盤創建: `df -h /mnt/wuchang-storage`

### 步驟 2: 本機數據備份

```powershell
# 時間: 2-4小時 (取決於數據量)
# 目標: 安全備份所有本機數據
```

-   [ ] 停止所有本機容器
    ```powershell
    docker-compose down
    ```
-   [ ] 備份 Odoo 數據庫
    ```powershell
    docker-compose up db -d
    docker exec wuchangv510-db-1 pg_dump -U odoo admin | Out-File backups\odoo.sql
    ```
-   [ ] 備份 Docker 卷數據
    -   [ ] odoo-db-data
    -   [ ] odoo-web-data
    -   [ ] caddy-data
-   [ ] 備份項目目錄
    -   [ ] wuchang_os/
    -   [ ] config/
    -   [ ] downloads/
    -   [ ] scripts/
    -   [ ] memory_store/
-   [ ] 驗證備份完整性: `dir backups\migration_*`
-   [ ] 備份大小檢查: > 5GB (預期)
-   [ ] 驗證備份可讀: `tar tzf backups\*.tar.gz | head`

### 步驟 3: 數據傳輸

```powershell
# 時間: 1-3小時 (取決於網絡速度)
# 目標: 將所有備份安全傳輸到伺服器
```

-   [ ] 建立伺服器備份接收目錄
    ```bash
    ssh admin@192.168.50.249 "mkdir -p /tmp/wuchang_backup"
    ```
-   [ ] 傳輸備份文件
    ```powershell
    scp -r backups\migration_*\* admin@192.168.50.249:/tmp/wuchang_backup/
    ```
-   [ ] 驗證文件傳輸完整: `ssh admin@192.168.50.249 "ls -lah /tmp/wuchang_backup/"`
-   [ ] 檢查磁盤空間: 確保伺服器有足夠空間
-   [ ] 計算傳輸校驗和 (可選但推薦)

### 步驟 4: 伺服器數據恢復

```bash
# 時間: 1-2小時
# 目標: 在伺服器上恢復所有數據
```

-   [ ] SSH 連接伺服器
-   [ ] 進入項目目錄: `cd ~/wuchang-V5.1.0`
-   [ ] 啟動數據庫容器
    ```bash
    docker-compose -f docker-compose.server.yml up -d db
    sleep 10
    ```
-   [ ] 驗證數據庫啟動: `docker ps | grep db`
-   [ ] 恢復數據庫
    ```bash
    cat /tmp/wuchang_backup/odoo.sql | docker exec -i wuchangv510-db-1 psql -U odoo
    ```
-   [ ] 驗證數據庫恢復
    ```bash
    docker exec wuchangv510-db-1 psql -U odoo -c "SELECT COUNT(*) FROM ir_module_module;"
    ```
-   [ ] 提取 Docker 卷備份
    ```bash
    cd /mnt/wuchang-storage/docker-volumes
    tar xzf /tmp/wuchang_backup/odoo-db-data.tar.gz
    tar xzf /tmp/wuchang_backup/odoo-web-data.tar.gz
    ```
-   [ ] 恢復項目文件
    ```bash
    cd ~/wuchang-V5.1.0
    unzip -o /tmp/wuchang_backup/wuchang_os.zip
    unzip -o /tmp/wuchang_backup/config.zip
    ```
-   [ ] 啟動全部容器
    ```bash
    docker-compose -f docker-compose.server.yml up -d
    ```
-   [ ] 驗證容器啟動
    ```bash
    docker-compose ps
    ```

### 步驟 5: 同步機制配置

```powershell
# 時間: 30分鐘
# 目標: 配置本機與伺服器的雙向同步
```

-   [ ] 執行自動同步配置
    ```powershell
    .\migrate_to_server.ps1 -Action sync-all
    ```
-   [ ] 驗證 Samba 掛載: `Test-Path Z:\`
-   [ ] 測試讀寫權限
    ```powershell
    Set-Content Z:\test.txt "測試"
    Get-Content Z:\test.txt
    Remove-Item Z:\test.txt
    ```
-   [ ] 啟動同步監視器
    ```powershell
    .\sync_with_server.ps1 -Mode watch
    # 按 Ctrl+C 停止 (之後會自動運行)
    ```
-   [ ] 檢查同步配置: `Get-PSDrive Z`

---

## ✅ 驗證與測試 (0.5-1 天)

### 網絡連通性測試

-   [ ] HTTP 訪問測試
    ```powershell
    Invoke-WebRequest http://192.168.50.249:8069 -TimeoutSec 10
    ```
-   [ ] HTTPS 訪問測試 (如適用)
-   [ ] SSH 連接測試
    ```powershell
    ssh admin@192.168.50.249 "echo 'SSH OK'"
    ```
-   [ ] DNS 解析測試 (如配置)
    ```powershell
    Resolve-DnsName wuchang.local
    ```
-   [ ] Ping 測試 (往返延遲 < 10ms)
    ```powershell
    Test-NetConnection 192.168.50.249 -Port 8069
    ```

### 數據完整性測試

-   [ ] 數據庫行數驗證
    ```powershell
    ssh admin@192.168.50.249 "docker exec wuchangv510-db-1 psql -U odoo -c 'SELECT COUNT(*) FROM ir_module_module;'"
    ```
-   [ ] 文件系統驗證
    ```powershell
    @(Test-Path "Z:\docker-volumes", "Z:\odoo-data", "Z:\backups")
    ```
-   [ ] 配置文件驗證 (逐個檢查關鍵配置)
    ```powershell
    ssh admin@192.168.50.249 "cat ~/wuchang-V5.1.0/docker-compose.server.yml | head -20"
    ```

### 應用功能測試

-   [ ] Odoo 登入測試
    -   打開瀏覽器: `http://192.168.50.249:8069`
    -   用默認憑證登入
    -   驗證儀表板加載
    -   檢查模塊列表
-   [ ] 數據庫連接測試
    ```bash
    ssh admin@192.168.50.249 "docker-compose exec db psql -U odoo -c '\dt' | head -20"
    ```
-   [ ] AI 內存存儲測試
    -   驗證路徑存在: `Z:\ai-memory\`
    -   檢查文件同步
-   [ ] 圖像上傳測試
    -   上傳測試文件到 `/mnt/jules`
    -   驗證本機可見
-   [ ] Portainer 訪問測試
    -   打開: `http://192.168.50.249:9000`
    -   驗證容器列表

### 同步測試

-   [ ] 本機 → 伺服器同步
    ```powershell
    .\sync_with_server.ps1 -Mode push
    # 驗證文件在伺服器上更新
    ```
-   [ ] 伺服器 → 本機同步
    ```powershell
    ssh admin@192.168.50.249 "touch /mnt/wuchang-storage/test_$(date +%s).txt"
    .\sync_with_server.ps1 -Mode pull
    # 驗證文件在本機出現
    ```
-   [ ] 雙向實時同步
    ```powershell
    .\sync_with_server.ps1 -Mode watch &
    # 監視3個同步周期
    ```

### 權限與安全測試

-   [ ] 本機用戶權限驗證
    ```powershell
    Get-Acl Z:\ | Format-List
    ```
-   [ ] 伺服器文件權限驗證
    ```bash
    ssh admin@192.168.50.249 "ls -la /mnt/wuchang-storage/ | head"
    ```
-   [ ] SSH 金鑰認證測試
    ```bash
    ssh -i /path/to/key admin@192.168.50.249 "whoami"
    ```
-   [ ] 防火牆開放端口驗證
    ```bash
    ssh admin@192.168.50.249 "sudo ufw status"
    ```

### 備份驗證

-   [ ] 本機備份可用
    ```powershell
    Test-Path "C:\wuchang V5.1.0\backups\migration_*"
    ```
-   [ ] 伺服器備份存在
    ```bash
    ssh admin@192.168.50.249 "ls -la /mnt/wuchang-storage/backups/"
    ```
-   [ ] 備份大小合理
    -   數據庫備份: 100MB-500MB (預期)
    -   卷備份: 1GB+ (預期)
    -   總大小: > 5GB (推薦)

---

## 🎯 上線部署 (1-3 天)

### 遷移驗收

-   [ ] 所有功能測試通過
-   [ ] 性能基準測試完成
-   [ ] 用戶驗收測試(UAT)通過
-   [ ] 安全掃描通過
-   [ ] 備份和恢復程序驗證

### 切換計劃

-   [ ] 制定用戶切換計劃
-   [ ] 安排維護窗口 (建議非高峰時段)
-   [ ] 準備回滾方案
-   [ ] 通知所有相關用戶
-   [ ] 準備技術支持團隊

### 雙運行驗證

-   [ ] 新伺服器運行 1 周
-   [ ] 監控系統日誌
-   [ ] 收集用戶反饋
-   [ ] 驗證性能指標
-   [ ] 檢查資源使用率

### 正式切換

-   [ ] 停止本機服務
-   [ ] 最後一次完整備份
-   [ ] 更新 DNS/負載均衡器
-   [ ] 修改路由器設置 (如需)
-   [ ] 通知外部服務提供商 (如 Cloudflare)
-   [ ] 監控外網訪問
-   [ ] 驗證用戶訪問正常

---

## 📊 遷移後維護 (持續)

### 每日檢查

-   [ ] 容器狀態監視
    ```bash
    ssh admin@192.168.50.249 "/usr/local/bin/wuchang-health-check"
    ```
-   [ ] 磁盤空間監控 (>20%可用空間)
-   [ ] 備份日誌檢查
-   [ ] 系統日誌查看
-   [ ] 同步狀態驗證

### 每周維護

-   [ ] 運行完整系統診斷
-   [ ] 清理過期備份 (>30 天)
-   [ ] 數據庫優化: `VACUUM ANALYZE`
-   [ ] Docker 系統清理
    ```bash
    docker system prune -a
    ```
-   [ ] 日誌輪轉檢查

### 每月維護

-   [ ] 完整系統備份測試
-   [ ] 恢復測試（驗證備份可用性）
-   [ ] 性能基準對比
-   [ ] 安全更新檢查
-   [ ] 用戶反饋收集

### 持續監控

-   [ ] 啟用自動備份
    ```bash
    # 驗證cron任務
    ssh admin@192.168.50.249 "crontab -l | grep wuchang"
    ```
-   [ ] 配置監控告警
-   [ ] 設置日誌聚合
-   [ ] 啟用性能監控
-   [ ] 定期安全審計

---

## 🆘 故障恢復計劃

### 如果遷移失敗

1. [ ] 立即停止遷移進程
2. [ ] 保留所有日誌檔案
3. [ ] 執行緊急回滾
    ```powershell
    .\migrate_to_server.ps1 -Action rollback
    ```
4. [ ] 驗證本機系統恢復
5. [ ] 分析失敗原因
6. [ ] 記錄詳細信息
7. [ ] 聯繫技術支持

### 如果遷移中斷

1. [ ] 檢查網絡連接
2. [ ] 驗證伺服器狀態
3. [ ] 查看容器日誌
4. [ ] 檢查磁盤空間
5. [ ] 從中斷點恢復
6. [ ] 重新啟動同步機制

### 如果發現數據丟失

1. [ ] 立即停止所有操作
2. [ ] 驗證備份完整性
3. [ ] 從備份恢復
    ```bash
    # 在伺服器上
    docker-compose down
    # [恢復備份]
    docker-compose up -d
    ```
4. [ ] 驗證數據恢復
5. [ ] 分析丟失原因
6. [ ] 實施補救措施

---

## 📋 文檔簽名

```
✅ 遷移計劃: MIGRATION_PLAN_SERVER_DEPLOYMENT.md
✅ 快速指南: MIGRATION_QUICK_START.md
✅ 自動腳本: migrate_to_server.ps1
✅ 同步工具: sync_with_server.ps1
✅ 伺服器初始化: server_init.sh
✅ 系統診斷: SYSTEM_DIAGNOSTICS.md
✅ 檢查清單: MIGRATION_CHECKLIST.md (本文檔)
✅ 完整總結: MIGRATION_COMPLETE_SUMMARY.md
```

---

## 📞 支持聯繫

-   **遷移問題**: 查看對應階段的日誌文件
-   **技術支持**: 查看 `MIGRATION_QUICK_START.md` 的故障排除部分
-   **緊急情況**: 執行 `rollback` 操作恢復到備份狀態
-   **更多幫助**: 參考 `MIGRATION_PLAN_SERVER_DEPLOYMENT.md` 的詳細說明

---

**檢查清單版本**: v1.0  
**最後更新**: 2026-01-10  
**狀態**: ✅ 完整準備就緒

---

## 🎉 遷移就緒確認

```
經過完整的準備和計劃，系統已準備好進行遷移。

請確認以下內容：
☑ 已閱讀所有文檔
☑ 已驗證伺服器連接
☑ 已備份重要數據
☑ 已預留足夠時間
☑ 已準備技術支持

準備開始遷移嗎？

執行: cd "C:\wuchang V5.1.0" && .\migrate_to_server.ps1 -Action prepare
```

祝遷移順利！🚀
