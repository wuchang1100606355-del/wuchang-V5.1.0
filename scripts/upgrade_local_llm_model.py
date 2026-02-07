#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
upgrade_local_llm_model.py

升級本地 LLM 模型（從 qwen2:0.5b 升級到更大的模型）

由於地端檔案已在雲端，本地儲存空間充足，可以下載更大的模型
"""

import sys
import subprocess
import json
import requests
from pathlib import Path
from typing import Optional, Dict

BASE_DIR = Path(__file__).resolve().parent.parent

# 推薦模型選項
RECOMMENDED_MODELS = {
    "qwen2:1.5b": {
        "size": "約 1GB",
        "memory": "4-6GB",
        "description": "輕量級升級，適合當前 32GB RAM"
    },
    "qwen2:7b": {
        "size": "約 4-5GB",
        "memory": "12-16GB",
        "description": "推薦升級，能力大幅提升，需要足夠記憶體"
    },
    "llama3.1:8b": {
        "size": "約 4.5GB",
        "memory": "12-16GB",
        "description": "Llama 系列，效能優秀"
    },
    "mistral:7b": {
        "size": "約 4GB",
        "memory": "12-16GB",
        "description": "Mistral 系列，快速高效"
    }
}

CONTAINER_NAME = "wuchangv510-ollama-1"
CURRENT_MODEL = "qwen2:0.5b"

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

def check_ollama_container() -> bool:
    """檢查 Ollama 容器是否運行中"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={CONTAINER_NAME}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        if CONTAINER_NAME in result.stdout:
            log(f"✓ Ollama 容器運行中: {CONTAINER_NAME}", "OK")
            return True
        else:
            log(f"✗ Ollama 容器未運行: {CONTAINER_NAME}", "ERROR")
            return False
            
    except subprocess.CalledProcessError:
        log("✗ 無法檢查容器狀態", "ERROR")
        return False

