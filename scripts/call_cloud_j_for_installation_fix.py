#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
呼叫雲端小J進行安裝前修正評估
根據安裝報告生成最妥適的修正建議
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime

WORKSPACE_PATH = Path(__file__).parent.parent
REPORTS_PATH = WORKSPACE_PATH / 'reports'

def load_installation_reports():
    """載入安裝報告"""
    reports = {}
    
    key_reports = [
        'MODULE_INSTALLATION_COMPLETE.md',
        'AUTO_SETUP_READY.md',
        'DEPLOYMENT_HISTORY_SUMMARY.md',
        'SYSTEM_HEALTH_REPORT.md',
        'installation_report_evaluation_20260122_203818.txt'
    ]
    
    for report_name in key_reports:
        report_path = REPORTS_PATH / report_name
        if report_path.exists():
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    reports[report_name] = f.read()
            except Exception as e:
                print(f"⚠️ 無法讀取 {report_name}: {e}")
    
    return reports

def load_deployment_info():
    """載入部署資訊"""
    deployment_files = list(REPORTS_PATH.glob('deployment_info_complete_*.json'))
    if deployment_files:
        latest = max(deployment_files, key=lambda p: p.stat().st_mtime)
        try:
            with open(latest, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 無法讀取部署資訊: {e}")
    return None

def call_local_ollama(prompt: str, model: str = "qwen2:7b") -> str:
    """呼叫本地 Ollama"""
    try:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7
            }
        }
        
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            return response.json().get('response', '')
        else:
            return f"錯誤: {response.status_code}"
    except Exception as e:
        return f"本地 LLM 調用失敗: {e}"

def call_cloud_ai(prompt: str) -> str:
    """呼叫雲端 AI（備援）"""
    # 這裡可以整合 Google Vertex AI 或其他雲端服務
    # 目前先使用本地備援
    return None

def generate_fix_prompt(reports: dict, deployment_info: dict) -> str:
    """生成修正提示詞"""
    
    prompt = f"""你是雲端小J，五常系統的AI助手。請根據以下安裝報告和部署資訊，為伺服器生成最妥適的安裝前修正建議。

## 當前系統狀態

### 部署資訊摘要
- 工作區: {deployment_info.get('workspace_path', 'N/A') if deployment_info else 'N/A'}
- Git 分支: {deployment_info.get('git_branch', 'N/A') if deployment_info else 'N/A'}
- Odoo 模組數量: {deployment_info.get('odoo_modules', {}).get('count', 0) if deployment_info else 0}
- Docker 狀態: {'可用' if deployment_info and deployment_info.get('docker', {}).get('available') else '不可用'}
- 容器數量: {deployment_info.get('docker', {}).get('containers', []) if deployment_info and deployment_info.get('docker') else []}

### 安裝報告摘要
"""
    
    # 添加報告摘要
    for report_name, content in reports.items():
        prompt += f"\n#### {report_name}\n"
        # 只取前500字元避免過長
        prompt += content[:500] + "...\n"
    
    prompt += """
## 已知問題

1. **Docker 容器未運行** - 需要啟動 Docker Desktop
2. **資料庫可能是新資料庫** - 備份目錄為空，可能需要初始化
3. **Odoo IDE 延伸模組安裝問題** - 每次都需要重新安裝且失敗
4. **Pyright 檔案枚舉過慢** - 工作區檔案過多

## 請提供

請生成一份詳細的「安裝前修正建議報告」，包含：

1. **環境準備檢查清單**
   - Docker 環境檢查
   - 資料庫狀態確認
   - 必要服務檢查

2. **問題修正步驟**
   - 針對每個已知問題的具體修正步驟
   - 優先順序排序
   - 執行順序建議

3. **配置優化建議**
   - pyrightconfig.json 配置
   - Docker Compose 優化
   - 資料庫初始化建議

4. **驗證步驟**
   - 修正後的驗證方法
   - 成功標準

請以結構化的 Markdown 格式輸出，確保建議清晰、可執行。
"""
    
    return prompt

def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("  🤖 呼叫雲端小J進行安裝前修正評估")
    print("=" * 60)
    
    # 1. 載入報告
    print("\n📋 載入安裝報告...")
    reports = load_installation_reports()
    print(f"✅ 載入 {len(reports)} 份報告")
    
    # 2. 載入部署資訊
    print("\n📊 載入部署資訊...")
    deployment_info = load_deployment_info()
    if deployment_info:
        print("✅ 部署資訊載入成功")
    else:
        print("⚠️ 未找到部署資訊")
    
    # 3. 生成提示詞
    print("\n🔧 生成修正提示詞...")
    prompt = generate_fix_prompt(reports, deployment_info)
    
    # 4. 呼叫 AI
    print("\n🤖 呼叫雲端小J（使用本地 Ollama 備援）...")
    print("   提示: 如果本地 Ollama 不可用，將使用備援方案")
    
    response = call_local_ollama(prompt, "qwen2:7b")
    
    if response and not response.startswith("錯誤") and not response.startswith("本地 LLM"):
        print("✅ 收到 AI 回應")
        
        # 5. 儲存結果
        output_file = REPORTS_PATH / f'cloud_j_installation_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        report_content = f"""# 雲端小J安裝前修正建議報告

