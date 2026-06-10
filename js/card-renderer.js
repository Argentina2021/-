/**
 * 企业产品卡片 HTML 渲染
 */
(function (global) {
  const COMPANY_COLUMNS = {
    '雄安国创中心科技有限公司': [
      ['闻识一号模组', '基于运动想象脑控技术的教育产品', '雄安国创天巡平台'],
      ['智冷魔方AIBOX产品', '基于RISC-V和开源鸿蒙操作系统的工业控制计算机', '生物可信认证防护系统', '“数字淀乡”时空一体化平台'],
    ],
    '洞见智慧科技（北京）有限公司': [
      ['洞见密态计算一体机', '洞见可信数据空间平台', '“见智 ”安全可信大模型'],
      ['洞见可信数据空间一体机', '洞见隐私计算平台'],
    ],
    '北京天创赛斯科技有限公司': [
      ['NB-loT模组', '智慧 AED（自动体外除颤器）'],
      ['基于PUF技术微标识安全芯片', '智慧消防'],
    ],
    '雄安安影科技有限公司': [
      ['便携式颅脑出血检测分析仪', '医学多模态问答与诊断解释大模型'],
      ['Nirvana多模态大模型'],
    ],
    '河北雄安星程智慧物业科技有限公司': [
      ['星程智慧物业（社区版）'],
      ['智慧运营', '建筑物联网', '智慧物业（商业版）'],
    ],
    '中电信数字城市科技有限公司': [
      ['医疗导诊大模型', '电信数城可信数据空间', '城市运行管理服务平台'],
      ['交管大模型', '织意智能体平台', '空地协同一体化服务平台', '智慧楼宇/智慧园区', '政务服务热线', '翼制造生产运营管理平台'],
    ],
    '中国铁塔（雄安）科技创新中心': [
      ['北斗室内定位基站', '23频全网多功能POI'],
      ['时空服务运营平台', '小塔地图APP'],
    ],
    '北京眼神科技有限公司': [
      ['虹膜毒检仪', '人脸虹膜面部融合识别一体机', '虹膜锁', '手指多模态识别仪'],
      ['心理行为分析产品', 'ABIS多模态生物识别统一平台'],
    ],
  };

  const PRODUCT_LAYOUT = {
    '闻识一号模组': 'side',
    '基于运动想象脑控技术的教育产品': 'side',
    '智冷魔方AIBOX产品': 'side',
    '生物可信认证防护系统': 'side',
    '雄安国创天巡平台': 'stack',
    '基于RISC-V和开源鸿蒙操作系统的工业控制计算机': 'stack',
    '“数字淀乡”时空一体化平台': 'stack',
  };

  const PRODUCT_IMAGE_ROTATE = new Set(['闻识一号模组']);

  const PRODUCT_IMAGE_COMPACT = new Set([
    '基于PUF技术微标识安全芯片',
    '三维可视化料层监测装置',
    'RISC-V内核超级SIM芯片CC2560A',
    'RISC-V内核IoT-NTN卫星通信芯片CM6620N',
    'RISC-V内核北斗短报文通信芯片CM3510',
    '多模态人脸虹膜面板机',
    '人脸虹膜面部融合识别一体机',
    '手指多模态识别仪',
    '虹膜毒检仪',
    '虹膜锁',
    'RISC-V AI训推一体机（安算昊辰 2524A）',
    '基于RISC-V的可信安全计算芯片',
    '安算可信安全高精度定位模组（FusionSecure-U）',
    '微型工控机',
  ]);

  const PRODUCT_IMAGE_COMPACT_SCALE = { '三维可视化料层监测装置': 2 };

  const PRODUCT_IMAGE_SCALE = {
    '卫星通讯芯片': 0.837,
    '北斗室内定位基站': 0.707,
  };

  const PRODUCT_IMAGE_UNIFORM = new Set(['边缘小站', 'AI信号机']);
  const PRODUCT_IMAGE_UNIFORM_HEIGHT = 200;

  const PRODUCT_IMAGES_ROW = new Set([
    'XMINNOV 英诺尔RISC-V 架构 RFID 多模态数据采集终端',
    '图知大模型',
  ]);

  const PRODUCT_IMAGES_ROW_AFTER = { '智慧消防': 1 };

  const PRODUCT_TITLE_SM = new Set([
    '雄安国创天巡平台',
    '生物可信认证防护系统',
    '基于RISC-V和开源鸿蒙操作系统的工业控制计算机',
    '“数字淀乡”时空一体化平台',
  ]);

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function formatIntro(intro) {
    if (!intro) return '';
    const lines = intro.split('\n').map((line) => line.trim()).filter(Boolean);
    if (lines.length <= 1) return `<p>${escapeHtml(intro)}</p>`;
    return lines.map((line) => `<p>${escapeHtml(line)}</p>`).join('');
  }

  function splitProducts(products) {
    const left = [];
    const right = [];
    products.forEach((product, index) => {
      (index % 2 === 0 ? left : right).push(product);
    });
    return [left, right];
  }

  function getProductLayout(name) {
    return PRODUCT_LAYOUT[name] || 'stack';
  }

  function getProductImages(product) {
    if (product.images && product.images.length) return product.images;
    const fallback = (typeof PRODUCT_IMAGES !== 'undefined' ? PRODUCT_IMAGES : global.PRODUCT_IMAGES)?.[product.name];
    return fallback ? [fallback] : [];
  }

  function renderProductImages(product, layout) {
    const images = getProductImages(product);
    if (!images.length) return '';

    const renderOne = (src, index) => {
      const rotate = layout === 'side' && PRODUCT_IMAGE_ROTATE.has(product.name) && index === 0;
      const compact = layout === 'stack' && PRODUCT_IMAGE_COMPACT.has(product.name);
      const uniform = layout === 'stack' && PRODUCT_IMAGE_UNIFORM.has(product.name);
      const compactScale = layout === 'stack' ? PRODUCT_IMAGE_COMPACT_SCALE[product.name] : null;
      const scale = layout === 'stack' ? PRODUCT_IMAGE_SCALE[product.name] : null;
      const cls = [
        'product-image',
        rotate ? 'product-image-rotate' : '',
        compact ? 'product-image-compact' : '',
        uniform ? 'product-image-uniform' : '',
        scale ? 'product-image-scaled' : '',
      ].filter(Boolean).join(' ');
      const scaleVars = [];
      if (compactScale) scaleVars.push(`--compact-scale-factor: ${compactScale}`);
      if (uniform) scaleVars.push(`--uniform-img-height: ${PRODUCT_IMAGE_UNIFORM_HEIGHT}px`);
      if (scale) scaleVars.push(`--img-scale-factor: ${scale}`);
      const scaleStyle = scaleVars.length ? ` style="${scaleVars.join('; ')}"` : '';
      return `<div class="${cls}"${scaleStyle}><img src="${escapeHtml(src)}" alt=""></div>`;
    };

    if (layout === 'single' && images.length > 1 && PRODUCT_IMAGES_ROW.has(product.name)) {
      return `<div class="product-images-row">${images.map(renderOne).join('')}</div>`;
    }

    const rowAfter = layout === 'stack' ? PRODUCT_IMAGES_ROW_AFTER[product.name] : null;
    if (rowAfter != null && images.length > rowAfter) {
      const head = images.slice(0, rowAfter).map((src, index) => renderOne(src, index)).join('');
      const tail = images.slice(rowAfter);
      const wrap = tail.length > 2 ? ' product-images-row-wrap' : '';
      const row = `<div class="product-images-row${wrap}">${tail.map((src, index) => renderOne(src, rowAfter + index)).join('')}</div>`;
      return head + row;
    }

    return images.map(renderOne).join('');
  }

  function renderProductBlock(product, options = {}) {
    const { single = false, company = '' } = options;
    const layout = single ? 'single' : getProductLayout(product.name);
    const contact = product.contact || '';
    const titleClass = PRODUCT_TITLE_SM.has(product.name) ? 'product-title product-title-sm' : 'product-title';
    const imageHtml = renderProductImages(product, layout, company);
    const contactHtml = contact ? `<p class="product-contact">${escapeHtml(contact)}</p>` : '';

    if (single) {
      return `
        <article class="product-block product-block-single">
          <h2 class="${titleClass}">${escapeHtml(product.name)}</h2>
          <div class="product-divider"></div>
          <div class="product-intro">${formatIntro(product.intro)}</div>
          ${imageHtml}
          ${contactHtml}
        </article>`;
    }

    if (layout === 'side') {
      return `
        <article class="product-block product-block-side">
          <h2 class="${titleClass}">${escapeHtml(product.name)}</h2>
          <div class="product-divider"></div>
          <div class="product-body-side">
            <div class="product-intro">${formatIntro(product.intro)}</div>
            ${imageHtml}
            ${contactHtml}
          </div>
        </article>`;
    }

    return `
      <article class="product-block product-block-stack">
        <h2 class="${titleClass}">${escapeHtml(product.name)}</h2>
        <div class="product-divider"></div>
        <div class="product-intro">${formatIntro(product.intro)}</div>
        ${imageHtml}
        ${contactHtml}
      </article>`;
  }

  function renderCardContent(bubble, cardBodyEl) {
    const products = bubble.products || [];
    if (!products.length) {
      cardBodyEl.innerHTML = '';
      return;
    }

    if (products.length === 1) {
      cardBodyEl.innerHTML = `
        <div class="card-content">
          <div class="card-columns card-columns-single">
            <div class="card-col card-col-single">
              ${renderProductBlock(products[0], { single: true, company: bubble.title })}
            </div>
          </div>
        </div>`;
      return;
    }

    let columns;
    const customColumns = COMPANY_COLUMNS[bubble.title];
    if (customColumns) {
      const productMap = Object.fromEntries(products.map((product) => [product.name, product]));
      columns = customColumns.map((names) => names.map((name) => productMap[name]).filter(Boolean));
    } else {
      columns = splitProducts(products);
    }

    cardBodyEl.innerHTML = `
      <div class="card-content">
        <div class="card-columns">
          <div class="card-col">${columns[0].map((p) => renderProductBlock(p, { company: bubble.title })).join('')}</div>
          <div class="card-col">${columns[1].map((p) => renderProductBlock(p, { company: bubble.title })).join('')}</div>
        </div>
      </div>`;
  }

  global.CardRenderer = { renderCardContent };
})(window);
