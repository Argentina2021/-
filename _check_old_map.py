# -*- coding: utf-8 -*-
import re
import zipfile
from pathlib import Path

xlsx = Path(__file__).parent / '4dc1d8c545cd61f7b8065fc98acc5311.xlsx'
wanted = ['ID_1235DDCCEC6F46748FAC56087B40384B', 'ID_3677DA6FF803478BAE50337BFFC54128']

with zipfile.ZipFile(xlsx) as z:
    cell = z.read('xl/cellimages.xml').decode('utf-8')
    rels = z.read('xl/_rels/cellimages.xml.rels').decode('utf-8')

rid_to_media = {}
for m in re.finditer(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', rels):
    target = m.group(2)
    if target != 'NULL':
        rid_to_media[m.group(1)] = target if target.startswith('xl/') else f'xl/{target}'

ids = re.findall(r'name="([^"]+)"', cell)
rids = re.findall(r'r:embed="(rId\d+)"', cell)
print('ids', len(ids), 'rids', len(rids))

for w in wanted:
    if w in ids:
        i = ids.index(w)
        rid = rids[i] if i < len(rids) else None
        media = rid_to_media.get(rid) if rid else None
        print('OLD', w, 'index', i, '->', media)

for block in re.split(r'(?=<etc:cellImage>)', cell):
    name_m = re.search(r'name="([^"]+)"', block)
    if not name_m or name_m.group(1) not in wanted:
        continue
    rid_m = re.search(r'r:embed="(rId\d+)"', block)
    media = rid_to_media.get(rid_m.group(1)) if rid_m else None
    print('NEW', name_m.group(1), '->', media)
