# STAPS Secure Kernel Delivery Package

## 概述
本資料夾包含 Wuchang STAPS (Space-Time Async Parallel System) 的核心加密模組與技術展示文件。
核心邏輯已透過 Cython 技術進行黑盒封裝 (Blackbox)，確保智慧財產權與演算法安全。

## 檔案清單
1. **staps_core.cp314-win_amd64.pyd**: 加密核心模組 (Binary)。無法被反編譯或查看原始碼。
2. **staps_kernel_service.py**: 原始碼對照 (供內部驗證用，交付客戶時請移除)。
3. **run_demo.py**: 演示腳本，展示如何在不接觸原始碼的情況下調用加密核心。
4. **STAPS_TECHNICAL_SPEC.md**: 技術規格說明書。
5. **PATENT_DECLARATION.md**: 專利與智財權宣告。

## 如何使用
確保您的環境已安裝 Python 3.10+。
直接執行演示腳本：
\\\ash
python run_demo.py
\\\

## 安全性說明
本核心採用 C-Extension 級別編譯，並啟用 -O3 優化。
所有核心變數與邏輯流程皆已轉化為機器語言。

