# -*- coding: utf-8 -*-
import json
from pathlib import Path

ROOT = Path(__file__).parent
companies = json.loads((ROOT / 'companies.json').read_text(encoding='utf-8'))
mapping = {}
for company in companies:
    for product in company.get('products', []):
        images = product.get('images') or []
        if images:
            mapping[product['name']] = images[0]

(ROOT / 'product_images.js').write_text(
    'const PRODUCT_IMAGES = ' + json.dumps(mapping, ensure_ascii=False, indent=2) + ';\n',
    encoding='utf-8',
)
print(f'Mapped {len(mapping)} products (first image)')
