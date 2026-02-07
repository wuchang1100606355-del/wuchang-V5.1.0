#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
little_j_learning_setup.py

地端小J學習功能配置工具（在抵免額內進行學習功能配置或一次性永久提升之套件升級）

功能：
- Ollama 模型管理（下載、升級、fine-tuning）
- 知識庫增強（RAG、向量資料庫）
- 學習功能配置（持續學習、知識更新）
- 套件升級（一次性永久提升）
"""

import sys
import json
import os
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "little_j_learning_config.json"
SETUP_LOG_FILE = BASE_DIR / "little_j_learning_setup.log"

# Ollama API 端點
OLLAMA_API_BASE = "http://localhost:11434"

# 推薦的 Ollama 模型（適合地端小J）
RECOMMENDED_MODELS = {
    "llama3.2": {
        "name": "llama3.2",
        "size": "3B",
        "description": "輕量級模型，適合本地運行",
        "use_case": "一般對話、系統分析",
        "priority": 1
    },
    "llama3.2:3b": {
        "name": "llama3.2:3b",
        "size": "3B",
        "description": "Llama 3.2 3B 參數版本",
        "use_case": "快速回應、資源節省",
        "priority": 2
    },
    "qwen2.5": {
        "name": "qwen2.5",
        "size": "7B",
        "description": "Qwen 2.5 中文優化模型",
        "use_case": "中文對話、社區分析",
        "priority": 1
    },
    "mistral": {
        "name": "mistral",
        "size": "7B",
        "description": "Mistral 7B 模型",
        "use_case": "多語言支援、推理能力",
        "priority": 2
    }
}

# 學習功能配置選項
LEARNING_FEATURES = {
    "rag_enabled": {
        "name": "RAG (Retrieval-Augmented Generation)",
        "description": "檢索增強生成，整合知識庫",
        "config_file": "rag_config.json",
        "status": "available"
    },
    "vector_database": {
        "name": "向量資料庫",
        "description": "用於知識庫向量化檢索",
        "config_file": "vector_db_config.json",
        "status": "available"
    },
    "fine_tuning": {
        "name": "模型 Fine-tuning",
        "description": "針對五常社區資料進行模型微調",
        "config_file": "fine_tuning_config.json",
        "status": "available"
    },
    "continuous_learning": {
        "name": "持續學習",
        "description": "自動從工作記錄中學習",
        "config_file": "continuous_learning_config.json",
        "status": "available"
    }
}


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌",
        "PROGRESS": "🔄"
    }
    icon = icons.get(level, "•")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{icon} [{timestamp}] [{level}] {message}"
    print(log_entry)
    
    try:
        with open(SETUP_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{log_entry}\n")
    except:
        pass


def check_ollama_connection() -> bool:
    """檢查 Ollama 連線"""
    try:
        response = requests.get(f"{OLLAMA_API_BASE}/api/tags", timeout=5)
        if response.status_code == 200:
            log("Ollama 連線正常", "OK")
            return True
        else:
            log(f"Ollama 連線異常: HTTP {response.status_code}", "ERROR")
            return False
    except requests.exceptions.ConnectionError:
        log("無法連線到 Ollama API，請確認 Ollama 服務正在運行", "ERROR")
        return False
    except Exception as e:
        log(f"檢查 Ollama 連線時發生錯誤: {e}", "ERROR")
        return False


def get_installed_models() -> List[str]:
    """取得已安裝的模型列表"""
    try:
        response = requests.get(f"{OLLAMA_API_BASE}/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            log(f"已安裝 {len(models)} 個模型", "OK")
            return models
        else:
            log(f"取得模型列表失敗: HTTP {response.status_code}", "ERROR")
            return []
    except Exception as e:
        log(f"取得模型列表時發生錯誤: {e}", "ERROR")
        return []


def download_model(model_name: str) -> bool:
    """下載 Ollama 模型"""
    log(f"開始下載模型: {model_name}", "PROGRESS")
    try:
        response = requests.post(
            f"{OLLAMA_API_BASE}/api/pull",
            json={"name": model_name},
            stream=True,
            timeout=300
        )
        
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "status" in data:
                            log(f"下載進度: {data['status']}", "PROGRESS")
                    except:
                        pass
            log(f"模型下載完成: {model_name}", "OK")
            return True
        else:
            log(f"下載模型失敗: HTTP {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"下載模型時發生錯誤: {e}", "ERROR")
        return False


def upgrade_model(model_name: str) -> bool:
    """升級 Ollama 模型（重新下載最新版本）"""
    log(f"開始升級模型: {model_name}", "PROGRESS")
    # 升級實際上就是重新下載
    return download_model(model_name)


def setup_rag_config() -> Dict[str, Any]:
    """設定 RAG 配置"""
    log("設定 RAG 配置", "PROGRESS")
    config = {
        "enabled": True,
        "knowledge_base_path": str(BASE_DIR / "wuchang_community_knowledge_base.json"),
        "index_path": str(BASE_DIR / "wuchang_community_knowledge_index.json"),
        "vector_db_path": str(BASE_DIR / "vector_db"),
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "chunk_size": 500,
        "chunk_overlap": 50,
        "top_k": 5,
        "timestamp": datetime.now().isoformat()
    }
    
    config_file = BASE_DIR / "rag_config.json"
    config_file.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    log(f"RAG 配置已儲存: {config_file.name}", "OK")
    return config


def setup_vector_database_config() -> Dict[str, Any]:
    """設定向量資料庫配置"""
    log("設定向量資料庫配置", "PROGRESS")
    config = {
        "enabled": True,
        "type": "chromadb",  # 或 "faiss", "pinecone"
        "storage_path": str(BASE_DIR / "vector_db"),
        "collection_name": "wuchang_knowledge",
        "embedding_dimension": 384,
        "timestamp": datetime.now().isoformat()
    }
    
    config_file = BASE_DIR / "vector_db_config.json"
    config_file.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    log(f"向量資料庫配置已儲存: {config_file.name}", "OK")
    return config


def setup_fine_tuning_config() -> Dict[str, Any]:
    """設定 Fine-tuning 配置"""
    log("設定 Fine-tuning 配置", "PROGRESS")
    config = {
        "enabled": False,  # 預設關閉，需要時再啟用
        "base_model": "llama3.2",
        "training_data_path": str(BASE_DIR / "fine_tuning_data"),
        "output_model_name": "wuchang-llama3.2",
        "epochs": 3,
        "learning_rate": 0.0001,
        "batch_size": 4,
        "timestamp": datetime.now().isoformat()
    }
    
    config_file = BASE_DIR / "fine_tuning_config.json"
    config_file.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    log(f"Fine-tuning 配置已儲存: {config_file.name}", "OK")
    return config


def setup_continuous_learning_config() -> Dict[str, Any]:
    """設定持續學習配置"""
    log("設定持續學習配置", "PROGRESS")
    config = {
        "enabled": True,
        "learning_sources": [
            "container_collaboration.log",
            "dual_j_work_log.json",
            "container_optimization_suggestions.json"
        ],
        "update_frequency": "daily",
        "knowledge_base_update": True,
        "model_update": False,  # 預設不更新模型，只更新知識庫
        "timestamp": datetime.now().isoformat()
    }
    
    config_file = BASE_DIR / "continuous_learning_config.json"
    config_file.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    log(f"持續學習配置已儲存: {config_file.name}", "OK")
    return config


def install_learning_packages() -> Dict[str, bool]:
    """安裝學習功能所需的 Python 套件"""
    log("安裝學習功能套件", "PROGRESS")
    packages = {
        "chromadb": "chromadb",  # 向量資料庫
        "sentence-transformers": "sentence-transformers",  # 嵌入模型
        "faiss-cpu": "faiss-cpu",  # 向量搜尋（備選）
        "langchain": "langchain",  # RAG 框架
        "langchain-community": "langchain-community"
    }
    
    results = {}
    for package_key, package_name in packages.items():
        try:
            __import__(package_key.replace("-", "_"))
            log(f"套件已安裝: {package_name}", "OK")
            results[package_name] = True
        except ImportError:
            log(f"安裝套件: {package_name}", "PROGRESS")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", package_name],
                    check=True,
                    capture_output=True,
                    text=True
                )
                log(f"已安裝: {package_name}", "OK")
                results[package_name] = True
            except subprocess.CalledProcessError as e:
                log(f"安裝失敗: {package_name} - {e}", "ERROR")
                results[package_name] = False
    
    return results


def main():
    """主函數"""
    log("開始地端小J學習功能配置", "PROGRESS")
    
    # 檢查 Ollama 連線
    if not check_ollama_connection():
        log("請先啟動 Ollama 服務（docker-compose up -d ollama）", "WARN")
        return
    
    # 載入現有配置
    config = {}
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except:
            pass
    
    config["last_setup"] = datetime.now().isoformat()
    
    # 取得已安裝的模型
    installed_models = get_installed_models()
    config["installed_models"] = installed_models
    
    # 檢查並下載推薦模型
    log("檢查推薦模型", "PROGRESS")
    model_results = {}
    for model_id, model_info in RECOMMENDED_MODELS.items():
        model_name = model_info["name"]
        if model_name in installed_models:
            log(f"模型已安裝: {model_name}", "OK")
            model_results[model_id] = {"status": "installed", "name": model_name}
        else:
            log(f"模型未安裝: {model_name}，開始下載", "PROGRESS")
            if download_model(model_name):
                model_results[model_id] = {"status": "installed", "name": model_name}
            else:
                model_results[model_id] = {"status": "failed", "name": model_name}
    
    config["model_setup"] = model_results
    
    # 安裝學習功能套件
    package_results = install_learning_packages()
    config["package_installation"] = package_results
    
    # 設定學習功能
    log("設定學習功能", "PROGRESS")
    learning_configs = {}
    
    # RAG 配置
    learning_configs["rag"] = setup_rag_config()
    
    # 向量資料庫配置
    learning_configs["vector_database"] = setup_vector_database_config()
    
    # Fine-tuning 配置
    learning_configs["fine_tuning"] = setup_fine_tuning_config()
    
    # 持續學習配置
    learning_configs["continuous_learning"] = setup_continuous_learning_config()
    
    config["learning_features"] = learning_configs
    
    # 儲存配置
    CONFIG_FILE.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    log(f"配置已儲存: {CONFIG_FILE.name}", "OK")
    
    # 生成報告
    report = generate_setup_report(config)
    report_file = BASE_DIR / f"little_j_learning_setup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_file.write_text(report, encoding="utf-8")
    log(f"報告已儲存: {report_file.name}", "OK")
    
    print("\n" + "="*60)
    print(report)
    print("="*60)
    
    log("地端小J學習功能配置完成", "OK")


def generate_setup_report(config: Dict[str, Any]) -> str:
    """生成設定報告"""
    report = []
    report.append("# 地端小J學習功能配置報告")
    report.append(f"\n生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 模型狀態
    report.append("## 模型狀態")
    if "model_setup" in config:
        for model_id, result in config["model_setup"].items():
            status_icon = "✅" if result["status"] == "installed" else "❌"
            report.append(f"\n### {status_icon} {result['name']}")
            report.append(f"- 狀態: {result['status']}")
    
    # 套件安裝狀態
    report.append("\n## 套件安裝狀態")
    if "package_installation" in config:
        for package, installed in config["package_installation"].items():
            status_icon = "✅" if installed else "❌"
            report.append(f"- {status_icon} {package}")
    
    # 學習功能配置
    report.append("\n## 學習功能配置")
    if "learning_features" in config:
        for feature_id, feature_config in config["learning_features"].items():
            enabled_icon = "✅" if feature_config.get("enabled", False) else "⚪"
            report.append(f"\n### {enabled_icon} {feature_id}")
            report.append(f"- 啟用: {feature_config.get('enabled', False)}")
            if "config_file" in LEARNING_FEATURES.get(feature_id, {}):
                report.append(f"- 配置檔案: {LEARNING_FEATURES[feature_id]['config_file']}")
    
    return "\n".join(report)


if __name__ == "__main__":
    main()
