#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
create_container_management_task_for_jules.py

建立容器管理任務給 JULES

功能：
- 檢查當前容器狀態
- 生成容器管理任務內容
- 上傳到 Google Tasks 供 JULES 處理
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def get_container_status():
    """取得當前容器狀態"""
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{.Names}}|{{.Status}}|{{.Image}}"],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            return []
        
        containers = []
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            parts = line.split('|', 2)
            if len(parts) >= 2:
                containers.append({
                    "name": parts[0],
                    "status": parts[1],
                    "image": parts[2] if len(parts) > 2 else ""
                })
        
        return containers
    except Exception as e:
        print(f"無法取得容器狀態: {e}")
        return []


def load_jules_memory_bank():
    """載入 JULES 記憶庫"""
    memory_file = BASE_DIR / "jules_memory_bank.json"
    if memory_file.exists():
        try:
            return json.loads(memory_file.read_text(encoding="utf-8"))
        except:
            return {}
    return {}


def create_container_management_task():
    """建立容器管理任務內容"""
    
    # 讀取記憶庫
    memory_bank = load_jules_memory_bank()
    
    # 取得當前容器狀態
    containers = get_container_status()
    
    running_containers = [c for c in containers if "Up" in c["status"]]
    stopped_containers = [c for c in containers if "Exited" in c["status"] or "Created" in c["status"]]
    
    # 標準容器列表
    standard_containers = [
        "wuchangv510-caddy-1",
        "wuchangv510-caddy-ui-1",
        "wuchangv510-cloudflared-1",
        "wuchangv510-db-1",
        "wuchangv510-ollama-1",
        "wuchangv510-open-webui-1",
        "wuchangv510-portainer-1",
        "wuchangv510-uptime-kuma-1",
        "wuchangv510-wuchang-web-1"
    ]
    
    # 準備記憶庫上下文
    memory_context = ""
    if memory_bank:
        partnership = memory_bank.get("partnership", {})
        memory_context = f"""
## 記憶庫上下文（請先閱讀）

### 夥伴關係
- **地端小 j**：{partnership.get('地端小j', {}).get('身份', '本地 LLM 助理')}
  - 職責：{', '.join(partnership.get('地端小j', {}).get('職責', [])[:3])}...
- **雲端小 j (JULES)**：{partnership.get('雲端小j', {}).get('身份', '雲端 AI 助理')}
  - 職責：{', '.join(partnership.get('雲端小j', {}).get('職責', [])[:3])}...
- **協作模式**：{partnership.get('協作模式', {}).get('流程', '')}

### 系統架構
- 標準容器數量：{memory_bank.get('system_architecture', {}).get('容器架構', {}).get('標準容器數量', 9)}
- 健康標準：{memory_bank.get('system_architecture', {}).get('容器架構', {}).get('健康標準', {}).get('目標', '')}

---
"""
    
    task_content = f"""# 容器管理權限轉移給 JULES

{memory_context}

## 任務目標

將 Docker 容器管理權限轉移給 JULES，讓 JULES 可以自動管理系統容器。

## 當前容器狀態

### 運行中的容器 ({len(running_containers)} 個)
"""
    
    for container in running_containers:
        is_standard = "✅" if container["name"] in standard_containers else "⚠️"
        task_content += f"- {is_standard} **{container['name']}** - {container['status']}\n"
        task_content += f"  - 映像: {container['image']}\n"
    
    if stopped_containers:
        task_content += f"\n### 已停止的容器 ({len(stopped_containers)} 個)\n"
        for container in stopped_containers:
            task_content += f"- ⏹️ **{container['name']}** - {container['status']}\n"
    
    task_content += f"""
## 標準容器配置

系統標準配置應有 **9 個容器**：

1. **wuchangv510-caddy-1** - Web 伺服器（端口 80, 443）
2. **wuchangv510-caddy-ui-1** - Caddy 管理介面（端口 8081, 8444）
3. **wuchangv510-cloudflared-1** - Cloudflare Tunnel
4. **wuchangv510-db-1** - PostgreSQL 資料庫（端口 5432）
5. **wuchangv510-ollama-1** - AI 模型服務（端口 11434）
6. **wuchangv510-open-webui-1** - AI 介面（端口 8080）
7. **wuchangv510-portainer-1** - 容器管理介面（端口 9000）
8. **wuchangv510-uptime-kuma-1** - 監控工具（端口 3001）
9. **wuchangv510-wuchang-web-1** - Odoo ERP 系統（端口 8069）

## JULES 容器管理指令格式

### 檢查容器狀態
```json
{{
  "type": "execute",
  "command": "docker ps -a",
  "description": "檢查所有容器狀態"
}}
```

### 啟動容器
```json
{{
  "type": "execute",
  "command": "docker start <container_name>",
  "description": "啟動指定容器"
}}
```

### 停止容器
```json
{{
  "type": "execute",
  "command": "docker stop <container_name>",
  "description": "停止指定容器"
}}
```

### 重啟容器
```json
{{
  "type": "execute",
  "command": "docker restart <container_name>",
  "description": "重啟指定容器"
}}
```

### 使用 docker-compose 管理
```json
{{
  "type": "execute",
  "command": "docker-compose up -d",
  "description": "啟動所有服務",
  "working_dir": "C:\\\\wuchang V5.1.0\\\\wuchang-V5.1.0"
}}
```

```json
{{
  "type": "execute",
  "command": "docker-compose restart <service_name>",
  "description": "重啟指定服務",
  "working_dir": "C:\\\\wuchang V5.1.0\\\\wuchang-V5.1.0"
}}
```

```json
{{
  "type": "execute",
  "command": "docker-compose ps",
  "description": "查看服務狀態",
  "working_dir": "C:\\\\wuchang V5.1.0\\\\wuchang-V5.1.0"
}}
```

### 查看容器日誌
```json
{{
  "type": "execute",
  "command": "docker logs <container_name> --tail 50",
  "description": "查看容器日誌"
}}
```

### 檢查容器健康
```json
{{
  "type": "execute",
  "command": "python check_container_status.py",
  "description": "檢查容器健康狀態",
  "working_dir": "C:\\\\wuchang V5.1.0\\\\wuchang-V5.1.0"
}}
```

## 自動化管理建議

### 1. 定期健康檢查
- 每小時檢查一次容器狀態
- 如果容器異常，自動重啟
- 記錄異常情況

### 2. 容器監控
- 監控容器資源使用（CPU、記憶體）
- 監控容器日誌錯誤
- 自動清理舊日誌

### 3. 自動備份
- 定期備份容器配置
- 備份資料庫
- 備份重要資料

## 需要 JULES 執行的操作

1. **確認容器管理權限**
   - [ ] 確認 JULES 可以執行 docker 命令
   - [ ] 確認 JULES 可以訪問 docker-compose 配置
   - [ ] 測試基本容器管理命令

2. **設定自動檢查**
   - [ ] 建立定期容器健康檢查任務
   - [ ] 設定異常容器自動重啟機制
   - [ ] 設定日誌記錄

3. **整合到 JULES 任務系統**
   - [ ] 將容器管理指令加入 JULES 可執行指令列表
   - [ ] 測試容器管理指令執行
   - [ ] 確認結果回報機制

## 相關檔案

- `check_container_status.py` - 容器狀態檢查腳本
- `check_standard_containers.py` - 標準容器檢查腳本
- `docker-compose.unified.yml` - Docker Compose 配置
- `CONTAINER_MANAGEMENT_GUIDE.md` - 容器管理指南

## 優先級

**中優先級** - 提升系統自動化管理能力

## 備註

請 JULES 協助：
1. 確認容器管理權限和指令格式
2. 建立定期健康檢查機制
3. 整合容器管理到 JULES 任務系統
"""
    
    return task_content


