#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雙螢幕模式打開 UI
在兩個瀏覽器視窗中打開，可以分別放在兩個螢幕上
"""

import time
import webbrowser
import subprocess
import sys

url = "http://127.0.0.1:8788/"

print("正在以雙螢幕模式打開 UI...")
print(f"URL: {url}")

# 打開第一個視窗
print("打開第一個視窗...")
webbrowser.open(url)
time.sleep(1)

# 打開第二個視窗
print("打開第二個視窗...")
if sys.platform == "win32":
    subprocess.Popen(['start', url], shell=True)
else:
    webbrowser.open_new(url)

print("已打開兩個瀏覽器視窗")
print("提示：可以將兩個視窗分別拖到兩個螢幕上")
