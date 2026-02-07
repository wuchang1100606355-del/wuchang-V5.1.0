#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
create_file_optimization_task_for_jules.py

建立本機及伺服器檔案優化合併任務給 JULES

功能：
- 生成詳細的網路問題描述
- 包含檢查和修復步驟
- 上傳到 Google Tasks 供 JULES 處理
"""

import sys
import json
import time
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def create_file_optimization_task():
    """建立檔案優化合併任務內容"""
    
    task_content = """# 本機及伺服器檔案優化合併任務

## 問題描述

系統目前存在網路連接問題，需要 JULES 協助解決。

## 當前狀態

### ✅ 已正常
- 控制中心運行中（端口 8788）
- VPN 連接正常（10.8.0.6 → 10.8.0.1）
- 本地服務正常

### ❌ 待解決
- 網路共享路徑不可訪問：`\\\\HOME-COMMPUT\\wuchang V5.1.0`
- 伺服器端服務無回應
- 環境變數未完整設定

## 需要檢查的項目

### 1. 網路共享路徑
- [ ] 確認伺服器名稱：`HOME-COMMPUT` vs `HOME-COMPUTER`
- [ ] 測試網路連接：`ping HOME-COMMPUT`
- [ ] 掃描網路上的電腦：`net view`
- [ ] 確認共享資料夾是否存在
- [ ] 檢查共享權限設定

### 2. 伺服器端服務
- [ ] 確認伺服器端控制中心是否運行
- [ ] 檢查實際應用伺服器 IP（可能不是 10.8.0.1）
- [ ] 掃描 VPN 網段內的其他 IP（10.8.0.2-10.8.0.10）
- [ ] 檢查防火牆設定
- [ ] 測試 TCP 連接（端口 8788, 8799）
- [ ] 測試 HTTP 健康檢查端點

### 3. 環境變數設定
- [ ] 設定 `WUCHANG_HEALTH_URL`（伺服器健康檢查 URL）
- [ ] 設定 `WUCHANG_COPY_TO`（正確的共享路徑）
- [ ] 設定 `WUCHANG_HUB_URL`（Little J Hub URL）
- [ ] 設定 `WUCHANG_HUB_TOKEN`（Hub 認證 Token）

## 修復步驟

### 步驟 1：確認網路共享
```powershell
# 測試伺服器連接
ping HOME-COMMPUT
ping HOME-COMPUTER

# 查看網路上的電腦
net view

# 嘗試訪問共享
dir \\HOME-COMMPUT\wuchang*
dir \\HOME-COMPUTER\wuchang*
```

### 步驟 2：映射網路磁碟機
```powershell
# 取消現有映射（如果有）
net use Z: /delete

# 使用認證資訊映射
net use Z: \\正確路徑\wuchang V5.1.0 /user:帳號 密碼 /persistent:yes

# 驗證映射
Test-Path Z:\
dir Z:\
```

### 步驟 3：設定環境變數
```powershell
# 設定健康檢查 URL
[System.Environment]::SetEnvironmentVariable("WUCHANG_HEALTH_URL", "https://coffeeLofe.asuscomm.com:8443/health", "User")

# 設定共享路徑
[System.Environment]::SetEnvironmentVariable("WUCHANG_COPY_TO", "Z:\", "User")

# 設定 Hub URL（如果需要）
[System.Environment]::SetEnvironmentVariable("WUCHANG_HUB_URL", "http://10.8.0.1:8799", "User")
```

### 步驟 4：測試連接
```powershell
# 測試健康檢查
Invoke-WebRequest -Uri $env:WUCHANG_HEALTH_URL -UseBasicParsing

# 測試檔案同步
python check_server_connection.py
```

## 預期結果

- ✅ 網路共享路徑可訪問
- ✅ 伺服器端服務可正常連接
- ✅ 環境變數正確設定
- ✅ 檔案同步功能正常

## 相關檔案

