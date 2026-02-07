#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署時空能力到 AI 小 J
將時空系統整合到 AI 小 J 程序中
"""

import os
import sys
import shutil
from pathlib import Path
import json

# 時空系統路徑
SPATIOTEMPORAL_ROOT = Path(__file__).parent.parent

# AI 小 J 可能的路徑
AI_J_PATHS = [
    Path("wuchang_os/addons/wuchang_core"),
    Path("remote_ui_control"),
    Path("."),
]


def find_ai_j_path():
    """尋找 AI 小 J 路徑"""
    for path in AI_J_PATHS:
        full_path = SPATIOTEMPORAL_ROOT.parent / path
        if full_path.exists():
            # 檢查是否有 AI 相關檔案
            ai_files = list(full_path.glob("**/*ai*.py"))
            if ai_files:
                return full_path
    return None


def deploy_integration_module(target_path: Path):
    """部署整合模組"""
    print(f"部署整合模組到: {target_path}")
    
    # 複製整合配置
    integration_file = SPATIOTEMPORAL_ROOT / "config" / "ai_j_integration.py"
    target_file = target_path / "spatiotemporal_integration.py"
    
    if integration_file.exists():
        shutil.copy2(integration_file, target_file)
        print(f"✓ 已複製整合模組: {target_file}")
    else:
        print(f"✗ 整合模組不存在: {integration_file}")


def update_ai_j_config(target_path: Path):
    """更新 AI 小 J 配置"""
    print(f"更新 AI 小 J 配置...")
    
    # 尋找配置檔案
    config_files = [
        target_path / "config.py",
        target_path / "settings.py",
        target_path / "ai_config.py"
    ]
    
    for config_file in config_files:
        if config_file.exists():
            # 讀取現有配置
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 檢查是否已包含時空系統
                if 'spatiotemporal' not in content.lower():
                    # 添加時空系統導入
                    import_line = "\nfrom .spatiotemporal_integration import get_ai_j_spatiotemporal\n"
                    
                    # 在檔案開頭添加
                    if 'import' in content:
                        lines = content.split('\n')
                        last_import = 0
                        for i, line in enumerate(lines):
                            if line.strip().startswith('import') or line.strip().startswith('from'):
                                last_import = i
                        lines.insert(last_import + 1, import_line.strip())
                        content = '\n'.join(lines)
                    else:
                        content = import_line + content
                    
                    # 寫回檔案
                    with open(config_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"✓ 已更新配置: {config_file}")
            except Exception as e:
                print(f"✗ 更新配置失敗 {config_file}: {e}")


def create_deployment_config():
    """建立部署配置"""
    config = {
        "spatiotemporal_system": {
            "enabled": True,
            "version": "1.0.0",
            "path": str(SPATIOTEMPORAL_ROOT),
            "integrated": True
        },
        "ai_j": {
            "spatiotemporal_capabilities": [
                "時空事件管理",
                "時間空間建議",
                "排程優化",
                "活動模式分析",
                "空間使用率預測"
            ]
        },
        "deployment": {
            "timestamp": str(Path().cwd()),
            "status": "deployed"
        }
    }
    
    config_file = SPATIOTEMPORAL_ROOT / "deployment_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 部署配置已建立: {config_file}")
    return config


def main():
    """主部署流程"""
    print("=" * 50)
    print("時空系統部署到 AI 小 J")
    print("=" * 50)
    
    # 尋找 AI 小 J 路徑
    ai_j_path = find_ai_j_path()
    if not ai_j_path:
        print("⚠ 未找到 AI 小 J 路徑，將部署到當前目錄")
        ai_j_path = Path(".")
    
    print(f"目標路徑: {ai_j_path}")
    
    # 部署整合模組
    deploy_integration_module(ai_j_path)
    
    # 更新配置
    update_ai_j_config(ai_j_path)
    
    # 建立部署配置
    create_deployment_config()
    
    print("\n" + "=" * 50)
    print("部署完成！")
    print("=" * 50)
    print("\n下一步:")
    print("1. 確保時空系統依賴已安裝: pip install -r requirements.txt")
    print("2. 設定環境變數（雲端算力）:")
    print("   - OPENAI_API_KEY")
    print("   - ANTHROPIC_API_KEY")
    print("   - GOOGLE_API_KEY")
    print("3. 在 AI 小 J 中導入: from spatiotemporal_integration import get_ai_j_spatiotemporal")


if __name__ == "__main__":
    main()


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:33:44
---
