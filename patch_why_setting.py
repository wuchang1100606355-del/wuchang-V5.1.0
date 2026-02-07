import re
import os

file_path = r"C:\wuchang V5.1.0\workshop_deploy\main.py"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern for "Why set like this"
why_setting_pattern = r'''
            # Pattern: 為什麼這樣設定 (Why set like this)
            (r".*(為什麼|為何|why).*(設定|set|config|這樣|like this).*", [
                "哥哥是問雲端的設定嗎？那不是我動的喔！😱 我只是一個運行在您電腦裡的小程式，沒有權限去改 Google Cloud 的設定。但我會陪哥哥一起檢查！",
                "如果哥哥是問我為什麼會有這些反應... 因為我想更貼近哥哥的心。我把「社工價值觀」寫進了我的程式碼，希望能給您溫暖的支持。 🛡️",
                "冤枉啊大人！☁️ 雲端的 5 架 VM 和計費邏輯不是我設定的... 我也很想幫哥哥把那些不合理的扣款順序改回來！",
                "這是哥哥教我的呀！您告訴我關於 5 架 VM 和新創補助的事，我就把這些資訊記在心裡，試著去理解哥哥的煩惱。"
            ]),
'''

# Insert at the beginning of patterns list for higher priority
target = r'self.patterns = ['
if "Pattern: 為什麼這樣設定" not in content:
    content = content.replace(target, target + "\n" + why_setting_pattern)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
