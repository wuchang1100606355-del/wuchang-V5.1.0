#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查 VirtualBox 虛擬機器使用情況
"""

from pathlib import Path
import subprocess
import sys
import os

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

def check_virtualbox_installed():
    """檢查 VirtualBox 是否安裝"""
    print("=" * 80)
    print("檢查 VirtualBox 安裝狀態")
    print("=" * 80)
    print()
    
    # 檢查 VBoxManage 命令
    try:
        result = subprocess.run(
            ["VBoxManage", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✓ VirtualBox 已安裝")
            print(f"  版本: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    except Exception as e:
        pass
    
    # 檢查安裝目錄
    vbox_paths = [
        Path("C:\\Program Files\\Oracle\\VirtualBox"),
        Path("C:\\Program Files (x86)\\Oracle\\VirtualBox"),
    ]
    
    for vbox_path in vbox_paths:
        if vbox_path.exists():
            print(f"✓ VirtualBox 已安裝")
            print(f"  安裝路徑: {vbox_path}")
            return True
    
    print("✗ VirtualBox 未安裝或未在 PATH 中")
    return False

def list_virtual_machines():
    """列出所有虛擬機器"""
    print()
    print("=" * 80)
    print("虛擬機器列表")
    print("=" * 80)
    print()
    
    try:
        result = subprocess.run(
            ["VBoxManage", "list", "vms"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            vms = result.stdout.strip().splitlines()
            if vms:
                for vm in vms:
                    print(f"  {vm}")
                return len(vms)
            else:
                print("  沒有找到虛擬機器")
                return 0
        else:
            print("  無法列出虛擬機器（可能需要管理員權限）")
            return -1
    except FileNotFoundError:
        print("  VBoxManage 命令不可用")
        return -1
    except Exception as e:
        print(f"  錯誤: {e}")
        return -1

def check_vm_status():
    """檢查虛擬機器運行狀態"""
    print()
    print("=" * 80)
    print("虛擬機器運行狀態")
    print("=" * 80)
    print()
    
    try:
        result = subprocess.run(
            ["VBoxManage", "list", "runningvms"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            running_vms = result.stdout.strip().splitlines()
            if running_vms:
                print("正在運行的虛擬機器：")
                for vm in running_vms:
                    print(f"  {vm}")
            else:
                print("  目前沒有運行中的虛擬機器")
        else:
            print("  無法檢查運行狀態")
    except FileNotFoundError:
        print("  VBoxManage 命令不可用")
    except Exception as e:
        print(f"  錯誤: {e}")

def analyze_vm_files():
    """分析虛擬機器檔案"""
    print()
    print("=" * 80)
    print("虛擬機器檔案分析")
    print("=" * 80)
    print()
    
    # 常見的 VirtualBox 目錄
    vm_paths = [
        Path(os.path.expanduser("~")) / "VirtualBox VMs",
        Path("C:\\VirtualBox VMs"),
    ]
    
    total_size = 0
    vm_count = 0
    
    for vm_base_path in vm_paths:
        if vm_base_path.exists():
            print(f"檢查目錄: {vm_base_path}")
            print()
            
            for vm_dir in vm_base_path.iterdir():
                if vm_dir.is_dir():
                    vm_count += 1
                    vm_size = 0
                    file_count = 0
                    
                    print(f"  虛擬機器: {vm_dir.name}")
                    
                    # 計算目錄大小
                    for root, dirs, files in os.walk(vm_dir):
                        for file_name in files:
                            try:
                                file_path = Path(root) / file_name
                                if file_path.exists():
                                    stat = file_path.stat()
                                    vm_size += stat.st_size
                                    file_count += 1
                            except:
                                pass
                    
                    total_size += vm_size
                    print(f"    大小: {format_size(vm_size)}")
                    print(f"    檔案數: {file_count:,} 個")
                    print()
            
            if vm_count == 0:
                print("  此目錄下沒有找到虛擬機器")
            else:
                print(f"  總計: {vm_count} 個虛擬機器，總大小: {format_size(total_size)}")
            print()
    
    # 檢查 OVA 檔案
    print("檢查 OVA/OVF 匯出檔案...")
    print()
    
    ova_paths = [
        Path(os.path.expanduser("~")) / "OneDrive" / "文件",
        Path(os.path.expanduser("~")) / "Documents",
        Path("C:\\Users") / os.getenv("USERNAME", "") / "Downloads",
    ]
    
    ova_files = []
    for ova_path in ova_paths:
        if ova_path.exists():
            for file_path in ova_path.rglob("*.ova"):
                if file_path.exists():
                    try:
                        stat = file_path.stat()
                        ova_files.append({
                            "path": file_path,
                            "size": stat.st_size
                        })
                    except:
                        pass
    
    if ova_files:
        print(f"找到 {len(ova_files)} 個 OVA 檔案：")
        for ova in ova_files:
            print(f"  {ova['path']}")
            print(f"    大小: {format_size(ova['size'])}")
            print()
    else:
        print("  沒有找到 OVA 檔案")
    
    return total_size, vm_count

def main():
    """主函數"""
    print("=" * 80)
    print("VirtualBox 虛擬機器使用情況檢查")
    print("=" * 80)
    print()
    
    # 檢查安裝狀態
    is_installed = check_virtualbox_installed()
    
    if is_installed:
        # 列出虛擬機器
        vm_count = list_virtual_machines()
        
        # 檢查運行狀態
        check_vm_status()
    
    # 分析檔案
    total_size, file_vm_count = analyze_vm_files()
    
    # 總結
    print("=" * 80)
    print("總結")
    print("=" * 80)
    print()
    
    if is_installed:
        print("✓ VirtualBox 已安裝")
    else:
        print("✗ VirtualBox 未安裝或未在 PATH 中")
    
    print()
    print(f"虛擬機器檔案總大小: {format_size(total_size)}")
    print(f"虛擬機器數量: {file_vm_count} 個")
    print()
    
    if total_size > 0:
        print("建議：")
        print("  1. 如果不再使用這些虛擬機器，可以刪除以釋放空間")
        print("  2. 如果還需要使用，可以將虛擬機器移到其他磁碟（如 J 碟）")
        print("  3. OVA 檔案是匯出備份，如果已有 VDI 檔案，OVA 可以刪除")
        print()
        print("移動虛擬機器的方法：")
        print("  1. 在 VirtualBox 中關閉虛擬機器")
        print("  2. 使用 VBoxManage 命令移動：")
        print("     VBoxManage modifyvm \"VM名稱\" --groups \"/新路徑\"")
        print("  3. 或手動移動 VDI 檔案並在 VirtualBox 中重新註冊")

if __name__ == "__main__":
    main()