def upload_to_google_tasks():
    """上傳任務到 Google Tasks"""
    try:
        from google_tasks_integration import get_google_tasks_integration
        
        integration = get_google_tasks_integration()
        
        # 尋找任務列表
        task_lists = integration.list_task_lists()
        target_list = None
        
        for task_list in task_lists:
            if "Wuchang" in task_list.title or "File Sync" in task_list.title:
                target_list = task_list
                break
        
        if not target_list:
            print("❌ 找不到適合的任務列表")
            print("請在 Google Tasks 中建立包含 'Wuchang' 或 'File Sync' 的任務列表")
            return False
        
        # 建立任務
        task_content = create_container_management_task()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        title = f"容器管理權限轉移給 JULES - {timestamp}"
        
        task = integration.create_task(
            task_list_id=target_list.id,
            title=title,
            notes=task_content
        )
        
        if task:
            print("✅ 任務已建立")
            print(f"   標題: {title}")
            print(f"   任務列表: {target_list.title}")
            print(f"   任務 ID: {task.id}")
            return True
        else:
            print("❌ 任務建立失敗")
            return False
            
    except ImportError:
        print("❌ 無法匯入 google_tasks_integration")
        print("請確認已安裝相關套件")
        return False
    except Exception as e:
        print(f"❌ 上傳任務時發生錯誤: {e}")
        return False


def main():
    """主函數"""
    print("=" * 70)
    print("建立容器管理任務給 JULES")
    print("=" * 70)
    print()
    
    # 檢查當前容器狀態
    print("【步驟 1：檢查當前容器狀態】")
    containers = get_container_status()
    print(f"找到 {len(containers)} 個容器")
    print()
    
    # 生成任務內容
    print("【步驟 2：生成任務內容】")
    task_content = create_container_management_task()
    
    # 儲存任務內容到檔案
    task_file = BASE_DIR / f"container_management_task_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    task_file.write_text(task_content, encoding='utf-8')
    print(f"✅ 任務內容已儲存到: {task_file.name}")
    print()
    
    # 詢問是否上傳到 Google Tasks
    print("【步驟 3：上傳到 Google Tasks】")
    try:
        upload = input("是否上傳到 Google Tasks？(y/n): ").strip().lower()
        if upload == 'y':
            if upload_to_google_tasks():
                print()
                print("✅ 任務已成功上傳到 Google Tasks")
                print("JULES 可以開始處理容器管理任務了")
            else:
                print()
                print("⚠️ 上傳失敗，但任務內容已儲存到檔案")
                print(f"您可以手動將內容複製到 Google Tasks: {task_file}")
        else:
            print("已跳過上傳")
            print(f"任務內容已儲存到: {task_file}")
    except KeyboardInterrupt:
        print()
        print("已取消")
    except Exception as e:
        print(f"發生錯誤: {e}")
        print(f"任務內容已儲存到: {task_file}")


if __name__ == "__main__":
    main()
