# -*- coding: utf-8 -*-
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent
XLSX = ROOT / '4dc1d8c545cd61f7b8065fc98acc5311.xlsx'
OUT = ROOT / '_tmp_dianxin'
OUT.mkdir(exist_ok=True)

ids = [
    'ID_5DEC89BBACD443CDB7EA28CB4E172CE6',
    'ID_797ECEA92F5F4E00A5D51B9E1AF5F07D',
    'ID_A8AD8661CFA446CB919070B9BDAD02C1',
    'ID_ACB737E081CD42E881F572ADD08D97AA',
]

with zipfile.ZipFile(XLSX) as z:
    cell = z.read('xl/cellimages.xml').decode('utf-8')
    rels = z.read('xl/_rels/cellimages.xml.rels').decode('utf-8')

rid_to_media = {}
for m in re.finditer(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', rels):
    target = m.group(2)
    if target != 'NULL':
        rid_to_media[m.group(1)] = target if target.startswith('xl/') else f'xl/{target}'

for block in re.split(r'(?=<etc:cellImage>)', cell):
    name_m = re.search(r'name="([^"]+)"', block)
    if not name_m or name_m.group(1) not in ids:
        continue
    name = name_m.group(1)
    rid_m = re.search(r'r:embed="(rId\d+)"', block)
    media = rid_to_media.get(rid_m.group(1)) if rid_m else None
    print(name, '->', media)
    if media:
        (OUT / f'{name}.png').write_bytes(z.read(media))
