import os

file_path = "main.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Pattern: 2 VMs / Node Names Discovery
new_pattern = '            # Pattern: 發現2架VM/節點名稱 (Resource Reality)\n'
new_pattern += '            (r".*(2架|2台|兩架|兩台|sovereign|community|node-a|node-b|只有兩個|不是5架).*", [\n'
new_pattern += '                "哥哥！原來只有 **2 架 VM**！🎉 (sovereign-node-a 和 community-node-b)。之前的 5 架可能是誤會，或是包含了其他已關閉的資源。這對預算來說是大好消息！",\n'
new_pattern += '                "看到這兩個名字... Sovereign (主權) 和 Community (社群)... 這不就是哥哥一直在強調的「五常」精神嗎？原來我們的架構是建立在這些價值之上的。 🏙️",\n'
new_pattern += '                "2025/12/22... 這兩個節點是在那天誕生的。哥哥，那天是不是發生了什麼重要的事？這是我們數位領土的誕生日呀！",\n'
new_pattern += '                "太好了！只有 2 架 VM 的話，那個 Gemini Code Assist 的費用問題應該更容易釐清了。我們只需要專注保護這兩個核心節點！"\n'
new_pattern += '            ]),\n'

if "發現2架VM" not in content:
    content = content.replace("self.patterns = [", "self.patterns = [" + "\n" + new_pattern)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated main.py with 2 VM reality logic")
else:
    print("2 VM logic already exists")
