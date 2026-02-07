# ESG / SDGs 主動賦能佐證（Wuchang AI）

本文件對應本專案的在地賦能作為，整理可稽核之證據來源與量化指標，支援 ESG/SDGs 專案申請。

## 一、對應目標（SDGs）

-   SDG 9 產業/創新/基礎建設：在地 AI 中台（本地 LLM + 儀表板 + 事件稽核）。
-   SDG 11 永續城市與社區：多語 / 長照 / 報修等社區服務技能，提升可近性。
-   SDG 16 和平/正義/健全制度：事件永久記錄（JSONL/CSV）、可追溯可稽核。
-   SDG 17 夥伴關係：可模擬新商家導入腳本、可複製流程 SOP。
    （視情況亦可對應 SDG 4 優質教育：數位素養培力工作坊）

## 二、ESG 對應

-   E（環境）：
    -   無紙化作業（公告草擬、數位看板即時同步）。
    -   遠端診斷與重載降低現場奔波。
-   S（社會）：
    -   多語翻譯（越語/印尼語/英語）降低族群障礙。
    -   長照/報修/法律/補助分流技能，擴大可近性。
-   G（治理）：
    -   本地優先 LLM（`LLM_FALLBACK` 可關閉雲端），強化隱私。
    -   事件永久記錄與 CSV 匯出，支援審計。

## 三、可稽核證據（來源與路徑）

-   即時儀表板：`/dashboard`（SSE 即時事件）
-   事件記錄：`events.log.jsonl` 與 `/events/export.csv`
-   LLM 來源：`/llm/chat` 回傳 `source=local/vertex`，與 `llm.chat` 事件對照
-   裝置狀態：`/devices`（含 `last_seen`）
-   網路佐證：`/network/arp`（路由與節點）
-   實景錄影：`logs/screen-*.mp4`（用 `scripts/record_screen_ffmpeg.ps1` 產出）
-   導入/營運文件：`docs/COMMUNITY_AI_BLUEPRINT.md`、`docs/NEW_MERCHANT_SERVICE_FLOW.md`

## 四、量化指標（KPI 建議）

-   服務使用量：技能執行次數（`skill.execute` 事件計數）
-   回應時間：`/skills/execute` 與 `llm.chat` 事件時間差（P50/P95）
-   一次成功率：`command.push` 後是否需人工介入（可在事件中加標註）
-   多語覆蓋率：翻譯技能 `target` 的語言分布
-   隱私合規率：`source=local` 占比（本地優先）

## 五、如何打包提交

執行：`scripts/collect_evidence.ps1`

-   產生 `logs/evidence/evidence-*.zip`，內含：
    -   `events.csv`、`events.log.jsonl`、`devices.json`、`arp.json`、`llm_chat.json`、`skills.json`
    -   `COMMUNITY_AI_BLUEPRINT.md`、`NEW_MERCHANT_SERVICE_FLOW.md`、`HARDWARE_REQUIREMENTS.md`
    -   最新 `screen-*.mp4`（若存在）

## 六、驗證步驟（審查用）

1. 開啟儀表板 `/dashboard`，檢視 `skill.execute`、`command.push`、`llm.chat` 等事件。
2. 對照 `events.csv` 與錄影檔畫面時間點。
3. 檢視 `llm_chat.json` 是否為 `source=local`（本地優先）。
4. 檢視 `devices.json` 中 `last_seen` 是否持續更新。
