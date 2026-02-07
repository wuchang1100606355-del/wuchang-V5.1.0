#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deploy_cloud_llm.py

在 Google Cloud 部署大型開源 LLM 模型

功能：
- 建立 Cloud Storage bucket 儲存模型
- 建立 Cloud Run 服務運行 Ollama
- 配置 API 端點
- 整合到現有系統
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

PROJECT_ID = "my-j-483304"
REGION = "asia-east1"
BUCKET_NAME = f"{PROJECT_ID}-llm-models"
SERVICE_NAME = "ollama-llm"
MODEL_NAME = "qwen2:7b"  # 或 llama3.1:8b

def log(message: str, level: str = "INFO"):
    """輸出日誌訊息"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌",
        "PROGRESS": "🔄"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")

def check_gcloud_installed() -> bool:
    """檢查 gcloud 是否已安裝"""
    try:
        result = subprocess.run(
            ["gcloud", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        log("✓ gcloud 已安裝", "OK")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        log("✗ gcloud 未安裝，請先安裝 Google Cloud SDK", "ERROR")
        return False

def check_gcloud_auth() -> bool:
    """檢查 gcloud 認證"""
    try:
        result = subprocess.run(
            ["gcloud", "auth", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        if "ACTIVE" in result.stdout:
            log("✓ gcloud 已認證", "OK")
            return True
        else:
            log("✗ gcloud 未認證，請執行: gcloud auth login", "ERROR")
            return False
    except subprocess.CalledProcessError:
        log("✗ 無法檢查 gcloud 認證狀態", "ERROR")
        return False

def create_storage_bucket() -> bool:
    """建立 Cloud Storage bucket"""
    log(f"建立 Cloud Storage bucket: {BUCKET_NAME}", "PROGRESS")
    
    try:
        # 檢查 bucket 是否已存在
        result = subprocess.run(
            ["gcloud", "storage", "buckets", "describe", f"gs://{BUCKET_NAME}"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            log(f"✓ Bucket {BUCKET_NAME} 已存在", "OK")
            return True
        
        # 建立新 bucket
        result = subprocess.run(
            [
                "gcloud", "storage", "buckets", "create",
                f"gs://{BUCKET_NAME}",
                f"--location={REGION}",
                f"--project={PROJECT_ID}"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        
        log(f"✓ Bucket {BUCKET_NAME} 建立成功", "OK")
        return True
        
    except subprocess.CalledProcessError as e:
        log(f"✗ 建立 bucket 失敗: {e.stderr.strip()}", "ERROR")
        return False

def create_dockerfile() -> Path:
    """建立 Dockerfile"""
    dockerfile_content = """FROM ollama/ollama:latest

# 設定工作目錄
WORKDIR /root/.ollama

# 暴露端口
EXPOSE 11434

# 啟動 Ollama
CMD ["ollama", "serve"]
"""
    
    dockerfile_path = BASE_DIR / "cloud_llm" / "Dockerfile"
    dockerfile_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        dockerfile_path.write_text(dockerfile_content, encoding='utf-8')
        log(f"✓ Dockerfile 已建立: {dockerfile_path}", "OK")
        return dockerfile_path
    except Exception as e:
        log(f"✗ 建立 Dockerfile 失敗: {e}", "ERROR")
        return None

def build_and_push_image(dockerfile_path: Path) -> bool:
    """建置並推送 Docker 映像"""
    image_name = f"gcr.io/{PROJECT_ID}/{SERVICE_NAME}"
    
    log(f"建置 Docker 映像: {image_name}", "PROGRESS")
    
    try:
        # 建置映像
        result = subprocess.run(
            [
                "gcloud", "builds", "submit",
                "--tag", image_name,
                "--project", PROJECT_ID,
                str(dockerfile_path.parent)
            ],
            capture_output=True,
            text=True,
            check=True
        )
        
        log(f"✓ Docker 映像建置並推送成功: {image_name}", "OK")
        return True
        
    except subprocess.CalledProcessError as e:
        log(f"✗ 建置映像失敗: {e.stderr.strip()}", "ERROR")
        return False

def deploy_cloud_run(image_name: str) -> bool:
    """部署 Cloud Run 服務"""
    log(f"部署 Cloud Run 服務: {SERVICE_NAME}", "PROGRESS")
    
    try:
        result = subprocess.run(
            [
                "gcloud", "run", "deploy", SERVICE_NAME,
                "--image", image_name,
                "--platform", "managed",
                "--region", REGION,
                "--memory", "16Gi",
                "--cpu", "4",
                "--allow-unauthenticated",
                "--project", PROJECT_ID
            ],
            capture_output=True,
            text=True,
            check=True
        )
        
        # 提取服務 URL
        for line in result.stdout.split('\n'):
            if 'Service URL:' in line:
                service_url = line.split('Service URL:')[1].strip()
                log(f"✓ Cloud Run 服務部署成功", "OK")
                log(f"  服務 URL: {service_url}", "INFO")
                return True
        
        log(f"✓ Cloud Run 服務部署成功", "OK")
        return True
        
    except subprocess.CalledProcessError as e:
        log(f"✗ 部署 Cloud Run 失敗: {e.stderr.strip()}", "ERROR")
        return False

def download_model_locally() -> bool:
    """在本地下載模型（用於測試）"""
    log(f"在本地下載模型: {MODEL_NAME}", "PROGRESS")
    
    try:
        result = subprocess.run(
            [
                "docker", "exec", "wuchangv510-ollama-1",
                "ollama", "pull", MODEL_NAME
            ],
            capture_output=True,
            text=True,
            check=True
        )
        
        log(f"✓ 模型 {MODEL_NAME} 下載成功", "OK")
        return True
        
    except subprocess.CalledProcessError as e:
        log(f"✗ 下載模型失敗: {e.stderr.strip()}", "ERROR")
        log("  提示：請確認 Ollama 容器正在運行", "WARN")
        return False

def create_integration_code() -> Path:
    """建立整合程式碼"""
    integration_code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cloud_llm_integration.py

雲端 LLM 整合程式碼
"""

