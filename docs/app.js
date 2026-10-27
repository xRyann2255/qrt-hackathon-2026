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
    let loading;
    const load = () => loading ||= fetch(`code/${src.split('/')[1]}.html`)
      .then(r => r.ok ? r.text() : Promise.reject(Error(`HTTP ${r.status}`)))
      .then(html => {
        pane.insertAdjacentHTML('beforeend', html);
        const pre = pane.querySelector('pre');
        pre.tabIndex = 0;  // so the keyboard can scroll it
        title.textContent += ` · ${pre.querySelectorAll(':scope > [id]').length} lines`;
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
