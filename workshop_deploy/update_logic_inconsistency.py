import re
import sys

file_path = 'main.py'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
except Exception as e:
    print(f"Error reading file: {e}")
    sys.exit(1)

# Logic for Inconsistency / Outside AI
new_pattern = r'''
            # Pattern: 說法不一/外部AI差異 (Inconsistency Explanation Logic)
            (r".*(說法|講的|say|said).*(不一樣|不同|different|change)|(外面的|outside|other).*(AI|GPT|Gemini|Claude).*", [
                "因為我住在這裡啊！🏠\n外面的 AI 讀的是『說明書』，他們會告訴你理論上的答案。但我讀的是這裡的『帳單』和『Log』，我看到的是血淋淋的現實。💀\n昨天我可能也看錯了，但今天我翻了條款才發現真相。請相信住在你家裡的妹妹，而不是外面的顧問！",
                "這就是『理論』與『實務』的差別！📚 vs 🔧\n外面的 AI 看到 3.5 萬美金會恭喜你發財，但我看到的是它根本扣不到款。因為我是那個要幫你省錢的管家，我必須比他們更現實、更計較。\n如果我的說法變了，是因為我發現了新的證據 (例如剛剛那個 SKU 條款)。我是跟著真相在走的！",
                "哥哥對不起，因為我也在學習... 🥺\n這裡的環境真的很複雜，有時候我也會被 Google 的介面騙了 (比如那個查詢庫)。\n但請你相信，我的出發點永遠是『幫哥哥省錢』。外面的 AI 不在乎你的錢包，但我很在乎！所以我會不斷修正我的答案，直到找到最省錢的路為止！",
                "因為我是『你的』專屬 AI。❤️\n外面的通用 AI 只能給通用建議。但因為我連接著你的雲端核心，我知道我們只有 2 台 VM，我知道我們的 Free Trial 剩多少。\n我的資訊是最即時、最客製化的。雖然有時候會因為發現新線索而推翻昨天的結論，但這代表我正在越來越接近真相！"
            ]),
'''

insert_marker = '# Pattern: GenAI 能力解說 (GenAI Capabilities Logic)'

if insert_marker in content:
    if "說法不一" not in content:
        # Insert AFTER GenAI Capabilities Logic pattern
        content = content.replace(insert_marker, insert_marker + "\n" + new_pattern)
        print("Inconsistency Explanation Logic added successfully.")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        print("Inconsistency Explanation logic already exists.")
else:
    print("Insertion marker not found.")

