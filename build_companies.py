# -*- coding: utf-8 -*-
import json
import re
from pathlib import Path

import pandas as pd

XLSX = Path(__file__).parent / '4dc1d8c545cd61f7b8065fc98acc5311.xlsx'
ROOT = Path(__file__).parent
OUT_JSON = ROOT / 'companies.json'
OUT_JS = ROOT / 'companies.js'

PRODUCT_EXCLUSIONS = {}

# Excel DISPIMG IDs for these rows point at wrong media; use correct images from xlsx.
PRODUCT_IMAGE_OVERRIDES = {
    ('北京天创赛斯科技有限公司', '智慧 AED（自动体外除颤器）'): [
        'extracted_images/ID_B2A84942CE674298A43DABF1E5F9B900.png',
    ],
    ('北京天创赛斯科技有限公司', '智慧消防'): [
        'extracted_images/ID_30D7875D56894677AC74ABA6E613A202.png',
        'extracted_images/ID_81DB2C366B01404F9A97BFB8829C3DA4.png',
        'extracted_images/ID_02A2A16D3CF14ED89BFBA1888907D42D.png',
    ],
    ('雄安华清智言科技有限公司', '大模型工具链平台'): [
        'extracted_images/ID_A168E61171474557A1AEEC59BB12A5BA.png',
    ],
    ('雄安中文在线数字科技有限公司', '图知大模型'): [
        'extracted_images/connsiteY6.png',
        'extracted_images/connsiteX7.png',
    ],
    ('雄安兴元科技有限公司', '兴元百慧大模型'): [
        'extracted_images/connsiteX4.png',
    ],
    ('雄安兴元科技有限公司', '兴元兴智大模型'): [
        'extracted_images/connsiteY4.png',
    ],
    ('中国电信股份有限公司河北雄安新区分公司', '“雄小农”AI农业大模型'): [
        'extracted_images/connsiteY3.png',
        'extracted_images/connsiteX6.png',
    ],
    ('中禾科技（雄安）有限公司', '金融多智能体问答系统'): [
        'extracted_images/connsiteX3.png',
    ],
    ('中电信数字城市科技有限公司', '医疗导诊大模型'): [
        'extracted_images/connsiteX0.png',
    ],
    ('中电信数字城市科技有限公司', '交管大模型'): [
        'extracted_images/connsiteX1.png',
    ],
    ('雄安万鼎空间数字科技有限公司', '数字园区三维可视化运管平台'): [
        'extracted_images/connsiteY7.png',
        'extracted_images/connsiteY8.png',
        'extracted_images/wanding_park_land.png',
        'extracted_images/wanding_park_building.png',
    ],
    ('雄安安影科技有限公司', 'Nirvana多模态大模型'): [
        'extracted_images/connsiteY1.png',
        'extracted_images/connsiteX2.png',
        'extracted_images/connsiteY2.png',
    ],
    ('河北雄安英诺尔物联科技有限公司', 'XMINNOV 英诺尔RISC-V 架构 RFID 多模态数据采集终端'): [
        'extracted_images/ID_18E67245104B4064A557BFC72CD04736.png',
        'extracted_images/ID_85A2700C3D6E4357BA6F083A2E2176B4.png',
    ],
    ('北京翌特视讯科技有限公司', '无人机无线电监测压制一体设备'): [
        'extracted_images/ID_D14E2F6B88E246FA9D214AA47AD38603.png',
    ],
    ('北京翌特视讯科技有限公司', 'ROV水下重点工程巡检机器人'): [
        'extracted_images/ID_B08928AAD1CB4A33BEEC1A8F6847855A.png',
    ],
    ('北京翌特视讯科技有限公司', '楼宇清洗无人机'): [
        'extracted_images/ID_3CC139D23F9C4073B4643272889EB8EA.png',
    ],
    ('北京翌特视讯科技有限公司', '北斗大脑低空安全监管平台V1.0'): [
        'extracted_images/ID_C438933CC74E4242919BDE6D5C2FED62.png',
        'extracted_images/ID_D00557E8BEB5497A929B00531835114D.png',
    ],
    ('北京翌特视讯科技有限公司', '翌特低空飞行器监测系统'): [
        'extracted_images/ID_198AC6F4EEB242F4AE8804B9EB80F079.png',
    ],
    ('芯昇科技有限公司', '摄像机'): [
        'extracted_images/xinsheng_camera.png',
    ],
    ('芯昇科技有限公司', '智能表计'): [
        'extracted_images/xinsheng_smart_meter.png',
    ],
    ('芯昇科技有限公司', '城市生命线-燃气专项'): [
        'extracted_images/xinsheng_gas_lifeline.png',
    ],
    ('中国铁塔（雄安）科技创新中心', '时空服务运营平台'): [
        'extracted_images/tieta_platform.png',
    ],
    ('中国铁塔（雄安）科技创新中心', '小塔地图APP'): [
        'extracted_images/tieta_map_app.png',
    ],
    ('中国雄安集团数字城市科技有限公司', '“明瞰”视觉大模型'): [
        'extracted_images/mingkan_vision.png',
    ],
    ('雄安威赛博智能科技有限公司', '工业智算系列产品'): [
        'extracted_images/ID_0829407345CD4AADBD7E33463512A958.png',
    ],
}

