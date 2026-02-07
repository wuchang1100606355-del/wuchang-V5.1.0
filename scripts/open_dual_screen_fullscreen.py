#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雙螢幕全螢幕模式
在兩個螢幕上分別打開全螢幕視窗，每個螢幕顯示完整的 UI
"""

import time
import webbrowser
import subprocess
import sys
import os

url = "http://127.0.0.1:8788/"

print("=" * 60)
print("🖥️  雙螢幕全螢幕模式啟動")
print("=" * 60)
print(f"URL: {url}")
print()

# 使用 PowerShell 在 Windows 上打開兩個全螢幕視窗
if sys.platform == "win32":
    print("正在打開第一個螢幕（主螢幕）...")
    # 第一個視窗：主螢幕，全螢幕
    ps_script = f'''
$url = "{url}"
$screen1 = [System.Windows.Forms.Screen]::PrimaryScreen
$browser = New-Object -ComObject Shell.Application
$browser.Open($url)
Start-Sleep -Seconds 1
# 使用 Chrome/Edge 的 kiosk 模式（全螢幕）
$chromePath = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
if (Test-Path $chromePath) {{
    Start-Process $chromePath -ArgumentList "--new-window", "--start-fullscreen", "--kiosk", $url
}} else {{
    $edgePath = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
    if (Test-Path $edgePath) {{
        Start-Process $edgePath -ArgumentList "--new-window", "--start-fullscreen", "--kiosk", $url
    }} else {{
        Start-Process $url
    }}
}}
'''
    
    # 執行 PowerShell 腳本
    try:
        subprocess.Popen([
            "powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script
        ], shell=False)
        print("✅ 第一個視窗已打開")
    except Exception as e:
        print(f"⚠️  使用備用方式打開第一個視窗: {e}")
        webbrowser.open(url)
    
    time.sleep(2)
    
    print()
    print("正在打開第二個螢幕...")
    # 第二個視窗：第二個螢幕，全螢幕
    ps_script2 = f'''
$url = "{url}?screen=2"
$chromePath = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
if (Test-Path $chromePath) {{
    Start-Process $chromePath -ArgumentList "--new-window", "--start-fullscreen", "--kiosk", $url
}} else {{
    $edgePath = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
    if (Test-Path $edgePath) {{
        Start-Process $edgePath -ArgumentList "--new-window", "--start-fullscreen", "--kiosk", $url
    }} else {{
        Start-Process $url
    }}
}}
'''
    
    try:
        subprocess.Popen([
            "powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script2
        ], shell=False)
        print("✅ 第二個視窗已打開")
    except Exception as e:
        print(f"⚠️  使用備用方式打開第二個視窗: {e}")
        webbrowser.open_new(url)
    
    print()
    print("=" * 60)
    print("✅ 雙螢幕全螢幕模式已啟動")
    print("=" * 60)
    print()
    print("提示：")
    print("  - 兩個視窗應該已經分別在兩個螢幕上全螢幕顯示")
    print("  - 如果視窗位置不對，可以手動拖動到對應的螢幕")
    print("  - 按 F11 可以切換全螢幕模式")
    print()
else:
    # Linux/Mac 的處理
    print("正在打開第一個視窗...")
    webbrowser.open(url)
    time.sleep(1)
    print("正在打開第二個視窗...")
    webbrowser.open_new(url)
    print("✅ 已打開兩個視窗（請手動調整到兩個螢幕並全螢幕）")
