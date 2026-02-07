#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
收集部署資訊腳本
收集所有與部署相關的配置和狀態資訊
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
import yaml

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

def collect_file_info(file_path: Path):
    """收集檔案資訊"""
    if not file_path.exists():
        return None
    
    stat = file_path.stat()
    return {
        'path': str(file_path.relative_to(WORKSPACE_PATH)),
        'exists': True,
        'size': stat.st_size,
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
    }

def collect_docker_compose_info():
    """收集 Docker Compose 配置資訊"""
    log("收集 Docker Compose 配置...", "INFO")
    
    compose_files = [
        'docker-compose.yml',
        'docker-compose.override.yml',
        'docker-compose.prod.yml',
        'docker-compose.dev.yml'
    ]
    
    info = {}
    
    for filename in compose_files:
        file_path = WORKSPACE_PATH / filename
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 嘗試解析 YAML
                    try:
                        data = yaml.safe_load(content)
                        info[filename] = {
                            'exists': True,
                            'services': list(data.get('services', {}).keys()) if isinstance(data, dict) else [],
                            'volumes': list(data.get('volumes', {}).keys()) if isinstance(data, dict) else [],
                            'networks': list(data.get('networks', {}).keys()) if isinstance(data, dict) else [],
                            'file_info': collect_file_info(file_path)
                        }
                    except:
                        info[filename] = {
                            'exists': True,
                            'parsed': False,
                            'file_info': collect_file_info(file_path)
                        }
            except Exception as e:
                info[filename] = {
                    'exists': True,
                    'error': str(e)
                }
        else:
            info[filename] = {'exists': False}
    
    return info

def collect_env_info():
    """收集環境變數配置資訊"""
    log("收集環境變數配置...", "INFO")
    
    env_files = [
        '.env',
        'env.example',
        '.env.example'
    ]
    
    info = {}
    
    for filename in env_files:
        file_path = WORKSPACE_PATH / filename
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 提取環境變數（不包含敏感資訊）
                    env_vars = {}
                    for line in content.split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            # 隱藏敏感值
                            if any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key', 'token']):
                                env_vars[key] = '***HIDDEN***'
                            else:
                                env_vars[key] = value.strip()
                    
                    info[filename] = {
                        'exists': True,
                        'variables': env_vars,
                        'file_info': collect_file_info(file_path)
                    }
            except Exception as e:
                info[filename] = {
                    'exists': True,
                    'error': str(e)
                }
        else:
            info[filename] = {'exists': False}
    
    return info

