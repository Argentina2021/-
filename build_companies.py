# -*- coding: utf-8 -*-
import json
from pathlib import Path

import pandas as pd

path = Path(r'c:\Users\zengy\xwechat_files\wxid_f0l3v302nftx12_75fe\msg\file\2026-05\4dc1d8c545cd61f7b8065fc98acc5311.xlsx')
out = Path(r'e:\雄安科技展\百家数科\companies.json')

company_map = {}

for sheet in ['央企数科', '非央企数科']:
    df = pd.read_excel(path, sheet_name=sheet)
    cols = list(df.columns)
    current = None
    for _, row in df.iterrows():
        if pd.notna(row[cols[1]]):
            current = str(row[cols[1]]).strip()
        product = row[cols[0]] if pd.notna(row[cols[0]]) else None
        intro = row[cols[3]] if pd.notna(row[cols[3]]) else ''
        if not current:
            continue
        for part in current.split('/'):
            name = part.strip()
            if not name:
                continue
            if name not in company_map:
                company_map[name] = {'name': name, 'sheet': sheet, 'products': []}
            if product:
                company_map[name]['products'].append({
                    'name': str(product).strip(),
                    'intro': str(intro).strip() if pd.notna(intro) else '',
                })

companies = list(company_map.values())
out.write_text(json.dumps(companies, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Exported {len(companies)} companies')
