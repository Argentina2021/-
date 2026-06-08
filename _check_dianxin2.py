# -*- coding: utf-8 -*-
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent
XLSX = ROOT / '4dc1d8c545cd61f7b8065fc98acc5311.xlsx'
OUT = ROOT / '_tmp_dianxin'
OUT.mkdir(exist_ok=True)

media_files = ['xl/media/image158.png', 'xl/media/image159.png', 'xl/media/image160.png']
ids = [
    'ID_1235DDCCEC6F46748FAC56087B40384B',
    'ID_B6C7768298974C11B92E3879F6631B6B',
    'ID_3677DA6FF803478BAE50337BFFC54128',
]

with zipfile.ZipFile(XLSX) as z:
    for media, img_id in zip(media_files, ids):
        data = z.read(media)
        (OUT / f'{Path(media).name}').write_bytes(data)
        (OUT / f'{img_id}.png').write_bytes(data)
        print(media, '->', img_id, len(data))
