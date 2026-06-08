# -*- coding: utf-8 -*-
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent
with zipfile.ZipFile(ROOT / '4dc1d8c545cd61f7b8065fc98acc5311.xlsx') as z:
    cell = z.read('xl/cellimages.xml').decode('utf-8')

keywords = ('导诊', '交管', '医疗', '交通', '明瞰', '66bf', 'a584b8', 'connsite')
for block in re.split(r'(?=<etc:cellImage>)', cell):
    name_m = re.search(r'name="([^"]+)"', block)
    if not name_m:
        continue
    name = name_m.group(1)
    descr_m = re.search(r'descr="([^"]*)"', block)
    descr = descr_m.group(1) if descr_m else ''
    blob = name + descr
    if any(k in blob for k in keywords):
        rid_m = re.search(r'r:embed="(rId\d+)"', block)
        print(name, '|', descr, '|', rid_m.group(1) if rid_m else 'no embed')
