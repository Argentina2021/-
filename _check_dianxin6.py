# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_excel(Path(__file__).parent / '4dc1d8c545cd61f7b8065fc98acc5311.xlsx', sheet_name='央企数科')
cols = list(df.columns)
company = None
for i, row in df.iterrows():
    if pd.notna(row[cols[1]]):
        company = str(row[cols[1]]).strip()
    if company != '中电信数字城市科技有限公司':
        continue
    product = row[cols[0]]
    imgs = []
    for col in cols[2:]:
        val = row[col]
        if pd.notna(val):
            imgs.extend(re.findall(r'DISPIMG\("([^"]+)"', str(val)))
    print(i + 2, product, imgs)