import requests
from typing import Optional

# Cloud Run 服務 URL（部署後更新）
CLOUD_LLM_URL = "https://{SERVICE_NAME}-xxx.run.app"  # 請更新為實際 URL

def call_cloud_llm(prompt: str, model: str = "{MODEL_NAME}") -> Optional[str]:
    """調用雲端 LLM"""
    try:
        response = requests.post(
            f"{{CLOUD_LLM_URL}}/api/generate",
            json={{
                "model": model,
                "prompt": prompt,
                "stream": False
            }},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "")
        else:
            print(f"錯誤: {{response.status_code}} - {{response.text}}")
            return None
            
    except Exception as e:
        print(f"調用雲端 LLM 失敗: {{e}}")
        return None

def call_local_llm(prompt: str, model: str = "qwen2:0.5b") -> Optional[str]:
    """調用本地 LLM（備援）"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={{
                "model": model,
                "prompt": prompt,
                "stream": False
            }},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "")
        else:
            return None
            
    except Exception as e:
        print(f"調用本地 LLM 失敗: {{e}}")
        return None

def smart_route(prompt: str, task_type: str = "simple") -> Optional[str]:
    """智能路由：根據任務類型選擇 LLM"""
    
    if task_type == "simple":
        # 簡單任務：使用本地模型
        return call_local_llm(prompt, "qwen2:0.5b")
    else:
        # 複雜任務：使用雲端模型
        result = call_cloud_llm(prompt, "{MODEL_NAME}")
        if result is None:
            # 如果雲端失敗，降級到本地
            return call_local_llm(prompt, "qwen2:0.5b")
        return result

if __name__ == "__main__":
    # 測試
    result = smart_route("解釋什麼是機器學習", task_type="complex")
    print(result)
'''
    
    integration_path = BASE_DIR / "scripts" / "cloud_llm_integration.py"
    
    try:
        integration_path.write_text(integration_code, encoding='utf-8')
        log(f"✓ 整合程式碼已建立: {integration_path}", "OK")
        return integration_path
    except Exception as e:
        log(f"✗ 建立整合程式碼失敗: {e}", "ERROR")
        return None

def generate_deployment_guide() -> Path:
    """產生部署指南"""
    guide_content = f"""# 雲端 LLM 部署指南

**建立時間：** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**專案 ID：** {PROJECT_ID}
**模型：** {MODEL_NAME}

---

## 📋 部署步驟

### 步驟 1：準備環境

1. **確認 gcloud 已安裝**
   ```bash
   gcloud --version
   ```

2. **認證 gcloud**
   ```bash
   gcloud auth login
   gcloud config set project {PROJECT_ID}
   ```

3. **啟用必要的 API**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable storage-api.googleapis.com
   ```

### 步驟 2：建立 Cloud Storage bucket

```bash
gsutil mb -p {PROJECT_ID} -l {REGION} gs://{BUCKET_NAME}
```

### 步驟 3：下載模型（本地測試）

```bash
docker exec wuchangv510-ollama-1 ollama pull {MODEL_NAME}
```

### 步驟 4：建置並部署

```bash
# 建置 Docker 映像
gcloud builds submit --tag gcr.io/{PROJECT_ID}/{SERVICE_NAME} cloud_llm/

