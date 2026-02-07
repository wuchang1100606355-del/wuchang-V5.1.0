import re
import sys

file_path = 'main.py'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
except Exception as e:
    print(f"Error reading file: {e}")
    sys.exit(1)

# Logic for Explaining Gemini Code Assist / GenAI
new_pattern = r'''
            # Pattern: 服務用途解釋 (Service Explanation Logic)
            (r".*(他|它|that|this).*(做甚麼|幹嘛|用途|function|for|what is|doing).*(GenAI|Code Assist|35218|35,218).*", [
                "那筆 ,218 綁定的 **Gemini Code Assist** 其實是一個『超級 AI 程式設計師』。👨‍💻\n它的功能是幫大企業寫程式、改 Bug、讀文件。但對我們這種正在蓋地基 (VM) 的階段來說，它就像是請了一個『年薪百萬的秘書』來搬磚頭，既浪費又沒必要。我們自己動手蓋 VM 就好了，不需要這位貴族秘書！",
                "它是 Google 的 **AI 寫扣助手** (就像付費版的我？)。🤖\n它可以直接在 IDE 裡幫你寫程式碼。但因為我們現在主要是在做『基礎建設』(開 VM、設網路)，比較少寫程式碼，所以這個服務對我們來說暫時用不到。放生它完全不可惜！",
                "簡單來說，它是給開發者用的『外掛』。🎮\n能幫忙生成程式碼、分析專案。但哥哥我們現在是『維運 (Ops)』模式，在管機器和網路，這個開發工具派不上用場。那筆錢就像是『只能買跑車零件的優惠券』，我們現在開的是貨車，所以真的用不到啦！",
                "那是 Google 最貴的 AI 服務之一！💰\n專門用來開發生成式 AI 應用程式的。但我們現在的需求很單純，就是要有穩定的 VM 來跑服務。那個高大上的東西，等我們以後發大財要搞 AI 創業時再考慮也不遲。現在讓它過期正好省心！"
            ]),
'''

insert_marker = '# Pattern: 額度適用範圍/SKU限制 (Credit SKU Logic)'

if insert_marker in content:
    if "服務用途解釋" not in content:
        # Insert AFTER SKU Logic pattern
        content = content.replace(insert_marker, insert_marker + "\n" + new_pattern)
        print("Service Explanation Logic added successfully.")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        print("Service Explanation logic already exists.")
else:
    print("Insertion marker not found.")

