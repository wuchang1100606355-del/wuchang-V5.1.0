#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢視本地資料庫檔案狀態，判斷是否為新資料庫
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime
import json

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

def check_docker_volumes():
    """檢查 Docker Volume 資訊"""
    log("檢查 Docker Volume 資訊...", "INFO")
    
    try:
        # 列出所有 volumes
        result = subprocess.run(
            ['docker', 'volume', 'ls', '--format', '{{.Name}}\t{{.Driver}}'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            volumes = result.stdout.strip().split('\n')
            wuchang_volumes = [v for v in volumes if 'wuchang' in v.lower() or 'odoo' in v.lower() or 'postgres' in v.lower()]
            
            if wuchang_volumes:
                log(f"找到 {len(wuchang_volumes)} 個相關 Volume:", "SUCCESS")
                for vol in wuchang_volumes:
                    print(f"  - {vol}")
                    
                    # 檢查 volume 的詳細資訊
                    inspect_result = subprocess.run(
                        ['docker', 'volume', 'inspect', vol.split('\t')[0]],
                        capture_output=True,
                        text=True
                    )
                    if inspect_result.returncode == 0:
                        vol_info = json.loads(inspect_result.stdout)[0]
                        mountpoint = vol_info.get('Mountpoint', 'N/A')
                        created = vol_info.get('CreatedAt', 'N/A')
                        print(f"    掛載點: {mountpoint}")
                        print(f"    建立時間: {created}")
            else:
                log("未找到相關的 Docker Volume", "WARNING")
            
            return wuchang_volumes
        else:
            log("無法列出 Docker Volumes", "ERROR")
            return []
    except FileNotFoundError:
        log("Docker 未運行或未安裝", "ERROR")
        return []
    except Exception as e:
        log(f"檢查 Volume 時發生錯誤: {e}", "ERROR")
        return []

def check_local_database_files():
    """檢查本地資料庫檔案"""
    log("檢查本地資料庫檔案...", "INFO")
    
    # 可能的資料庫檔案位置
    possible_paths = [
        WORKSPACE_PATH / 'database',
        WORKSPACE_PATH / 'data' / 'postgres',
        WORKSPACE_PATH / 'local_storage' / 'database',
        WORKSPACE_PATH / 'containers' / 'data',
    ]
    
    database_files = []
    
    for db_path in possible_paths:
        if db_path.exists():
            log(f"找到資料庫目錄: {db_path}", "SUCCESS")
            
            # 遞迴搜尋資料庫相關檔案
            for root, dirs, files in os.walk(db_path):
                for file in files:
                    file_path = Path(root) / file
                    # 檢查檔案類型
                    if any(file.endswith(ext) for ext in ['.sql', '.dump', '.backup', '.db', '.sqlite']):
                        stat = file_path.stat()
                        file_info = {
                            'path': str(file_path.relative_to(WORKSPACE_PATH)),
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime),
                            'created': datetime.fromtimestamp(stat.st_ctime)
                        }
                        database_files.append(file_info)
    
    if database_files:
        log(f"找到 {len(database_files)} 個資料庫相關檔案:", "SUCCESS")
        for file_info in database_files:
            print(f"  📄 {file_info['path']}")
            print(f"     大小: {file_info['size']:,} bytes")
            print(f"     建立時間: {file_info['created'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"     修改時間: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
            print()
    else:
        log("未找到本地資料庫檔案", "INFO")
        log("資料庫可能存儲在 Docker Volume 中", "INFO")
    
    return database_files

def check_docker_compose_config():
    """檢查 Docker Compose 配置中的資料庫設定"""
    log("檢查 Docker Compose 配置...", "INFO")
    
    compose_files = [
        WORKSPACE_PATH / 'docker-compose.yml',
        WORKSPACE_PATH / 'docker-compose.override.yml'
    ]
    
    db_config = {}
    
    for compose_file in compose_files:
        if compose_file.exists():
            log(f"檢查 {compose_file.name}...", "DEBUG")
            try:
                with open(compose_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # 檢查資料庫相關配置
                    if 'POSTGRES_DB' in content or 'postgres' in content.lower():
                        # 提取資料庫名稱
                        import re
                        db_name_match = re.search(r'POSTGRES_DB[=:]\s*(\w+)', content)
                        if db_name_match:
                            db_config['database_name'] = db_name_match.group(1)
                        
                        # 檢查 volume 配置
                        volume_matches = re.findall(r'-\s*([^:]+):([^\s]+)', content)
                        for host_path, container_path in volume_matches:
                            if 'postgres' in container_path.lower() or 'data' in container_path.lower():
                                db_config['volume_mount'] = f"{host_path} -> {container_path}"
                        
                        log(f"在 {compose_file.name} 中找到資料庫配置", "SUCCESS")
            except Exception as e:
                log(f"讀取 {compose_file.name} 時發生錯誤: {e}", "WARNING")
    
    if db_config:
        print("資料庫配置:")
        for key, value in db_config.items():
            print(f"  {key}: {value}")
    else:
        log("未找到資料庫配置", "WARNING")
    
    return db_config

def check_database_backups():
    """檢查資料庫備份"""
    log("檢查資料庫備份...", "INFO")
    
    backup_dirs = [
        WORKSPACE_PATH / 'database' / 'backups',
        WORKSPACE_PATH / 'backups' / 'database',
    ]
    
    backups = []
    
    for backup_dir in backup_dirs:
        if backup_dir.exists():
            log(f"找到備份目錄: {backup_dir}", "SUCCESS")
            for file in backup_dir.iterdir():
                if file.is_file():
                    stat = file.stat()
                    backups.append({
                        'name': file.name,
                        'path': str(file.relative_to(WORKSPACE_PATH)),
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime)
                    })
    
    if backups:
        log(f"找到 {len(backups)} 個備份檔案:", "SUCCESS")
        for backup in backups:
            print(f"  📦 {backup['name']}")
            print(f"     大小: {backup['size']:,} bytes")
            print(f"     修改時間: {backup['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        log("未找到資料庫備份", "INFO")
    
    return backups

def check_database_age_in_container():
    """檢查容器內資料庫的年齡（如果 Docker 運行中）"""
    log("檢查容器內資料庫狀態...", "INFO")
    
    try:
        # 查找資料庫容器
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}}', '--filter', 'name=db'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            db_container = result.stdout.strip().split('\n')[0]
            log(f"找到資料庫容器: {db_container}", "SUCCESS")
            
            # 檢查資料庫建立時間
            query = """
            SELECT 
                datname,
                pg_size_pretty(pg_database_size(datname)) as size,
                (SELECT MIN(stat_reset) FROM pg_stat_database WHERE datname = current_database()) as first_activity
            FROM pg_database 
            WHERE datistemplate = false
            ORDER BY datname;
            """
            
            cmd = [
                'docker', 'exec', db_container,
                'psql', '-U', 'odoo', '-t', '-A', '-F', '|', '-c', query
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                log("資料庫資訊:", "SUCCESS")
                print(result.stdout)
                return True
        else:
            log("未找到運行中的資料庫容器", "WARNING")
            return False
    except Exception as e:
        log(f"檢查容器內資料庫時發生錯誤: {e}", "WARNING")
        return False

def determine_if_new_database():
    """判斷是否為新資料庫"""
    log("分析資料庫狀態...", "INFO")
    
    indicators = {
        'new_database': [],
        'existing_database': []
    }
    
    # 檢查本地檔案
    local_files = check_local_database_files()
    if not local_files:
        indicators['new_database'].append("未找到本地資料庫檔案")
    else:
        # 檢查檔案年齡
        now = datetime.now()
        for file_info in local_files:
            age_days = (now - file_info['created']).days
            if age_days < 7:
                indicators['new_database'].append(f"檔案 {file_info['path']} 建立於 {age_days} 天前")
            else:
                indicators['existing_database'].append(f"檔案 {file_info['path']} 建立於 {age_days} 天前")
    
    # 檢查備份
    backups = check_database_backups()
    if not backups:
        indicators['new_database'].append("未找到資料庫備份")
    else:
        indicators['existing_database'].append(f"找到 {len(backups)} 個備份檔案")
    
    # 總結
    print("\n" + "=" * 60)
    print("📊 資料庫狀態分析")
    print("=" * 60)
    
    if len(indicators['new_database']) > len(indicators['existing_database']):
        log("判斷結果: 可能是新資料庫", "INFO")
        print("\n新資料庫指標:")
        for indicator in indicators['new_database']:
            print(f"  • {indicator}")
    else:
        log("判斷結果: 可能是現有資料庫", "INFO")
        print("\n現有資料庫指標:")
        for indicator in indicators['existing_database']:
            print(f"  • {indicator}")
    
    if indicators['new_database']:
        print("\n新資料庫指標:")
        for indicator in indicators['new_database']:
            print(f"  • {indicator}")

def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("  📊 本地資料庫檔案檢視工具")
    print("=" * 60)
    
    # 1. 檢查 Docker Volumes
    print("\n" + "-" * 60)
    volumes = check_docker_volumes()
    
    # 2. 檢查本地檔案
    print("\n" + "-" * 60)
    local_files = check_local_database_files()
    
    # 3. 檢查 Docker Compose 配置
    print("\n" + "-" * 60)
    db_config = check_docker_compose_config()
    
    # 4. 檢查備份
    print("\n" + "-" * 60)
    backups = check_database_backups()
    
    # 5. 檢查容器內資料庫（如果 Docker 運行）
    print("\n" + "-" * 60)
    container_check = check_database_age_in_container()
    
    # 6. 判斷是否為新資料庫
    print("\n" + "-" * 60)
    determine_if_new_database()
    
    print("\n" + "=" * 60)
    print("  ✅ 檢視完成")
    print("=" * 60)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
