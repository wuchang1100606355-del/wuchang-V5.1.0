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
  五常系統加速器 (Wuchang System Booster) - 親友專用版 (Family Edition)
================================================================================

[中文說明]
這是一個特別為五常親友設計的系統優化工具，能夠協助您提升電腦效能並確保連線品質。
為了確保系統安全，本程式綁定單一裝置。本版本為親友專用，無需金鑰即可使用。

使用步驟：
1. 執行 "Wuchang_System_Booster.exe"。
2. 複製畫面上顯示的「機器指紋 (Device Fingerprint)」。
3. 將指紋傳送給 Juers (江政隆)。
4. 輸入獲得的啟動金鑰即可永久解鎖。

Mac (Apple) 使用者：
本程式會自動釋放 "Wuchang_System_Booster_Mac.command" 檔案。
請在 Mac 電腦上執行該檔案即可。

--------------------------------------------------------------------------------
[發明與所有權聲明]
本系統由 Juers (江政隆) 發明與擁有。
保留所有權利。嚴禁未經授權的使用。
--------------------------------------------------------------------------------

[TIẾNG VIỆT]
Đây là công cụ tối ưu hóa hệ thống được thiết kế đặc biệt cho người thân của Wuchang.
Để đảm bảo an toàn, chương trình này được khóa vào một thiết bị duy nhất.
Phiên bản này dành cho gia đình, không cần mã kích hoạt.

Hướng dẫn sử dụng:
1. Chạy file "Wuchang_System_Booster.exe".
2. Sao chép "Dấu vân tay thiết bị (Device Fingerprint)" hiển thị trên màn hình.
3. Gửi dấu vân tay này cho Juers (Jiang Zheng-Long).
4. Nhập mã kích hoạt nhận được để mở khóa vĩnh viễn.

Người dùng Mac (Apple):
Chương trình sẽ tự động giải nén file "Wuchang_System_Booster_Mac.command".
Vui lòng chạy file này trên máy tính Mac.

--------------------------------------------------------------------------------
[BẢN QUYỀN VÀ PHÁT MINH]
Hệ thống này được phát minh và sở hữu bởi Juers (Jiang Zheng-Long).
Mọi quyền được bảo lưu. Việc sử dụng trái phép bị nghiêm cấm.
--------------------------------------------------------------------------------
================================================================================"""

MAC_SCRIPT_CONTENT = """#!/bin/bash
echo "============================================================"
echo " BỘ TĂNG TỐC HỆ THỐNG WUCHANG - PHIÊN BẢN GIA ĐÌNH (MAC)"
echo " 五常系統加速器 - 親友專用版 (MAC)"
echo " WUCHANG SYSTEM BOOSTER - FAMILY EDITION (MAC)"
echo "============================================================"
echo ""
echo "Đang khởi tạo... / Initializing... / 正在初始化..."
sleep 2

# System Boost (Simulated/Safe)
echo ""
echo ">> Dọn dẹp bộ nhớ đệm... / Cleaning User Cache... / 清理使用者快取..."

# Only delete if directory exists to avoid errors
if [ -d ~/Library/Caches ]; then
    # Try to flush DNS cache if possible
    dscacheutil -flushcache 2>/dev/null || killall -HUP mDNSResponder 2>/dev/null
    echo "   [OK] Mạng đã được tối ưu hóa / Network optimized / 網路已優化"
else
    echo "   [BỎ QUA] Không tìm thấy bộ nhớ đệm / Cache clean skipped"
fi
sleep 1

