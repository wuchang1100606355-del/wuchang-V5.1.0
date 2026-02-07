import re
import sys

file_path = 'main.py'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
except Exception as e:
    print(f"Error reading file: {e}")
    sys.exit(1)

# Logic for GenAI Capabilities (App/Animation)
new_pattern = r'''
            # Pattern: GenAI 能力解說 (GenAI Capabilities Logic)
            (r".*(複雜|complex|做|make|develop|開發).*(APP|手機|mobile|動畫|animation|video|影片).*(嗎|can|could).*", [
                "可以！而且超級強！💪\n這就是那筆 3.5 萬美金的真正用途：它能用來開發**超複雜的生成式 AI 應用**，甚至是自動生成動畫腳本或影片的後端系統。它是給『AI 創業家』用的神兵利器！✨\n但對我們這種還在煩惱 VM 硬碟費用的『基礎建設組』來說，這就像是給了我們一台法拉利引擎，但我們還在蓋車庫... 用不到啊！😩",
                "它絕對做得到！🚀\nGoogle 的 GenAI App Builder 就是專門用來做這種高科技應用的。如果你想做一個『自動生成動畫的 App』，那這筆錢就超好用。\n可是哥哥... 我們現在連網站都還沒架好，VM 還在算流量費。這種高階玩法，等我們以後變成科技大亨再來玩吧！現在讓它過期沒關係，我們養不起這頭神獸。🐉",
                "這就是它的強項！🎬\n它不只能寫 APP，還能接上 Vertex AI 做影像生成。如果你是動畫公司的老闆，這筆錢簡直是天上掉下來的禮物。\n但現實是... 我們只是想架個 WordPress 或跑個小程式。拿核子彈來打蚊子太浪費了 (而且我們還付不起核子彈的維護費)。所以放生它是為了我們的錢包著想！💸",
                "哥哥你問到重點了！🎯\n它就是設計來做這些『未來科技』的。你想得到的 AI 功能，它幾乎都能幫你實現。\n但問題是：**我們現在的專案階段用不到**。我們還在蓋地基，不需要買太空梭的燃料。把這筆虛幻的額度忘了吧，我們專心顧好那筆 ,823 的真錢就好！"
            ]),
'''

insert_marker = '# Pattern: 服務用途解釋 (Service Explanation Logic)'

if insert_marker in content:
    if "GenAI 能力解說" not in content:
        # Insert AFTER Service Explanation Logic pattern
        content = content.replace(insert_marker, insert_marker + "\n" + new_pattern)
        print("GenAI Capabilities Logic added successfully.")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        print("GenAI Capabilities logic already exists.")
else:
    print("Insertion marker not found.")

