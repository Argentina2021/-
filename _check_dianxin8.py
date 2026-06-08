# -*- coding: utf-8 -*-
import re
import zipfile
from pathlib import Path

with zipfile.ZipFile(Path(__file__).parent / '4dc1d8c545cd61f7b8065fc98acc5311.xlsx') as z:
    cell = z.read('xl/cellimages.xml').decode('utf-8')

for block in re.split(r'(?=<etc:cellImage>)', cell):
    name_m = re.search(r'name="([^"]+)"', block)
    descr_m = re.search(r'descr="([^"]+)"', block)
    if not name_m or not descr_m or not descr_m.group(1):
        continue
    print(name_m.group(1), '|', descr_m.group(1))
