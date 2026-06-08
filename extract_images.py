# -*- coding: utf-8 -*-
import json
import re
import zipfile
from pathlib import Path

import pandas as pd

path = Path(__file__).parent / '4dc1d8c545cd61f7b8065fc98acc5311.xlsx'
out_dir = Path(__file__).parent / 'extracted_images'
out_dir.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(path) as z:
    cellimages = z.read('xl/cellimages.xml').decode('utf-8')
    rels = z.read('xl/_rels/cellimages.xml.rels').decode('utf-8')
    media_files = [n for n in z.namelist() if re.match(r'xl/media/image\d+\.(png|jpe?g)$', n, re.I)]

    rid_to_media = {}
    for m in re.finditer(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', rels):
        target = m.group(2)
        if target == 'NULL':
            continue
        rid_to_media[m.group(1)] = target if target.startswith('xl/') else f'xl/{target}'

    id_to_file = {}
    for block in re.split(r'(?=<etc:cellImage>)', cellimages):
        name_m = re.search(r'name="([^"]+)"', block)
        rid_m = re.search(r'r:embed="(rId\d+)"', block)
        if not name_m or not rid_m:
            continue
        media = rid_to_media.get(rid_m.group(1))
        if media:
            id_to_file[name_m.group(1)] = media

    extracted = 0
    for img_id, media_path in id_to_file.items():
        data = z.read(media_path)
        safe_name = img_id.replace('/', '_') + '.png'
        (out_dir / safe_name).write_bytes(data)
        extracted += 1

print('Media PNG files in xlsx:', len(media_files))
print('cellimages ID mappings:', len(id_to_file))
print('Extracted by ID:', extracted)

def parse_dispimg(val):
    if pd.isna(val):
        return []
    return re.findall(r'DISPIMG\("([^"]+)"', str(val))

results = []
for sheet_idx, sheet_name in enumerate(['央企数科', '非央企数科']):
    df = pd.read_excel(path, sheet_name=sheet_idx)
    cols = list(df.columns)
    for row_i, row in df.iterrows():
        imgs = []
        for col in cols[2:]:
            imgs.extend(parse_dispimg(row[col]))
        imgs = list(dict.fromkeys(imgs))
        product = row[cols[0]] if pd.notna(row[cols[0]]) else None
        if imgs or product:
            mapped = [id_to_file.get(i) for i in imgs]
            results.append({
                'sheet': sheet_name,
                'row': row_i + 2,
                'product': product,
                'dispimg_ids': imgs,
                'media_files': mapped,
                'all_resolved': all(m is not None for m in mapped) if imgs else None,
            })

with_images = [r for r in results if r['dispimg_ids']]
resolved = [r for r in with_images if r['all_resolved']]
unresolved = [r for r in with_images if not r['all_resolved']]

print(f'Rows with DISPIMG: {len(with_images)}')
print(f'Fully resolved: {len(resolved)}')
print(f'Unresolved: {len(unresolved)}')
if unresolved[:3]:
    print('Unresolved samples:', json.dumps(unresolved[:3], ensure_ascii=False, indent=2))

report = {
    'can_read_images': len(unresolved) == 0,
    'media_png_count': len(media_files),
    'dispimg_mapping_count': len(id_to_file),
    'rows_with_images': len(with_images),
    'fully_resolved_rows': len(resolved),
    'unresolved_rows': len(unresolved),
}
Path(__file__).parent.joinpath('image_extract_report.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8'
)
print(json.dumps(report, ensure_ascii=False, indent=2))
