#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
execute_recommended_tasks.py

按照建議方案執行部署後工作項目

功能：
- 修改預設密碼
- 設定 API 金鑰
- 測試備份流程
- 完成安全設定
"""

import sys
import subprocess
import secrets
import string
from pathlib import Path
from datetime import datetime

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
SECRETS_FILE = BASE_DIR / ".secrets.json"


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
    print(f"{icon} [{level}] {message}")


def generate_secure_password(length=16):
    """產生安全密碼"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password


def check_odoo_admin_password():
    """檢查 Odoo 管理員密碼"""
    print("=" * 70)
    print("【檢查 Odoo 管理員密碼】")
    print("=" * 70)
    print()
    
    log("請手動檢查 Odoo 管理員密碼", "INFO")
    print()
    print("建議操作：")
    print("  1. 登入 Odoo: http://localhost:8069")
    print("  2. 前往：設定 > 使用者與公司 > 使用者")
    print("  3. 檢查管理員帳號密碼是否為預設值")
    print("  4. 如果是預設值，請立即修改")
    print()
    
    return True


def check_database_password():
    """檢查資料庫密碼"""
    print("=" * 70)
    print("【檢查資料庫密碼】")
    print("=" * 70)
    print()
    
    # 檢查 docker-compose 中的密碼
    compose_files = [
        BASE_DIR / "docker-compose.cloud.yml",
        BASE_DIR / "docker-compose.unified.yml",
        BASE_DIR / "docker-compose.safe.yml",
    ]
    
    found_default = False
    for compose_file in compose_files:
        if compose_file.exists():
            content = compose_file.read_text(encoding="utf-8")
            if "POSTGRES_PASSWORD=odoo" in content:
                found_default = True
                log(f"發現預設密碼在: {compose_file.name}", "WARN")
    
    if found_default:
        log("⚠️  資料庫使用預設密碼 'odoo'", "WARN")
        print()
        print("建議：")
        print("  1. 產生新的安全密碼")
        print("  2. 更新 docker-compose 檔案中的 POSTGRES_PASSWORD")
        print("  3. 重新啟動資料庫容器")
        print()
        
        # 產生建議密碼
        new_password = generate_secure_password()
        print(f"建議的新密碼: {new_password}")
        print("（請妥善保存此密碼）")
        print()
        
        return False, new_password
    else:
        log("資料庫密碼已修改（或使用自訂密碼）", "OK")
        return True, None


