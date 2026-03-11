import csv
import sys
import os
import urllib.request
import io

TEMPLATE_FILE = 'menu_template.html'
DATA_FILE = 'menu_data.csv'
OUTPUT_FILE = 'menu_b5.html'

# スプレッドシートの公開URL（後で岩田様に設定していただく想定）
# 例: https://docs.google.com/spreadsheets/d/.../export?format=csv
SPREADSHEET_CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQi87lV_4n_ziuBX_B3UE-lXkowN89TuKEjRLj6gUTKTpp7C7wZCX7pvbyPs9ka16jWSESUKSadup4U/pub?output=csv'

def load_data(filepath, url=''):
    data = {
        'main': [],
        'topping': [],
        'topping_note': [],
        'limited': [],
        'drink': []
    }
    
    try:
        # URLが設定されている場合は、Webから直接CSVをダウンロードして読み込む
        if url:
            print("Webからスプレッドシートのデータを取得しています...")
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                csv_content = response.read().decode('utf-8')
                f = io.StringIO(csv_content)
        else:
            print("ローカルのCSVファイルを読み込んでいます...")
            f = open(filepath, newline='', encoding='utf-8')
            
        reader = csv.DictReader(f)
        for row in reader:
            if not row or 'category' not in row:
                continue
            cat = row['category']
            if cat in data:
                data[cat].append(row)
                
        if not url:
            f.close()
            
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)
        
    return data

def build_topping_html(toppings):
    html = '<ul class="topping-list">\n'
    for t in toppings:
        html += f'                        <li class="topping-item">{t["name"]}</li>\n'
    html += '                    </ul>'
    return html

def build_topping_note_html(notes):
    html = '<div class="topping-note">\n'
    for n in notes:
        html += f'                        {n["name"]} <span class="price-text">{n["price"]}</span><br>\n'
    # 最後のbrを削る
    if html.endswith('<br>\n'):
        html = html[:-5] + '\n'
    html += '                    </div>'
    return html

def build_limited_html(limited_items):
    html = ''
    for item in limited_items:
        html += f'''                    <div class="limited-item">
                        <p class="limited-desc">{item["description"]}</p>
                        <p class="limited-name">{item["name"]}</p>
                        <p class="limited-price">{item["price"]}</p>
                    </div>\n'''
    return html

def build_drink_html(drinks):
    html = '<ul class="drink-list">\n'
    for d in drinks:
        html += f'                            <li class="drink-item"><span class="drink-name-part">{d["name"]}</span><span>{d["price"]}</span></li>\n'
    html += '                        </ul>'
    return html

def main():
    if not os.path.exists(TEMPLATE_FILE):
        print(f"Template file '{TEMPLATE_FILE}' not found.")
        sys.exit(1)

    data = load_data(DATA_FILE, SPREADSHEET_CSV_URL)
    
    # テンプレートを読み込む
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template_content = f.read()

    # 主要データの抽出
    main_item = data['main'][0] if data['main'] else {'name': '商品未設定', 'price': '¥---', 'description': '', 'note': ''}
    
    # HTMLパーツの組み立て
    topping_html = build_topping_html(data['topping'])
    topping_note_html = build_topping_note_html(data['topping_note'])
    limited_html = build_limited_html(data['limited'])
    drink_html = build_drink_html(data['drink'])

    # テンプレート内のプレースホルダーを置換
    # (ここでは直接タグ構造をプレースホルダー化済みのテンプレートを想定)
    new_content = template_content.replace('<!-- {{MAIN_TITLE}} -->', main_item["name"])
    new_content = new_content.replace('<!-- {{MAIN_PRICE}} -->', main_item["price"])
    new_content = new_content.replace('<!-- {{MAIN_DESC}} -->', main_item["description"])
    new_content = new_content.replace('<!-- {{MAIN_NOTE}} -->', main_item["note"])
    new_content = new_content.replace('<!-- {{TOPPING_LIST}} -->', topping_html)
    new_content = new_content.replace('<!-- {{TOPPING_NOTE}} -->', topping_note_html)
    new_content = new_content.replace('<!-- {{LIMITED_LIST}} -->', limited_html)
    new_content = new_content.replace('<!-- {{DRINK_LIST}} -->', drink_html)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Successfully generated {OUTPUT_FILE} from {DATA_FILE}")

if __name__ == '__main__':
    main()