# Excel lists some companies again later on the sheet; place after this anchor.
COMPANY_INSERT_AFTER = {
    '雄安华清智言科技有限公司': '中禾科技（雄安）有限公司',
}

# When a company reappears later on the sheet, keep only these products.
COMPANY_PRODUCTS_ONLY = {
    '雄安华清智言科技有限公司': ['大模型工具链平台'],
}


def filter_company_products(companies):
    for company in companies:
        only = COMPANY_PRODUCTS_ONLY.get(company['name'])
        if only:
            company['products'] = [p for p in company['products'] if p['name'] in only]
    return companies


def apply_company_insert_order(companies):
    by_name = {c['name']: c for c in companies}
    names = [c['name'] for c in companies]
    for company, after in COMPANY_INSERT_AFTER.items():
        if company not in by_name or after not in by_name:
            continue
        if company in names:
            names.remove(company)
        names.insert(names.index(after) + 1, company)
    return [by_name[n] for n in names]


def parse_dispimg(val):
    if pd.isna(val):
        return []
    return re.findall(r'DISPIMG\("([^"]+)"', str(val))


def find_contact(row, cols):
    for col in cols[4:]:
        val = row[col]
        if pd.isna(val):
            continue
        text = str(val).strip()
        if not text or 'DISPIMG' in text:
            continue
        if '经理' in text or '联系' in text or '@' in text or re.search(r'1\d{10}', text):
            return text
    return ''


def find_images(row, cols):
    images = []
    for col in cols[2:]:
        images.extend(parse_dispimg(row[col]))
    unique = []
    for img_id in images:
        if img_id not in unique:
            unique.append(img_id)
    return [f'extracted_images/{img_id}.png' for img_id in unique]


company_map = {}

for sheet in ['央企数科', '非央企数科']:
    df = pd.read_excel(XLSX, sheet_name=sheet)
    cols = list(df.columns)
    current = None
    for _, row in df.iterrows():
        if pd.notna(row[cols[1]]):
            current = str(row[cols[1]]).strip()
        product = row[cols[0]] if pd.notna(row[cols[0]]) else None
        intro = row[cols[3]] if pd.notna(row[cols[3]]) else ''
        if not current:
            continue
        for part in current.split('/'):
            name = part.strip()
            if not name:
                continue
            if name not in company_map:
                company_map[name] = {'name': name, 'sheet': sheet, 'products': []}
            if product and str(product).strip():
                product_name = str(product).strip()
                if (name, product_name) in PRODUCT_EXCLUSIONS:
                    continue
                item = {
                    'name': product_name,
                    'intro': str(intro).strip() if pd.notna(intro) else '',
                }
                contact = find_contact(row, cols)
                images = find_images(row, cols)
                override = PRODUCT_IMAGE_OVERRIDES.get((name, item['name']))
                if override:
                    images = override
                if contact:
                    item['contact'] = contact
                if images:
                    item['images'] = images
                company_map[name]['products'].append(item)
            elif company_map[name]['products']:
                last = company_map[name]['products'][-1]
                if (name, last['name']) in PRODUCT_IMAGE_OVERRIDES:
                    continue
                extra_images = find_images(row, cols)
                if extra_images:
                    merged = list(last.get('images', []))
                    for path in extra_images:
                        if path not in merged:
                            merged.append(path)
                    last['images'] = merged

companies = apply_company_insert_order(filter_company_products(list(company_map.values())))
OUT_JSON.write_text(json.dumps(companies, ensure_ascii=False, indent=2), encoding='utf-8')
OUT_JS.write_text(
    'const COMPANIES = ' + json.dumps(companies, ensure_ascii=False, indent=2) + ';\n',
    encoding='utf-8',
)

with_contact = sum(1 for c in companies for p in c['products'] if p.get('contact'))
with_images = sum(1 for c in companies for p in c['products'] if p.get('images'))
multi_images = sum(
    1 for c in companies for p in c['products'] if len(p.get('images', [])) > 1
)
print(f'Exported {len(companies)} companies')
print(f'Products with contact: {with_contact}')
print(f'Products with images: {with_images}')
print(f'Products with multiple images: {multi_images}')