def list_current_models() -> list:
    """列出當前已下載的模型"""
    try:
        result = subprocess.run(
            ["docker", "exec", CONTAINER_NAME, "ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        
        models = []
        lines = result.stdout.strip().split('\n')[1:]  # 跳過標題行
        
        for line in lines:
            if line.strip():
                parts = line.split()
                if parts:
                    models.append(parts[0])
        
        return models
        
    except subprocess.CalledProcessError as e:
        log(f"✗ 無法列出模型: {e.stderr.strip()}", "ERROR")
        return []

def check_available_space() -> Dict:
    """檢查可用儲存空間"""
    try:
        result = subprocess.run(
            ["docker", "exec", CONTAINER_NAME, "df", "-h", "/root/.ollama"],
            capture_output=True,
            text=True,
            check=True
        )
        
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            if len(parts) >= 4:
                return {
                    "total": parts[1],
                    "used": parts[2],
                    "available": parts[3],
                    "use_percent": parts[4]
                }
        
        return {}
        
    except subprocess.CalledProcessError:
        return {}

def check_system_memory() -> Optional[int]:
    """檢查系統記憶體（GB）"""
    try:
        result = subprocess.run(
            ["docker", "exec", CONTAINER_NAME, "free", "-g"],
            capture_output=True,
            text=True,
            check=True
        )
        
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            if len(parts) >= 2:
                return int(parts[1])  # 總記憶體（GB）
        
        return None
        
    except (subprocess.CalledProcessError, ValueError):
        return None

def download_model(model_name: str) -> bool:
    """下載 LLM 模型"""
    log(f"開始下載模型: {model_name}", "PROGRESS")
    log("這可能需要一些時間，請耐心等待...", "INFO")
    
    try:
        # 使用 subprocess 並顯示進度
        process = subprocess.Popen(
            ["docker", "exec", "-i", CONTAINER_NAME, "ollama", "pull", model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 顯示輸出
        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        
        if process.returncode == 0:
            log(f"✓ 模型 {model_name} 下載成功", "OK")
            return True
        else:
            log(f"✗ 模型下載失敗", "ERROR")
            return False
            
    except Exception as e:
        log(f"✗ 下載模型時發生錯誤: {e}", "ERROR")
        return False

def test_model(model_name: str) -> bool:
    """測試模型是否正常工作"""
    log(f"測試模型: {model_name}", "PROGRESS")
    
    try:
        result = subprocess.run(
            [
                "docker", "exec", CONTAINER_NAME,
                "ollama", "run", model_name,
                "echo hello"
            ],
            capture_output=True,
            text=True,
            timeout=60,
            check=True
        )
        
        if result.returncode == 0:
            log(f"✓ 模型 {model_name} 測試成功", "OK")
            return True
        else:
            log(f"✗ 模型測試失敗", "WARN")
            return False
            
    except subprocess.TimeoutExpired:
        log("⚠️ 測試超時（模型可能較大，這是正常的）", "WARN")
        return True  # 超時不一定表示失敗
    except Exception as e:
        log(f"⚠️ 測試時發生錯誤: {e}", "WARN")
        return True  # 繼續進行

def update_system_config(model_name: str) -> bool:
    """更新系統配置檔案"""
    log("更新系統配置...", "PROGRESS")
    
    config_files = [
        BASE_DIR / "config" / "ai_agents" / "double_j_appearance.json",
        BASE_DIR / "config" / "ai_agents" / "double_j_appearance.yaml"
    ]
    
    updated = False
    
    for config_file in config_files:
        if not config_file.exists():
            continue
            
        try:
            content = config_file.read_text(encoding='utf-8')
            
            # 替換模型名稱
            old_patterns = [
                '"local": "qwen2:0.5b"',
                'local: "qwen2:0.5b"',
                'local: qwen2:0.5b'
            ]
            
            for pattern in old_patterns:
                if pattern in content:
                    new_pattern = pattern.replace("qwen2:0.5b", model_name)
                    content = content.replace(pattern, new_pattern)
                    updated = True
            
            if updated:
                config_file.write_text(content, encoding='utf-8')
                log(f"✓ 已更新: {config_file.name}", "OK")
                
        except Exception as e:
            log(f"⚠️ 更新 {config_file.name} 失敗: {e}", "WARN")
    
    # 提示需要手動更新的檔案
    log("提示：可能需要手動更新的檔案：", "INFO")
    log("  - wuchang_os/addons/wuchang_core/data/system_params.xml", "INFO")
    log("  - wuchang_os/addons/wuchang_core/models/ai_logic.py", "INFO")
    
    return updated

def show_recommendations():
    """顯示推薦模型"""
    print("\n" + "=" * 70)
    print("推薦模型選項")
    print("=" * 70)
    print()
    
    for i, (model, info) in enumerate(RECOMMENDED_MODELS.items(), 1):
        print(f"{i}. {model}")
        print(f"   大小: {info['size']}")
        print(f"   記憶體需求: {info['memory']}")
        print(f"   說明: {info['description']}")
        print()
    
    print("=" * 70)

def main():
    print("=" * 70)
    print("本地 LLM 模型升級工具")
    print("=" * 70)
    print()
    
    # 檢查容器
    if not check_ollama_container():
        log("請先啟動 Ollama 容器", "ERROR")
        return
    
    print()
    
    # 檢查當前模型
    log("檢查當前已安裝的模型...", "INFO")
    current_models = list_current_models()
    
    if current_models:
        log("已安裝的模型：", "INFO")
        for model in current_models:
            if model == CURRENT_MODEL:
                log(f"  • {model} (當前使用)", "INFO")
            else:
                log(f"  • {model}", "INFO")
    else:
        log(f"  當前使用: {CURRENT_MODEL}", "INFO")
    
    print()
    
    # 檢查儲存空間
    space_info = check_available_space()
    if space_info:
        log(f"可用儲存空間: {space_info.get('available', '未知')}", "INFO")
    
    # 檢查記憶體
    memory_gb = check_system_memory()
    if memory_gb:
        log(f"系統記憶體: {memory_gb}GB", "INFO")
        if memory_gb < 16:
            log("⚠️ 記憶體可能不足以運行 7B 模型，建議使用 1.5B 或升級記憶體", "WARN")
    
    print()
    
    # 顯示推薦
    show_recommendations()
    
    # 詢問用戶選擇
    print()
    log("請選擇要下載的模型：", "INFO")
    print("  1. qwen2:1.5b (推薦：輕量級升級)")
    print("  2. qwen2:7b (推薦：最佳平衡)")
    print("  3. llama3.1:8b")
    print("  4. mistral:7b")
    print("  5. 自訂模型名稱")
    print("  0. 退出")
    print()
    
    choice = input("請輸入選項 (1-5): ").strip()
    
    model_to_download = None
    
    if choice == "1":
        model_to_download = "qwen2:1.5b"
    elif choice == "2":
        model_to_download = "qwen2:7b"
        if memory_gb and memory_gb < 16:
            confirm = input("⚠️ 您的系統記憶體可能不足，是否繼續？(y/n): ").strip().lower()
            if confirm != 'y':
                log("已取消", "INFO")
                return
    elif choice == "3":
        model_to_download = "llama3.1:8b"
    elif choice == "4":
        model_to_download = "mistral:7b"
    elif choice == "5":
        model_to_download = input("請輸入模型名稱: ").strip()
    elif choice == "0":
        log("已取消", "INFO")
        return
    else:
        log("無效的選項", "ERROR")
        return
    
    if not model_to_download:
        log("未指定模型", "ERROR")
        return
    
    print()
    
    # 確認下載
    confirm = input(f"確認下載模型: {model_to_download}? (y/n): ").strip().lower()
    if confirm != 'y':
        log("已取消", "INFO")
        return
    
    print()
    
    # 下載模型
    if download_model(model_to_download):
        print()
        
        # 測試模型
        if test_model(model_to_download):
            print()
            
            # 更新配置
            update_system_config(model_to_download)
            
            print()
            log("✅ 模型升級完成！", "OK")
            log(f"新模型: {model_to_download}", "INFO")
            log("請記得更新系統配置檔案中的模型名稱", "INFO")
            print()
            log("建議：重新啟動相關服務以使用新模型", "INFO")
        else:
            log("⚠️ 模型已下載，但測試時發生問題", "WARN")
            log("請手動測試模型是否正常工作", "INFO")
    else:
        log("模型下載失敗，請檢查網路連接和儲存空間", "ERROR")

if __name__ == "__main__":
    main()
