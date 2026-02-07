import csv
from io import StringIO
from collections import defaultdict

BAD_IMAGE_KEYS = {
    "https://storage.googleapis.com/quickclick_products/library/20578/web-ZeyNXrd4b,QC_P_39095596,P_49180031,O7835309,,,",
    "https://storage.googleapis.com/quickclick_products/library/20578/web-q0KzdGR09,QC_P_39095597,P_49180040,O8536132,,,",
}

MAIN_PRODUCTS_CSV = """主商品菜單編號,主商品編號,主商品類別,主商品名稱,主商品價格,主商品描述,主商品圖片,主商品代碼,主商品料號,套用加購選單,Ubereats價格,Ubereats圖片,Foodpanda價格,Foodpanda圖片
M387676,49180031,義式咖啡,招牌咖啡,85,"<p>採用聊閣秘方基底豆，搭配品皇咖啡所生產的特級奶精調製而成，較特調咖啡奶精使用較多</p>\n", `https://storage.googleapis.com/quickclick_products/library/20578/web-ZeyNXrd4b,QC_P_39095596,P_49180031,O7835309,,,`
M387676,49180040,義式咖啡,特調咖啡,75,"<p>以本店精選基底豆搭配品皇奶精粉調製而成</p>\n", `https://storage.googleapis.com/quickclick_products/library/20578/web-q0KzdGR09,QC_P_39095597,P_49180040,O8536132,,,`
M387676,49180058,義式咖啡,咖啡拿鐵,90,"<p>Coffee Latte</p>\n\n<p>以牛奶為主角的咖啡飲品，深受消費這喜愛，為本店唯一能與美式咖啡競爭...</p>",QC_P_39095598,P_49180058,O7835313,,,
M387676,60978239,咖啡豆,肯亞AA,445,"<p><!--StartFragment --></p>\n\n<p>來自非洲高原的 Kenya AA，是咖啡愛好者心中的經典之選。這款豆子以其明亮果酸、層次豐富的莓果香氣與乾淨的口感著稱，讓每一口都像在品嚐一杯花果茶。</p>\n\n<ul>\n\t<li>風味筆記：黑醋栗、柑橘皮、烏梅、紅酒般的圓潤質地</li>\n\t<li>處理法：水洗（雙重發酵），風味純淨、酸質明亮</li>\n\t<li>烘焙建議：淺中焙，展現其果酸與花香的最佳平衡</li>\n\t<li>產區與品種：來自 Nyeri 高海拔地區，SL28 / SL34 品種，風味細緻、層次豐富</li>\n</ul>\n\n<p>這是一款適合靜心品味的精品咖啡，無論是手沖還是冷萃，都能展現其獨特魅力。推薦給喜歡果香調、酸甜平衡的你。</p>\n\n<p>\u00a0</p>\n\n<p>\u00a0</p>\n\n<p><!--EndFragment --></p>\n",,,P_60978239,O8640678,,,
M387676,49180035,濾掛咖啡,黃金曼特寧,400,"<p>來自印尼亞齊省的曼特寧豆經三次人工選豆，淘汰約25%的特選3A黃金...</p>",,,P_49180035,O7835317,,,
"""

OPTION_GROUP_NAMES_CSV = """題型選項組合編號,題型選項組合名稱
O7835309,尺寸(30)+溫度+甜度
O7835310,尺寸(35)+溫度+甜度
O7835311,尺寸(40)+溫度+甜度
O7835312,尺寸(5)+溫度+甜度
O7835313,尺寸(10)+溫度+甜度
O7835314,尺寸(15)+溫度+甜度
O7835315,貝果口味
O7835316,尺寸(25)+溫度+甜度
O7835317,黃金曼特寧+耶加雪夫
O7835318,曼特寧+藍山
O7835319,曼巴
O7835320,招牌咖啡豆
O7835321,尺寸(40)+糖漿口味+溫度+甜度
O7835325,尺寸(20)+溫度+甜度
O7835326,厚片口味
O7835329,簡餐飲品
O8536132,特調加購
O8640678,手沖溫控方式
O8701672,定食飲料
O8701886,加購鮮奶咖啡
O8796286,西西里調整項目
"""