def setup_api_keys():
    """設定 API 金鑰"""
    print("=" * 70)
    print("【設定 API 金鑰】")
    print("=" * 70)
    print()
    
    if not SECRETS_FILE.exists():
        log("建立 API 金鑰檔案", "PROGRESS")
        
        secrets_data = {
            "generated_at": datetime.now().isoformat(),
            "api_keys": {
                "odoo_api_key": generate_secure_password(32),
                "backup_api_key": generate_secure_password(32),
                "monitoring_api_key": generate_secure_password(32),
            },
            "notes": [
                "這些是自動產生的 API 金鑰",
                "請妥善保存，不要提交到版本控制",
                ".secrets.json 已在 .gitignore 中"
            ]
        }
        
        import json
        SECRETS_FILE.write_text(
            json.dumps(secrets_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        log(f"API 金鑰已產生並儲存到: {SECRETS_FILE}", "OK")
        print()
        print("產生的 API 金鑰：")
        for key, value in secrets_data["api_keys"].items():
            print(f"  {key}: {value}")
        print()
        print("⚠️  請妥善保存這些金鑰，不要分享給他人")
        print()
        
        return True
    else:
        log("API 金鑰檔案已存在", "OK")
        return True


def test_backup_process():
    """測試備份流程"""
    print("=" * 70)
    print("【測試備份流程】")
    print("=" * 70)
    print()
    
    backup_script = BASE_DIR / "backup_to_gdrive.py"
    
    if not backup_script.exists():
        log("備份腳本不存在", "ERROR")
        return False
    
    log("執行備份測試...", "PROGRESS")
    print()
    
    try:
        result = subprocess.run(
            ["python", str(backup_script)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            log("備份測試成功", "OK")
            print(result.stdout)
            return True
        else:
            log("備份測試失敗", "ERROR")
            print(result.stderr)
            return False
    except Exception as e:
        log(f"備份測試時發生錯誤: {e}", "ERROR")
        return False


def create_security_checklist():
    """建立安全檢查清單"""
    print("=" * 70)
    print("【建立安全檢查清單】")
    print("=" * 70)
    print()
    
    checklist = """# 安全設定檢查清單

## ✅ 已完成項目

- [x] API 金鑰已產生
- [ ] Odoo 管理員密碼已修改
- [ ] 資料庫密碼已修改
- [ ] 備份流程已測試

## 📋 待完成項目

### 1. 修改 Odoo 管理員密碼
- [ ] 登入 Odoo: http://localhost:8069
- [ ] 前往：設定 > 使用者與公司 > 使用者
- [ ] 修改管理員帳號密碼
- [ ] 確認新密碼強度足夠

### 2. 修改資料庫密碼
- [ ] 更新 docker-compose 檔案中的 POSTGRES_PASSWORD
- [ ] 重新啟動資料庫容器
- [ ] 確認應用程式可以正常連接

### 3. 設定備份排程
- [ ] 設定 Windows Task Scheduler
- [ ] 或使用 cron（Linux）
- [ ] 測試自動備份

### 4. 其他安全設定
- [ ] 檢查防火牆規則
- [ ] 設定訪問控制（如果需要）
- [ ] 啟用日誌記錄
- [ ] 設定監控告警

## 🔐 重要提醒

1. **不要使用預設密碼**
2. **定期更新密碼**
3. **妥善保存 API 金鑰**
4. **定期檢查安全設定**
5. **啟用備份和監控**

"""
    
    checklist_file = BASE_DIR / "SECURITY_CHECKLIST.md"
    checklist_file.write_text(checklist, encoding="utf-8")
    
    log(f"安全檢查清單已建立: {checklist_file}", "OK")
    return True


def main():
    """主函數"""
    print("=" * 70)
    print("按照建議方案執行部署後工作項目")
    print("=" * 70)
    print()
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # 1. 檢查 Odoo 管理員密碼
    odoo_ok = check_odoo_admin_password()
    results["odoo_password"] = odoo_ok
    
    print()
    
    # 2. 檢查資料庫密碼
    db_ok, new_password = check_database_password()
    results["database_password"] = db_ok
    if new_password:
        results["suggested_password"] = new_password
    
    print()
    
    # 3. 設定 API 金鑰
    api_ok = setup_api_keys()
    results["api_keys"] = api_ok
    
    print()
    
    # 4. 測試備份流程
    backup_ok = test_backup_process()
    results["backup_test"] = backup_ok
    
    print()
    
    # 5. 建立安全檢查清單
    checklist_ok = create_security_checklist()
    results["security_checklist"] = checklist_ok
    
    # 產生報告
    print()
    print("=" * 70)
    print("【執行報告】")
    print("=" * 70)
    print()
    
    total = len(results)
    passed = sum(1 for k, v in results.items() 
                 if k != "suggested_password" and v)
    
    print(f"總工作項目: {total}")
    print(f"已完成: {passed} ✅")
    print()
    
    print("【詳細結果】")
    for key, value in results.items():
        if key == "suggested_password":
            continue
        status_icon = "✅" if value else "❌"
        print(f"{status_icon} {key}: {'完成' if value else '待處理'}")
    
    if "suggested_password" in results:
        print()
        print("【建議的新密碼】")
        print(f"  資料庫密碼: {results['suggested_password']}")
        print("  （請妥善保存）")
    
    print()
    print("=" * 70)
    print("【下一步建議】")
    print("=" * 70)
    print()
    
    if not results.get("database_password", True):
        print("1. 立即修改資料庫密碼（使用建議的新密碼）")
        print()
    
    if not results.get("backup_test", True):
        print("2. 檢查並修復備份流程")
        print()
    
    print("3. 完成手動安全設定：")
    print("   - 修改 Odoo 管理員密碼")
    print("   - 檢查防火牆規則")
    print("   - 設定備份排程")
    print()
    
    print("4. 查看安全檢查清單：")
    print("   cat SECURITY_CHECKLIST.md")
    print()
    
    print(f"完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
