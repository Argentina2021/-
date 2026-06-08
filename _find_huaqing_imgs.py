# -*- coding: utf-8 -*-
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

xlsx = Path('4dc1d8c545cd61f7b8065fc98acc5311.xlsx')
out = Path('_tmp_huaqing')
out.mkdir(exist_ok=True)

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
    media_to_id = {}
    for i, img_id in enumerate(ids):
        if i < len(rids):
            media = rid_to_media.get(rids[i])
            if media:
                media_to_id[media] = img_id

    for n in range(55, 70):
        for ext in ('png', 'jpeg'):
            p = f'xl/media/image{n}.{ext}'
            if p in z.namelist():
                data = z.read(p)
                (out / f'image{n}{Path(p).suffix}').write_bytes(data)
                print(f'image{n} -> {media_to_id.get(p, "NO ID")}')

def parse_dispimg(val):
    if pd.isna(val):
        return []
    return re.findall(r'DISPIMG\("([^"]+)"', str(val))

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
        if any(x in ('ID_A168E61171474557A1AEEC59BB12A5BA', 'ID_DF523CD92B8F4F5AAEE7150BD91BEF4E', 'ID_613CD75027FB475AAFBD7965169F3943') for x in imgs):
            print(f'{company} | {product} | {imgs}')
