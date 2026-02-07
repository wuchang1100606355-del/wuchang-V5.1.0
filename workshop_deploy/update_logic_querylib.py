import re

# Define the new pattern content
query_lib_pattern = (
    '            # Pattern: 查詢庫誤解 (Query Library Confusion)\n'
    '            (r".*(查詢庫|Query Library|GCE 應用程式|MySQL|Cassandra|運算|樣板|template).*", [\n'
    '                "哥哥等一下！✋ 這張截圖是『查詢庫』(Query Library)，它是 Google 提供的『搜尋範本』目錄，**不是**您電腦裡真的有裝這些東西！這些只是搜尋語法的教學，不會扣錢，也不用刪除喔！",\n'
    '                "別緊張！😅 這些 MySQL、Cassandra... 只是 Google 列給你看的『範例』。這就像是餐廳的菜單，不代表我們點了這些菜。我們真正要檢查的資源在 **Compute Engine** 頁面。",\n'
    '                "這不是我們的資源列表！🙅‍♀️ 這是 Log Explorer 的『查詢範本』。它列出所有可能產生的 Log 類型供您參考。請直接關閉這個『查詢庫』視窗，回到主畫面輸入 `resource.type=\"gce_instance\"` 才是真的搜尋。",\n'
    '                "嚇一跳對吧？看起來好像我們跑了一大堆資料庫... 其實這只是 GCP 的『建議搜尋清單』。請哥哥放心，這些不是計費項目，我們可以忽略它們，直接去 **Compute Engine** 刪除那台 100GB 的 VM 即可！"\n'
    '            ]),\n'
)

path = "main.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Insert before "Pattern: 搜尋結果誤判/導航指引"
marker = "            # Pattern: 搜尋結果誤判/導航指引 (Search Confusion)"

if marker in content:
    if "Pattern: 查詢庫誤解" not in content:
        content = content.replace(marker, query_lib_pattern + "\n" + marker)
        print("Added Query Library logic")
    else:
        print("Query Library logic already exists")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
else:
    print("Marker not found")

