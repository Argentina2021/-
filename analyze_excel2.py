# -*- coding: utf-8 -*-
import json
from collections import Counter, defaultdict

with open(r'e:\雄安科技展\百家数科\excel_data.json', encoding='utf-8') as f:
    data = json.load(f)

keywords = {
    'AI/大模型': ['AI', '大模型', '智能体', 'DeepSeek', 'MaaS', 'TopASK', 'LimiX', '数字员工'],
    '数据/可信空间': ['数据', '可信', '空间', '隐私', '区块链'],
    '安全/合规': ['安全', '合规', 'SOC', 'ABIS', '生物识别', '虹膜', '指纹', '网安', 'TopASK'],
    '芯片/硬件': ['芯片', 'RISC-V', 'SIM', 'SoC', 'MCU', '模组', 'POI', '北斗', '终端', '工控机', 'AIBOX'],
    '城市/政务': ['城市', '政务', '12345', 'IOC', 'CIM', '城管', '生命线', '体测'],
    '工业/制造': ['工业', '制造', 'MOM', 'MES', '石油', '巡检', '钢铁', '翼制'],
    '交通/低空/车路': ['交通', '低空', '车路', '停车', '北斗', '信号机', '边缘小站'],
    '医疗/健康': ['医疗', '医院', 'HIS', '导诊', 'AED', '出血', 'Drug'],
    '办公/协同': ['办公', 'OA', 'OneOffice', '协同', 'TopDC'],
    '金融/供应链': ['金融', '供应链', '征信', '信创', '云合链'],
    '能源/双碳/燃气': ['能源', '双碳', '碳', '燃气', '用电', '绿电'],
    '教育/培训': ['教育', '培训', '学习', '美术'],
    '物联网/感知': ['物联网', '传感器', '表计', '监测', '无人机', '机器人'],
    '气象/环境': ['气象', '风清', '风衡', '风源', '风和'],
    '物业/园区/BIM': ['物业', '园区', 'BIM', '楼宇', '智慧楼'],
}

def categorize(name):
    if not name:
        return ['其他']
    cats = []
    for cat, kws in keywords.items():
        if any(k in str(name) for k in kws):
            cats.append(cat)
    return cats if cats else ['其他']

def analyze_products(products, label):
    cat_counter = Counter()
    company_counter = Counter()
    short_intro = []
    no_company_explicit = []
    
    for p in products:
        for c in categorize(p['product']):
            cat_counter[c] += 1
        company_counter[p['company']] += 1
        if p['intro_len'] < 50:
            short_intro.append(p)
        if not p.get('company'):
            no_company_explicit.append(p)
    
    return {
        'label': label,
        'total': len(products),
        'categories': dict(cat_counter.most_common()),
        'top_companies': company_counter.most_common(10),
        'short_intro_count': len(short_intro),
        'short_intro_samples': [{'product': x['product'], 'len': x['intro_len']} for x in short_intro[:8]],
        'avg_intro_len': round(sum(p['intro_len'] for p in products) / len(products)),
    }

s1 = analyze_products(data['products_sheet1'], '央企数科')
s2 = analyze_products(data['products_sheet2'], '非央企数科')

# Combined unique products
all_products = data['products_sheet1'] + data['products_sheet2']
all_names = [p['product'] for p in all_products if p['product']]
unique_names = set(all_names)

# Data quality
empty_rows_sheet1 = 107 - 99  # from shape
issues = []
for p in data['products_sheet1']:
    if 'DISPIMG' in str(p.get('intro_preview', '')):
        issues.append('简介列含图片公式')
        break

multi_image_rows = sum(1 for p in data['products_sheet1'] if p['intro_len'] == 0)

report = {
    'summary': {
        'sheets': data['sheet_names'],
        'sheet1_products': s1['total'],
        'sheet2_products': s2['total'],
        'total_products': s1['total'] + s2['total'],
        'unique_product_names': len(unique_names),
        'companies_sheet1': len(data['companies_sheet1']),
        'companies_sheet2': len(set(p['company'] for p in data['products_sheet2'])),
    },
    'sheet1': s1,
    'sheet2': s2,
    'structure': {
        'columns': ['产品名称', '企业名称', '图片', '简介', 'Unnamed:4-6(额外图片列)'],
        'image_format': 'WPS DISPIMG 嵌入图片公式',
        'company_fill_pattern': '同一企业多个产品时，仅首行填写企业名称，后续行留空（已通过向下填充解析）',
    },
    'sheet1_company_products': dict(Counter(p['company'] for p in data['products_sheet1']).most_common()),
    'sheet2_company_products': dict(Counter(p['company'] for p in data['products_sheet2']).most_common()),
}

with open(r'e:\雄安科技展\百家数科\excel_report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(json.dumps(report, ensure_ascii=False, indent=2))