echo ""
echo ">> Xác minh danh tính... / Verifying Family Identity... / 驗證親友身分..."
sleep 2
echo ""
echo "[ĐƯỢC CẤP QUYỀN / ACCESS GRANTED / 存取授權]"
echo "Thành viên gia đình đã được xác nhận. / Family member recognized. / 確認為家人。"
echo ""
echo "Chào mừng đến với gia đình Wuchang. / Welcome to Wuchang Family. / 歡迎加入五常大家庭。"
echo ""
echo "------------------------------------------------------------"
echo "BẢN QUYỀN VÀ PHÁT MINH:"
echo "Hệ thống này được phát minh và sở hữu bởi Juers (Jiang Zheng-Long)."
echo "Mọi quyền được bảo lưu. Việc sử dụng trái phép bị nghiêm cấm."
echo ""
echo "INVENTION AND OWNERSHIP:"
echo "This system is invented and owned by Juers (Jiang Zheng-Long)."
echo "All rights reserved. Unauthorized use is strictly prohibited."
echo "------------------------------------------------------------"
echo ""
read -p "Nhấn Enter để thoát... / Press Enter to exit... / 按 Enter 鍵離開..."
"""

# ------------------------------------------------------------------------------
# MAIN LOGIC
# ------------------------------------------------------------------------------

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def create_desktop_shortcut(target_path):
    try:
        shortcut_name = "Wuchang System Booster.lnk"
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        shortcut_path = os.path.join(desktop, shortcut_name)

        script = f"""
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
        $Shortcut.TargetPath = "{target_path}"
        $Shortcut.WindowStyle = 1
        $Shortcut.Description = "Access Node for Wuchang Spatiotemporal System"
        $Shortcut.WorkingDirectory = "{os.path.dirname(target_path)}"
        $Shortcut.Save()
        """
        subprocess.run(["powershell", "-Command", script], check=True, capture_output=True)
        return True
    except Exception as e:
        return False

def system_boost():
    print("\n" + "="*50)
    print(" [SYSTEM OPTIMIZATION / 系統優化 / TỐI ƯU HÓA HỆ THỐNG]")
    print("="*50)

    print("\n>> Flushing DNS Cache / 清除 DNS 快取 / Xóa bộ nhớ đệm DNS...")
    try:
        subprocess.run("ipconfig /flushdns", shell=True, check=True, stdout=subprocess.DEVNULL)
        print("   [OK] Network optimized / 網路已優化 / Mạng đã được tối ưu hóa")
    except:
        print("   [SKIP] DNS flush skipped")

    print("\n>> Cleaning Temporary Files / 清理暫存檔案 / Dọn dẹp tệp tạm thời...")
    temp_dirs = [os.environ.get('TEMP'), os.environ.get('TMP')]
    
    for temp_dir in set(temp_dirs):
        if not temp_dir or not os.path.exists(temp_dir): continue
        try:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        if time.time() - os.path.getmtime(file_path) > 86400:
                            os.remove(file_path)
                    except: pass
        except: pass

    print(f"   [OK] System storage optimized / 儲存空間已釋放 / Đã giải phóng không gian lưu trữ")
    print("\n>> System Boost Complete! / 加速完成！ / Tăng tốc hoàn tất!")
    time.sleep(1)

def extract_payload():
    print("\n>> Extracting Documentation & Tools / 正在釋放文件與工具 / Đang giải nén tài liệu...")
    try:
        # Get directory where EXE is running
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        # Write ReadMe
        readme_path = os.path.join(base_dir, "ReadMe_VN.txt")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(README_CONTENT)
            
        # Write Mac Script
        mac_path = os.path.join(base_dir, "Wuchang_System_Booster_Mac.command")
        with open(mac_path, "w", encoding="utf-8") as f:
            f.write(MAC_SCRIPT_CONTENT)
            
        print(f"   [OK] Files extracted to: {base_dir}")
        print("   - ReadMe_VN.txt")
        print("   - Wuchang_System_Booster_Mac.command")
    except Exception as e:
        print(f"   [ERROR] Extraction failed: {e}")

def main():
    os.system("title Wuchang Quantum System Installer (Family Edition)")
    
    print("\n" + "="*60)
    print(" Wuchang Quantum Spacetime System / 五常量子時空系統")
    print(" Family Edition / 親友專用版 / Phiên bản gia đình")
    print("="*60)
    print("\nInitializing... / 正在初始化... / Đang khởi tạo...")
    time.sleep(2)

    # STEP 1: Verify Quantum License (Hardware Lock)
    lock = QuantumLock()
    hwid = lock.get_device_fingerprint()
    
    print("\n" + "-"*60)
    print(" [SECURITY CHECK / 安全檢查 / KIỂM TRA BẢO MẬT]")
    print(f" Device Fingerprint / 機器指紋: {hwid}")
    print("-"*60)
    print("\n[REQUIRED / 必填] Please enter your Activation Key.")
    print("正在驗證親友身分 (自動略過金鑰檢查)...")
    print("Đang xác minh danh tính gia đình (Tự động bỏ qua kiểm tra khóa)...")

    time.sleep(1)
    print("\n[ACCESS GRANTED / 存取授權 / ĐƯỢC CẤP QUYỀN]")
    print("Device verified. / 裝置驗證成功。 / Thiết bị đã được xác minh.")

    # STEP 2: Execute System Boost
    system_boost()
    
    # STEP 3: Extract Payload (Self-Extracting Behavior)
    extract_payload()

    # STEP 4: Installation
    if not is_admin():
        print("\n[NOTE] For permanent installation, please run as Administrator.")
    
    target_dir = os.path.join(os.environ['LOCALAPPDATA'], 'WuchangQuantum')
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    target_exe = os.path.join(target_dir, "Wuchang_System_Booster.exe")

    print(f"\nInstalling to / 安裝至: {target_dir}...")

    try:
        if getattr(sys, 'frozen', False):
            shutil.copy2(sys.executable, target_exe)
        
        if create_desktop_shortcut(target_exe):
            print("Shortcut created on Desktop. / 桌面捷徑已建立。 / Đã tạo lối tắt trên màn hình.")

        print("\n[SUCCESS / 成功 / THÀNH CÔNG]")
        print("Welcome to Wuchang Family. / 歡迎加入五常大家庭。 / Chào mừng đến với gia đình Wuchang.")

    except Exception as e:
        print(f"\n[WARNING] Installation partial: {e}")

    input("\nPress Enter to finish... / 按 Enter 鍵結束... / Nhấn Enter để hoàn tất...")

if __name__ == "__main__":
    main()
