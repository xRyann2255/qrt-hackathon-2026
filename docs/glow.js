// A wake in the background dots: a smoothed follower chases the pointer and leaves a short trail; dots near the
// trail turn faint yellow, brighter the faster the pointer moves, and fade within half a second once it stops.
// One canvas under the page, redrawn only while the trail is alive (no frames when idle). Mouse and trackpad only.
if (matchMedia('(hover: hover) and (pointer: fine)').matches && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const STEP = 22, OFF = 3, R = 70, MAX_A = 0.42, FOLLOW = 45, FADE = 160;  // px, px, px, alpha, ms, ms
  const cv = document.body.appendChild(document.createElement('canvas')), ctx = cv.getContext('2d');
  cv.className = 'glow';
  const accent = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#f2d061';
  let dpr = 1, w = 0, h = 0;
  const size = () => { dpr = devicePixelRatio || 1; w = innerWidth; h = innerHeight; cv.width = w * dpr; cv.height = h * dpr; };
  size(); addEventListener('resize', size);

  let px = 0, py = 0, fx = 0, fy = 0, seen = false, running = false, last = 0;
  const trail = [];  // {x, y, e}: page coordinates (so scrolling leaves the wake in place), energy 0..1

  function frame(now) {
    const dt = Math.min(50, now - last || 16); last = now;
    // The follower eases toward the pointer; its speed sets the energy of the point it drops
    const k = 1 - Math.exp(-dt / FOLLOW), nx = fx + (px - fx) * k, ny = fy + (py - fy) * k;
    const moved = Math.hypot(nx - fx, ny - fy); fx = nx; fy = ny;
    if (moved > 0.3) trail.push({x: fx + scrollX, y: fy + scrollY, e: Math.min(1, 0.12 + moved / dt / 1.4)});
    const decay = Math.exp(-dt / FADE);
    for (const p of trail) p.e *= decay;
    while (trail.length && (trail[0].e < 0.03 || trail.length > 40)) trail.shift();

    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    if (trail.length) {
      let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
      for (const p of trail) { x0 = Math.min(x0, p.x); y0 = Math.min(y0, p.y); x1 = Math.max(x1, p.x); y1 = Math.max(y1, p.y); }
      const i0 = Math.ceil((x0 - R - OFF) / STEP), i1 = Math.floor((x1 + R - OFF) / STEP);
      const j0 = Math.ceil((y0 - R - OFF) / STEP), j1 = Math.floor((y1 + R - OFF) / STEP);
      const buckets = [[], [], [], [], [], []], R2 = R * R;
      for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) {
        const dx0 = i * STEP + OFF, dy0 = j * STEP + OFF;
        let v = 0;
        for (const p of trail) { const d2 = (dx0 - p.x) ** 2 + (dy0 - p.y) ** 2; if (d2 < R2) v += p.e * (1 - d2 / R2) ** 2; }
        if (v > 0.06) buckets[Math.min(5, Math.floor(Math.min(1, v) * 6))].push(dx0 - scrollX, dy0 - scrollY);
      }
      ctx.fillStyle = accent;
      buckets.forEach((b, n) => {
        if (!b.length) return;
        const t = (n + 1) / 6, r = 1 + 0.6 * t;
        ctx.globalAlpha = MAX_A * t;
        ctx.beginPath();
        for (let q = 0; q < b.length; q += 2) { ctx.moveTo(b[q] + r, b[q + 1]); ctx.arc(b[q], b[q + 1], r, 0, 7); }
        ctx.fill();
      });
    }
    running = trail.length > 0 || Math.hypot(px - fx, py - fy) > 0.3;
    if (running) requestAnimationFrame(frame);
  }
  const wake = () => { if (!running) { running = true; last = performance.now(); requestAnimationFrame(frame); } };
  addEventListener('pointermove', e => {
    px = e.clientX; py = e.clientY;
    if (!seen) { seen = true; fx = px; fy = py; }
    wake();
  }, {passive: true});
  addEventListener('scroll', wake, {passive: true});
  document.addEventListener('mouseout', e => { if (!e.relatedTarget) seen = false; });
}
