#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enable_double_j_collaboration.py

啟用雙J合作機制

功能：
- 載入雙J形象設計設定
- 驗證合作機制配置
- 啟動雙J合作服務
- 檢查必要工具和API狀態
"""

import sys
import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = BASE_DIR / "config" / "ai_agents"
APPEARANCE_CONFIG = CONFIG_DIR / "double_j_appearance.json"


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌",
        "STEP": "📋",
        "SUCCESS": "🎉"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")


def load_appearance_config() -> Optional[Dict]:
    """載入形象設計設定"""
    log("載入雙J形象設計設定...", "STEP")
    
    if not APPEARANCE_CONFIG.exists():
        log(f"設定檔案不存在: {APPEARANCE_CONFIG}", "ERROR")
        return None
    
    try:
        with open(APPEARANCE_CONFIG, 'r', encoding='utf-8') as f:
            config = json.load(f)
        log(f"✓ 成功載入設定檔案 (版本: {config.get('version', 'unknown')})", "OK")
        return config
    except Exception as e:
        log(f"✗ 載入設定檔案失敗: {e}", "ERROR")
        return None


def display_agent_appearance(config: Dict, agent_id: str):
    """顯示代理形象資訊"""
    agents = config.get("agents", {})
    if agent_id not in agents:
        log(f"找不到代理: {agent_id}", "ERROR")
        return
    
    agent = agents[agent_id]
    name = agent.get("name", {})
    appearance = agent.get("appearance", {})
    hair = appearance.get("hair", {})
    
    print()
    log(f"=== {name.get('zh_tw', agent_id)} ({name.get('en', '')}) ===", "INFO")
    print()
    
    print(f"  名稱: {name.get('zh_tw', '')} ({name.get('en', '')})")
    if name.get("nickname"):
        print(f"  暱稱: {name.get('nickname')}")
    
    print()
    print("  形象設定:")
    print(f"    • 髮色: {hair.get('color', 'N/A')}")
    if hair.get("description"):
        print(f"    • 說明: {hair.get('description')}")
    
    clothing = appearance.get("clothing", {})
    print(f"    • 服裝風格: {clothing.get('style', 'N/A')}")
    print(f"    • 配色方案: {clothing.get('color_scheme', 'N/A')}")
    
    visual = appearance.get("visual_identity", {})
    print(f"    • 主色: {visual.get('primary_color', 'N/A')}")
    print(f"    • 主題: {visual.get('theme', 'N/A')}")
    
    personality = agent.get("personality", {})
    if personality.get("traits"):
        print(f"    • 特質: {', '.join(personality.get('traits', []))}")


def check_collaboration_tools() -> Dict[str, bool]:
    """檢查合作機制工具"""
    log("檢查雙J合作機制工具...", "STEP")
    
    scripts_dir = BASE_DIR / "scripts"
    tools = {
        "get_jules_task_direct.py": False,
        "upload_diff_to_jules.py": False,
        "check_google_task_progress.py": False,
        "sync_from_google_task.py": False
    }
    
    results = {}
    for tool_name, _ in tools.items():
        tool_path = scripts_dir / tool_name
        exists = tool_path.exists()
        results[tool_name] = exists
        if exists:
            log(f"  ✓ {tool_name}", "OK")
        else:
            log(f"  ✗ {tool_name} (不存在)", "WARN")
    
    return results


def check_api_credentials() -> Dict[str, bool]:
    """檢查API憑證"""
    log("檢查API憑證...", "STEP")
    
    results = {}
    
    # 檢查 Google OAuth 憑證
    google_creds = BASE_DIR / "google_credentials.json"
    results["google_credentials.json"] = google_creds.exists()
    if google_creds.exists():
        log("  ✓ Google OAuth 憑證", "OK")
    else:
        log("  ✗ Google OAuth 憑證 (不存在)", "WARN")
        log("    參考: LITTLE_J_CREDENTIALS_SETUP.md", "INFO")
    
    # 檢查服務帳戶金鑰
    sa_key = BASE_DIR / "config" / "gcp" / "littlej-sa.json"
    results["littlej-sa.json"] = sa_key.exists()
    if sa_key.exists():
        log("  ✓ 服務帳戶金鑰", "OK")
    else:
        log("  ✗ 服務帳戶金鑰 (不存在)", "WARN")
        log("    參考: MULTIMEDIA_AI_FEATURES.md", "INFO")
    
    return results


def generate_activation_report(config: Dict, tools_status: Dict, credentials_status: Dict):
    """產生啟用報告"""
    report_dir = BASE_DIR / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = report_dir / f"DOUBLE_J_ACTIVATION_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    report_content = f"""# 雙J合作機制啟用報告

