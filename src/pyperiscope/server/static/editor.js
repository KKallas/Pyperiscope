// Screenshot editor: draws a screenshot with overlays and lets the operator
// mark a main box, a click point, detail boxes, or pick a numbered candidate.
// All coordinates are in screenshot pixels (what the API expects).
const COLORS = { main: '#2f7cf6', click: '#e0368c', detail: '#f08a00', cand: '#22a352', pick: '#16c25a', best: '#e2b400' };
const MAX_DETAILS = 4;

class Editor {
  constructor(host, { tools = ['main', 'click', 'detail'], onChange = () => {} } = {}) {
    this.onChange = onChange;
    this.zoom = 'fit';
    this.st = { main: null, click: null, details: [], candidates: [], picked: null, best: null };
    host.innerHTML = `
      <div class="ed-bar">
        <div class="seg ed-tools"></div>
        <div class="seg ed-zoom">
          <button data-z="fit">Fit</button><button data-z="0.5">50%</button>
          <button data-z="1">100%</button><button data-z="2">200%</button>
        </div>
        <span class="ed-pos muted"></span>
      </div>
      <div class="ed-scroll"><canvas class="ed-canvas"></canvas><canvas class="ed-loupe" width="168" height="168"></canvas></div>
      <div class="ed-hint muted"></div>`;
    this.scroll = host.querySelector('.ed-scroll');
    this.canvas = host.querySelector('.ed-canvas');
    this.loupe = host.querySelector('.ed-loupe');
    this.hint = host.querySelector('.ed-hint');
    this.toolBar = host.querySelector('.ed-tools');
    this.pos = host.querySelector('.ed-pos');
    host.querySelectorAll('.ed-zoom button').forEach(b => b.onclick = () => { this.zoom = b.dataset.z; this.layout(); });
    this.setTools(tools);
    this.bindPointer();
    new ResizeObserver(() => this.zoom === 'fit' && this.layout()).observe(this.scroll);
  }

  setTools(tools) {
    this.tools = tools;
    const labels = { main: 'Main box', click: 'Click point', detail: 'Detail box', pick: 'Pick candidate' };
    this.toolBar.innerHTML = tools.map(t => `<button data-t="${t}">${labels[t]}</button>`).join('');
    this.toolBar.querySelectorAll('button').forEach(b => b.onclick = () => this.useTool(b.dataset.t));
    this.useTool(tools[0]);
  }

  useTool(tool) {
    this.tool = tool;
    this.toolBar.querySelectorAll('button').forEach(b => b.classList.toggle('on', b.dataset.t === tool));
    const hints = {
      main: 'Drag a box around the element to find. Keep it tight but include its text/edges.',
      click: 'Click where the mouse should click (defaults to the centre of the main box).',
      detail: `Drag a box around something unique near the target (up to ${MAX_DETAILS}). Backspace removes the last.`,
      pick: 'Click the numbered green candidate that is the right one.',
    };
    this.hint.textContent = hints[tool] || '';
  }

  load(src) {
    return new Promise((ok, fail) => {
      const img = new Image();
      img.onload = () => { this.img = img; this.layout(); ok(img); };
      img.onerror = () => fail(new Error('could not load screenshot'));
      img.src = src;
    });
  }

  set(patch) { Object.assign(this.st, patch); this.draw(); }

  scale() {
    if (!this.img) return 1;
    return this.zoom === 'fit' ? Math.min(1, (this.scroll.clientWidth - 2) / this.img.width) : Number(this.zoom);
  }

  layout() {
    if (!this.img) return;
    const z = this.scale(), dpr = window.devicePixelRatio || 1;
    this.canvas.style.width = `${Math.round(this.img.width * z)}px`;
    this.canvas.style.height = `${Math.round(this.img.height * z)}px`;
    this.canvas.width = Math.round(this.img.width * z * dpr);
    this.canvas.height = Math.round(this.img.height * z * dpr);
    this.draw();
  }

  toImage(ev) {
    const r = this.canvas.getBoundingClientRect(), z = this.scale();
    return [Math.max(0, Math.min(this.img.width, (ev.clientX - r.left) / z)),
            Math.max(0, Math.min(this.img.height, (ev.clientY - r.top) / z))];
  }

