# -*- coding: utf-8 -*-
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
df = pd.read_excel(ROOT / '4dc1d8c545cd61f7b8065fc98acc5311.xlsx', sheet_name='央企数科')
cols = list(df.columns)
print('columns:', cols)
current = None
for i, row in df.iterrows():
    if pd.notna(row[cols[1]]):
        current = str(row[cols[1]]).strip()
    if i + 2 not in (24, 25):
        continue
    print('\nrow', i + 2, 'company', current)
    for j, col in enumerate(cols):
        val = row[col]
        if pd.notna(val):
            s = str(val)
            if 'DISPIMG' in s or j < 4:
                print(' ', j, col, s[:120])
