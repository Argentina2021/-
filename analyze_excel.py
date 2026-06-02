# -*- coding: utf-8 -*-
import json
import pandas as pd
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path = r'c:\Users\zengy\xwechat_files\wxid_f0l3v302nftx12_75fe\msg\file\2026-05\4dc1d8c545cd61f7b8065fc98acc5311.xlsx'
xl = pd.ExcelFile(path)
print('SHEETS:', xl.sheet_names)

for idx, name in enumerate(xl.sheet_names):
    df = pd.read_excel(path, sheet_name=name, header=0)
    print(f'\n===== Sheet {idx+1}: {name} =====')
    print('Shape:', df.shape)
    print('Columns:', list(df.columns))
    for col in df.columns:
        print(f'  {col}: non-null={df[col].notna().sum()}')

df1 = pd.read_excel(path, sheet_name=0, header=0)
df2 = pd.read_excel(path, sheet_name=1, header=0)

col_product = df1.columns[0]
col_company = df1.columns[1]
col_image = df1.columns[2]
col_intro = df1.columns[3]

print('\n===== CONTENT ANALYSIS =====')
rows = []
current_company = None
for i, row in df1.iterrows():
    product = row[col_product] if pd.notna(row[col_product]) else None
    company = row[col_company] if pd.notna(row[col_company]) else None
    intro = row[col_intro] if pd.notna(row[col_intro]) else None
    if company:
        current_company = company
    if product or intro:
        rows.append({
            'row': i + 2,
            'product': product,
            'company': company or current_company,
            'has_image': pd.notna(row[col_image]),
            'intro_len': len(str(intro)) if intro else 0,
            'intro_preview': (str(intro)[:80] + '...') if intro and len(str(intro)) > 80 else (str(intro) if intro else '')
        })

print(f'Total content entries (sheet1): {len(rows)}')
named_products = [r for r in rows if r['product']]
print(f'Entries with product name: {len(named_products)}')
print(f'Entries without product name (sub-items): {len(rows) - len(named_products)}')

companies = set(r['company'] for r in rows if r['company'])
print(f'Unique companies (sheet1): {len(companies)}')

# Sheet 2
col2_product = df2.columns[0]
col2_company = df2.columns[1]
rows2 = []
current_company2 = None
for i, row in df2.iterrows():
    product = row[col2_product] if pd.notna(row[col2_product]) else None
    company = row[col2_company] if pd.notna(row[col2_company]) else None
    intro_col = df2.columns[3] if len(df2.columns) > 3 else None
    intro = row[intro_col] if intro_col and pd.notna(row[intro_col]) else None
    if company:
        current_company2 = company
    if product or intro:
        rows2.append({
            'row': i + 2,
            'product': product,
            'company': company or current_company2,
            'intro_len': len(str(intro)) if intro else 0,
        })

print(f'\nTotal content entries (sheet2): {len(rows2)}')
companies2 = set(r['company'] for r in rows2 if r['company'])
print(f'Unique companies (sheet2): {len(companies2)}')

# Category grouping by keywords
keywords = {
    'AI/大模型': ['AI', '大模型', '智能', 'DeepSeek', 'MaaS', 'TopASK', 'LimiX'],
    '数据/可信空间': ['数据', '可信', '空间', '隐私'],
    '安全/合规': ['安全', '合规', 'SOC', 'ABIS', '生物识别', '虹膜', '指纹'],
    '芯片/硬件': ['芯片', 'RISC-V', 'SIM', 'SoC', 'MCU', '模组', 'POI', '北斗'],
    '城市/政务': ['城市', '政务', '12345', 'IOC', 'CIM', '城管'],
    '工业/制造': ['工业', '制造', 'MOM', 'MES', '石油', '巡检'],
    '交通/低空': ['交通', '低空', '车路', '停车', '北斗'],
    '医疗': ['医疗', '医院', 'HIS'],
    '办公/协同': ['办公', 'OA', 'OneOffice', '协同'],
    '金融/供应链': ['金融', '供应链', '征信', '征信'],
    '能源/双碳': ['能源', '双碳', '碳', '燃气', '用电'],
    '教育': ['教育', '培训', '学习'],
}

def categorize(name):
    if not name:
        return '其他/未命名'
    cats = []
    for cat, kws in keywords.items():
        if any(k in str(name) for k in kws):
            cats.append(cat)
    return cats if cats else ['其他']

from collections import Counter
cat_counter = Counter()
for r in rows:
    cats = categorize(r['product'])
    for c in cats:
        cat_counter[c] += 1

print('\n===== CATEGORY DISTRIBUTION (by product name keywords) =====')
for cat, cnt in cat_counter.most_common():
    print(f'  {cat}: {cnt}')

print('\n===== COMPANY LIST (sheet1) =====')
for c in sorted(companies):
    cnt = sum(1 for r in rows if r['company'] == c)
    print(f'  {c} ({cnt} items)')

print('\n===== ALL PRODUCTS (sheet1) =====')
for r in rows:
    pname = r['product'] or '(未命名子项)'
    print(f"  [{r['row']}] {pname} — {r['company']}")

if rows2:
    print('\n===== ALL PRODUCTS (sheet2) =====')
    for r in rows2:
        pname = r['product'] or '(未命名子项)'
        print(f"  [{r['row']}] {pname} — {r['company']}")

# Save structured data
out = {
    'sheet_names': xl.sheet_names,
    'sheet1_count': len(rows),
    'sheet2_count': len(rows2),
    'companies_sheet1': sorted(companies),
    'products_sheet1': rows,
    'products_sheet2': rows2,
}
with open(r'e:\雄安科技展\百家数科\excel_data.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print('\nSaved excel_data.json')
