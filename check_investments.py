"""檢查初期投資資料結構"""
from calculate_shangpin_donation_total import INITIAL_INVESTMENTS

print("=" * 60)
print("初期投資項目容器檢查")
print("=" * 60)
print()

print(f"項目總數：{len(INITIAL_INVESTMENTS)}")
print()

total = 0
for i, item in enumerate(INITIAL_INVESTMENTS, 1):
    print(f"{i}. {item['item']}")
    print(f"   日期：{item['date']}")
    print(f"   金額：{item['amount']:,} 元")
    print(f"   說明：{item['description'][:50]}...")
    print()
    total += item['amount']

print("=" * 60)
print(f"總金額驗證：{total:,} 元")
print("=" * 60)

# 檢查資料結構完整性
print("\n資料結構檢查：")
required_fields = ['date', 'item', 'amount', 'description']
all_valid = True
for i, item in enumerate(INITIAL_INVESTMENTS, 1):
    for field in required_fields:
        if field not in item:
            print(f"❌ 項目 {i} 缺少欄位：{field}")
            all_valid = False
        elif not item[field]:
            print(f"⚠️  項目 {i} 欄位 {field} 為空")
            all_valid = False

if all_valid:
    print("[OK] 所有項目資料結構完整")
else:
    print("[ERROR] 發現資料結構問題")
