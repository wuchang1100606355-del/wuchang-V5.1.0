#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cloud_sync_config.py

雲端同步配置模組

功能：
- 統一管理雲端同步路徑配置
- 確保只同步到「五常雲端空間」
- 單向寫入（本機 -> 雲端）
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional


def get_wuchang_cloud_path() -> Optional[Path]:
    """
    獲取五常雲端空間路徑
    
    優先順序：
    1. 環境變數 WUCHANG_CLOUD_PATH
    2. 預設路徑：J:\共用雲端硬碟\五常雲端空間 (Windows)
    3. 其他可能的 Google Drive 路徑
    """
    # 優先使用環境變數
    env_path = os.getenv("WUCHANG_CLOUD_PATH", "").strip()
    if env_path:
        path = Path(env_path).expanduser().resolve()
        if path.exists():
            return path
    
    # Windows 預設路徑
    if sys.platform == "win32":
        default_paths = [
            Path(r"J:\共用雲端硬碟\五常雲端空間"),
            Path(r"J:\我的雲端硬碟\五常雲端空間"),
            Path.home() / "Google Drive" / "五常雲端空間",
            Path.home() / "Google 雲端硬碟" / "五常雲端空間",
            Path("G:/Google Drive/五常雲端空間"),
            Path("G:/Google 雲端硬碟/五常雲端空間"),
        ]
    else:
        # Linux/Mac 路徑
        default_paths = [
            Path.home() / "Google Drive" / "五常雲端空間",
            Path("/mnt/google-drive/五常雲端空間"),
            Path("/home") / Path.home().name / "Google Drive" / "五常雲端空間",
        ]
    
    # 尋找存在的路徑
    for path in default_paths:
        if path.exists() and path.is_dir():
            return path.resolve()
    
    return None


def ensure_wuchang_cloud_path() -> Path:
    """
    確保五常雲端空間路徑存在，不存在則創建
    
    返回：Path 對象
    拋出：RuntimeError 如果無法創建
    """
    path = get_wuchang_cloud_path()
    
    if path is None:
        # 嘗試創建預設路徑
        if sys.platform == "win32":
            default_path = Path(r"J:\共用雲端硬碟\五常雲端空間")
        else:
            default_path = Path.home() / "Google Drive" / "五常雲端空間"
        
        try:
            default_path.mkdir(parents=True, exist_ok=True)
            return default_path.resolve()
        except Exception as e:
            raise RuntimeError(
                f"無法創建五常雲端空間路徑: {default_path}\n"
                f"錯誤: {e}\n"
                f"請手動創建目錄或設定 WUCHANG_CLOUD_PATH 環境變數"
            )
    
    return path


def get_sync_directories() -> dict[str, Path]:
    """
    獲取同步目錄結構
    
    返回：包含各類別目錄的字典
    """
    base_path = ensure_wuchang_cloud_path()
    
    return {
        "base": base_path,
        "reports": base_path / "reports",
        "scripts": base_path / "scripts",
        "database": base_path / "database" / "backups",
        "uploads": base_path / "uploads",
        "config": base_path / "config",
        "backups": base_path / "backups",
    }


def validate_cloud_path(path: Path) -> bool:
    """
    驗證路徑是否在五常雲端空間內
    
    參數：
        path: 要驗證的路徑
    
    返回：True 如果在五常雲端空間內，False 否則
    """
    cloud_path = get_wuchang_cloud_path()
    if cloud_path is None:
        return False
    
    try:
        # 檢查路徑是否在雲端空間內
        resolved_path = path.resolve()
        resolved_cloud = cloud_path.resolve()
        
        # 使用 Path.is_relative_to (Python 3.9+)
        try:
            return resolved_path.is_relative_to(resolved_cloud)
        except AttributeError:
            # Python 3.8 兼容
            return str(resolved_path).startswith(str(resolved_cloud))
    except Exception:
        return False


# 同步配置常量
SYNC_MODE = "bidirectional"  # 雙向同步：支援下載和上傳
SYNC_DIRECTION = "both"  # 同步方向：both(雙向), download(雲端->本機), upload(本機->雲端)
ALLOWED_SYNC_PATHS = ["五常雲端空間"]  # 只允許同步到五常雲端空間


def get_sync_config() -> dict:
    """
    獲取同步配置
    
    返回：同步配置字典
    """
    return {
        "mode": SYNC_MODE,
        "direction": SYNC_DIRECTION,
        "cloud_path": str(ensure_wuchang_cloud_path()),
        "allowed_paths": ALLOWED_SYNC_PATHS,
        "bidirectional": True,  # 支援雙向同步
        "description": "本機磁碟與雲端硬碟雙向同步：本地端夾下載五常雲端空間變更，本地進行變更上傳雲端空間",
    }


if __name__ == "__main__":
    """測試配置"""
    # 設定 UTF-8 編碼輸出
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except:
            pass
    
    print("=" * 60)
    print("雲端同步配置測試")
    print("=" * 60)
    print()
    
    cloud_path = get_wuchang_cloud_path()
    if cloud_path:
        print(f"[OK] 五常雲端空間路徑: {cloud_path}")
    else:
        print("[WARN] 未找到五常雲端空間路徑")
        print("  嘗試創建...")
        try:
            cloud_path = ensure_wuchang_cloud_path()
            print(f"[OK] 已創建: {cloud_path}")
        except Exception as e:
            print(f"[ERROR] 創建失敗: {e}")
            sys.exit(1)
    
    print()
    print("同步目錄結構：")
    dirs = get_sync_directories()
    for name, path in dirs.items():
        exists = "[OK]" if path.exists() else "[MISSING]"
        print(f"  {exists} {name}: {path}")
    
    print()
    print("同步配置：")
    config = get_sync_config()
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    print()
    print("=" * 60)
