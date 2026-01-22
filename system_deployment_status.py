#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
system_deployment_status.py

系統部署狀態檢查工具

功能：
- 檢查伺服器運行狀態
- 檢查系統部署狀態
- 檢查服務健康狀態
- 檢查系統感知功能
- 生成完整狀態報告
"""

from __future__ import annotations

import json
import os
import platform
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Optional, Any
from urllib.error import URLError
from urllib.request import Request, urlopen

BASE_DIR = Path(__file__).resolve().parent


def check_port(host: str, port: int, timeout: float = 2.0) -> Dict[str, Any]:
    """檢查端口是否開放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return {
            "open": result == 0,
            "host": host,
            "port": port,
        }
    except Exception as e:
        return {
            "open": False,
            "host": host,
            "port": port,
            "error": str(e),
        }


def check_http_service(url: str, timeout: float = 3.0) -> Dict[str, Any]:
    """檢查 HTTP 服務健康狀態"""
    try:
        req = Request(url)
        req.add_header("Accept", "application/json, text/plain;q=0.9")
        with urlopen(req, timeout=timeout) as resp:
            status = int(getattr(resp, "status", 200))
            content_type = str(resp.headers.get("Content-Type", ""))
            return {
                "ok": 200 <= status < 300,
                "status": status,
                "content_type": content_type,
                "url": url,
            }
    except URLError as e:
        return {
            "ok": False,
            "status": 0,
            "error": str(e),
            "url": url,
        }
    except Exception as e:
        return {
            "ok": False,
            "status": 0,
            "error": str(e),
            "url": url,
        }


def get_process_info(port: int) -> Optional[Dict[str, Any]]:
    """獲取端口對應的進程資訊"""
    try:
        if platform.system() == "win32":
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            for line in result.stdout.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = int(parts[-1])
                        # 獲取進程名稱
                        try:
                            task_result = subprocess.run(
                                ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV"],
                                capture_output=True,
                                text=True,
                                timeout=3,
                            )
                            if task_result.returncode == 0:
                                lines = task_result.stdout.strip().splitlines()
                                if len(lines) > 1:
                                    import csv
                                    reader = csv.reader([lines[1]])
                                    row = next(reader)
                                    if len(row) >= 1:
                                        return {
                                            "pid": pid,
                                            "name": row[0].strip('"'),
                                        }
                        except Exception:
                            pass
                        return {"pid": pid}
        return None
    except Exception:
        return None


def check_system_neural_network() -> Dict[str, Any]:
    """檢查系統神經網路狀態"""
    try:
        from system_neural_network import get_neural_network
        nn = get_neural_network()
        if not nn.running:
            nn.start()
        perception = nn.get_system_perception()
        return {
            "available": True,
            "running": nn.running,
            "total_nodes": perception.get("total_nodes", 0),
            "overall_health": perception.get("overall_health", "unknown"),
        }
    except ImportError:
        return {"available": False, "error": "module_not_installed"}
    except Exception as e:
        return {"available": False, "error": str(e)}


def check_encrypted_storage() -> Dict[str, Any]:
    """檢查加密儲存系統狀態"""
    try:
        from encrypted_storage_manager import get_storage_manager
        storage = get_storage_manager()
        devices = storage.list_devices()
        return {
            "available": True,
            "device_count": len(devices),
            "devices": devices,
        }
    except ImportError:
        return {"available": False, "error": "module_not_installed"}
    except Exception as e:
        return {"available": False, "error": str(e)}


def check_pii_storage() -> Dict[str, Any]:
    """檢查個資儲存系統狀態"""
    pii_enabled = os.getenv("WUCHANG_PII_ENABLED", "").strip().lower() == "true"
    try:
        from pii_storage_manager import get_pii_storage_manager
        pii_manager = get_pii_storage_manager()
        return {
            "enabled": pii_enabled,
            "available": True,
            "default_device": pii_manager.default_device_id or "未設定",
        }
    except ImportError:
        return {
            "enabled": pii_enabled,
            "available": False,
            "error": "module_not_installed",
        }
    except Exception as e:
        return {
            "enabled": pii_enabled,
            "available": False,
            "error": str(e),
        }


