# GCP 憑證放置規範（小 J 服務帳戶）

將在 Google Cloud 專案建立的服務帳戶金鑰 JSON 檔，存到此路徑，檔名建議：`littlej-sa.json`。

容器內掛載位置：`/mnt/jules-config/gcp/littlej-sa.json`

docker-compose 已設定環境變數：`GOOGLE_APPLICATION_CREDENTIALS=/mnt/jules-config/gcp/littlej-sa.json`，因此：

-   Odoo/附屬 Python 程式使用 `vertexai` 時，會自動使用這個金鑰進行 ADC 驗證。
-   若未放置此檔，雲端路徑將不可用（仍可走本地 Ollama 或 REST API Key 模式）。

建議權限（最小化）：

-   `roles/aiplatform.user`（Vertex AI User）
-   `roles/storage.objectViewer`（讀取模型/Artifacts 時可能需要）
-   （可選）`roles/serviceusage.serviceUsageConsumer`

> 注意：請妥善保護此 JSON，不要同步到公開版本庫。此專案已將 `config/` 掛載為唯讀給容器使用。
