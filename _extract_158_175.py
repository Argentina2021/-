# -*- coding: utf-8 -*-
import zipfile
from pathlib import Path

xlsx = Path('4dc1d8c545cd61f7b8065fc98acc5311.xlsx')
out = Path('_tmp_hq2')
out.mkdir(exist_ok=True)
with zipfile.ZipFile(xlsx) as z:
    for n in range(158, 176):
        for ext in ('png', 'jpeg'):
            p = f'xl/media/image{n}.{ext}'
            if p in z.namelist():
                (out / f'image{n}{Path(p).suffix}').write_bytes(z.read(p))
print('ok')