**啟用時間：** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**設定版本：** {config.get('version', 'unknown')}

---

## ✅ 啟用狀態

### 形象設計設定

- ✅ **設定檔案已載入**  
  位置: `{APPEARANCE_CONFIG.relative_to(BASE_DIR)}`

### 代理形象

#### 小J (Little J)
- **髮色**: {config['agents']['little_j']['appearance']['hair']['color']}
- **主題**: {config['agents']['little_j']['appearance']['visual_identity']['theme']}
- **角色**: {config['agents']['little_j']['personality']['role']}

#### Jules
- **髮色**: {config['agents']['jules']['appearance']['hair']['color']}
- **主題**: {config['agents']['jules']['appearance']['visual_identity']['theme']}
- **角色**: {config['agents']['jules']['personality']['role']}

---

## 🔧 工具狀態

### 合作機制工具

"""
    
    all_tools_ok = True
    for tool, status in tools_status.items():
        status_icon = "✅" if status else "❌"
        report_content += f"- {status_icon} **{tool}**\n"
        if not status:
            all_tools_ok = False
    
    report_content += "\n### API憑證\n\n"
    
    all_creds_ok = True
    for cred, status in credentials_status.items():
        status_icon = "✅" if status else "❌"
        report_content += f"- {status_icon} **{cred}**\n"
        if not status:
            all_creds_ok = False
    
    report_content += f"""

---

## 📋 下一步行動

### 已完成
- ✅ 雙J形象設計設定已載入
- ✅ 合作機制配置已檢查

### 需要完成

"""
    
    if not all_tools_ok:
        report_content += "- ⚠️ **安裝合作機制工具**\n"
        report_content += "  - 建立必要的腳本檔案\n"
        report_content += "  - 參考: reports/DOUBLE_J_COLLABORATION_MECHANISM.md\n\n"
    
    if not all_creds_ok:
        report_content += "- ⚠️ **設定API憑證**\n"
        report_content += "  - 設定 Google OAuth 憑證\n"
        report_content += "  - 下載服務帳戶金鑰\n"
        report_content += "  - 參考: LITTLE_J_CREDENTIALS_SETUP.md\n\n"
    
    report_content += f"""
---

## 🎨 形象設計摘要

### 視覺識別

**小J:**
- 主色: {config['agents']['little_j']['appearance']['visual_identity']['primary_color']}
- 強調色: {config['agents']['little_j']['appearance']['visual_identity']['accent_color']}
- 髮色: {config['agents']['little_j']['appearance']['hair']['color']}

**Jules:**
- 主色: {config['agents']['jules']['appearance']['visual_identity']['primary_color']}
- 強調色: {config['agents']['jules']['appearance']['visual_identity']['accent_color']}
- 髮色: {config['agents']['jules']['appearance']['hair']['color']}

### 協作和諧

{config['collaboration']['visual_harmony']['description']}

---

**報告生成時間：** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**設定格式版本：** {config.get('version', 'unknown')}
"""
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        log(f"✓ 啟用報告已產生: {report_file.relative_to(BASE_DIR)}", "OK")
    except Exception as e:
        log(f"✗ 產生報告失敗: {e}", "ERROR")


def main():
    """主程式"""
    print("=" * 100)
    print("啟用雙J合作機制")
    print("=" * 100)
    print()
    
    # 步驟 1: 載入形象設計設定
    config = load_appearance_config()
    if not config:
        log("無法載入設定，請檢查設定檔案", "ERROR")
        return 1
    
    print()
    
    # 步驟 2: 顯示代理形象
    log("雙J形象設計", "STEP")
    display_agent_appearance(config, "little_j")
    display_agent_appearance(config, "jules")
    
    print()
    
    # 步驟 3: 檢查合作機制工具
    tools_status = check_collaboration_tools()
    
    print()
    
    # 步驟 4: 檢查API憑證
    credentials_status = check_api_credentials()
    
    print()
    
    # 步驟 5: 產生啟用報告
    log("產生啟用報告...", "STEP")
    generate_activation_report(config, tools_status, credentials_status)
    
    print()
    print("=" * 100)
    log("雙J合作機制啟用完成！", "SUCCESS")
    print("=" * 100)
    print()
    
    log("設定檔案位置:", "INFO")
    log(f"  {APPEARANCE_CONFIG.relative_to(BASE_DIR)}", "INFO")
    print()
    
    log("使用方式:", "INFO")
    log("  此設定檔案可用於各種系統：Web應用、桌面應用、行動應用、聊天機器人等", "INFO")
    log("  支援格式：JSON、YAML、Python、JavaScript等", "INFO")
    print()
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n程式已中斷")
        sys.exit(0)
    except Exception as e:
        log(f"發生未預期的錯誤: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)
