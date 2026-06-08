# -*- coding: utf-8 -*-
import re
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

with zipfile.ZipFile(Path(__file__).parent / '4dc1d8c545cd61f7b8065fc98acc5311.xlsx') as z:
    cell = z.read('xl/cellimages.xml').decode('utf-8')

keys = ['导诊', '交管', '医疗', '交通', '医院', '大模型', '织意', '可信', '城市', '园区', '铁塔', '时空', 'One', '政务']
for block in re.split(r'(?=<etc:cellImage>)', cell):
    name_m = re.search(r'name="([^"]+)"', block)
    descr_m = re.search(r'descr="([^"]+)"', block)
    if not name_m or not descr_m or not descr_m.group(1):
        continue
    line = f"{name_m.group(1)} | {descr_m.group(1)}"
    if any(k in line for k in keys):
        print(line)
