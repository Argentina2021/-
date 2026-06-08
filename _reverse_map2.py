# -*- coding: utf-8 -*-
import re
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

xlsx = Path(__file__).parent / '4dc1d8c545cd61f7b8065fc98acc5311.xlsx'

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

# old index map
id_to_media_old = {}
media_to_id_old = {}
for i, img_id in enumerate(ids):
    if i < len(rids):
        media = rid_to_media.get(rids[i])
        if media:
            id_to_media_old[img_id] = media
            media_to_id_old[media] = img_id

# block map
id_to_media_new = {}
for block in re.split(r'(?=<etc:cellImage>)', cell):
    name_m = re.search(r'name="([^"]+)"', block)
    rid_m = re.search(r'r:embed="(rId\d+)"', block)
    if name_m and rid_m:
        media = rid_to_media.get(rid_m.group(1))
        if media:
            id_to_media_new[name_m.group(1)] = media

for media in ['xl/media/image158.png', 'xl/media/image160.png', 'xl/media/image174.png', 'xl/media/image176.png', 'xl/media/image178.png']:
    print(media)
    print('  OLD id:', media_to_id_old.get(media))
    print('  NEW ids:', [k for k, v in id_to_media_new.items() if v == media])

print('\nID_1235 old', id_to_media_old.get('ID_1235DDCCEC6F46748FAC56087B40384B'))
print('ID_1235 new', id_to_media_new.get('ID_1235DDCCEC6F46748FAC56087B40384B'))
print('ID_3677 old', id_to_media_old.get('ID_3677DA6FF803478BAE50337BFFC54128'))
print('ID_3677 new', id_to_media_new.get('ID_3677DA6FF803478BAE50337BFFC54128'))
