# -*- coding: utf-8 -*-
"""
Cloud Little J Intelligence (雲端小J 智能核心)
--------------------------------------------------
將雲端算力轉用於「系統邏輯索引」與「真相研究」，而非單純翻譯。

功能：
1. 系統邏輯索引 (System Logic Indexing)：掃描所有工具，理解其邏輯，建立「時空索引」(Spacetime Index)。
2. 智能審計 (Intelligent Audit)：讀取工具並生成帶有時間戳記的「時光印記」日誌 (TOOL_HISTORY_LOG.md)。
3. 真相研究驗證 (Truth Verification)：(未來) 對接雲端大腦進行複雜的社會/政治分析。

版本：V3.0.0 (Brain Upgrade)
作者：Little J (Digital Twin)
"""

import os
import time
import glob
import json
import datetime
from pathlib import Path

# 嘗試匯入 Google Generative AI 函式庫 (僅作為潛在能力保留，目前主要依賴邏輯分析)
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

class CloudLittleJBrain:
    def __init__(self, workspace_root=None):
        self.workspace_root = workspace_root or os.path.dirname(os.path.abspath(__file__))
        self.log_file = os.path.join(self.workspace_root, "TOOL_HISTORY_LOG.md")
        self.index_file = os.path.join(self.workspace_root, "SYSTEM_LOGIC_INDEX.json")
        self.tools_found = []

    def scan_tools(self):
        """掃描工具庫中的所有 Python 工具"""
        print(f"🔍 正在掃描工具庫: {self.workspace_root}...")
        self.tools_found = []
        
        # 掃描 Python 檔案
        for file_path in glob.glob(os.path.join(self.workspace_root, "*.py")):
            filename = os.path.basename(file_path)
            if filename in ["__init__.py", "cloud_little_j_intelligence.py"]:
                continue
                
            tool_info = self._analyze_tool(file_path)
            self.tools_found.append(tool_info)
            print(f"  - 發現工具: {filename} ({tool_info['description']})")
            
        return self.tools_found

    def _analyze_tool(self, file_path):
        """分析工具檔案內容 (簡易靜態分析)"""
        filename = os.path.basename(file_path)
        description = "未知工具"
        has_main = False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 嘗試提取 docstring
                if '"""' in content:
                    parts = content.split('"""')
                    if len(parts) >= 2:
                        description = parts[1].strip().split('\n')[0]
                
                if "if __name__ == '__main__':" in content or 'if __name__ == "__main__":' in content:
                    has_main = True
                    
        except Exception as e:
            description = f"分析失敗: {e}"
            
        return {
            "filename": filename,
            "path": file_path,
            "description": description,
            "has_main": has_main,
            "last_modified": datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        }

    def generate_index(self):
        """生成系統邏輯索引 (JSON)"""
        index_data = {
            "generated_at": datetime.datetime.now().isoformat(),
            "tool_count": len(self.tools_found),
            "tools": self.tools_found,
            "logic_map": {
                "core": [],
                "research": [],
                "utility": [],
                "web": []
            }
        }
        
        # 簡單分類邏輯
        for tool in self.tools_found:
            name = tool['filename'].lower()
            if "research" in name or "simulate" in name:
                index_data['logic_map']['research'].append(tool['filename'])
            elif "core" in name or "reset" in name:
                index_data['logic_map']['core'].append(tool['filename'])
            elif "web" in name or "html" in name:
                index_data['logic_map']['web'].append(tool['filename'])
            else:
                index_data['logic_map']['utility'].append(tool['filename'])
                
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=4, ensure_ascii=False)
        
        print(f"✅ 系統邏輯索引已建立: {self.index_file}")
        return index_data

    def update_audit_log(self):
        """更新時光印記日誌 (Audit Log)"""
        
        # 讀取現有日誌
        existing_content = ""
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_entries = []
        if "# 工具庫使用記錄 (Tool Usage History)" not in existing_content:
            new_entries.append("# 工具庫使用記錄 (Tool Usage History)\n")
            new_entries.append("> 「誰哪天用它做什麼，我要一查就到」 — Juers\n")
        
        new_entries.append(f"\n## 🕒 索引掃描時間點: {timestamp}")
        new_entries.append("| 工具名稱 (Tool) | 描述 (Description) | 最後修改時間 (Last Modified) | 分類 (Category) |")
        new_entries.append("|---|---|---|---|")
        
        index_data = self.generate_index() # 確保索引是最新的
        
        for tool in self.tools_found:
            # 判斷分類
            category = "Utility"
            for cat, tools in index_data['logic_map'].items():
                if tool['filename'] in tools:
                    category = cat.capitalize()
                    break
            
            new_entries.append(f"| `{tool['filename']}` | {tool['description']} | {tool['last_modified']} | {category} |")
            
        new_entries.append(f"\n*共索引 {len(self.tools_found)} 個工具工具*")
        
        # 將新內容附加到檔案（如果檔案已存在，這裡選擇覆蓋或附加，鑑於這是"索引更新"，我們附加新的快照）
        # 但為了避免檔案無限增長，我們可能希望只保留最新的索引表，並將舊的歸檔。
        # 根據用戶 "留一份索引黨" 的要求，這應該是一個最新的目錄。
        # 而 "時光印記" 是指使用記錄。
        
        # 這裡我們做一個 "最新狀態快照" + "歷史操作日誌" 的混合體
        
        final_content = "\n".join(new_entries)
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(final_content) # 這裡先覆蓋，保持索引是最新的狀態表
            
        print(f"✅ 時光印記日誌已更新: {self.log_file}")

if __name__ == "__main__":
    brain = CloudLittleJBrain()
    brain.scan_tools()
    brain.update_audit_log()
    print("\n🧠 雲端小J智能核心執行完畢。")
    print("💡 提示：此工具已從「單純翻譯」升級為「系統邏輯索引與審計」，避免浪費算力。")
