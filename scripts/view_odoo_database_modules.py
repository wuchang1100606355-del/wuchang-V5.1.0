#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢視 Odoo 容器內的資料庫與模組資訊
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# 工作區路徑
WORKSPACE_PATH = Path(__file__).parent.parent

def log(message: str, level: str = "INFO"):
    """記錄訊息"""
    icons = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️",
        "DEBUG": "🔍"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")

def check_docker_running():
    """檢查 Docker 是否運行"""
    try:
        result = subprocess.run(
            ['docker', 'ps'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def get_container_name():
    """獲取 Odoo 容器名稱"""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}}', '--filter', 'name=wuchang'],
            cwd=WORKSPACE_PATH,
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            containers = [c.strip() for c in result.stdout.strip().split('\n') if c.strip()]
            for container in containers:
                if 'web' in container.lower() or 'odoo' in container.lower():
                    return container
            return containers[0] if containers else None
        return None
    except Exception as e:
        log(f"獲取容器名稱時發生錯誤: {e}", "ERROR")
        return None

def get_db_container_name():
    """獲取資料庫容器名稱"""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}}', '--filter', 'name=wuchang'],
            cwd=WORKSPACE_PATH,
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            containers = [c.strip() for c in result.stdout.strip().split('\n') if c.strip()]
            for container in containers:
                if 'db' in container.lower() or 'postgres' in container.lower():
                    return container
        return None
    except Exception as e:
        log(f"獲取資料庫容器名稱時發生錯誤: {e}", "ERROR")
        return None

