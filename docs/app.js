// Shared by the demo pages: run a C++ solver in a Web Worker (a new run stops the previous one), draw SVG,
// report state and results, and play a skippable animation.
let worker;
function solve(q, input, env) {
  if (worker) worker.terminate();
  worker = new Worker('run.js');
  return new Promise((resolve, reject) => {
    worker.onmessage = e => e.data.error ? reject(new Error(e.data.error)) : resolve(e.data);
    worker.onerror = e => reject(new Error(e.message || 'worker failed'));
    worker.postMessage({q, input, env});
  });
}

const $ = id => document.getElementById(id);

function svgEl(tag, attrs, parent) {
  const e = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
}

// state: 'busy' while solving, 'error', or 'done'. The stage's data-state drives the styles.
function status(text, state = 'done') {
  $('status').textContent = text;
  $('stage').dataset.state = state;
  if (state !== 'done') { cancelAnimationFrame(anim); $('skip').hidden = true; }
  if (state === 'busy') metrics([]);
}

function metrics(pairs) {  // [[label, value, isScore], ...] into the results list
  $('metrics').replaceChildren(...pairs.flatMap(([k, v, score]) => {
    const dt = document.createElement('dt'), dd = document.createElement('dd');
    dt.textContent = k; dd.textContent = v;
    if (score) dd.className = 'score';
    return [dt, dd];
  }));
}

// Call step(0) .. step(n - 1) spread over ms; the stage button skips to the end, then offers a replay.
const still = matchMedia('(prefers-reduced-motion: reduce)');
let anim;
function play(n, step, replay, ms = 1500) {
  cancelAnimationFrame(anim);
  const btn = $('skip'), t0 = performance.now();
  let i = 0;
  const upTo = k => { while (i < Math.min(k, n)) step(i++); };
  const finish = () => { cancelAnimationFrame(anim); upTo(n); btn.textContent = 'Replay'; btn.onclick = replay; };
  btn.hidden = false;
  btn.textContent = 'Skip animation';
  btn.onclick = finish;
  if (still.matches) return finish();
  const tick = now => { upTo(Math.ceil((now - t0) / ms * n)); if (i < n) anim = requestAnimationFrame(tick); else finish(); };
  anim = requestAnimationFrame(tick);
}

// Show code: the pane #code (data-src = the file's repo path) gets code/qN.html, written by tools/highlight-code.py,
// on first open. The #show-code button toggles it; a pane that starts visible (q3) loads at once.
{
  const pane = $('code'), btn = $('show-code');
  if (pane) {
    const src = pane.dataset.src;
    pane.insertAdjacentHTML('afterbegin', `<div class="bar"><b>${src}</b><span><button>Copy</button>` +
      `<a href="https://github.com/xRyann2255/qrt-hackathon-2026/blob/main/${src}">GitHub</a></span></div>`);
    const title = pane.querySelector('.bar b'), copy = pane.querySelector('.bar button');
    // glow.js redraws its canvas on every pointermove, even under this opaque pane where its dots can't be seen, and that
    // made the code's highlight paint two frames late. Moves inside the pane don't reach its listener on window.
    pane.addEventListener('pointermove', e => e.stopPropagation(), {passive: true});
    let loading;
    const load = () => loading ||= fetch(`code/${src.split('/')[1]}.html`)
      .then(r => r.ok ? r.text() : Promise.reject(Error(`HTTP ${r.status}`)))
      .then(html => {
        pane.insertAdjacentHTML('beforeend', html);
        const pre = pane.querySelector('pre');
        pre.tabIndex = 0;  // so the keyboard can scroll it
        title.textContent += ` · ${pre.querySelectorAll(':scope > [id]').length} lines`;
        if (pane.querySelector('.tip')) {  // notes: hovering, tapping or tabbing to a chunk lights its lines and shows its note
          let note = pane.querySelector('.note');
          if (note) note.append(document.createElement('br'));
          else pane.querySelector('.bar').after(note = Object.assign(document.createElement('p'), {className: 'note'}));
          note.insertAdjacentHTML('beforeend', '<span class="mouse">Hover over</span><span class="touch">Tap</span> a block of code to see what it does.');
          let on = '-1', lit = [], tip, at, ptr, touch = false;  // ptr: the mouse's [x, y] while it is over the code
          const light = c => {
            if (c === on) return;
            lit.forEach(e => e.classList.remove('on'));
            lit = c === '-1' ? [] : [...pre.querySelectorAll(`[data-c="${c}"]`), tip = $(`note-${c}`)];
            lit.forEach(e => e.classList.add('on'));
            on = c;
          };
          // The note goes just below the row (above it if asked or if there is no room below), near x, inside the viewport
          const place = (row, x, up) => {
            const r = row.getBoundingClientRect(), {clientWidth: W, clientHeight: H} = document.documentElement;
            const h = tip.offsetHeight;
            if (up ? r.top - h - 6 < 0 : r.bottom + h + 6 > H) up = !up;
            tip.style.top = `${up ? r.top - h - 6 : r.bottom + 6}px`;
            tip.style.left = `${Math.max(8, Math.min(x - 24, W - tip.offsetWidth - 8))}px`;
            at = [row, x, up];
          };
          const show = (row, x) => {
            const c = row?.dataset.c ?? '-1';
            if (c !== on) { light(c); if (row) place(row, x, false); return; }
            if (!row) return;
            const t = tip.getBoundingClientRect(), r = row.getBoundingClientRect();
            if (t.top < r.bottom && t.bottom > r.top) place(row, x, t.top > r.top);  // it never covers the row in use
          };
          const rowOf = e => e.target.closest('[data-c]');
          pre.onpointerover = e => e.pointerType !== 'touch' && show(rowOf(e), (ptr = [e.clientX, e.clientY])[0]);
          pre.onpointerleave = e => { if (e.pointerType !== 'touch') { ptr = null; light('-1'); } };
          pre.onpointerdown = e => touch = e.pointerType === 'touch';
          pre.onclick = e => touch && rowOf(e)?.dataset.c === on ? light('-1') : show(rowOf(e), e.clientX);  // a second tap closes
          pre.addEventListener('focusin', e => e.target.matches('[data-c]:focus-visible') && show(e.target, e.target.getBoundingClientRect().left + 64));
          pre.addEventListener('focusout', e => pre.contains(e.relatedTarget) || light('-1'));
          document.addEventListener('click', e => pre.contains(e.target) || light('-1'));
          document.addEventListener('keydown', e => e.key === 'Escape' && light('-1'));
          addEventListener('scroll', () => {  // the note stays by its row, and off the row now under a still mouse
            if (on === '-1') return;
            place(...at);
            if (ptr) show(document.elementFromPoint(...ptr)?.closest('[data-c]'), ptr[0]);
          }, {capture: true, passive: true});
        }
        return pre;
      });
    const show = () => load().catch(e => title.textContent = `${src}: could not load (${e.message})`);
    copy.onclick = () => load().then(pre => navigator.clipboard.writeText(pre.textContent))
      .then(() => 'Copied', () => 'Copy failed')
      .then(text => { copy.textContent = text; setTimeout(() => copy.textContent = 'Copy', 1500); });
    if (btn) btn.onclick = () => {
      pane.hidden = !pane.hidden;
      btn.textContent = pane.hidden ? 'Show code' : 'Hide code';
      btn.setAttribute('aria-expanded', !pane.hidden);
      if (!pane.hidden) show().then(() => pane.scrollIntoView({block: 'nearest'}));
    };
    if (!pane.hidden) show();
  }
}
