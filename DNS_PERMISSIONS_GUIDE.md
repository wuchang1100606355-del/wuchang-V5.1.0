# 權限不足問題說明與解決方案

## 什麼是「權限不足」？

「權限不足」（Permission Denied）是指在嘗試執行某個操作時，當前使用的帳號或服務帳號沒有足夠的權限來完成該操作。

## 在 Google Cloud DNS API 中的權限不足

### 常見錯誤訊息

```
ERROR: (gcloud.dns.managed-zones.create) PERMISSION_DENIED: 
The caller does not have permission

或

403 Forbidden: The caller does not have permission
```

### 原因分析

1. **IAM 角色不足**
   - 帳號沒有被授予必要的 IAM 角色
   - 服務帳號缺少 DNS 管理權限

2. **API 未啟用**
   - Cloud DNS API 未在專案中啟用
   - 需要先啟用 API 才能使用

3. **專案權限問題**
   - 不是專案的擁有者或編輯者
   - 沒有專案層級的權限

4. **服務帳號權限不足**
   - 服務帳號沒有正確的 IAM 角色
   - 金鑰檔案路徑錯誤或過期

## 需要的權限

### 最小權限要求

要管理 Google Cloud DNS，需要以下 IAM 角色之一：

1. **DNS 管理員** (roles/dns.admin)
   - 完整 DNS 管理權限
   - 可以建立、修改、刪除 DNS 區域和記錄

2. **DNS 編輯者** (roles/dns.editor)
   - 可以修改 DNS 記錄
   - 但不能建立或刪除 DNS 區域

3. **專案編輯者** (roles/editor)
   - 專案層級的編輯權限
   - 包含 DNS 管理權限

4. **專案擁有者** (roles/owner)
   - 完整專案權限
   - 包含所有 DNS 管理權限

### 具體權限列表

DNS 管理員角色包含以下權限：

```
dns.managedZones.create
dns.managedZones.delete
dns.managedZones.get
dns.managedZones.list
dns.managedZones.update
dns.resourceRecordSets.create
dns.resourceRecordSets.delete
dns.resourceRecordSets.get
dns.resourceRecordSets.list
dns.resourceRecordSets.update
```

## 如何檢查權限

### 方法一：透過 Google Cloud Console

1. 前往 IAM 和管理 → IAM
2. 找到您的帳號或服務帳號
3. 查看已授予的角色
4. 確認是否有 DNS 相關角色

### 方法二：透過 gcloud CLI

```bash
# 檢查當前使用者的權限
gcloud projects get-iam-policy PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:user:YOUR_EMAIL"

# 檢查服務帳號權限
gcloud projects get-iam-policy PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:SERVICE_ACCOUNT_EMAIL"
```

### 方法三：測試操作

```bash
# 嘗試列出 DNS 區域（需要 dns.managedZones.list 權限）
gcloud dns managed-zones list

# 如果出現權限錯誤，表示權限不足
```

## 解決方案

### 方案一：授予 IAM 角色（推薦）

#### 為使用者帳號授予權限

```bash
# 授予 DNS 管理員角色給使用者
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="user:YOUR_EMAIL@example.com" \
    --role="roles/dns.admin"
```

#### 為服務帳號授予權限

```bash
# 授予 DNS 管理員角色給服務帳號
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:SERVICE_ACCOUNT@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/dns.admin"
```

### 方案二：透過 Google Cloud Console

1. 前往「IAM 和管理」→「IAM」
2. 點擊「授予存取權」
3. 輸入使用者或服務帳號
4. 選擇角色：「DNS 管理員」
5. 點擊「儲存」

### 方案三：使用專案擁有者帳號

如果您是專案擁有者，可以：
1. 直接使用擁有者帳號操作
2. 或授予其他帳號必要的權限

## 權限檢查腳本

以下是一個 Python 腳本，用於檢查 Google Cloud DNS 權限：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_dns_permissions.py

