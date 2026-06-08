# -*- coding: utf-8 -*-
import re
import zipfile
from pathlib import Path

xlsx = Path('4dc1d8c545cd61f7b8065fc98acc5311.xlsx')
out = Path('_tmp_llm_scan')
out.mkdir(exist_ok=True)

with zipfile.ZipFile(xlsx) as z:
    media = []
    for name in z.namelist():
        m = re.match(r'xl/media/image(\d+)\.png', name)
        if m:
            media.append((int(m.group(1)), name))
    media.sort()
    # extract all png under 250 for manual scan subset - batch 100-157
    for num, name in media:
        if 100 <= num <= 157:
            (out / f'image{num}.png').write_bytes(z.read(name))
            print('wrote', num)
