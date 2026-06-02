# -*- coding: utf-8 -*-
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

path = Path(r'c:\Users\zengy\xwechat_files\wxid_f0l3v302nftx12_75fe\msg\file\2026-05\4dc1d8c545cd61f7b8065fc98acc5311.xlsx')

XDR = '{http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
ETC = '{http://www.wps.cn/officeDocument/2017/etCustomData}'

with zipfile.ZipFile(path) as z:
    root = ET.fromstring(z.read('xl/cellimages.xml'))
    rels = z.read('xl/_rels/cellimages.xml.rels').decode()

rid_to_media = {}
for m in re.finditer(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', rels):
    t = m.group(2)
    if t != 'NULL':
        rid_to_media[m.group(1)] = 'xl/' + t if not t.startswith('xl/') else t

id_to_file = {}
null_ids = []
for ci in root.iter(f'{ETC}cellImage'):
    name_el = ci.find(f'.//{XDR}cNvPr')
    blip = ci.find(f'.//{A}blip')
    if name_el is None:
        continue
    img_id = name_el.get('name')
    rid = blip.get(f'{R}embed') if blip is not None else None
    media = rid_to_media.get(rid) if rid else None
    id_to_file[img_id] = media
    if not media:
        null_ids.append({'id': img_id, 'rid': rid})

import pandas as pd
all_dispimg = []
for sheet_idx in [0, 1]:
    df = pd.read_excel(path, sheet_name=sheet_idx)
    for row_i, row in df.iterrows():
        for col in df.columns[2:7]:
            val = row[col]
            if pd.isna(val):
                continue
            for img_id in re.findall(r'DISPIMG\("([^"]+)"', str(val)):
                all_dispimg.append(img_id)

unique = set(all_dispimg)
resolved = [i for i in unique if id_to_file.get(i)]
unresolved = [i for i in unique if not id_to_file.get(i)]

report = {
    'total_image_files_in_xlsx': len([n for n in zipfile.ZipFile(path).namelist() if re.search(r'xl/media/image\d+\.', n)]),
    'cellimages_entries': len(id_to_file),
    'unique_dispimg_in_table': len(unique),
    'resolved': len(resolved),
    'unresolved': len(unresolved),
    'unresolved_ids': unresolved,
    'null_mapping_entries': null_ids[:5],
    'null_mapping_count': len(null_ids),
}
print(json.dumps(report, ensure_ascii=False, indent=2))
