/**
 * 双屏气泡交互核心 — role: 'control' | 'display'
 */
(function (global) {
  const VIEW_W = 1920;
  const H = 1080;
  const FONT_FAMILY = '"MiSans VF", "MiSans", sans-serif';
  const BUBBLE_SIZE_SCALE = 0.8;
  const AVG_R = Math.round(92 * BUBBLE_SIZE_SCALE);
  const R_SPREAD = 0;
  const GRAVITY = 0.000020;
  const BUOYANCY = GRAVITY;
  const AIR_DRAG = 0.016;
  const MAX_SPEED = 0.48;
  const ACTIVE_HOVER_SCALE = 1.34;
  const HOVER_SCALE = 1.06;

  function bubbleParallax(b) {
    return 0.82 + b.z * 0.18;
  }

  function getAirForce(b, time) {
    const t = time * 0.001;
    const influence = 0.28 + b.z * 0.72;
    const globalX = Math.sin(t * 0.11 + 0.4) * 0.006
      + Math.sin(t * 0.063 + 1.8) * 0.004
      + Math.sin(t * 0.028 + 2.6) * 0.003;
    const globalY = Math.cos(t * 0.085 + 0.9) * 0.003
      + Math.sin(t * 0.051 + 3.1) * 0.002;
    const localX = Math.sin(t * b.swayFreq1 + b.swayPhase1) * 0.011
      + Math.sin(t * b.swayFreq2 + b.swayPhase2) * 0.007
      + Math.sin(t * 0.27 + b.swayPhase3) * 0.004;
    const localY = Math.cos(t * b.swayFreq1 * 0.87 + b.swayPhase2) * 0.009
      + Math.cos(t * b.swayFreq2 * 1.25 + b.swayPhase1) * 0.005;
    const gust = Math.sin(t * 0.042 + b.gustPhase) * Math.cos(t * 0.029 + b.gustPhase * 1.7);
    return {
      fx: (globalX + localX + gust * 0.005) * influence,
      fy: (globalY + localY + gust * 0.003) * influence,
    };
  }

  class Bubble {
    constructor(cfg, index) {
      this.baseR = AVG_R + (Math.random() - 0.5) * R_SPREAD * 2;
      this.r = this.baseR;
      this.x = cfg.x * cfg.worldW;
      this.y = cfg.y * H;
      this.z = 0.12 + Math.random() * 0.88;
      this.depthScale = 0.68 + this.z * 0.42;
      this.depthAlpha = 0.38 + this.z * 0.62;
      this.vx = (Math.random() - 0.5) * 0.08;
      this.vy = (Math.random() - 0.5) * 0.06;
      this.mass = this.baseR * this.baseR * (0.7 + this.z * 0.3);
      this.title = cfg.title || `企业 ${index + 1}`;
      this.content = cfg.content || '';
      this.products = cfg.products || [];
      this.swayPhase1 = Math.random() * Math.PI * 2;
      this.swayPhase2 = Math.random() * Math.PI * 2;
      this.swayPhase3 = Math.random() * Math.PI * 2;
      this.gustPhase = Math.random() * Math.PI * 2;
      this.swayFreq1 = 0.12 + Math.random() * 0.22;
      this.swayFreq2 = 0.06 + Math.random() * 0.14;
      this.swayX = 0;
      this.swayY = 0;
      this.wobblePhase = Math.random() * Math.PI * 2;
      this.breathPhase = Math.random() * Math.PI * 2;
      this.breathSpeed = 0.35 + Math.random() * 0.28;
      this.breathAmp = 0.04 + Math.random() * 0.08;
      this.sizeScale = 1;
      this.hoverScale = 1;
      this.targetHoverScale = 1;
      this.isActive = false;
      this.labelLayout = null;
      this.index = index;
    }

    update(time, dt, worldW) {
      const t = time * 0.001;
      const air = getAirForce(this, time);
      const vol = this.baseR * this.baseR;
      const lift = (BUOYANCY * vol - GRAVITY * vol) * dt;
      const drag = AIR_DRAG * (0.85 + (1 - this.z) * 0.25);
      const ax = air.fx - this.vx * drag;
      const ay = air.fy + lift - this.vy * drag;
      this.vx += ax * dt;
      this.vy += ay * dt;
      const maxSpeed = MAX_SPEED * (0.75 + this.z * 0.35);
      const speed = Math.hypot(this.vx, this.vy);
      if (speed > maxSpeed) {
        this.vx = (this.vx / speed) * maxSpeed;
        this.vy = (this.vy / speed) * maxSpeed;
      }
      this.swayX = Math.sin(t * this.swayFreq1 + this.swayPhase1) * (3 + this.z * 4)
        + Math.sin(t * this.swayFreq2 * 1.6 + this.swayPhase3) * (1.5 + this.z * 2);
      this.swayY = Math.cos(t * this.swayFreq2 + this.swayPhase2) * (2.5 + this.z * 3)
        + Math.cos(t * this.swayFreq1 * 0.7 + this.swayPhase1) * (1.2 + this.z * 1.8);
      this.x += this.vx * dt;
      this.y += this.vy * dt;
      this.sizeScale = 1
        + Math.sin(t * this.breathSpeed + this.breathPhase) * this.breathAmp
        + Math.sin(t * this.breathSpeed * 0.55 + this.breathPhase * 1.7) * this.breathAmp * 0.3;

      const desiredScale = this.isActive ? ACTIVE_HOVER_SCALE : (this.targetHoverScale > 1 ? HOVER_SCALE : 1);
      this.hoverScale += (desiredScale - this.hoverScale) * 0.09;
      this.r = this.baseR * this.sizeScale * this.hoverScale * this.depthScale;
      this.mass = this.baseR * this.baseR * (0.7 + this.z * 0.3);

      const pad = this.r + 4;
      const soft = 0.012 * dt;
      if (this.x < pad) { this.x += (pad - this.x) * 0.06; this.vx = Math.abs(this.vx) * 0.08 + soft; }
      if (this.x + pad > worldW) { this.x -= (this.x + pad - worldW) * 0.06; this.vx = -Math.abs(this.vx) * 0.08 - soft; }
      if (this.y < pad) { this.y += (pad - this.y) * 0.06; this.vy = Math.abs(this.vy) * 0.08 + soft * 0.5; }
      if (this.y + pad > H) { this.y -= (this.y + pad - H) * 0.06; this.vy = -Math.abs(this.vy) * 0.08 - soft * 0.5; }
    }

    drawX(scroll) {
      return this.x + scroll * (1 - bubbleParallax(this));
    }

    contains(worldX, worldY, scroll) {
      const cx = this.drawX(scroll) + this.swayX;
      const cy = this.y + this.swayY;
      const dx = worldX - cx;
      const dy = worldY - cy;
      const hitR = this.r * (1.04 + (1 - this.z) * 0.1);
      return dx * dx + dy * dy <= hitR * hitR;
    }
  }

  function resolveCollision(a, b) {
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const dist = Math.hypot(dx, dy);
    const minDist = a.r + b.r;
    if (dist === 0 || dist >= minDist) return;
    const nx = dx / dist;
    const ny = dy / dist;
    const overlap = minDist - dist;
    const totalMass = a.mass + b.mass;
    a.x -= nx * overlap * (b.mass / totalMass);
    a.y -= ny * overlap * (b.mass / totalMass);
    b.x += nx * overlap * (a.mass / totalMass);
    b.y += ny * overlap * (a.mass / totalMass);
    const dvx = a.vx - b.vx;
    const dvy = a.vy - b.vy;
    const dvn = dvx * nx + dvy * ny;
    if (dvn > 0) return;
    const restitution = 0.22;
    const impulse = (-(1 + restitution) * dvn) / (1 / a.mass + 1 / b.mass);
    a.vx -= (impulse / a.mass) * nx * 0.65;
    a.vy -= (impulse / a.mass) * ny * 0.65;
    b.vx += (impulse / b.mass) * nx * 0.65;
    b.vy += (impulse / b.mass) * ny * 0.65;
  }

  function generateBubbleConfigs(companies, worldW) {
    const bubbleCount = companies.length;
    const bubblesPerView = 30;
    const configs = [];
    for (let i = 0; i < bubbleCount; i++) {
      const panel = Math.floor(i / bubblesPerView);
      const idxInPanel = i % bubblesPerView;
      const countInPanel = Math.min(bubblesPerView, bubbleCount - panel * bubblesPerView);
      const cols = 6;
      const rows = Math.ceil(countInPanel / cols);
      const col = idxInPanel % cols;
      const row = Math.floor(idxInPanel / cols);
      const jitterX = Math.sin(i * 2.399) * 0.05;
      const jitterY = Math.cos(i * 1.713) * 0.05;
      const lx = (col + 0.5) / cols + jitterX;
      const ly = (row + 0.5) / rows + jitterY;
      const marginX = 0.05;
      const marginY = 0.05;
      const absX = panel * VIEW_W + marginX * VIEW_W + lx * VIEW_W * (1 - 2 * marginX);
      const absY = marginY * H + ly * H * (1 - 2 * marginY);
      const company = companies[i];
      configs.push({
        x: absX / worldW,
        y: absY / H,
        worldW,
        title: company.name,
        content: company.products.map((p) => p.name).join('、'),
        products: company.products,
      });
    }
    return configs;
  }

  function createDualScreenApp(options) {
    const role = options.role;
    const isControl = role === 'control';
    const isDisplay = role === 'display';
    const sync = new global.BubblesSync(role);

    const companies = typeof COMPANIES !== 'undefined' ? COMPANIES : (global.COMPANIES || []);
    const bubbleCount = companies.length;
    const bubblesPerView = 30;
    const panelCount = Math.ceil(bubbleCount / bubblesPerView);
    const worldW = VIEW_W * panelCount;
    const maxScroll = worldW - VIEW_W;

    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d', { alpha: true });
    const overlay = document.getElementById('overlay');
    const cardTitle = document.getElementById('card-title');
    const cardBody = document.getElementById('card-body');
    const cardPrev = document.querySelector('.card-nav-prev');
    const cardNext = document.querySelector('.card-nav-next');
    const app = document.getElementById('app');
    const viewport = document.getElementById('viewport');
    const scrollHint = document.getElementById('scroll-hint');
    const scrollDots = document.getElementById('scroll-dots');
    const syncStatus = document.getElementById('sync-status');
    const bgVideo = document.getElementById('bg-video');

    canvas.width = VIEW_W;
    canvas.height = H;

    let viewScale = 1;
    let scrollX = 0;
    let fontsReady = false;
    let labelsPrepared = false;
    let hoveredBubble = null;
    let activeBubble = null;
    let cardOpen = false;
    let suppressScrollBroadcast = false;

    const bubbleConfigs = generateBubbleConfigs(companies, worldW);
    const bubbles = bubbleConfigs.map((cfg, i) => new Bubble(cfg, i));

    function fitStage() {
      viewScale = Math.min(window.innerWidth / VIEW_W, window.innerHeight / H);
      app.style.transform = `scale(${viewScale})`;
    }
    window.addEventListener('resize', fitStage);
    fitStage();

    function wrapTextLines(context, text, maxWidth) {
      const chars = [...text];
      const lines = [];
      let line = '';
      for (const ch of chars) {
        const test = line + ch;
        if (context.measureText(test).width > maxWidth && line) {
          lines.push(line);
          line = ch;
        } else {
          line = test;
        }
      }
      if (line) lines.push(line);
      return lines;
    }

    function computeLabelLayout(bubble) {
      const r = bubble.baseR;
      const maxWidth = r * 1.45;
      let fontSize = Math.min(r * 0.19, 17);
      let lines = [];
      for (let i = 0; i < 8; i++) {
        ctx.font = `520 ${fontSize}px ${FONT_FAMILY}`;
        lines = wrapTextLines(ctx, bubble.title, maxWidth);
        if (lines.length <= 4) break;
        fontSize -= 1;
      }
      bubble.labelLayout = { lines, fontSize, lineHeight: fontSize * 1.22 };
    }

    function prepareAllLabelLayouts() {
      if (!fontsReady || labelsPrepared) return;
      for (const b of bubbles) computeLabelLayout(b);
      labelsPrepared = true;
    }

    function drawBubbleLabel(context, bubble) {
      if (!bubble.title || !fontsReady) return;
      if (!bubble.labelLayout) computeLabelLayout(bubble);
      const { lines, fontSize, lineHeight } = bubble.labelLayout;
      const breathScale = bubble.r / bubble.baseR;
      context.save();
      context.scale(breathScale, breathScale);
      context.textAlign = 'center';
      context.textBaseline = 'middle';
      context.fillStyle = bubble.isActive ? 'rgba(255, 255, 255, 1)' : 'rgba(255, 255, 255, 0.93)';
      context.shadowColor = bubble.isActive ? 'rgba(80, 180, 255, 0.55)' : 'rgba(0, 40, 80, 0.35)';
      context.shadowBlur = bubble.isActive ? 8 / breathScale : 4 / breathScale;
      context.font = `520 ${fontSize}px ${FONT_FAMILY}`;
      const totalH = lines.length * lineHeight;
      let y = -totalH / 2 + lineHeight / 2;
      for (const ln of lines) {
        context.fillText(ln, 0, y);
        y += lineHeight;
      }
      context.shadowBlur = 0;
      context.restore();
    }

    function drawBubble(b, time, scroll) {
      const t = time * 0.001;
      const r = b.r;
      const wobble = 1 + Math.sin(t * 1.1 + b.wobblePhase) * 0.006;
      const dx = b.drawX(scroll) + b.swayX;
      const dy = b.y + b.swayY;
      const depthBlur = (1 - b.z) * 2.5;
      const hasActive = activeBubble != null;
      const dimOthers = isControl && hasActive && !b.isActive;

      ctx.save();
      ctx.globalAlpha = dimOthers ? b.depthAlpha * 0.42 : (b.isActive ? Math.min(1, b.depthAlpha * 1.55) : b.depthAlpha);
      ctx.translate(dx, dy);
      ctx.scale(wobble, 1 / wobble * (1 + (wobble - 1) * 0.25));

      if (depthBlur > 0.3 && !b.isActive) {
        ctx.shadowColor = 'rgba(120, 210, 255, 0.15)';
        ctx.shadowBlur = depthBlur;
      }

      if (b.isActive) {
        const activeGlow = ctx.createRadialGradient(0, 0, r * 0.4, 0, 0, r * 2.4);
        activeGlow.addColorStop(0, 'rgba(120, 220, 255, 0.35)');
        activeGlow.addColorStop(0.45, 'rgba(80, 200, 255, 0.18)');
        activeGlow.addColorStop(1, 'rgba(60, 160, 220, 0)');
        ctx.beginPath();
        ctx.arc(0, 0, r * 2.4, 0, Math.PI * 2);
        ctx.fillStyle = activeGlow;
        ctx.fill();
      }

      const outerGlow = ctx.createRadialGradient(0, 0, r * 0.6, 0, 0, r * 1.8);
      outerGlow.addColorStop(0, `rgba(100, 200, 255, ${0.05 + b.z * 0.03 + (b.isActive ? 0.12 : 0)})`);
      outerGlow.addColorStop(0.5, 'rgba(80, 180, 240, 0.03)');
      outerGlow.addColorStop(1, 'rgba(60, 160, 220, 0)');
      ctx.beginPath();
      ctx.arc(0, 0, r * 1.8, 0, Math.PI * 2);
      ctx.fillStyle = outerGlow;
      ctx.fill();

      const body = ctx.createRadialGradient(-r * 0.15, -r * 0.2, r * 0.05, 0, 0, r);
      body.addColorStop(0, b.isActive ? 'rgba(15, 40, 60, 0.22)' : 'rgba(5, 15, 25, 0.15)');
      body.addColorStop(0.35, 'rgba(10, 30, 50, 0.08)');
      body.addColorStop(0.65, b.isActive ? 'rgba(80, 200, 255, 0.22)' : 'rgba(60, 180, 230, 0.12)');
      body.addColorStop(0.85, b.isActive ? 'rgba(140, 230, 255, 0.55)' : 'rgba(120, 210, 255, 0.35)');
      body.addColorStop(0.95, b.isActive ? 'rgba(210, 248, 255, 0.85)' : 'rgba(180, 235, 255, 0.55)');
      body.addColorStop(1, b.isActive ? 'rgba(230, 252, 255, 0.95)' : 'rgba(200, 245, 255, 0.7)');
      ctx.beginPath();
      ctx.arc(0, 0, r, 0, Math.PI * 2);
      ctx.fillStyle = body;
      ctx.fill();

      ctx.beginPath();
      ctx.arc(0, 0, r - 1, 0, Math.PI * 2);
      ctx.strokeStyle = b.isActive ? 'rgba(200, 250, 255, 0.85)' : 'rgba(160, 230, 255, 0.45)';
      ctx.lineWidth = b.isActive ? 2.5 : 1.5;
      ctx.stroke();

      ctx.beginPath();
      ctx.ellipse(-r * 0.22, -r * 0.32, r * 0.35, r * 0.18, -0.4, 0, Math.PI * 2);
      const highlight = ctx.createRadialGradient(-r * 0.22, -r * 0.32, 0, -r * 0.22, -r * 0.32, r * 0.4);
      highlight.addColorStop(0, b.isActive ? 'rgba(255, 255, 255, 0.85)' : 'rgba(255, 255, 255, 0.55)');
      highlight.addColorStop(0.4, 'rgba(200, 240, 255, 0.2)');
      highlight.addColorStop(1, 'rgba(200, 240, 255, 0)');
      ctx.fillStyle = highlight;
      ctx.fill();

      ctx.beginPath();
      ctx.arc(-r * 0.28, -r * 0.38, r * 0.07, 0, Math.PI * 2);
      ctx.fillStyle = b.isActive ? 'rgba(255, 255, 255, 0.95)' : 'rgba(255, 255, 255, 0.75)';
      ctx.fill();

      ctx.beginPath();
      ctx.ellipse(r * 0.1, r * 0.38, r * 0.28, r * 0.1, 0.2, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(100, 200, 255, 0.12)';
      ctx.fill();

      if (b.targetHoverScale > 1 && !b.isActive) {
        ctx.beginPath();
        ctx.arc(0, 0, r, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(180, 240, 255, 0.6)';
        ctx.lineWidth = 2;
        ctx.stroke();
      }

      drawBubbleLabel(ctx, b);
      ctx.shadowBlur = 0;
      ctx.restore();
    }

    function shouldHideCanvas() {
      return isDisplay && cardOpen;
    }

    function render(time) {
      ctx.clearRect(0, 0, VIEW_W, H);
      if (shouldHideCanvas()) return;

      ctx.save();
      ctx.translate(-scrollX, 0);
      const sorted = [...bubbles].sort((a, b) => a.z - b.z || a.r - b.r);
      for (const b of sorted) {
        const drawXPos = b.drawX(scrollX);
        if (drawXPos + b.r < scrollX - 30 || drawXPos - b.r > scrollX + VIEW_W + 30) continue;
        drawBubble(b, time, scrollX);
      }
      ctx.restore();
    }

    function physicsStep(time, dt) {
      if (shouldHideCanvas()) return;
      for (const b of bubbles) b.update(time, dt, worldW);
      for (let i = 0; i < bubbles.length; i++) {
        for (let j = i + 1; j < bubbles.length; j++) {
          resolveCollision(bubbles[i], bubbles[j]);
        }
      }
    }

    function clampScroll(v) {
      return Math.max(0, Math.min(maxScroll, v));
    }

    let scrollAnim = null;
    const SCROLL_ANIM_MS = 180;

    function cancelScrollAnim() {
      if (scrollAnim != null) {
        cancelAnimationFrame(scrollAnim);
        scrollAnim = null;
      }
    }

    function scrollToBubble(bubble, fromRemote, animated = true) {
      if (!bubble) return;
      const targetScroll = clampScroll(bubble.x - VIEW_W * 0.5);
      if (fromRemote || !animated) {
        cancelScrollAnim();
        setScroll(targetScroll, fromRemote);
        return;
      }
      cancelScrollAnim();
      const startScroll = scrollX;
      const startTime = performance.now();
      function tick(now) {
        const t = Math.min(1, (now - startTime) / SCROLL_ANIM_MS);
        const eased = 1 - Math.pow(1 - t, 3);
        setScroll(startScroll + (targetScroll - startScroll) * eased);
        if (t < 1) {
          scrollAnim = requestAnimationFrame(tick);
        } else {
          scrollAnim = null;
        }
      }
      scrollAnim = requestAnimationFrame(tick);
    }

    function broadcastState() {
      sync.send({
        type: 'state',
        scrollX,
        selectedIndex: activeBubble ? activeBubble.index : null,
        cardOpen: activeBubble != null,
      });
    }

    function setScroll(x, fromRemote) {
      scrollX = clampScroll(x);
      updateScrollUI();
      if (!fromRemote && isControl && !suppressScrollBroadcast) {
        sync.send({ type: 'scroll', scrollX });
      }
    }

    function updateScrollUI() {
      const panel = Math.round(scrollX / VIEW_W);
      scrollDots.querySelectorAll('.scroll-dot').forEach((dot, i) => {
        dot.classList.toggle('active', i === panel);
      });
      scrollHint.classList.toggle('hidden', scrollX > 40 && scrollX < maxScroll - 40);
    }

    for (let i = 0; i < panelCount; i++) {
      const dot = document.createElement('div');
      dot.className = 'scroll-dot' + (i === 0 ? ' active' : '');
      scrollDots.appendChild(dot);
    }

    function setActiveBubble(bubble, fromRemote) {
      for (const b of bubbles) {
        b.isActive = bubble != null && b === bubble;
        if (!b.isActive) b.targetHoverScale = 1;
      }
      activeBubble = bubble;
      if (isControl && !fromRemote) {
        sync.send({
          type: bubble ? 'select' : 'close',
          index: bubble ? bubble.index : null,
        });
      }
    }

    function openCard(bubble, fromRemote) {
      if (!bubble || !overlay) return;
      setActiveBubble(bubble, fromRemote);
      scrollToBubble(bubble, fromRemote);
      cardTitle.textContent = bubble.title;
      global.CardRenderer.renderCardContent(bubble, cardBody);
      cardOpen = true;
      viewport.classList.add('card-open');
      overlay.classList.add('active');
      if (isDisplay && !fromRemote) {
        sync.send({ type: 'select', index: bubble.index });
      }
    }

    function closeCard(fromRemote) {
      cardOpen = false;
      if (overlay) overlay.classList.remove('active');
      viewport.classList.remove('card-open');
      setActiveBubble(null, fromRemote);
      if (isDisplay && !fromRemote) {
        sync.send({ type: 'close' });
      }
    }

    function navigateCard(delta, fromRemote) {
      if (!activeBubble) return;
      const nextIndex = (activeBubble.index + delta + bubbles.length) % bubbles.length;
      if (isDisplay) {
        openCard(bubbles[nextIndex], fromRemote);
        if (!fromRemote) sync.send({ type: 'navigate', index: nextIndex });
      } else if (isControl) {
        setActiveBubble(bubbles[nextIndex], fromRemote);
        sync.send({ type: 'navigate', index: nextIndex });
      }
    }

    function selectBubbleOnControl(bubble) {
      if (activeBubble === bubble) {
        setActiveBubble(null);
        sync.send({ type: 'close' });
        return;
      }
      setActiveBubble(bubble);
      scrollToBubble(bubble, false, true);
      sync.send({ type: 'select', index: bubble.index });
    }

    // ——— 背景视频 ———
    if (bgVideo) {
      bgVideo.src = 'bg.mp4';
      function startBgVideo() {
        const p = bgVideo.play();
        if (p && p.catch) {
          p.catch(() => {
            document.addEventListener('pointerdown', () => bgVideo.play(), { once: true });
          });
        }
      }
      bgVideo.addEventListener('loadeddata', startBgVideo);
      bgVideo.addEventListener('canplay', startBgVideo);
      bgVideo.load();
      startBgVideo();
    }

    document.fonts.load('500 16px "MiSans VF"').then(() => {
      fontsReady = true;
      prepareAllLabelLayouts();
    });
    document.fonts.ready.then(() => {
      fontsReady = true;
      prepareAllLabelLayouts();
    });

    let lastTime = 0;
    function loop(time) {
      const dt = lastTime ? Math.min((time - lastTime) / 16.667, 2.5) : 1;
      physicsStep(time, dt);
      render(time);
      lastTime = time;
      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);

    // ——— 滑动交互（仅一体机） ———
    const DRAG_THRESHOLD_MOUSE = 6;
    const DRAG_THRESHOLD_TOUCH = 16;

    let pointerActive = false;
    let pointerId = null;
    let pointerIsTouch = false;
    let panStartX = 0;
    let panStartScroll = 0;
    let panCommitted = false;
    let panMoved = false;
    let suppressClick = false;

    function getDragThreshold(isTouch) {
      return isTouch ? DRAG_THRESHOLD_TOUCH : DRAG_THRESHOLD_MOUSE;
    }

    function onPointerDown(e) {
      if (!isControl || cardOpen) return;
      if (e.pointerType === 'mouse' && e.button !== 0) return;

      cancelScrollAnim();
      pointerActive = true;
      pointerId = e.pointerId;
      pointerIsTouch = e.pointerType === 'touch';
      panCommitted = false;
      panMoved = false;
      panStartX = e.clientX;
      panStartScroll = scrollX;
      canvas.classList.add('grabbing');
      viewport.setPointerCapture(e.pointerId);
    }

    function onPointerMove(e) {
      if (!pointerActive || e.pointerId !== pointerId) return;

      const dx = (e.clientX - panStartX) / viewScale;
      const dist = Math.abs(dx);

      // A：未超过阈值前不滚动（滑动死区）
      if (!panCommitted) {
        if (dist <= getDragThreshold(pointerIsTouch)) return;
        panCommitted = true;
        panMoved = true;
      }

      setScroll(panStartScroll - dx);
    }

    function onPointerUp(e) {
      if (!pointerActive || e.pointerId !== pointerId) return;

      if (!panMoved) {
        tryInteractAt(e.clientX, e.clientY);
      }
      suppressClick = true;

      pointerActive = false;
      pointerId = null;
      panCommitted = false;
      panMoved = false;
      canvas.classList.remove('grabbing');
      try { viewport.releasePointerCapture(e.pointerId); } catch (_) { /* ignore */ }
    }

    function onPointerCancel(e) {
      if (!pointerActive || e.pointerId !== pointerId) return;
      pointerActive = false;
      pointerId = null;
      panCommitted = false;
      panMoved = false;
      suppressClick = true;
      canvas.classList.remove('grabbing');
      try { viewport.releasePointerCapture(e.pointerId); } catch (_) { /* ignore */ }
    }

    if (isControl) {
      viewport.addEventListener('pointerdown', onPointerDown);
      viewport.addEventListener('pointermove', onPointerMove);
      viewport.addEventListener('pointerup', onPointerUp);
      viewport.addEventListener('pointercancel', onPointerCancel);

      viewport.addEventListener('wheel', (e) => {
        cancelScrollAnim();
        const delta = Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : e.deltaY;
        setScroll(scrollX + delta);
        e.preventDefault();
      }, { passive: false });
    }

    function getCanvasPosFromClient(clientX, clientY) {
      const rect = viewport.getBoundingClientRect();
      return {
        x: (clientX - rect.left) / viewScale + scrollX,
        y: (clientY - rect.top) / viewScale,
      };
    }

    function getCanvasPos(e) {
      return getCanvasPosFromClient(e.clientX, e.clientY);
    }

    function hitBubble(worldX, worldY) {
      const sorted = [...bubbles].sort((a, b) => a.z - b.z || a.r - b.r);
      for (let i = sorted.length - 1; i >= 0; i--) {
        if (sorted[i].contains(worldX, worldY, scrollX)) return sorted[i];
      }
      return null;
    }

    function tryInteractAt(clientX, clientY) {
      const { x, y } = getCanvasPosFromClient(clientX, clientY);
      const bubble = hitBubble(x, y);
      if (isControl) {
        if (bubble) selectBubbleOnControl(bubble);
        else if (activeBubble) {
          setActiveBubble(null);
          sync.send({ type: 'close' });
        }
      } else if (isDisplay && bubble) {
        openCard(bubble);
      }
    }

    if (isControl) {
      viewport.addEventListener('mousemove', (e) => {
        if (pointerActive) return;
        const { x, y } = getCanvasPos(e);
        const found = hitBubble(x, y);
        if (hoveredBubble && hoveredBubble !== found) hoveredBubble.targetHoverScale = 1;
        hoveredBubble = found;
        if (found && !found.isActive) {
          found.targetHoverScale = HOVER_SCALE;
          canvas.classList.add('pointer');
        } else {
          canvas.classList.remove('pointer');
        }
      });

      viewport.addEventListener('click', (e) => {
        if (suppressClick) {
          suppressClick = false;
          return;
        }
        if (panMoved) return;
        tryInteractAt(e.clientX, e.clientY);
      });
    }

    // ——— 大屏卡片交互 ———
    if (isDisplay && overlay) {
      if (cardPrev) {
        cardPrev.addEventListener('click', (e) => {
          e.stopPropagation();
          navigateCard(-1);
        });
      }
      if (cardNext) {
        cardNext.addEventListener('click', (e) => {
          e.stopPropagation();
          navigateCard(1);
        });
      }
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeCard();
      });
      document.addEventListener('keydown', (e) => {
        if (!cardOpen) return;
        if (e.key === 'Escape') closeCard();
        if (e.key === 'ArrowLeft') navigateCard(-1);
        if (e.key === 'ArrowRight') navigateCard(1);
      });
    }

    // ——— 双屏同步 ———
    sync.on((msg) => {
      switch (msg.type) {
        case 'ping':
          if (isControl) {
            sync.send({
              type: 'pong',
              scrollX,
              selectedIndex: activeBubble ? activeBubble.index : null,
            });
          }
          break;
        case 'pong':
          break;
        case 'state':
          if (msg.scrollX != null) setScroll(msg.scrollX, true);
          if (isDisplay) {
            if (msg.selectedIndex != null) {
              openCard(bubbles[msg.selectedIndex], true);
            } else {
              suppressScrollBroadcast = true;
              closeCard(true);
              suppressScrollBroadcast = false;
            }
          }
          if (isControl && msg.selectedIndex != null) {
            setActiveBubble(bubbles[msg.selectedIndex], true);
          } else if (isControl && msg.selectedIndex === null) {
            setActiveBubble(null, true);
          }
          break;
        case 'scroll':
          if (isDisplay) setScroll(msg.scrollX, true);
          break;
        case 'select':
          if (isDisplay && msg.index != null) openCard(bubbles[msg.index], true);
          if (isControl && msg.index != null) setActiveBubble(bubbles[msg.index], true);
          break;
        case 'close':
          if (isDisplay) closeCard(true);
          if (isControl) setActiveBubble(null, true);
          break;
        case 'navigate':
          if (msg.index != null) {
            if (isDisplay) openCard(bubbles[msg.index], true);
            if (isControl) setActiveBubble(bubbles[msg.index], true);
          }
          break;
        case 'request-state':
          if (isControl) broadcastState();
          break;
        default:
          break;
      }
    });

    if (isDisplay) {
      sync.send({ type: 'request-state' });
    }

    if (syncStatus) {
      setInterval(() => {
        const connected = sync.isPeerConnected();
        syncStatus.classList.toggle('connected', connected);
        syncStatus.classList.toggle('waiting', !connected);
        syncStatus.textContent = connected
          ? (isControl ? '已连接大屏' : '已连接一体机')
          : (isControl ? '等待大屏连接…' : '等待一体机连接…');
      }, 1000);
    }

    return { sync, role };
  }

  global.createDualScreenApp = createDualScreenApp;
})(window);
