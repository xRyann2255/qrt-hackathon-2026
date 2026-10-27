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
  if (state !== 'done') { cancelAnimationFrame(frame); $('skip').hidden = true; }
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
let frame;
function play(n, step, replay, ms = 1500) {
  cancelAnimationFrame(frame);
  const btn = $('skip'), t0 = performance.now();
  let i = 0;
  const upTo = k => { while (i < Math.min(k, n)) step(i++); };
  const finish = () => { cancelAnimationFrame(frame); upTo(n); btn.textContent = 'Replay'; btn.onclick = replay; };
  btn.hidden = false;
  btn.textContent = 'Skip animation';
  btn.onclick = finish;
  if (still.matches) return finish();
  const tick = now => { upTo(Math.ceil((now - t0) / ms * n)); if (i < n) frame = requestAnimationFrame(tick); else finish(); };
  frame = requestAnimationFrame(tick);
}
