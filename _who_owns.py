# -*- coding: utf-8 -*-
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

def parse_dispimg(val):
    if pd.isna(val):
        return []
    return re.findall(r'DISPIMG\("([^"]+)"', str(val))

xlsx = Path('4dc1d8c545cd61f7b8065fc98acc5311.xlsx')

with zipfile.ZipFile(xlsx) as z:
    cellimages = z.read('xl/cellimages.xml').decode('utf-8')
    rels = z.read('xl/_rels/cellimages.xml.rels').decode('utf-8')
    rid_to_media = {}
    for m in re.finditer(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', rels):
        target = m.group(2)
        if target == 'NULL':
            continue
        rid_to_media[m.group(1)] = target if target.startswith('xl/') else f'xl/{target}'
    ids = re.findall(r'name="([^"]+)"', cellimages)
    rids = re.findall(r'r:embed="(rId\d+)"', cellimages)
    id_to_media = {}
    media_to_id = {}
    for i, img_id in enumerate(ids):
        if i < len(rids):
            media = rid_to_media.get(rids[i])
            if media:
                id_to_media[img_id] = media
                media_to_id[media] = img_id

for media in ['xl/media/image62.png', 'xl/media/image57.png', 'xl/media/image186.png', 'xl/media/image187.png']:
    print(f'{media} -> {media_to_id.get(media)}')

targets = {media_to_id.get(m) for m in ['xl/media/image62.png', 'xl/media/image57.png'] if media_to_id.get(m)}

for sheet in ['央企数科', '非央企数科']:
    df = pd.read_excel(xlsx, sheet_name=sheet)
    cols = list(df.columns)
    company = None
    for _, row in df.iterrows():
        if pd.notna(row[cols[1]]):
            company = str(row[cols[1]]).strip()
        product = row[cols[0]] if pd.notna(row[cols[0]]) else None
        if not product:
            continue
        imgs = []
        for col in cols[2:]:
            imgs.extend(parse_dispimg(row[col]))
        if any(i in targets for i in imgs):
            print(f'{company} | {product} | {imgs}')