**生成時間:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**來源:** 基於安裝報告和部署資訊分析

---

{response}

---

## 附錄：使用的報告

"""
        for report_name in reports.keys():
            report_content += f"- {report_name}\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n✅ 修正建議已儲存至: {output_file}")
        print("\n" + "=" * 60)
        print("  修正建議摘要")
        print("=" * 60)
        print(response[:500] + "..." if len(response) > 500 else response)
        
    else:
        print("❌ AI 調用失敗，使用備援方案...")
        # 生成基本修正建議
        generate_basic_fix_suggestions(reports, deployment_info)
    
    return 0

def generate_basic_fix_suggestions(reports: dict, deployment_info: dict):
    """生成基本修正建議（備援方案）"""
    output_file = REPORTS_PATH / f'basic_installation_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    
    content = f"""# 安裝前修正建議報告（基本版）

**生成時間:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 1. 環境準備檢查清單

### Docker 環境
- [ ] 啟動 Docker Desktop
- [ ] 確認 Docker 版本: 29.1.3
- [ ] 檢查容器狀態: `docker ps -a`
- [ ] 確認 Volume 掛載正常

### 資料庫狀態
- [ ] 確認資料庫容器運行狀態
- [ ] 檢查資料庫是否為新資料庫
- [ ] 確認是否需要從備份恢復
- [ ] 驗證資料庫連接

### 必要服務
- [ ] Odoo 服務
- [ ] PostgreSQL 資料庫
- [ ] Caddy 反向代理（如需要）
- [ ] Cloudflare Tunnel（如需要）

## 2. 問題修正步驟

### 問題 1: Docker 容器未運行
**優先級:** 🔴 高

**步驟:**
1. 啟動 Docker Desktop
2. 等待 Docker 完全啟動
3. 執行 `docker-compose ps` 檢查狀態
4. 如有問題，執行 `docker-compose up -d`

### 問題 2: Odoo IDE 延伸模組安裝問題
**優先級:** 🟡 中

**步驟:**
1. 執行 `python scripts/fix_odoo_ide_extension.py`
2. 檢查模組在資料庫中的狀態
3. 修復模組狀態為 'installed'
4. 驗證模組是否正常運作

### 問題 3: 資料庫可能是新資料庫
**優先級:** 🟡 中

**步驟:**
1. 檢查資料庫中的模組數量
2. 確認是否有必要資料
3. 如有備份，考慮恢復
4. 如為新資料庫，執行初始化腳本

### 問題 4: Pyright 檔案枚舉過慢
**優先級:** 🟢 低

**步驟:**
1. 建立 `pyrightconfig.json`
2. 排除不必要的目錄
3. 重啟編輯器

## 3. 配置優化建議

### pyrightconfig.json
```json
{{
  "exclude": [
    "**/node_modules",
    "**/__pycache__",
    "**/.git",
    "**/backups",
    "**/logs",
    "**/database/backups",
    "**/containers",
    "**/downloads",
    "**/uploads",
    "**/reports"
  ]
}}
```

### Docker Compose 優化
- 確認所有服務配置正確
- 檢查 Volume 掛載路徑
- 驗證環境變數設定

## 4. 驗證步驟

1. **Docker 驗證**
   ```bash
   docker ps
   docker-compose ps
   ```

2. **資料庫驗證**
   ```bash
   docker exec <db_container> psql -U odoo -d admin -c "SELECT COUNT(*) FROM ir_module_module;"
   ```

3. **Odoo 驗證**
   - 訪問 Odoo 後台
   - 檢查模組列表
   - 確認 IDE 模組狀態

4. **服務驗證**
   - 檢查所有服務端口
   - 驗證服務響應

## 執行順序建議

1. 🔴 啟動 Docker Desktop（必須）
2. 🟡 檢查並修復資料庫狀態
3. 🟡 修復 Odoo IDE 模組問題
4. 🟢 優化 Pyright 配置

---
**注意:** 此為基本建議，建議優先執行高優先級項目。
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ 基本修正建議已儲存至: {output_file}")

if __name__ == '__main__':
    sys.exit(main())
