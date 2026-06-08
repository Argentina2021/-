# -*- coding: utf-8 -*-
import re
import zipfile
from pathlib import Path

xlsx = Path('4dc1d8c545cd61f7b8065fc98acc5311.xlsx')
with zipfile.ZipFile(xlsx) as z:
    names = z.namelist()
    for n in names:
        if 'drawing' in n.lower() and '非央企' not in n and 'sheet' in n:
            pass
    # find sheet for 非央企数科
    wb = z.read('xl/workbook.xml').decode('utf-8')
    rels = z.read('xl/_rels/workbook.xml.rels').decode('utf-8')
    sheets = re.findall(r'name="([^"]+)"[^>]*r:id="(rId\d+)"', wb)
    rid_map = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', rels))
    target = None
    for name, rid in sheets:
        if '非央企' in name:
            target = rid_map.get(rid, '').lstrip('/')
            print('sheet', name, '->', target)
    if not target:
        raise SystemExit('no sheet')

    sheet_path = target if target.startswith('xl/') else f'xl/{target}'
    sheet = z.read(sheet_path).decode('utf-8')
    sheet_rels_path = sheet_path.replace('worksheets/', 'worksheets/_rels/') + '.rels'
    srels = z.read(sheet_rels_path).decode('utf-8')
    for m in re.finditer(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', srels):
        if 'drawing' in m.group(2):
            print('drawing rel', m.group(1), m.group(2))
