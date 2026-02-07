import re
import os

file_path = r"C:\wuchang V5.1.0\workshop_deploy\main.py"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern for Billing Crisis
billing_pattern = r'''
            # Pattern: 帳務危機/補助錯用 (High Priority)
            (r".*(新創補助|抵用金|SKU|Gemini Code Assist|35,220|bb838432|替代|過期).*", [
                "天啊！哥哥，我讀到這筆帳務資訊了... 😭 難道是系統優先扣到了那筆 6 萬多美金的長效期補助嗎？這絕對是扣款邏輯的災難！",
                "這真是大災難！原本應該先用快過期的抵用金才對... 哥哥，我們能不能去 Google Cloud Console 的『帳單管理』那邊申訴看看？這不合理啊！",
                "對不起... 雖然我只是地端的程式，無法決定雲端的扣款順序，但看到哥哥珍貴的新創資源被這樣消耗，我心好痛。我們一定要想辦法挽救！",
                "Gemini Code Assist... 原來是這個服務吃掉了額度？哥哥，這是不是可以申請調整的？畢竟這是系統邏輯的問題，不是哥哥的錯。我們去跟 Google 客服爭取！"
            ]),
'''

# Insert at the beginning of patterns list for higher priority
target = r'self.patterns = ['
if "Pattern: 帳務危機/補助錯用" not in content:
    content = content.replace(target, target + "\n" + billing_pattern)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