def collect_database_info():
    """收集資料庫相關資訊"""
    log("收集資料庫資訊...", "INFO")
    
    info = {
        'database_directory': collect_file_info(WORKSPACE_PATH / 'database'),
        'backups': []
    }
    
    backup_path = WORKSPACE_PATH / 'database' / 'backups'
    if backup_path.exists():
        for item in backup_path.iterdir():
            if item.is_dir():
                stat = item.stat()
                info['backups'].append({
                    'name': item.name,
                    'type': 'directory',
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            elif item.is_file():
                stat = item.stat()
                info['backups'].append({
                    'name': item.name,
                    'type': 'file',
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
    
    return info

def collect_odoo_config_info():
    """收集 Odoo 配置資訊"""
    log("收集 Odoo 配置...", "INFO")
    
    info = {}
    
    # 檢查配置目錄
    config_path = WORKSPACE_PATH / 'config'
    if config_path.exists():
        info['config_directory'] = {
            'exists': True,
            'path': str(config_path.relative_to(WORKSPACE_PATH))
        }
        
        # 檢查 Odoo 配置檔案
        odoo_conf = config_path / 'odoo.conf'
        if odoo_conf.exists():
            info['odoo_conf'] = collect_file_info(odoo_conf)
    
    # 檢查 addons 目錄
    addons_paths = [
        WORKSPACE_PATH / 'wuchang_os' / 'addons',
        WORKSPACE_PATH / 'addons'
    ]
    
    info['addons_paths'] = []
    for addons_path in addons_paths:
        if addons_path.exists():
            modules = [d.name for d in addons_path.iterdir() if d.is_dir() and (d / '__manifest__.py').exists()]
            info['addons_paths'].append({
                'path': str(addons_path.relative_to(WORKSPACE_PATH)),
                'exists': True,
                'module_count': len(modules),
                'modules': modules[:20]  # 只列出前 20 個
            })
    
    return info

def collect_docker_status():
    """收集 Docker 狀態資訊"""
    log("收集 Docker 狀態...", "INFO")
    
    info = {
        'docker_available': False,
        'containers': [],
        'volumes': [],
        'images': []
    }
    
    try:
        # 檢查 Docker 是否可用
        result = subprocess.run(
            ['docker', '--version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            info['docker_available'] = True
            info['docker_version'] = result.stdout.strip()
            
            # 檢查容器
            result = subprocess.run(
                ['docker', 'ps', '-a', '--format', '{{.Names}}\t{{.Status}}\t{{.Image}}'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 3:
                            info['containers'].append({
                                'name': parts[0],
                                'status': parts[1],
                                'image': parts[2]
                            })
            
            # 檢查 Volumes
            result = subprocess.run(
                ['docker', 'volume', 'ls', '--format', '{{.Name}}\t{{.Driver}}'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            vol_name = parts[0]
                            # 只收集相關的 volumes
                            if any(keyword in vol_name.lower() for keyword in ['wuchang', 'odoo', 'postgres']):
                                info['volumes'].append({
                                    'name': vol_name,
                                    'driver': parts[1]
                                })
    except FileNotFoundError:
        info['error'] = 'Docker not found'
    except Exception as e:
        info['error'] = str(e)
    
    return info

def collect_scripts_info():
    """收集腳本資訊"""
    log("收集腳本資訊...", "INFO")
    
    scripts_path = WORKSPACE_PATH / 'scripts'
    info = {
        'scripts_directory': collect_file_info(scripts_path) if scripts_path.exists() else None,
        'scripts': []
    }
    
    if scripts_path.exists():
        for script_file in scripts_path.iterdir():
            if script_file.is_file() and script_file.suffix in ['.py', '.sh', '.bat', '.ps1']:
                info['scripts'].append({
                    'name': script_file.name,
                    'type': script_file.suffix,
                    'file_info': collect_file_info(script_file)
                })
    
    return info

def collect_project_structure():
    """收集專案結構資訊"""
    log("收集專案結構...", "INFO")
    
    key_directories = [
        'wuchang_os',
        'config',
        'database',
        'scripts',
        'containers',
        'backups',
        'logs',
        'uploads',
        'reports',
        'docs'
    ]
    
    structure = {}
    
    for dir_name in key_directories:
        dir_path = WORKSPACE_PATH / dir_name
        if dir_path.exists():
            structure[dir_name] = {
                'exists': True,
                'path': str(dir_path.relative_to(WORKSPACE_PATH)),
                'is_directory': dir_path.is_dir()
            }
        else:
            structure[dir_name] = {'exists': False}
    
    return structure

def collect_system_info():
    """收集系統資訊"""
    log("收集系統資訊...", "INFO")
    
    info = {
        'workspace_path': str(WORKSPACE_PATH),
        'collection_time': datetime.now().isoformat(),
        'python_version': sys.version,
        'platform': sys.platform
    }
    
    # 嘗試獲取 Git 資訊
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            cwd=WORKSPACE_PATH,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            info['git_repository'] = True
            # 獲取當前分支
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=WORKSPACE_PATH,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                info['git_branch'] = result.stdout.strip()
    except:
        info['git_repository'] = False
    
    return info

def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("  📊 部署資訊收集工具")
    print("=" * 60)
    
    deployment_info = {
        'system_info': collect_system_info(),
        'project_structure': collect_project_structure(),
        'docker_compose': collect_docker_compose_info(),
        'environment': collect_env_info(),
        'database': collect_database_info(),
        'odoo_config': collect_odoo_config_info(),
        'docker_status': collect_docker_status(),
        'scripts': collect_scripts_info()
    }
    
    # 儲存為 JSON
    output_file = WORKSPACE_PATH / 'reports' / f'deployment_info_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(deployment_info, f, ensure_ascii=False, indent=2)
    
    log(f"部署資訊已儲存至: {output_file}", "SUCCESS")
    
    # 顯示摘要
    print("\n" + "=" * 60)
    print("  📋 部署資訊摘要")
    print("=" * 60)
    print(f"工作區路徑: {deployment_info['system_info']['workspace_path']}")
    print(f"收集時間: {deployment_info['system_info']['collection_time']}")
    print(f"Python 版本: {deployment_info['system_info']['python_version'].split()[0]}")
    
    # Docker Compose
    compose_count = sum(1 for f, info in deployment_info['docker_compose'].items() if info.get('exists'))
    print(f"Docker Compose 檔案: {compose_count} 個")
    
    # 環境變數檔案
    env_count = sum(1 for f, info in deployment_info['environment'].items() if info.get('exists'))
    print(f"環境變數檔案: {env_count} 個")
    
    # 資料庫備份
    backup_count = len(deployment_info['database'].get('backups', []))
    print(f"資料庫備份: {backup_count} 個")
    
    # Odoo 模組
    total_modules = sum(len(path.get('modules', [])) for path in deployment_info['odoo_config'].get('addons_paths', []))
    print(f"Odoo 模組路徑: {len(deployment_info['odoo_config'].get('addons_paths', []))} 個")
    print(f"發現模組: {total_modules} 個")
    
    # Docker 狀態
    if deployment_info['docker_status'].get('docker_available'):
        print(f"Docker 容器: {len(deployment_info['docker_status'].get('containers', []))} 個")
        print(f"Docker Volumes: {len(deployment_info['docker_status'].get('volumes', []))} 個")
    else:
        print("Docker: 未運行或未安裝")
    
    # 腳本
    script_count = len(deployment_info['scripts'].get('scripts', []))
    print(f"腳本檔案: {script_count} 個")
    
    print("\n" + "=" * 60)
    print("  ✅ 資訊收集完成")
    print("=" * 60)
    print(f"\n完整資訊已儲存至: {output_file}")
    
    return 0

if __name__ == '__main__':
    try:
        import yaml
    except ImportError:
        log("警告: PyYAML 未安裝，將跳過 YAML 解析", "WARNING")
        yaml = None
    
    sys.exit(main())
