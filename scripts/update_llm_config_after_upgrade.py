#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_llm_config_after_upgrade.py

模型升級後自動更新系統配置檔案
"""

import sys
import re
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_FILES = {
    "json": BASE_DIR / "config" / "ai_agents" / "double_j_appearance.json",
    "yaml": BASE_DIR / "config" / "ai_agents" / "double_j_appearance.yaml",
}

OLD_MODEL = "qwen2:0.5b"
NEW_MODEL = "qwen2:7b"  # 可以通過參數指定

def log(message: str, level: str = "INFO"):
    """輸出日誌訊息"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")

def update_json_config(file_path: Path, old_model: str, new_model: str) -> bool:
    """更新 JSON 配置檔案"""
    try:
        if not file_path.exists():
            log(f"檔案不存在: {file_path}", "WARN")
            return False
        
        content = file_path.read_text(encoding='utf-8')
        
        # 替換模型名稱
        patterns = [
            (f'"local": "{old_model}"', f'"local": "{new_model}"'),
            (f'"local":\\s*"{old_model}"', f'"local": "{new_model}"'),
        ]
        
        updated = False
        for pattern, replacement in patterns:
            if pattern in content or re.search(pattern.replace('"', '["\']'), content):
                content = re.sub(
                    pattern.replace('"', '["\']').replace('(', r'\(').replace(')', r'\)'),
                    replacement,
                    content
                )
                updated = True
        
        if updated:
            file_path.write_text(content, encoding='utf-8')
            log(f"✓ 已更新: {file_path.name}", "OK")
            return True
        else:
            log(f"未找到需要更新的內容: {file_path.name}", "INFO")
            return False
            
    except Exception as e:
        log(f"✗ 更新失敗: {e}", "ERROR")
        return False

def update_yaml_config(file_path: Path, old_model: str, new_model: str) -> bool:
    """更新 YAML 配置檔案"""
    try:
        if not file_path.exists():
            log(f"檔案不存在: {file_path}", "WARN")
            return False
        
        content = file_path.read_text(encoding='utf-8')
        
        # 替換模型名稱
        patterns = [
            (f'local: "{old_model}"', f'local: "{new_model}"'),
            (f'local: {old_model}', f'local: {new_model}'),
            (f'local:\\s*"{old_model}"', f'local: "{new_model}"'),
            (f'local:\\s*{old_model}', f'local: {new_model}'),
        ]
        
        updated = False
        for pattern, replacement in patterns:
            if pattern in content or re.search(pattern.replace('"', '["\']?'), content):
                content = re.sub(
                    pattern.replace('"', '["\']?').replace('(', r'\(').replace(')', r'\)'),
                    replacement,
                    content
                )
                updated = True
        
        if updated:
            file_path.write_text(content, encoding='utf-8')
            log(f"✓ 已更新: {file_path.name}", "OK")
            return True
        else:
            log(f"未找到需要更新的內容: {file_path.name}", "INFO")
            return False
            
    except Exception as e:
        log(f"✗ 更新失敗: {e}", "ERROR")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='更新 LLM 模型配置')
    parser.add_argument('--model', default='qwen2:7b', help='新的模型名稱 (預設: qwen2:7b)')
    parser.add_argument('--old-model', default='qwen2:0.5b', help='舊的模型名稱 (預設: qwen2:0.5b)')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("LLM 模型配置更新工具")
    print("=" * 70)
    print()
    
    log(f"更新模型配置: {args.old_model} → {args.model}", "INFO")
    print()
    
    updated_count = 0
    
    # 更新 JSON 配置
    if CONFIG_FILES["json"].exists():
        if update_json_config(CONFIG_FILES["json"], args.old_model, args.model):
            updated_count += 1
    else:
        log(f"檔案不存在: {CONFIG_FILES['json']}", "WARN")
    
    # 更新 YAML 配置
    if CONFIG_FILES["yaml"].exists():
        if update_yaml_config(CONFIG_FILES["yaml"], args.old_model, args.model):
            updated_count += 1
    else:
        log(f"檔案不存在: {CONFIG_FILES['yaml']}", "WARN")
    
    print()
    
    if updated_count > 0:
        log(f"✅ 成功更新 {updated_count} 個配置檔案", "OK")
        log("提示：還需要手動更新 system_params.xml 檔案", "INFO")
        log("路徑: wuchang_os/addons/wuchang_core/data/system_params.xml", "INFO")
    else:
        log("⚠️ 沒有更新任何檔案", "WARN")
        log("請確認配置檔案存在且包含正確的模型名稱", "INFO")

if __name__ == "__main__":
    main()
