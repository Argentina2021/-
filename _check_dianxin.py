# -*- coding: utf-8 -*-
import re
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
XLSX = ROOT / '4dc1d8c545cd61f7b8065fc98acc5311.xlsx'

products_wanted = {'医疗导诊大模型', '交管大模型'}

df = pd.read_excel(XLSX, sheet_name='央企数科')
cols = list(df.columns)
current = None
for i, row in df.iterrows():
    if pd.notna(row[cols[1]]):
        current = str(row[cols[1]]).strip()
    product = str(row[cols[0]]).strip() if pd.notna(row[cols[0]]) else ''
    if product not in products_wanted:
        continue
    imgs = []
    for col in cols[2:]:
        val = row[col]
        if pd.notna(val):
            imgs.extend(re.findall(r'DISPIMG\("([^"]+)"', str(val)))
    print('row', i + 2, product, '->', imgs)

with zipfile.ZipFile(XLSX) as z:
    cell = z.read('xl/cellimages.xml').decode('utf-8')
    rels = z.read('xl/_rels/cellimages.xml.rels').decode('utf-8')

rid_to_media = {}
for m in re.finditer(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', rels):
    target = m.group(2)
    if target != 'NULL':
        rid_to_media[m.group(1)] = target if target.startswith('xl/') else f'xl/{target}'

ids_wanted = {
    'ID_1235DDCCEC6F46748FAC56087B40384B',
    'ID_3677DA6FF803478BAE50337BFFC54128',
    'ID_B6C7768298974C11B92E3879F6631B6B',
}

for block in re.split(r'(?=<etc:cellImage>)', cell):
    name_m = re.search(r'name="([^"]+)"', block)
    if not name_m:
        continue
    name = name_m.group(1)
    descr_m = re.search(r'descr="([^"]*)"', block)
    descr = descr_m.group(1) if descr_m else ''
    rid_m = re.search(r'r:embed="(rId\d+)"', block)
    if name in ids_wanted or any(k in descr for k in ('导诊', '交管', '医疗', '交通', '66bf49', 'a584b8')):
        media = rid_to_media.get(rid_m.group(1)) if rid_m else None
        print('cellimage', name, 'descr=', descr, 'media=', media)
