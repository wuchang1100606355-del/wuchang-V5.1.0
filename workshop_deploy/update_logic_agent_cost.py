import re

file_path = 'main.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if pattern already exists
if "安裝代理程式/按鈕扣費" in content:
    print("Pattern already exists.")
    exit()

# Define the new pattern and responses
new_pattern = """
            # Pattern: 安裝代理程式/按鈕扣費 (Ops Agent Cost)
            (r".*(按|點|click|install|安裝).*(扣錢|收費|花錢|cost|charge|錢).*", [
                "哥哥，那個『安裝作業套件代理程式』(Ops Agent) 本身是**免費**的軟體。但是！它收集的數據量如果太多，超過每個月的免費額度（通常是 50GB 日誌），就會開始收費。以我們現在的省錢策略，建議**不要按**，基本的監控就夠用了！",
                "這個按鈕本身不會扣款！它是用來安裝 Google 的監控軟體。不過，安裝後它會產生額外的 Log 和 Metrics，這些數據**可能會**產生費用。為了保險起見，我們暫時維持現狀就好，不用安裝喔！ 🛡️",
                "小心為上！�� 雖然軟體免費，但『數據儲存』是要錢的。既然我們已經有基礎的 CPU 監控圖表了，除非哥哥需要看到記憶體 (Memory) 的詳細數據，否則我們可以跳過這一步，幫新創團隊省預算！",
                "別擔心，按下去的那一刻不會扣錢。但它是個『吃數據怪獸』的開關！👻 為了避免日後帳單驚嚇，我們還是先不要安裝這個進階監控代理程式比較安全。"
            ]),
"""

# Find the insertion point (after "查詢庫誤解" pattern)
insert_marker = '# Pattern: 查詢庫誤解 (Query Library Confusion)'
parts = content.split(insert_marker)

if len(parts) > 1:
    new_content = parts[0] + new_pattern + insert_marker + parts[1]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully added Agent Cost Logic pattern.")
else:
    print("Could not find insertion point.")

