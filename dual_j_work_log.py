#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dual_j_work_log.py

雙 j 工作日誌系統
- 地端小 j 和雲端小 j (JULES) 的工作日誌
- UI 可讀格式（JSON + HTML）
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 設定 UTF-8 編碼
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
WORK_LOG_DIR = BASE_DIR / "dual_j_work_logs"
WORK_LOG_DIR.mkdir(exist_ok=True)

# 日誌檔案
DAILY_LOG_FILE = WORK_LOG_DIR / f"work_log_{datetime.now().strftime('%Y%m%d')}.json"
ALL_LOGS_JSON = WORK_LOG_DIR / "all_logs.json"
WORK_LOG_HTML = BASE_DIR / "dual_j_work_log.html"


def load_daily_log() -> List[Dict[str, Any]]:
    """載入今日日誌"""
    if DAILY_LOG_FILE.exists():
        try:
            return json.loads(DAILY_LOG_FILE.read_text(encoding="utf-8"))
        except:
            return []
    return []


def save_daily_log(logs: List[Dict[str, Any]]):
    """儲存今日日誌"""
    try:
        DAILY_LOG_FILE.write_text(
            json.dumps(logs, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    except Exception as e:
        print(f"儲存日誌失敗: {e}")


def add_work_log(
    agent: str,
    work_type: str,
    description: str,
    status: str = "completed",
    details: Dict[str, Any] = None,
    result: str = None
) -> Dict[str, Any]:
    """新增工作日誌"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent,  # "地端小 j" 或 "雲端小 j (JULES)"
        "work_type": work_type,  # "監控檢查", "問題偵測", "任務執行", "結果驗證" 等
        "description": description,
        "status": status,  # "completed", "failed", "in_progress"
        "details": details or {},
        "result": result
    }
    
    # 載入今日日誌
    logs = load_daily_log()
    logs.append(log_entry)
    
    # 儲存
    save_daily_log(logs)
    
    # 更新總日誌
    update_all_logs(log_entry)
    
    # 更新 HTML
    generate_html_log()
    
    return log_entry


def update_all_logs(log_entry: Dict[str, Any]):
    """更新總日誌檔案"""
    try:
        if ALL_LOGS_JSON.exists():
            all_logs = json.loads(ALL_LOGS_JSON.read_text(encoding="utf-8"))
        else:
            all_logs = []
        
        all_logs.append(log_entry)
        
        # 只保留最近 1000 筆
        all_logs = all_logs[-1000:]
        
        ALL_LOGS_JSON.write_text(
            json.dumps(all_logs, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    except Exception as e:
        print(f"更新總日誌失敗: {e}")


def generate_html_log():
    """生成 HTML 格式的日誌（UI 可讀）"""
    try:
        # 載入今日日誌
        today_logs = load_daily_log()
        
        # 載入最近 7 天的日誌
        recent_logs = []
        for i in range(7):
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            date = date.replace(day=date.day - i)
            log_file = WORK_LOG_DIR / f"work_log_{date.strftime('%Y%m%d')}.json"
            if log_file.exists():
                try:
                    day_logs = json.loads(log_file.read_text(encoding="utf-8"))
                    recent_logs.extend(day_logs)
                except:
                    pass
        
        # 按時間排序（最新的在前）
        recent_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # 生成 HTML
        html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>雙 j 工作日誌 - wuchang.life</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: 'Microsoft JhengHei', 'Segoe UI', Arial, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      padding: 20px;
      min-height: 100vh;
    }}
    .container {{
      max-width: 1400px;
      margin: 0 auto;
      background: white;
      border-radius: 15px;
      padding: 30px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }}
    h1 {{
      color: #333;
      text-align: center;
      margin-bottom: 10px;
      font-size: 2.2em;
    }}
    .subtitle {{
      text-align: center;
      color: #666;
      margin-bottom: 30px;
      font-size: 1.1em;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 15px;
      margin-bottom: 30px;
    }}
    .stat-card {{
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 20px;
      border-radius: 10px;
      text-align: center;
    }}
    .stat-card h3 {{
      font-size: 2em;
      margin-bottom: 5px;
    }}
    .stat-card p {{
      font-size: 0.9em;
      opacity: 0.9;
    }}
    .log-entry {{
      background: #f8f9fa;
      border-left: 4px solid #667eea;
      padding: 15px;
      margin-bottom: 15px;
      border-radius: 5px;
      transition: transform 0.2s;
    }}
    .log-entry:hover {{
      transform: translateX(5px);
      box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }}
    .log-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }}
    .log-agent {{
      font-weight: bold;
      font-size: 1.1em;
      color: #667eea;
    }}
    .log-time {{
      color: #666;
      font-size: 0.9em;
    }}
    .log-type {{
      display: inline-block;
      background: #667eea;
      color: white;
      padding: 3px 10px;
      border-radius: 12px;
      font-size: 0.85em;
      margin-right: 10px;
    }}
    .log-description {{
      margin: 10px 0;
      line-height: 1.6;
    }}
    .log-status {{
      display: inline-block;
      padding: 3px 10px;
      border-radius: 12px;
      font-size: 0.85em;
      font-weight: bold;
    }}
    .status-completed {{
      background: #28a745;
      color: white;
    }}
    .status-failed {{
      background: #dc3545;
      color: white;
    }}
    .status-in_progress {{
      background: #ffc107;
      color: #333;
    }}
    .log-result {{
      margin-top: 10px;
      padding: 10px;
      background: #e9ecef;
      border-radius: 5px;
      font-family: 'Courier New', monospace;
      font-size: 0.9em;
    }}
    .filter-buttons {{
      display: flex;
      gap: 10px;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }}
    .filter-btn {{
      padding: 8px 16px;
      border: 2px solid #667eea;
      background: white;
      color: #667eea;
      border-radius: 20px;
      cursor: pointer;
      transition: all 0.3s;
    }}
    .filter-btn:hover {{
      background: #667eea;
      color: white;
    }}
    .filter-btn.active {{
      background: #667eea;
      color: white;
    }}
    .empty-state {{
      text-align: center;
      padding: 60px 20px;
      color: #666;
    }}
    .empty-state-icon {{
      font-size: 4em;
      margin-bottom: 20px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>🤝 雙 j 工作日誌</h1>
    <p class="subtitle">地端小 j 與雲端小 j (JULES) 協作記錄</p>
    
    <div class="stats">
      <div class="stat-card">
        <h3>{len(today_logs)}</h3>
        <p>今日工作記錄</p>
      </div>
      <div class="stat-card">
        <h3>{len([l for l in recent_logs if l.get('agent') == '地端小 j'])}</h3>
        <p>地端小 j 記錄</p>
      </div>
      <div class="stat-card">
        <h3>{len([l for l in recent_logs if l.get('agent') == '雲端小 j (JULES)'])}</h3>
        <p>雲端小 j 記錄</p>
      </div>
      <div class="stat-card">
        <h3>{len([l for l in recent_logs if l.get('status') == 'completed'])}</h3>
        <p>已完成工作</p>
      </div>
    </div>
    
    <div class="filter-buttons">
      <button class="filter-btn active" onclick="filterLogs('all')">全部</button>
      <button class="filter-btn" onclick="filterLogs('地端小 j')">地端小 j</button>
      <button class="filter-btn" onclick="filterLogs('雲端小 j (JULES)')">雲端小 j</button>
      <button class="filter-btn" onclick="filterLogs('completed')">已完成</button>
      <button class="filter-btn" onclick="filterLogs('failed')">失敗</button>
    </div>
    
    <div id="log-container">
"""
        
        # 生成日誌條目
        if recent_logs:
            for log_entry in recent_logs:
                agent = log_entry.get("agent", "未知")
                work_type = log_entry.get("work_type", "")
                description = log_entry.get("description", "")
                status = log_entry.get("status", "completed")
                timestamp = log_entry.get("timestamp", "")
                result = log_entry.get("result", "")
                
                # 格式化時間
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    time_str = timestamp
                
                status_class = f"status-{status}"
                status_text = {
                    "completed": "✅ 已完成",
                    "failed": "❌ 失敗",
                    "in_progress": "🔄 進行中"
                }.get(status, status)
                
                html_content += f"""
      <div class="log-entry" data-agent="{agent}" data-status="{status}">
        <div class="log-header">
          <div>
            <span class="log-agent">{agent}</span>
            <span class="log-type">{work_type}</span>
          </div>
          <span class="log-time">{time_str}</span>
        </div>
        <div class="log-description">{description}</div>
        <div>
          <span class="log-status {status_class}">{status_text}</span>
        </div>
"""
                
                if result:
                    html_content += f"""
        <div class="log-result">{result}</div>
"""
                
                html_content += """
      </div>
"""
        else:
            html_content += """
      <div class="empty-state">
        <div class="empty-state-icon">📝</div>
        <h3>尚無工作記錄</h3>
        <p>等待地端小 j 和雲端小 j 開始工作...</p>
      </div>
"""
        
        html_content += """
    </div>
  </div>
  
  <script>
    function filterLogs(filter) {
      const entries = document.querySelectorAll('.log-entry');
      const buttons = document.querySelectorAll('.filter-btn');
      
      // 更新按鈕狀態
      buttons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent.trim() === (filter === 'all' ? '全部' : 
            filter === 'completed' ? '已完成' : 
            filter === 'failed' ? '失敗' : filter)) {
          btn.classList.add('active');
        }
      });
      
      // 過濾日誌
      entries.forEach(entry => {
        if (filter === 'all') {
          entry.style.display = 'block';
        } else if (filter === 'completed' || filter === 'failed') {
          entry.style.display = entry.dataset.status === filter ? 'block' : 'none';
        } else {
          entry.style.display = entry.dataset.agent === filter ? 'block' : 'none';
        }
      });
    }
    
    // 自動刷新（每 30 秒）
    setInterval(() => {
      location.reload();
    }, 30000);
  </script>
</body>
</html>
"""
        
        # 儲存 HTML
        WORK_LOG_HTML.write_text(html_content, encoding="utf-8")
        
    except Exception as e:
        print(f"生成 HTML 日誌失敗: {e}")


def get_recent_logs(days: int = 7, agent: str = None) -> List[Dict[str, Any]]:
    """取得最近的工作日誌"""
    logs = []
    
    for i in range(days):
        date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        date = date.replace(day=date.day - i)
        log_file = WORK_LOG_DIR / f"work_log_{date.strftime('%Y%m%d')}.json"
        
        if log_file.exists():
            try:
                day_logs = json.loads(log_file.read_text(encoding="utf-8"))
                if agent:
                    day_logs = [l for l in day_logs if l.get("agent") == agent]
                logs.extend(day_logs)
            except:
                pass
    
    # 按時間排序
    logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return logs


if __name__ == "__main__":
    # 測試
    print("測試雙 j 工作日誌系統...")
    
    # 新增測試日誌
    add_work_log(
        agent="地端小 j",
        work_type="監控檢查",
        description="每小時容器狀態檢查完成",
        status="completed",
        result="9 個標準容器全部運行中，系統健康度 100%"
    )
    
    add_work_log(
        agent="雲端小 j (JULES)",
        work_type="任務執行",
        description="執行容器維護任務",
        status="completed",
        result="容器狀態已恢復正常"
    )
    
    print("✅ 測試日誌已新增")
    print(f"HTML 日誌: {WORK_LOG_HTML}")