  bindPointer() {
    let start = null;
    const norm = (a, b) => [Math.round(Math.min(a[0], b[0])), Math.round(Math.min(a[1], b[1])),
                            Math.round(Math.abs(a[0] - b[0])), Math.round(Math.abs(a[1] - b[1]))];
    this.canvas.addEventListener('pointerdown', ev => {
      if (!this.img) return;
      const p = this.toImage(ev);
      if (this.tool === 'click') { this.st.click = p.map(Math.round); this.changed(); return; }
      if (this.tool === 'pick') { this.pickAt(p); return; }
      if (this.tool === 'detail' && this.st.details.length >= MAX_DETAILS) { toast(`At most ${MAX_DETAILS} details`); return; }
      start = p; this.canvas.setPointerCapture(ev.pointerId);
    });
    this.canvas.addEventListener('pointermove', ev => {
      if (!this.img) return;
      const p = this.toImage(ev);
      this.pos.textContent = `x ${Math.round(p[0])}  y ${Math.round(p[1])}`;
      this.drawLoupe(p, ev);
      if (start) { this.drag = norm(start, p); this.draw(); }
    });
    this.canvas.addEventListener('pointerleave', () => { this.loupe.style.display = 'none'; });
    this.canvas.addEventListener('pointerup', ev => {
      if (!start) return;
      const box = norm(start, this.toImage(ev));
      start = null; this.drag = null;
      if (box[2] < 6 || box[3] < 6) { this.draw(); return; }
      if (this.tool === 'main') { this.st.main = box; this.st.click = null; }
      if (this.tool === 'detail') this.st.details.push(box);
      this.changed();
    });
    window.addEventListener('keydown', ev => {
      if (ev.target.closest('input, textarea, select')) return;
      if (ev.key === 'Backspace' && this.st.details.length) { this.st.details.pop(); this.changed(); }
    });
  }

  pickAt([x, y]) {
    const i = this.st.candidates.findIndex(c => x >= c.box[0] && y >= c.box[1] && x <= c.box[0] + c.box[2] && y <= c.box[1] + c.box[3]);
    if (i >= 0) { this.st.picked = i; this.changed(); if (this.tools.includes('detail')) this.useTool('detail'); }
  }

  changed() { this.draw(); this.onChange(this.st); }

  clickPoint() {
    const m = this.st.main;
    return this.st.click || (m && [Math.round(m[0] + m[2] / 2), Math.round(m[1] + m[3] / 2)]);
  }

  draw() {
    if (!this.img) return;
    const c = this.canvas.getContext('2d'), z = this.scale() * (window.devicePixelRatio || 1);
    c.setTransform(1, 0, 0, 1, 0, 0);
    c.drawImage(this.img, 0, 0, this.canvas.width, this.canvas.height);
    c.setTransform(z, 0, 0, z, 0, 0);
    const px = 1 / this.scale();   // one CSS pixel, in image units: keeps labels readable at any zoom
    const box = (b, color, label, fill, dash) => {
      c.save(); c.lineWidth = px * (fill ? 2 : 1.5); c.strokeStyle = color; c.setLineDash(dash ? [6 * px, 4 * px] : []);
      if (fill) { c.fillStyle = color + '33'; c.fillRect(...b); }
      c.strokeRect(...b);
      if (label) {
        c.font = `600 ${12 * px}px system-ui, sans-serif`;
        const w = c.measureText(label).width + 10 * px, h = 18 * px;
        c.fillStyle = color; c.fillRect(b[0], b[1] - h, w, h);
        c.fillStyle = '#fff'; c.fillText(label, b[0] + 5 * px, b[1] - 5 * px);
      }
      c.restore();
    };
    this.st.candidates.forEach((m, i) => box(m.box, i === this.st.picked ? COLORS.pick : COLORS.cand,
      `[${i}] ${m.score.toFixed(2)}`, i === this.st.picked));
    if (this.st.best) box(this.st.best, COLORS.best, `best ${this.st.best.score} (too low)`, false, true);
    if (this.st.main) box(this.st.main, COLORS.main, 'MAIN', true);
    this.st.details.forEach((d, i) => box(d, COLORS.detail, `D${i + 1}`, true));
    if (this.drag) box(this.drag, this.tool === 'detail' ? COLORS.detail : COLORS.main, null, false, true);
    const p = this.clickPoint();
    if (p) {
      c.strokeStyle = COLORS.click; c.lineWidth = 2 * px; const r = 9 * px;
      c.beginPath(); c.moveTo(p[0] - r, p[1]); c.lineTo(p[0] + r, p[1]); c.moveTo(p[0], p[1] - r); c.lineTo(p[0], p[1] + r); c.stroke();
    }
  }

  drawLoupe([x, y], ev) {
    const L = this.loupe, c = L.getContext('2d'), span = 42;
    L.style.display = 'block';
    const r = this.scroll.getBoundingClientRect();
    L.style.left = `${ev.clientX - r.left + this.scroll.scrollLeft + 24}px`;
    L.style.top = `${ev.clientY - r.top + this.scroll.scrollTop + 24}px`;
    c.imageSmoothingEnabled = false;
    c.clearRect(0, 0, L.width, L.height);
    c.drawImage(this.img, x - span / 2, y - span / 2, span, span, 0, 0, L.width, L.height);
    c.strokeStyle = COLORS.click; c.lineWidth = 1;
    c.beginPath(); c.moveTo(L.width / 2, 0); c.lineTo(L.width / 2, L.height); c.moveTo(0, L.height / 2); c.lineTo(L.width, L.height / 2); c.stroke();
  }
}
