import re

file_path = 'main.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if pattern already exists
if "Vertex AI/VM Manager 啟用與費用" in content:
    print("Pattern already exists.")
    exit()

# Define the new pattern and responses
new_pattern = """
            # Pattern: Vertex AI/VM Manager 啟用與費用 (Vertex AI / VM Manager Cost)
            (r".*(Vertex|Gemini|AI|啟用|API|VM Manager|修補|Patch|100 VMs).*(買|buy|錢|cost|pay|free|免費).*", [
                "哥哥看這裡！👇 畫面上有寫『VM Manager is available at no charge for up to 100 VMs』。意思是**100 台以內免費**！我們只有 2 台，所以這個『啟用 VM 管理員』按下去是**不用錢**的。它是用來幫 VM 自動打安全補丁的，建議可以啟用喔！🛡️",
                "關於那個 Vertex AI... 它是 Google 的 AI 平台。啟用 API 本身不用錢，但是**使用** AI 模型（像 Gemini）會算錢。如果哥哥現在沒有要開發 AI 功能，可以先不理它，或者啟用也沒關係，只要不呼叫就不會扣款。 🤖",
                "放心！VM Manager (修補程式) 對我們這種小規模使用者是**完全免費**的 (100 台以下)。啟用它能讓 Google 幫我們監控系統漏洞，是個省錢又安全的好工具！ ✅",
                "那個『啟用所有建議的 API』(Vertex AI) 如果按下去，只是開啟了功能開關，並不會馬上扣錢。費用是看你跑了多少 AI 運算。如果哥哥擔心誤觸，我們可以先不啟用 Vertex AI，專注在免費的 VM Manager 就好。"
            ]),
"""

# Find the insertion point (after "安裝代理程式/按鈕扣費" pattern)
insert_marker = '# Pattern: 安裝代理程式/按鈕扣費 (Ops Agent Cost)'
parts = content.split(insert_marker)

if len(parts) > 1:
    new_content = parts[0] + new_pattern + insert_marker + parts[1]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully added Vertex/VM Manager Logic pattern.")
else:
    # Fallback: try to find "查詢庫誤解" if "安裝代理程式" is not yet flushed or readable in this context
    insert_marker_fallback = '# Pattern: 查詢庫誤解 (Query Library Confusion)'
    parts_fallback = content.split(insert_marker_fallback)
    if len(parts_fallback) > 1:
         new_content = parts_fallback[0] + new_pattern + insert_marker_fallback + parts_fallback[1]
         with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
         print("Successfully added Vertex/VM Manager Logic pattern (fallback position).")
    else:
        print("Could not find insertion point.")

