# -*- coding: utf-8 -*-
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

XDR = '{http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'

xlsx = Path(__file__).parent / '4dc1d8c545cd61f7b8065fc98acc5311.xlsx'
target_rows = {67, 68, 69, 70}  # excel rows 68-71 (0-based)

with zipfile.ZipFile(xlsx) as z:
    wb = z.read('xl/workbook.xml').decode('utf-8')
    rels = z.read('xl/_rels/workbook.xml.rels').decode('utf-8')
    sheets = re.findall(r'name="([^"]+)"[^>]*r:id="(rId\d+)"', wb)
    rid_map = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', rels))
    sheet_path = None
    for name, rid in sheets:
        if name == '央企数科':
            t = rid_map.get(rid, '').lstrip('/')
            sheet_path = t if t.startswith('xl/') else f'xl/{t}'
            break

    sheet_name = Path(sheet_path).name
    srels_path = f'xl/worksheets/_rels/{sheet_name}.rels'
    srels = z.read(srels_path).decode('utf-8')
    drawing_target = None
    for m in re.finditer(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', srels):
        if 'drawing' in m.group(2):
            drawing_target = m.group(2).lstrip('/')
            if not drawing_target.startswith('xl/'):
                drawing_target = f'xl/{drawing_target}'
            break

    print('sheet:', sheet_path)
    print('drawing:', drawing_target)

    drels_path = drawing_target.replace('drawings/', 'drawings/_rels/') + '.rels'
    drels = z.read(drels_path).decode('utf-8')
    media_map = {}
    for m in re.finditer(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', drels):
        t = m.group(2)
        media_map[m.group(1)] = t if t.startswith('../') else t

    root = ET.fromstring(z.read(drawing_target))
    for anchor in root:
        tag = anchor.tag.split('}')[-1]
        if tag not in ('twoCellAnchor', 'oneCellAnchor'):
            continue
        from_el = anchor.find(f'{XDR}from')
        if from_el is None:
            continue
        row = int(from_el.find(f'{XDR}row').text)
        col = int(from_el.find(f'{XDR}col').text)
        if row not in target_rows:
            continue
        blip = anchor.find(f'.//{A}blip')
        name_el = anchor.find(f'.//{XDR}cNvPr')
        embed = blip.get(f'{R}embed') if blip is not None else None
        media = media_map.get(embed, '')
        name = name_el.get('name') if name_el is not None else ''
        print(f'row={row+1} col={col} name={name!r} media={media}')
