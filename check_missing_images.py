# -*- coding: utf-8 -*-
import json
import re
import zipfile
from pathlib import Path

import pandas as pd

path = Path(r'c:\Users\zengy\xwechat_files\wxid_f0l3v302nftx12_75fe\msg\file\2026-05\4dc1d8c545cd61f7b8065fc98acc5311.xlsx')

with zipfile.ZipFile(path) as z:
    cellimages = z.read('xl/cellimages.xml').decode('utf-8')
    rels = z.read('xl/_rels/cellimages.xml.rels').decode('utf-8')

ids = set(re.findall(r'name="([^"]+)"', cellimages))
rid_to_media = {}
for m in re.finditer(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', rels):
    target = m.group(2)
    if target != 'NULL':
        rid_to_media[m.group(1)] = target if target.startswith('xl/') else f'xl/{target}'
rids = re.findall(r'r:embed="(rId\d+)"', cellimages)
id_list = re.findall(r'name="([^"]+)"', cellimages)
id_to_file = {id_list[i]: rid_to_media.get(rids[i]) for i in range(min(len(id_list), len(rids)))}

all_dispimg = set()
unresolved = []
for sheet_idx, sheet_name in enumerate(['央企数科', '非央企数科']):
    df = pd.read_excel(path, sheet_name=sheet_idx)
    for row_i, row in df.iterrows():
        for col in df.columns[2:7]:
            val = row[col]
            if pd.isna(val):
                continue
            for img_id in re.findall(r'DISPIMG\("([^"]+)"', str(val)):
                all_dispimg.add(img_id)
                if img_id not in id_to_file or not id_to_file[img_id]:
                    unresolved.append({
                        'sheet': sheet_name,
                        'row': row_i + 2,
                        'product': row[df.columns[0]],
                        'id': img_id,
                    })

print('Unique DISPIMG IDs in cells:', len(all_dispimg))
print('IDs in cellimages.xml:', len(ids))
print('Missing from cellimages:', len(all_dispimg - ids))
print('Missing IDs:', sorted(all_dispimg - ids))
print('Unresolved entries:', len(unresolved))
for u in unresolved:
    print(f"  {u['sheet']} row{u['row']} {u['product']} -> {u['id']}")

# Check NULL external
null_rids = re.findall(r'Id="(rId\d+)"[^>]*Target="NULL"', rels)
print('NULL external rIds:', null_rids)
if null_rids:
    for i, rid in enumerate(rids):
        if rid in null_rids:
            print(f'  NULL maps to image id: {id_list[i]}')

report = {
    'total_dispimg_ids_in_cells': len(all_dispimg),
    'total_cellimages_mappings': len(ids),
    'missing_ids': sorted(all_dispimg - ids),
    'unresolved_count': len(unresolved),
    'extractable_count': len(all_dispimg & ids),
    'success_rate': f'{len(all_dispimg & ids)}/{len(all_dispimg)}',
}
Path(r'e:\雄安科技展\百家数科\image_detail_report.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8'
)
print(json.dumps(report, ensure_ascii=False, indent=2))