OPTION_DETAILS_CSV = """題型選項組合編號,加購題型,加購題型顯示名稱,加購選項,加購選項顯示名稱,加購選項價格,加購題型描述,選項題型(單/雙),是否必填(Y/N),子選單菜單編號,加購選項代碼,加購題型代碼
O7835309,尺寸,尺寸,L(+30),L,30,,單,Y,,QC_OI_26159949,QC_OG_6924334
O7835309,尺寸,尺寸,M(+0),M,0,,單,Y,,QC_OI_26159972,QC_OG_6924334
O7835309,尺寸,尺寸,S(-15),S,-15,,單,Y,,QC_OI_31851882,QC_OG_6924334
O7835309,甜度,甜度,正常100%,正常100%,0,,單,Y,,QC_OI_26159948,QC_OG_6924335
O7835309,甜度,甜度,少糖75%,少糖75%,0,,單,Y,,QC_OI_26159955,QC_OG_6924335
O7835313,溫度,溫度,去冰,去冰,0,,單,Y,,QC_OI_26159951,QC_OG_6924337
O7835313,溫度,溫度,微冰,微冰,0,,單,Y,,QC_OI_26159951,QC_OG_6924337
O7835313,溫度,溫度,溫,溫,0,,單,Y,,QC_OI_26159953,QC_OG_6924337
O7835314,尺寸,尺寸,L(+15),L,15,,單,Y,,QC_OI_26159963,QC_OG_6924338
O7835314,尺寸,尺寸,M(+0),M,0,,單,Y,,QC_OI_26159972,QC_OG_6924338
O8536132,甜度,甜度,正常100%,正常100%,0,,單,Y,,QC_OI_26159948,QC_OG_6924339
O8536132,甜度,甜度,半糖50%,半糖50%,0,,單,Y,,QC_OI_26159956,QC_OG_6924339
O8640678,手沖溫控方式,手沖溫控方式,一般熱飲,一般熱飲,0,,單,Y,,QC_OI_32039266,QC_OG_6924340
O8640678,手沖溫控方式,手沖溫控方式,保溫瓶,保溫瓶,0,,單,Y,,QC_OI_32039267,QC_OG_6924340
"""


def parse_csv_string(csv_string):
    f = StringIO(csv_string.strip())
    reader = csv.reader(f, dialect='excel')
    try:
        header = next(reader)
    except StopIteration:
        return []
    header = [h.strip() for h in header]
    expected_cols = len(header)
    data = []
    for row in reader:
        if len(row) < expected_cols:
            row.extend([''] * (expected_cols - len(row)))
        if len(row) > expected_cols:
            row = row[:expected_cols]
        try:
            data.append(dict(zip(header, row)))
        except Exception:
            continue
    return data


def integrate_menu_data():
    main_products = parse_csv_string(MAIN_PRODUCTS_CSV)
    option_group_names = parse_csv_string(OPTION_GROUP_NAMES_CSV)
    option_details = parse_csv_string(OPTION_DETAILS_CSV)

    group_name_map = {item['題型選項組合編號']: item['題型選項組合名稱'] for item in option_group_names}

    group_options_map = defaultdict(lambda: defaultdict(list))
    for detail in option_details:
        gid = detail['題型選項組合編號']
        opt_type = detail['加購題型']
        name = detail['加購選項顯示名稱']
        try:
            price = int(detail['加購選項價格'])
        except ValueError:
            price = 0
        group_options_map[gid][opt_type].append({
            '名稱': name,
            '價格變動': price,
            '是否必選': detail.get('是否必填(Y/N)', 'N'),
            '題型': detail.get('選項題型(單/雙)', '單'),
        })

    integrated = []
    for p in main_products:
        gid = p.get('套用加購選單')
        entry = {
            '名稱': p.get('主商品名稱', ''),
            '價格': p.get('主商品價格', ''),
            '類別': p.get('主商品類別', ''),
            '代碼': p.get('主商品代碼', ''),
            '料號': p.get('主商品料號', ''),
            '圖片': (p.get('主商品圖片', '') or '').strip().strip('`'),
            '加購組合編號': gid or '',
            '加購組合名稱': group_name_map.get(gid, '無'),
            '加購選項': group_options_map.get(gid, {}),
        }
        integrated.append(entry)
    return integrated


def check_completeness(integrated):
    problems = []
    for item in integrated:
        name = item['名稱'] or '(未命名)'
        # 價格
        try:
            price = int(str(item['價格']).strip())
        except Exception:
            problems.append(f"價格缺失或非數字: {name}")
        # 代碼/料號
        if not item['代碼'] and not item['料號']:
            problems.append(f"代碼/料號皆缺失: {name}")
        # 圖片
        img = item.get('圖片', '')
        if img and (',' in img or img in BAD_IMAGE_KEYS or not img.startswith('http')):
            problems.append(f"圖片連結不可用: {name}")
        # 加購選單存在性
        gid = item['加購組合編號']
        if gid and item['加購組合名稱'] == '無':
            problems.append(f"加購組合未定義: {name} ({gid})")
        # 必選題型完整性
        opts = item['加購選項']
        for t, arr in opts.items():
            if arr and arr[0].get('是否必選', 'N') == 'Y' and len(arr) == 0:
                problems.append(f"必選題型無選項: {name} ({t})")
    return problems


def format_output(integrated, problems):
    out = []
    out.append(f"商品數量: {len(integrated)}")
    out.append(f"問題數量: {len(problems)}")
    if problems:
        out.append("問題清單:")
        out.extend([f"- {p}" for p in problems])
    out.append("\n預覽 (前 5 筆):")
    for item in integrated[:5]:
        img_ok = 'OK' if item.get('圖片') and item.get('圖片') not in BAD_IMAGE_KEYS and ',' not in item.get('圖片') and item.get('圖片').startswith('http') else '缺圖或無效'
        out.append(f"【{item['名稱']}】NT$ {item['價格']} | 類別: {item['類別']} | 加購: {item['加購組合名稱']} | 圖片: {img_ok}")
    return "\n".join(out)


if __name__ == '__main__':
    data = integrate_menu_data()
    probs = check_completeness(data)
    print(format_output(data, probs))
