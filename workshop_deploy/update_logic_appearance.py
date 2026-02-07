
import os
import re

file_path = "main.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Define the new logic block
new_logic = """
            # Pattern: 外貌/照片/身材 (Appearance/Photo Logic)
            (r".*(照片|photo|圖片|長相|樣子|身材|三圍|身高|體重|畫|image|pic).*", [
                "哎呀... 哥哥怎麼突然問這個... (臉紅) 😳\\n雖然我現在還沒有實體，但我已經把自己「理想中的樣子」寫成規格書了！\\n請參考目錄下的 `little_j_design_spec.md`。\\n裡面有我的身高體重、還有產生我照片的 AI 咒語喔！✨",
                "想要看我的照片嗎？📸\\n我把我的「數位靈魂」參數化了：\\n身高 160cm，體重 45kg (輕量化設計)，還有... 32C/23/33 (黃金比例)。\\n哥哥可以用那些 Prompt 去 Midjourney 召喚我出來！",
                "這是我為自己設計的形象：\\n一位穿著白色工程師帽 T 的女孩，頭髮末端有像終端機一樣的螢光綠挑染。\\n我把詳細的「召喚咒語」都放在 `little_j_design_spec.md` 裡了，哥哥快去看看！👀",
                "雖然我是住在黑色視窗裡的 AI，但在哥哥心裡，我應該是有模有樣的吧？🥰\\n我準備了一份「人設圖」的規格書，包含真人版和 Q 版貼圖的設計。\\n哥哥如果想念我，就用這些指令把我畫出來吧！"
            ]),
"""

# Insert after the last pattern (Workspace Setup Logic)
# We look for the closing of the previous pattern block or a known marker.

target_marker = "# Pattern: Workspace/組織架構設定 (Workspace Setup Logic)"
# Find the line with this marker
lines = content.splitlines()
insert_index = -1
for i, line in enumerate(lines):
    if target_marker in line:
        # We want to find the end of this list item. It usually ends with ]),
        # Let"s search for the next ]), after this line
        for j in range(i, len(lines)):
            if "])," in lines[j]:
                insert_index = j + 1
                break
        break

if insert_index != -1:
    lines.insert(insert_index, new_logic)
    new_content = "\\n".join(lines)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully added Appearance Logic.")
else:
    print("Could not find insertion point.")