def check_authorization_system() -> Dict[str, Any]:
    """檢查授權系統狀態"""
    try:
        from authorized_administrators import (
            validate_authorizations,
            get_all_valid_authorizations,
        )
        validation = validate_authorizations()
        authorizations = get_all_valid_authorizations()
        return {
            "available": True,
            "total_authorizations": validation.get("total_count", 0),
            "valid_authorizations": validation.get("valid_count", 0),
            "validation": validation,
        }
    except ImportError:
        return {"available": False, "error": "module_not_installed"}
    except Exception as e:
        return {"available": False, "error": str(e)}


def check_environment_variables() -> Dict[str, Any]:
    """檢查環境變數設定"""
    env_vars = {
        "WUCHANG_HUB_TOKEN": os.getenv("WUCHANG_HUB_TOKEN", ""),
        "WUCHANG_HUB_URL": os.getenv("WUCHANG_HUB_URL", ""),
        "WUCHANG_HEALTH_URL": os.getenv("WUCHANG_HEALTH_URL", ""),
        "WUCHANG_COPY_TO": os.getenv("WUCHANG_COPY_TO", ""),
        "WUCHANG_SYSTEM_DB_DIR": os.getenv("WUCHANG_SYSTEM_DB_DIR", ""),
        "WUCHANG_WORKSPACE_OUTDIR": os.getenv("WUCHANG_WORKSPACE_OUTDIR", ""),
        "WUCHANG_PII_OUTDIR": os.getenv("WUCHANG_PII_OUTDIR", ""),
        "WUCHANG_PII_ENABLED": os.getenv("WUCHANG_PII_ENABLED", ""),
        "WUCHANG_PII_STORAGE_DEVICE": os.getenv("WUCHANG_PII_STORAGE_DEVICE", ""),
    }
    
    return {
        "configured": {k: bool(v) for k, v in env_vars.items()},
        "values": {k: "***" if "TOKEN" in k or "PASSWORD" in k else v for k, v in env_vars.items()},
    }


def check_auto_start_task() -> Dict[str, Any]:
    """檢查開機自動啟動任務"""
    if platform.system() != "win32":
        return {"available": False, "error": "not_windows"}
    
    try:
        task_name = "五常系統-開機自動啟動服務器"
        result = subprocess.run(
            ["schtasks", "/Query", "/TN", task_name, "/FO", "JSON"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return {
                "registered": True,
                "task_name": task_name,
            }
        else:
            return {
                "registered": False,
                "task_name": task_name,
            }
    except Exception as e:
        return {
            "registered": False,
            "error": str(e),
        }


def get_deployment_status() -> Dict[str, Any]:
    """獲取完整的部署狀態"""
    status = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "platform": platform.platform(),
        "system": platform.system(),
        "servers": {},
        "services": {},
        "modules": {},
        "environment": {},
    }
    
    # 檢查伺服器狀態
    servers = {
        "control_center": {
            "name": "本機中控台",
            "port": 8788,
            "url": "http://127.0.0.1:8788/",
        },
        "little_j_hub": {
            "name": "Little J Hub",
            "port": 8799,
            "url": "http://127.0.0.1:8799/",
        },
    }
    
    for server_id, config in servers.items():
        port_check = check_port("127.0.0.1", config["port"])
        http_check = check_http_service(config["url"])
        process_info = get_process_info(config["port"])
        
        status["servers"][server_id] = {
            "name": config["name"],
            "port": config["port"],
            "url": config["url"],
            "port_open": port_check.get("open", False),
            "http_ok": http_check.get("ok", False),
            "http_status": http_check.get("status", 0),
            "process": process_info,
        }
    
    # 檢查模組狀態
    status["modules"] = {
        "neural_network": check_system_neural_network(),
        "encrypted_storage": check_encrypted_storage(),
        "pii_storage": check_pii_storage(),
        "authorization": check_authorization_system(),
    }
    
    # 檢查環境變數
    status["environment"] = check_environment_variables()
    
    # 檢查自動啟動任務
    status["auto_start"] = check_auto_start_task()
    
    # 計算整體狀態
    all_servers_ok = all(
        s.get("http_ok", False) for s in status["servers"].values()
    )
    status["overall_status"] = "healthy" if all_servers_ok else "degraded"
    
    return status


def main():
    """主函數"""
    status = get_deployment_status()
    print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
