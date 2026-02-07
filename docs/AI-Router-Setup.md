# 總路由 AI 管轄（Local-first, Cloud-fallback）

本規劃將 AI 路由統一：

-   主要：本地 Ollama（路由伺服器 192.168.50.1 或同區網主機）
-   備援：Google Vertex AI（Gemini），以服務帳戶小 J 驗證

## 一、專案中的關鍵設定位置

-   Odoo 模組邏輯：`wuchang_os/addons/wuchang_core/models/ai_logic.py`（先走本地，失敗再走雲端）
-   系統參數（Odoo 內）：
    -   `wuchang.ai_mode`（建議 `local_ollama`）
    -   `wuchang.llm_base_url`（本地 Ollama 位址，例如 `http://192.168.50.1:11434`）
    -   `wuchang.cloud_approved`（`true` 才會啟用雲端備援）
    -   `wuchang.google.project_id`、`wuchang.google.location`
    -   `wuchang.gemini_api_key`（若走 `google.generativeai` REST 需 API Key）
-   容器掛載與憑證：
    -   服務帳戶 JSON 放 `config/gcp/littlej-sa.json`
    -   `docker-compose.yml` 已設 `GOOGLE_APPLICATION_CREDENTIALS=/mnt/jules-config/gcp/littlej-sa.json`

## 二、在 Google Cloud 建立「小 J」服務帳戶

1. 進入目標專案（例如：`my-j-483304`）。
2. IAM & Admin → Service Accounts → Create Service Account：
    - 名稱：`littlej-sa`
    - 說明：`Wuchang Local-first Cloud-fallback AI`
3. 指派角色（最小權限）：
    - `Vertex AI User`（`roles/aiplatform.user`）
    - `Storage Object Viewer`（`roles/storage.objectViewer`）
    - （可選）`Service Usage Consumer`（`roles/serviceusage.serviceUsageConsumer`）
4. 建立金鑰（JSON），下載後放到本機專案：`config/gcp/littlej-sa.json`。
5. 啟用 API：
    - Vertex AI API -（若用 REST Key）Generative Language API

> 你的截圖（IAM 權限對話框）中，新增「主體」時填入此服務帳戶的 Email，角色選 `Vertex AI User` 即可。

## 三、本地（192.168.50.1）Ollama 節點

1. 在 192.168.50.1 主機安裝 Docker，啟動本地 LLM：
    ```bash
    docker run -d --name ollama -p 11434:11434 -v /opt/wuchang/ollama:/root/.ollama ollama/ollama:latest
    # 可選：拉常用模型
    docker exec -it ollama ollama pull llama3.1
    ```
2. 於 Odoo 後台設定：
    - `wuchang.ai_mode = local_ollama`
    - `wuchang.llm_base_url = http://192.168.50.1:11434`
    - `wuchang.cloud_approved = true`（啟用雲端備援）

## 四、筆電（本機 UI）

-   以 `docker-compose.yml` 啟動 `wuchang-web`（Odoo）與 `caddy`。
-   將 `config/gcp/littlej-sa.json` 放妥即可讓雲端備援生效。

## 五、驗證步驟

-   本地：關閉網路或停用 Vertex AI，測試是否仍可由 Ollama 產生回應。
-   雲端備援：將 Ollama 暫停，確認 AI 功能會自動切到 Vertex（`ai_logic.py` 路徑）。

## 六、常見問題

-   若 `vertexai.init` 失敗，檢查：
    -   `GOOGLE_APPLICATION_CREDENTIALS` 是否在容器內可讀。
    -   專案 `project_id` 與 `location`（`us-central1` 等）是否正確。
    -   服務帳戶是否具 `Vertex AI User` 角色。
-   若使用 `google.generativeai` REST，需要在 `wuchang.gemini_api_key` 放入 API Key。