def list_databases(db_container):
    """列出所有資料庫"""
    log("列出所有資料庫...", "INFO")
    try:
        query = "SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;"
        cmd = [
            'docker', 'exec', db_container,
            'psql', '-U', 'odoo', '-t', '-c', query
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            databases = [db.strip() for db in result.stdout.strip().split('\n') if db.strip()]
            log(f"找到 {len(databases)} 個資料庫:", "SUCCESS")
            for db in databases:
                print(f"  - {db}")
            return databases
        else:
            log(f"查詢資料庫失敗: {result.stderr}", "ERROR")
            return []
    except Exception as e:
        log(f"列出資料庫時發生錯誤: {e}", "ERROR")
        return []

def get_module_list(db_container, db_name='admin'):
    """獲取模組列表"""
    log(f"獲取資料庫 '{db_name}' 中的模組列表...", "INFO")
    
    query = """
    SELECT 
        name,
        state,
        latest_version,
        author,
        category_id,
        shortdesc
    FROM ir_module_module
    ORDER BY state, name;
    """
    
    try:
        cmd = [
            'docker', 'exec', db_container,
            'psql', '-U', 'odoo', '-d', db_name,
            '-c', query
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout
        else:
            log(f"查詢模組列表失敗: {result.stderr}", "ERROR")
            return None
    except Exception as e:
        log(f"獲取模組列表時發生錯誤: {e}", "ERROR")
        return None

def get_module_by_state(db_container, db_name='admin', state='to install'):
    """根據狀態獲取模組"""
    log(f"獲取狀態為 '{state}' 的模組...", "INFO")
    
    query = f"""
    SELECT 
        name,
        state,
        latest_version,
        shortdesc
    FROM ir_module_module
    WHERE state = '{state}'
    ORDER BY name;
    """
    
    try:
        cmd = [
            'docker', 'exec', db_container,
            'psql', '-U', 'odoo', '-d', db_name,
            '-c', query
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout
        else:
            log(f"查詢模組失敗: {result.stderr}", "ERROR")
            return None
    except Exception as e:
        log(f"獲取模組時發生錯誤: {e}", "ERROR")
        return None

def get_ide_modules(db_container, db_name='admin'):
    """獲取 IDE 相關模組"""
    log("獲取 IDE 相關模組...", "INFO")
    
    query = """
    SELECT 
        name,
        state,
        latest_version,
        shortdesc
    FROM ir_module_module
    WHERE name LIKE '%ide%' 
       OR name LIKE '%editor%'
       OR shortdesc LIKE '%IDE%'
       OR shortdesc LIKE '%editor%'
    ORDER BY name;
    """
    
    try:
        cmd = [
            'docker', 'exec', db_container,
            'psql', '-U', 'odoo', '-d', db_name,
            '-c', query
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout
        else:
            log(f"查詢 IDE 模組失敗: {result.stderr}", "ERROR")
            return None
    except Exception as e:
        log(f"獲取 IDE 模組時發生錯誤: {e}", "ERROR")
        return None

def get_module_statistics(db_container, db_name='admin'):
    """獲取模組統計資訊"""
    log("獲取模組統計資訊...", "INFO")
    
    query = """
    SELECT 
        state,
        COUNT(*) as count
    FROM ir_module_module
    GROUP BY state
    ORDER BY state;
    """
    
    try:
        cmd = [
            'docker', 'exec', db_container,
            'psql', '-U', 'odoo', '-d', db_name,
            '-c', query
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout
        else:
            log(f"查詢統計資訊失敗: {result.stderr}", "ERROR")
            return None
    except Exception as e:
        log(f"獲取統計資訊時發生錯誤: {e}", "ERROR")
        return None

def get_installed_modules(db_container, db_name='admin', limit=50):
    """獲取已安裝的模組（前 N 個）"""
    log(f"獲取已安裝的模組（前 {limit} 個）...", "INFO")
    
    query = f"""
    SELECT 
        name,
        latest_version,
        author,
        shortdesc
    FROM ir_module_module
    WHERE state = 'installed'
    ORDER BY name
    LIMIT {limit};
    """
    
    try:
        cmd = [
            'docker', 'exec', db_container,
            'psql', '-U', 'odoo', '-d', db_name,
            '-c', query
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout
        else:
            log(f"查詢已安裝模組失敗: {result.stderr}", "ERROR")
            return None
    except Exception as e:
        log(f"獲取已安裝模組時發生錯誤: {e}", "ERROR")
        return None

def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("  📊 Odoo 資料庫與模組檢視工具")
    print("=" * 60)
    
    # 檢查 Docker
    if not check_docker_running():
        log("Docker 未運行，請先啟動 Docker Desktop", "ERROR")
        return 1
    
    # 獲取容器名稱
    db_container = get_db_container_name()
    if not db_container:
        log("找不到資料庫容器，嘗試使用預設名稱...", "WARNING")
        # 嘗試常見的容器名稱
        possible_names = ['wuchangv510-db-1', 'wuchang-db-1', 'db']
        for name in possible_names:
            try:
                result = subprocess.run(
                    ['docker', 'inspect', name],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    db_container = name
                    log(f"找到資料庫容器: {db_container}", "SUCCESS")
                    break
            except:
                continue
        
        if not db_container:
            log("無法找到資料庫容器", "ERROR")
            log("請確認 Docker 容器正在運行", "INFO")
            return 1
    
    log(f"使用資料庫容器: {db_container}", "INFO")
    
    # 列出所有資料庫
    print("\n" + "-" * 60)
    databases = list_databases(db_container)
    
    if not databases:
        log("未找到任何資料庫", "WARNING")
        return 1
    
    # 使用第一個資料庫或 'admin'
    db_name = 'admin' if 'admin' in databases else databases[0]
    log(f"使用資料庫: {db_name}", "INFO")
    
    # 模組統計資訊
    print("\n" + "-" * 60)
    print("📈 模組狀態統計")
    print("-" * 60)
    stats = get_module_statistics(db_container, db_name)
    if stats:
        print(stats)
    
    # IDE 相關模組
    print("\n" + "-" * 60)
    print("🔧 IDE 相關模組")
    print("-" * 60)
    ide_modules = get_ide_modules(db_container, db_name)
    if ide_modules:
        print(ide_modules)
    else:
        log("未找到 IDE 相關模組", "WARNING")
    
    # 待安裝的模組
    print("\n" + "-" * 60)
    print("⏳ 待安裝的模組 (state = 'to install')")
    print("-" * 60)
    to_install = get_module_by_state(db_container, db_name, 'to install')
    if to_install:
        print(to_install)
    else:
        log("沒有待安裝的模組", "INFO")
    
    # 待升級的模組
    print("\n" + "-" * 60)
    print("⬆️ 待升級的模組 (state = 'to upgrade')")
    print("-" * 60)
    to_upgrade = get_module_by_state(db_container, db_name, 'to upgrade')
    if to_upgrade:
        print(to_upgrade)
    else:
        log("沒有待升級的模組", "INFO")
    
    # 已安裝的模組（前 50 個）
    print("\n" + "-" * 60)
    print("✅ 已安裝的模組 (前 50 個)")
    print("-" * 60)
    installed = get_installed_modules(db_container, db_name, 50)
    if installed:
        print(installed)
    
    # 完整的模組列表（可選，輸出較長）
    print("\n" + "-" * 60)
    print("📋 完整模組列表")
    print("-" * 60)
    print("(輸入 'y' 查看完整列表，其他鍵跳過)")
    try:
        user_input = input().strip().lower()
        if user_input == 'y':
            full_list = get_module_list(db_container, db_name)
            if full_list:
                print(full_list)
    except:
        pass
    
    print("\n" + "=" * 60)
    print("  ✅ 檢視完成")
    print("=" * 60)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
