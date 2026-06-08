# -*- coding: utf-8 -*-
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent
XLSX = ROOT / '4dc1d8c545cd61f7b8065fc98acc5311.xlsx'
OUT = ROOT / '_tmp_dianxin'
OUT.mkdir(exist_ok=True)

with zipfile.ZipFile(XLSX) as z:
    for i in range(170, 185):
        name = f'xl/media/image{i}.png'
        if name in z.namelist():
            data = z.read(name)
            (OUT / f'image{i}.png').write_bytes(data)
            print(name, len(data))