檢查 Google Cloud DNS 權限
"""

import sys
import subprocess
import json
from typing import Dict, List, Tuple

def check_gcloud_installed() -> bool:
    """檢查 gcloud CLI 是否已安裝"""
    try:
        subprocess.run(["gcloud", "--version"], 
                      capture_output=True, 
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_current_project() -> str:
    """獲取當前專案 ID"""
    try:
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""

def get_current_user() -> str:
    """獲取當前使用者"""
    try:
        result = subprocess.run(
            ["gcloud", "config", "get-value", "account"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""

def check_dns_api_enabled(project_id: str) -> bool:
    """檢查 Cloud DNS API 是否已啟用"""
    try:
        result = subprocess.run(
            ["gcloud", "services", "list", 
             "--enabled", 
             "--filter", "name:dns.googleapis.com",
             "--project", project_id],
            capture_output=True,
            text=True,
            check=True
        )
        return "dns.googleapis.com" in result.stdout
    except subprocess.CalledProcessError:
        return False

def check_dns_permissions(project_id: str, user_email: str) -> Dict:
    """檢查 DNS 權限"""
    permissions = {
        "can_list_zones": False,
        "can_create_zone": False,
        "can_list_records": False,
        "roles": []
    }
    
    # 檢查 IAM 角色
    try:
        result = subprocess.run(
            ["gcloud", "projects", "get-iam-policy", project_id,
             "--flatten", "bindings[].members",
             "--filter", f"bindings.members:{user_email}",
             "--format", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        
        policy = json.loads(result.stdout)
        for binding in policy.get("bindings", []):
            role = binding.get("role", "")
            permissions["roles"].append(role)
            
            # 檢查是否有 DNS 相關角色
            if "dns.admin" in role or "dns.editor" in role:
                permissions["can_list_zones"] = True
                permissions["can_create_zone"] = True
                permissions["can_list_records"] = True
            elif "editor" in role or "owner" in role:
                permissions["can_list_zones"] = True
                permissions["can_create_zone"] = True
                permissions["can_list_records"] = True
    except subprocess.CalledProcessError:
        pass
    
    # 實際測試權限
    try:
        # 測試列出 DNS 區域
        subprocess.run(
            ["gcloud", "dns", "managed-zones", "list",
             "--project", project_id],
            capture_output=True,
            check=True
        )
        permissions["can_list_zones"] = True
    except subprocess.CalledProcessError:
        pass
    
    return permissions

def main():
    """主函數"""
    print("=" * 60)
    print("Google Cloud DNS 權限檢查工具")
    print("=" * 60)
    print()
    
    # 檢查 gcloud 是否安裝
    if not check_gcloud_installed():
        print("❌ 錯誤：gcloud CLI 未安裝")
        print("請先安裝 Google Cloud SDK")
        print("下載地址：https://cloud.google.com/sdk/docs/install")
        sys.exit(1)
    
    print("✓ gcloud CLI 已安裝")
    print()
    
    # 獲取當前專案
    project_id = get_current_project()
    if not project_id:
        print("❌ 錯誤：未設定專案")
        print("請執行：gcloud config set project PROJECT_ID")
        sys.exit(1)
    
    print(f"專案 ID: {project_id}")
    
    # 獲取當前使用者
    user_email = get_current_user()
    if user_email:
        print(f"當前使用者: {user_email}")
    print()
    
    # 檢查 API 是否啟用
    print("檢查 Cloud DNS API...")
    if check_dns_api_enabled(project_id):
        print("✓ Cloud DNS API 已啟用")
    else:
        print("❌ Cloud DNS API 未啟用")
        print("請執行：gcloud services enable dns.googleapis.com")
        print()
    
    # 檢查權限
    print("檢查 DNS 權限...")
    permissions = check_dns_permissions(project_id, user_email)
    
    print(f"已授予的角色: {', '.join(permissions['roles']) if permissions['roles'] else '無'}")
    print()
    
    # 顯示權限狀態
    print("權限狀態：")
    print(f"  列出 DNS 區域: {'✓' if permissions['can_list_zones'] else '✗'}")
    print(f"  建立 DNS 區域: {'✓' if permissions['can_create_zone'] else '✗'}")
    print(f"  管理 DNS 記錄: {'✓' if permissions['can_list_records'] else '✗'}")
    print()
    
    # 提供建議
    if not permissions['can_list_zones']:
        print("⚠ 權限不足！")
        print()
        print("解決方案：")
        print(f"  授予 DNS 管理員角色：")
        print(f"  gcloud projects add-iam-policy-binding {project_id} \\")
        print(f"      --member='user:{user_email}' \\")
        print(f"      --role='roles/dns.admin'")
        print()
    else:
        print("✓ 權限正常，可以管理 DNS")

if __name__ == "__main__":
    main()
```

## 常見權限錯誤與解決方法

### 錯誤 1: "The caller does not have permission"

**原因**：帳號沒有 DNS 管理權限

**解決方法**：
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="user:YOUR_EMAIL" \
    --role="roles/dns.admin"
```

### 錯誤 2: "API dns.googleapis.com is not enabled"

**原因**：Cloud DNS API 未啟用

**解決方法**：
```bash
gcloud services enable dns.googleapis.com --project=PROJECT_ID
```

### 錯誤 3: "Service account does not have permission"

**原因**：服務帳號權限不足

**解決方法**：
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
    --role="roles/dns.admin"
```

## 最佳實踐

1. **使用服務帳號**
   - 為應用程式使用服務帳號而非個人帳號
   - 服務帳號更安全且易於管理

2. **最小權限原則**
   - 只授予必要的權限
   - 避免使用過於寬鬆的角色（如 owner）

3. **定期審查權限**
   - 定期檢查 IAM 政策
   - 移除不再需要的權限

4. **使用自訂角色**
   - 如果預設角色權限過大，可以建立自訂角色
   - 只包含必要的權限

## 相關資源

- [Google Cloud IAM 文件](https://cloud.google.com/iam/docs)
- [Cloud DNS IAM 權限](https://cloud.google.com/dns/docs/access-control)
- [IAM 角色參考](https://cloud.google.com/iam/docs/understanding-roles)