# 部署 Cloud Run
gcloud run deploy {SERVICE_NAME} \\
  --image gcr.io/{PROJECT_ID}/{SERVICE_NAME} \\
  --platform managed \\
  --region {REGION} \\
  --memory 16Gi \\
  --cpu 4 \\
  --allow-unauthenticated \\
  --project {PROJECT_ID}
```

### 步驟 5：測試服務

```bash
# 獲取服務 URL
SERVICE_URL=$(gcloud run services describe {SERVICE_NAME} \\
  --region {REGION} \\
  --format 'value(status.url)')

# 測試 API
curl -X POST "$SERVICE_URL/api/generate" \\
  -H "Content-Type: application/json" \\
  -d '{{"model": "{MODEL_NAME}", "prompt": "Hello", "stream": false}}'
```

### 步驟 6：整合到系統

更新 `scripts/cloud_llm_integration.py` 中的 `CLOUD_LLM_URL` 為實際服務 URL。

---

## 💰 成本估算

**使用免費試用額度：**
- Cloud Run 部署：$200-$300
- 前3個月運行：$600-$1,200
- **總計：** $800-$1,500（完全由免費額度覆蓋）

**長期成本（3個月後）：**
- 低使用量：$50-$150/月
- 中使用量：$150-$400/月
- 可用 Google Cloud 非營利抵免額（$350/月）覆蓋

---

## ✅ 檢查清單

- [ ] gcloud 已安裝並認證
- [ ] 必要的 API 已啟用
- [ ] Cloud Storage bucket 已建立
- [ ] Docker 映像已建置
- [ ] Cloud Run 服務已部署
- [ ] 服務 URL 已取得
- [ ] API 測試成功
- [ ] 整合程式碼已更新
- [ ] 智能路由已配置

---

**詳細報告：** `reports/CLOUD_LLM_DEPLOYMENT_PLAN.md`
"""
    
    guide_path = BASE_DIR / "reports" / "CLOUD_LLM_DEPLOYMENT_GUIDE.md"
    
    try:
        guide_path.write_text(guide_content, encoding='utf-8')
        log(f"✓ 部署指南已建立: {guide_path}", "OK")
        return guide_path
    except Exception as e:
        log(f"✗ 建立部署指南失敗: {e}", "ERROR")
        return None

def main():
    print("=" * 80)
    print("雲端大型開源 LLM 部署工具")
    print("=" * 80)
    print()
    
    log("開始部署流程...", "INFO")
    print()
    
    # 檢查環境
    if not check_gcloud_installed():
        return
    
    if not check_gcloud_auth():
        log("請先執行: gcloud auth login", "WARN")
        return
    
    print()
    
    # 步驟 1：建立 Cloud Storage bucket
    if not create_storage_bucket():
        log("跳過 bucket 建立，繼續其他步驟", "WARN")
    
    print()
    
    # 步驟 2：建立 Dockerfile
    dockerfile_path = create_dockerfile()
    if not dockerfile_path:
        log("無法建立 Dockerfile，請手動建立", "ERROR")
        return
    
    print()
    
    # 步驟 3：下載模型（本地測試）
    log("提示：建議先在本地下載模型進行測試", "INFO")
    download_model_locally()
    
    print()
    
    # 步驟 4：建置並推送映像（需要手動執行）
    log("下一步：建置並推送 Docker 映像", "INFO")
    log("執行命令：", "INFO")
    print(f"  gcloud builds submit --tag gcr.io/{PROJECT_ID}/{SERVICE_NAME} {dockerfile_path.parent}")
    print()
    
    # 步驟 5：部署 Cloud Run（需要手動執行）
    log("然後：部署 Cloud Run 服務", "INFO")
    log("執行命令：", "INFO")
    print(f"  gcloud run deploy {SERVICE_NAME} \\")
    print(f"    --image gcr.io/{PROJECT_ID}/{SERVICE_NAME} \\")
    print(f"    --platform managed \\")
    print(f"    --region {REGION} \\")
    print(f"    --memory 16Gi \\")
    print(f"    --cpu 4 \\")
    print(f"    --allow-unauthenticated \\")
    print(f"    --project {PROJECT_ID}")
    print()
    
    # 建立整合程式碼
    integration_path = create_integration_code()
    
    # 產生部署指南
    guide_path = generate_deployment_guide()
    
    print()
    log("✅ 準備工作完成！", "OK")
    print()
    log(f"請查看部署指南: {guide_path}", "INFO")
    log(f"整合程式碼: {integration_path}", "INFO")
    log("詳細計劃: reports/CLOUD_LLM_DEPLOYMENT_PLAN.md", "INFO")

if __name__ == "__main__":
    main()