- `network_interconnection_config.json` - 網路配置
- `check_server_connection.py` - 連接檢查工具
- `fix_network_drive.py` - 網路磁碟機修復工具
- `diagnose_network_share.py` - 網路共享診斷工具

## 優先級

**高優先級** - 影響檔案同步和系統整合

## 備註

請 JULES 協助：
1. 確認正確的伺服器名稱和共享路徑
2. 檢查伺服器端服務狀態
3. 提供正確的連接資訊
4. 協助完成環境變數設定
"""
    
    return task_content


def upload_task_to_jules():
    """上傳任務到 Google Tasks"""
    try:
        from google_tasks_integration import get_google_tasks_integration
        
        integration = get_google_tasks_integration()
        
        # 獲取或建立任務列表
        task_lists = integration.list_task_lists()
        target_list = None
        
        for task_list in task_lists:
            if "Wuchang" in task_list.title or "File Sync" in task_list.title:
                target_list = task_list
                break
        
        if not target_list:
            # 建立新的任務列表
            target_list = integration.create_task_list("Wuchang File Optimization")
            print(f"✓ 已建立任務列表: {target_list.title}")
        
        # 建立任務
        task_title = f"本機及伺服器檔案優化合併 - {time.strftime('%Y-%m-%d %H:%M')}"
        task_content = create_file_optimization_task()
        
        task = integration.create_task(
            task_list_id=target_list.id,
            title=task_title,
            notes=task_content
        )
        
        print()
        print("=" * 70)
        print("【任務已建立】")
        print("=" * 70)
        print()
        print(f"任務標題: {task_title}")
        print(f"任務列表: {target_list.title}")
        print(f"任務 ID: {task.id}")
        print()
        print("任務內容已上傳到 Google Tasks")
        print("JULES 可以在 Google Tasks 中查看並處理")
        print()
        
        # 嘗試獲取任務 URL
        try:
            task_url = f"https://jules.google.com/task/{task.id}"
            print(f"任務連結: {task_url}")
        except:
            pass
        
        return task
        
    except Exception as e:
        print(f"✗ 上傳任務失敗: {e}")
        print()
        print("任務內容已準備好，可以手動複製到 Google Tasks")
        print()
        return None


def main():
    """主函數"""
    print("=" * 70)
    print("建立本機及伺服器檔案優化合併任務給 JULES")
    print("=" * 70)
    print()
    
    # 生成任務內容
    task_content = create_file_optimization_task()
    
    # 顯示任務內容
    print("【任務內容預覽】")
    print()
    print(task_content[:500] + "...")
    print()
    
    # 上傳到 Google Tasks
    print("正在上傳到 Google Tasks...")
    print()
    
    task = upload_task_to_jules()
    
    if task:
        print("=" * 70)
        print("【完成】")
        print("=" * 70)
        print()
        print("✓ 任務已成功上傳到 Google Tasks")
        print()
        print("JULES 現在可以：")
        print("  1. 在 Google Tasks 中查看任務")
        print("  2. 按照步驟檢查和本機及伺服器檔案優化合併")
        print("  3. 更新任務狀態")
        print()
        
        # 儲存任務內容到檔案
        task_file = BASE_DIR / f"network_fix_task_{time.strftime('%Y%m%d_%H%M%S')}.md"
        task_file.write_text(task_content, encoding="utf-8")
        print(f"✓ 任務內容已儲存到: {task_file.name}")
        print()
        return 0
    else:
        print("=" * 70)
        print("【需要手動上傳】")
        print("=" * 70)
        print()
        print("請手動將以下內容複製到 Google Tasks：")
        print()
        print("-" * 70)
        print(task_content)
        print("-" * 70)
        print()
        
        # 儲存任務內容到檔案
        task_file = BASE_DIR / f"network_fix_task_{time.strftime('%Y%m%d_%H%M%S')}.md"
        task_file.write_text(task_content, encoding="utf-8")
        print(f"✓ 任務內容已儲存到: {task_file.name}")
        print("  可以開啟此檔案複製內容")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
