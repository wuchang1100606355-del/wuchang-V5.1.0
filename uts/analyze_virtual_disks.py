#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析虛擬硬碟大小和使用情況
"""

from pathlib import Path
import os
import sys
import subprocess

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

def format_size(size: int) -> str:
    """格式化檔案大小"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def get_file_info(file_path: Path):
    """獲取檔案資訊"""
    try:
        stat = file_path.stat()
        return {
            "exists": True,
            "size": stat.st_size,
            "mtime": stat.st_mtime,
        }
    except:
        return {"exists": False, "size": 0, "mtime": 0}

def analyze_docker_disk():
    """分析 Docker 虛擬硬碟"""
    print("=" * 80)
    print("Docker 虛擬硬碟分析")
    print("=" * 80)
    print()
    
    docker_paths = [
        Path(os.path.expanduser("~")) / "AppData" / "Local" / "Docker" / "wsl" / "disk" / "docker_data.vhdx",
        Path("C:\\Users") / os.getenv("USERNAME", "") / "AppData" / "Local" / "Docker" / "wsl" / "disk" / "docker_data.vhdx",
    ]
    
    for docker_path in docker_paths:
        if docker_path.exists():
            info = get_file_info(docker_path)
            size_gb = info["size"] / (1024**3)
            
            print(f"檔案: {docker_path}")
            print(f"  大小: {format_size(info['size'])} ({size_gb:.2f} GB)")
            print()
            
            # 檢查 Docker 使用情況
            try:
                result = subprocess.run(
                    ["docker", "system", "df"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    print("Docker 磁碟使用情況：")
                    print(result.stdout)
                    print()
            except:
                print("  無法檢查 Docker 使用情況（Docker 可能未運行）")
                print()
            
            # 檢查是否可以壓縮
            print("建議：")
            print("  1. Docker 虛擬硬碟會隨著使用自動增長")
            print("  2. 可以通過以下方式清理：")
            print("     docker system prune -a --volumes")
            print("  3. 壓縮虛擬硬碟（需要停止 Docker）：")
            print("     Optimize-VHD -Path \"$docker_path\" -Mode Full")
            print()
            
            return info["size"]
    
    print("未找到 Docker 虛擬硬碟")
    print()
    return 0

def analyze_wsl_disk():
    """分析 WSL 虛擬硬碟"""
    print("=" * 80)
    print("WSL 虛擬硬碟分析")
    print("=" * 80)
    print()
    
    wsl_paths = [
        Path(os.path.expanduser("~")) / "AppData" / "Local" / "wsl",
        Path("C:\\Users") / os.getenv("USERNAME", "") / "AppData" / "Local" / "wsl",
    ]
    
    total_size = 0
    
    for wsl_base in wsl_paths:
        if wsl_base.exists():
            print(f"檢查目錄: {wsl_base}")
            print()
            
            for vhdx_file in wsl_base.rglob("*.vhdx"):
                info = get_file_info(vhdx_file)
                if info["exists"]:
                    size_gb = info["size"] / (1024**3)
                    total_size += info["size"]
                    
                    print(f"  檔案: {vhdx_file.name}")
                    print(f"    大小: {format_size(info['size'])} ({size_gb:.2f} GB)")
                    print()
    
    if total_size > 0:
        print(f"WSL 總大小: {format_size(total_size)}")
        print()
        print("建議：")
        print("  1. WSL 虛擬硬碟會隨著使用自動增長")
        print("  2. 可以通過以下方式清理：")
        print("     wsl --shutdown")
        print("     Optimize-VHD -Path \"路徑\" -Mode Full")
        print()
    
    return total_size

def analyze_bluestacks_disk():
    """分析 BlueStacks 虛擬硬碟"""
    print("=" * 80)
    print("BlueStacks 虛擬硬碟分析")
    print("=" * 80)
    print()
    
    bs_path = Path("C:\\ProgramData\\BlueStacks_msi5\\Engine\\Nougat64\\Data.vhdx")
    
    if bs_path.exists():
        info = get_file_info(bs_path)
        size_gb = info["size"] / (1024**3)
        
        print(f"檔案: {bs_path}")
        print(f"  大小: {format_size(info['size'])} ({size_gb:.2f} GB)")
        print()
        
        print("建議：")
        print("  1. BlueStacks 是 Android 模擬器")
        print("  2. 如果不再使用，可以卸載 BlueStacks")
        print("  3. 或移動到其他磁碟")
        print()
        
        return info["size"]
    
    print("未找到 BlueStacks 虛擬硬碟")
    print()
    return 0

def check_virtual_disk_usage():
    """檢查虛擬硬碟的實際使用情況"""
    print("=" * 80)
    print("虛擬硬碟實際使用情況")
    print("=" * 80)
    print()
    
    print("注意：虛擬硬碟檔案（.vhdx, .vdi）的大小不等於實際使用空間")
    print("虛擬硬碟會預先分配空間，即使內部檔案較少，檔案本身也可能很大")
    print()
    
    print("常見原因：")
    print("  1. 動態擴展：虛擬硬碟會自動增長，但不會自動縮小")
    print("  2. 刪除檔案後：虛擬硬碟內部刪除檔案不會立即釋放空間")
    print("  3. 快照和備份：可能包含多個版本的資料")
    print("  4. 日誌檔案：應用程式日誌可能累積很大")
    print()

def main():
    """主函數"""
    print("=" * 80)
    print("虛擬硬碟大小分析")
    print("=" * 80)
    print()
    
    total_size = 0
    
    # 分析 Docker
    docker_size = analyze_docker_disk()
    total_size += docker_size
    
    # 分析 WSL
    wsl_size = analyze_wsl_disk()
    total_size += wsl_size
    
    # 分析 BlueStacks
    bs_size = analyze_bluestacks_disk()
    total_size += bs_size
    
    # 檢查使用情況
    check_virtual_disk_usage()
    
    # 總結
    print("=" * 80)
    print("總結")
    print("=" * 80)
    print()
    
    print(f"虛擬硬碟總大小: {format_size(total_size)} ({total_size / (1024**3):.2f} GB)")
    print()
    
    print("為什麼虛擬硬碟這麼大？")
    print("  1. 動態擴展機制：虛擬硬碟會自動增長以容納資料")
    print("  2. 不會自動縮小：刪除內部檔案不會減少 .vhdx 檔案大小")
    print("  3. 碎片整理：虛擬硬碟內部可能有碎片，需要壓縮")
    print("  4. 快照和備份：可能包含歷史資料")
    print()
    
    print("如何減少虛擬硬碟大小？")
    print("  1. 清理內部資料：")
    print("     - Docker: docker system prune -a --volumes")
    print("     - WSL: 清理 Linux 系統內的檔案")
    print("  2. 壓縮虛擬硬碟（需要停止相關服務）：")
    print("     Optimize-VHD -Path \"路徑\" -Mode Full")
    print("  3. 如果不再使用，刪除虛擬硬碟")
    print()

if __name__ == "__main__":
    main()
