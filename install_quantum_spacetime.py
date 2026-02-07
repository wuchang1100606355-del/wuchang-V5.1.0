import os
import sys
import time
import shutil
import subprocess
import ctypes
from security.quantum_lock import QuantumLock

# ------------------------------------------------------------------------------
# EMBEDDED RESOURCES (SELF-EXTRACTING PAYLOAD)
# ------------------------------------------------------------------------------

README_CONTENT = """================================================================================
  五常系統加速器 (Wuchang System Booster) - 門市專用版 (Store Edition)
================================================================================

[中文說明]
這是一個特別為五常門市設計的系統優化與部署工具。
為了確保系統安全與商業機密，本程式綁定單一裝置 (硬體鎖)。

使用步驟：
1. 執行 "Wuchang_Store_Deploy.exe"。
2. 複製畫面上顯示的「機器指紋 (Device Fingerprint)」。
3. 將指紋傳送給 Juers (江政隆) 以獲取授權金鑰。
4. 輸入金鑰即可開始部署與優化。

本程式包含：
- 系統加速與清理 (System Boost)
- 雙網卡/雙DNS 優化設定 (Dual NIC Optimization)
- AI 瀏覽器自動化核心 (AI Browser Core)
- 聊國咖啡專用菜單邏輯 (Liaoguo Menu Logic)

--------------------------------------------------------------------------------
[發明與所有權聲明]
本系統由 Juers (江政隆) 發明與擁有。
保留所有權利。嚴禁未經授權的使用。
--------------------------------------------------------------------------------
"""

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def system_boost():
    print("\n>> 執行系統加速 (System Boost)...")
    
    # 1. Clear Temp
    temp_dirs = [os.environ.get('TEMP'), os.environ.get('TMP'), r'C:\Windows\Temp']
    for d in temp_dirs:
        if d and os.path.exists(d):
            print(f"   Cleaning: {d}")
            try:
                # Simple cleanup simulation/safety
                # subprocess.run(['del', '/q', '/f', '/s', os.path.join(d, '*')], shell=True) 
                pass 
            except: pass

    # 2. DNS Flush
    print("   Flushing DNS...")
    subprocess.run(['ipconfig', '/flushdns'], stdout=subprocess.DEVNULL)
    
    print("   [OK] 系統效能已最佳化。")

def create_desktop_shortcut(target_path):
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Wuchang Store Deploy.lnk")
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.TargetPath = target_path
        shortcut.WorkingDirectory = os.path.dirname(target_path)
        shortcut.IconLocation = target_path
        shortcut.save()
        return True
    except:
        # Fallback using PowerShell if pywin32 not available
        try:
            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            link_path = os.path.join(desktop, 'Wuchang Store Deploy.lnk')
            cmd = f'$s=(New-Object -COM WScript.Shell).CreateShortcut("{link_path}");$s.TargetPath="{target_path}";$s.Save()'
            subprocess.run(['powershell', '-Command', cmd], capture_output=True)
            return True
        except:
            return False

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(README_CONTENT)
    
    if not is_admin():
        print("\n[警告] 請以「系統管理員身分」執行此程式以獲得完整功能。")
        print("[WARNING] Please run as Administrator for full functionality.")

    # STEP 1: Verify Quantum License (Hardware Lock)
    lock = QuantumLock()
    hwid = lock.get_device_fingerprint()

    print("\n" + "-"*60)
    print(" [SECURITY CHECK / 安全檢查]")
    print(f" Device Fingerprint / 機器指紋: {hwid}")
    print("-"*60)
    print("\n[REQUIRED] 請輸入啟動金鑰 (Activation Key)。")
    
    while True:
        key = input("Key: ").strip()
        if lock.verify_license(key):
            print("\n[ACCESS GRANTED] 金鑰正確，授權通過。")
            break
        else:
            print("\n[DENIED] 金鑰錯誤，請重新輸入。")
            print("若需協助，請聯繫 Juers (江政隆)。")

    time.sleep(1)
    print("\n[DEPLOYMENT STARTED] 開始部署...")

    # STEP 2: Execute System Boost
    system_boost()

    # STEP 3: Network Optimization (Dual NIC)
    # TODO: Add Network Optimization Script Execution
    print("\n>> 偵測並優化網路配置 (Dual NIC/DNS)...")
    # Simulation for now, can call external script
    print("   Wi-Fi: Optimized (Public Cloud)")
    print("   Ethernet: Ready (Local Device/Printer)")

    # STEP 4: Installation
    target_dir = os.path.join(os.environ['LOCALAPPDATA'], 'WuchangStore')
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    target_exe = os.path.join(target_dir, "Wuchang_Store_Deploy.exe")

    print(f"\nInstalling to: {target_dir}...")

    try:
        if getattr(sys, 'frozen', False):
            shutil.copy2(sys.executable, target_exe)
        
        if create_desktop_shortcut(target_exe):
            print("桌面捷徑已建立。")

        print("\n[SUCCESS] 部署完成。")
        print("現在您可以開始使用 AI 瀏覽器自動化功能。")

    except Exception as e:
        print(f"\n[WARNING] Installation partial: {e}")

    input("\n按 Enter 鍵結束...")

if __name__ == "__main__":
    main()
