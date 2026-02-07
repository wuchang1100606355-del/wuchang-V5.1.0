# 系統日誌規範（Wuchang AI）

目的：確保客製化 AI 之所有關鍵事件可被「繁體中文可辨識」且「部分英文字段標準化」的方式每日保存，供稽核/報告/追溯。

## 一、資料夾結構

-   logs/
    -   audit/
        -   conversations/ # 手動或自動保存之對話存檔（.txt / .md）
        -   daily/ # 每日彙整快照（YYYY-MM-DD/）
-   根目錄檔案：events.log.jsonl（即時事件永久記錄，JSONL）

## 二、檔名與命名規則

-   對話存檔：`YYYY-MM-DD-conversation.txt`
-   每日彙整資料夾：`logs/audit/daily/YYYY-MM-DD/`
-   每日匯出檔：
    -   `events-YYYY-MM-DD.csv`
    -   `events-YYYY-MM-DD.jsonl`
    -   `devices-YYYY-MM-DD.json`
    -   `skills-YYYY-MM-DD.json`
    -   `SUMMARY.md`

## 三、語言與格式要求

-   語言：
    -   對外/對人閱讀：以繁體中文為主，必要之技術鍵值（如 type、source、device_id）可保留英文。
-   格式：
    -   即時事件：JSONL（每行一事件），欄位建議包含：
        -   `ts`：ISO8601 時間（UTC）
        -   `type`：事件類型（如 device.register / device.heartbeat / command.push / device.poll / llm.chat / skill.execute）
        -   `device_id`、`device_type`、`hostname`、`ip`（若適用）
        -   `count`、`source`（local|vertex）、`prompt`（若適用）
    -   匯出：CSV（/events/export.csv）

## 四、隱私與遮罩

-   個資（電話、身分證等）不得寫入事件；若需保留，應以 `***` 遮罩或摘要化。
-   內容提示（prompt）僅保存必要上下文，不含個資；如含敏感資訊，應在寫入前先遮罩。

## 五、保存與保留

-   即時事件（events.log.jsonl）：持續累積，建議每日至少一次快照歸檔。
-   每日彙整（daily/）：保留至少 365 天；可採「超期壓縮 + 校驗」策略降低容量。

## 六、排程與自動化

-   以 Windows 工作排程（Task Scheduler）每日 23:59 執行 `scripts/rotate_audit_logs.ps1`：
    -   產出每日資料夾與 CSV/JSONL/裝置/技能快照
    -   生成 SUMMARY.md（含事件類型統計）

## 七、稽核建議

-   月度：抽查 3 日，核對 `/dashboard` 事件流與 `events-*.csv` 對時
-   事件比對：`llm.chat` 的 `source` 應與示範錄影一致（local 優先）
-   變更：任何政策變更（如 LLM_FALLBACK）需另存變更紀錄於 daily/SUMMARY.md

## 八、責任與版本

-   版本：v1.0（2026-01-10）
-   維護：Wuchang AI（系統維運） / 協會秘書處（稽核）
