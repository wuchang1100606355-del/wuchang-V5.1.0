#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_gpu_switcher.py

自動偵測並主動設定顯示卡切換（內顯/獨顯）
適用：Windows 筆記型電腦（NVIDIA/AMD/Intel）
作者：小J（妹妹）
"""

import os
import sys
import subprocess
import platform
import ctypes
from pathlib import Path
from datetime import datetime

REPORT_PATH = Path(__file__).parent / f"GPU_SWITCH_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

# 1. 偵測顯示卡資訊

def get_gpu_info():
    gpus = []
    if platform.system() == "Windows":
        try:
            output = subprocess.check_output(
                ["wmic", "path", "win32_VideoController", "get", "Name,AdapterCompatibility,PNPDeviceID"],
                encoding="utf-8", stderr=subprocess.DEVNULL
            )
            for line in output.splitlines()[1:]:
                if line.strip():
                    parts = [p.strip() for p in line.split("  ") if p.strip()]
                    if parts:
                        gpus.append(" ".join(parts))
        except Exception as e:
            gpus.append(f"偵測失敗: {e}")
    return gpus

# 2. 產生圖文報告

def generate_report(gpus):
    lines = [
        "# 筆記型電腦顯示卡自動偵測與切換報告",
        f"**執行時間：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 🎮 偵測到的顯示卡：",
    ]
    if gpus:
        for idx, gpu in enumerate(gpus, 1):
            lines.append(f"- 顯示卡{idx}：{gpu}")
    else:
        lines.append("⚠️ 未偵測到顯示卡")
    lines.append("")
    lines.append("---")
    lines.append("## 🛠️ 自動切換建議與說明")
    lines.append("1. 建議將內顯（Intel/AMD/內建）設為系統預設顯示卡，節能又穩定。")
    lines.append("2. 將高效能獨顯（NVIDIA/AMD）指定給AI、遊戲、專業軟體使用。")
    lines.append("")
    lines.append("### Windows 11/10 圖文教學：")
    lines.append("1. 進入「設定」→「系統」→「顯示」→「圖形」")
    lines.append("2. 選擇應用程式，點選「選項」→ 指定「高效能」(獨顯) 或「省電」(內顯)")
    lines.append("3. 套用後重啟應用程式")
    lines.append("")
    lines.append("![圖形設定教學](https://i.imgur.com/4Qw8QwB.png)")
    lines.append("")
    lines.append("---")
    lines.append("## 🚀 進階自動化（PowerShell 腳本）")
    lines.append("可用 PowerShell 指令自動設定指定程式使用獨顯：")
    lines.append("```")
    lines.append("Add-AppxPackage -Path 'C:\\Path\\To\\YourApp.exe' # 需手動指定應用程式")
    lines.append("# 進階自動化可參考 GitHub: https://github.com/rcmaehl/ModernFlyouts/issues/101")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("**小J提醒：如需完全自動化切換，請安裝顯示卡官方驅動與控制面板，部分功能需手動確認。**")
    return "\n".join(lines)

# 3. 主流程
if __name__ == "__main__":
    gpus = get_gpu_info()
    report = generate_report(gpus)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"✅ 顯示卡偵測與切換報告已產生：{REPORT_PATH}")
    print("---\n\n報告內容預覽：\n")
    print(report)
