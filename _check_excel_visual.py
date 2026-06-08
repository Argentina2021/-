# -*- coding: utf-8 -*-
import re
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

xlsx = Path(__file__).parent / '4dc1d8c545cd61f7b8065fc98acc5311.xlsx'
with zipfile.ZipFile(xlsx) as z:
    names = [n for n in z.namelist() if 'drawing' in n.lower() or 'sheet1' in n.lower()]
    for n in sorted(names)[:30]:
        print(n)
