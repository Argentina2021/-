# -*- coding: utf-8 -*-
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / 'extracted_images'
XLSX = ROOT / '4dc1d8c545cd61f7b8065fc98acc5311.xlsx'

pairs = [
    ('xl/media/image176.png', 'wanding_park_land.png'),
    ('xl/media/image177.png', 'wanding_park_building.png'),
]

with zipfile.ZipFile(XLSX) as z:
    for media, name in pairs:
        data = z.read(media)
        dest = OUT / name
        dest.write_bytes(data)
        print('wrote', dest, len(data))
