i# 五常AI 雙J協作檔案索引（Google Tasks + Gemini 3 非營利雲端版）

本索引自動標註所有重要檔案，並說明其在雙J協作（地端小j + 雲端小j）流程中的角色。

---

## 1. 雙J協作核心腳本

- config/ai_agents/enable_double_j_collaboration.py
  - 啟用雙J協作主控腳本，載入形象、驗證設定、啟動協作服務。
- config/sync_from_google_task.py
  - 從 Google Tasks 取得任務內容，並同步到本地檔案。
- config/check_google_task_progress.py
  - 查詢 Google Tasks 任務進度，供雙J協作狀態回報。
- scripts/get_jules_task_direct.py
  - 直接從 Google Tasks 取得任務（支援多種ID格式），不依賴傳統API流量。

---

## 2. 雲端 Gemini 3 非營利版協作

- 透過 Google for Nonprofits 免費配額，雲端小j可自動呼叫 Gemini 3 API 處理高階AI任務。
- 任務分派、進度回報、結果同步皆以 Google Tasks 為橋接核心。

---

## 3. 自動化與索引說明

- 所有協作腳本均可自動化排程（如 Windows 工作排程、Linux cron、Google Apps Script 定時觸發）。
- 任務建立、狀態同步、結果回報皆可自動寫入 Google Tasks，並標註來源（地端/雲端）、處理狀態、完成時間。
- 檔案與腳本皆已標註用途，方便家族AI與人類成員查閱與維護。

---

## 4. 實踐建議

1. 地端小j遇到複雜任務時，自動建立 Google Tasks 任務，並附上檔案索引或需求說明。
2. 雲端小j定時檢查 Google Tasks，遇到新任務自動呼叫 Gemini 3 處理，並將結果寫回任務。
3. 所有協作紀錄、進度、結果都在 Google Tasks 透明同步，家族成員可隨時查閱。

---

> 本索引可自動更新，若有新腳本或協作流程，請補充於本文件。
