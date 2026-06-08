# -*- coding: utf-8 -*-
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_excel(Path(__file__).parent / '4dc1d8c545cd61f7b8065fc98acc5311.xlsx', sheet_name='央企数科')
row24 = df.iloc[22]
row25 = df.iloc[23]
for label, row in [('24', row24), ('25', row25)]:
    print('=== row', label, '===')
    for col, val in row.items():
        if pd.notna(val):
            print(col, ':', str(val)[:200])
