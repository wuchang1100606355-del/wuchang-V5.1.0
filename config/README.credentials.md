# 憑證配置（本地優先 / 雲端備援）

此專案採「本地優先（Ollama）→ 雲端備援（Vertex AI/Gemini）」模式。

-   服務帳戶金鑰請放在：`config/gcp-sa.json`
-   Docker 會將 `config/` 以唯讀掛載到容器：`/mnt/jules-config`
-   透過 `docker-compose.override.yml` 指定：`GOOGLE_APPLICATION_CREDENTIALS=/mnt/jules-config/gcp-sa.json`

## 建立服務帳戶（GCP）

1. 建立/選擇專案（例如：`my-j-483304`）。
2. 啟用 API：Vertex AI API。
3. 建立 Service Account：`littlej-vertex@my-j-483304.iam.gserviceaccount.com`（名稱可自訂）。
4. IAM 權限授予此 Service Account 角色：
    - Vertex AI User
    - Storage Object Viewer（若有用到 GCS 資料）
5. 產生 JSON 金鑰並下載為 `gcp-sa.json` → 放到 `config/` 目錄。

## 啟用 Odoo 內部參數（一次性）

容器啟動後，於 `wuchang-web` 內執行：

```bash
odoo shell -d admin < /mnt/extra-addons/../../scripts/odoo_set_vertex_params.py
```

或直接在 Odoo 的「系統參數」設定：

-   `wuchang.cloud_approved=true`
-   `wuchang.google.project_id=my-j-483304`
-   `wuchang.google.location=us-central1`
-   `wuchang.gen_model=gemini-1.5-flash`

## 重啟服務

```bash
docker compose down
copy docker-compose.override.yml.example docker-compose.override.yml
# 將 gcp-sa.json 放入 config/ 後
docker compose up -d
```

完成後，Vertex AI 函式會透過 ADC 自動讀取金鑰並接通 Gemini。
