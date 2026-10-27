// Shared by the C++ demo pages: run a solver in a Web Worker (a new run stops the previous one) and draw SVG.
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

function status(text, isError) {
  $('status').textContent = text;
  $('status').className = isError ? 'err' : '';
}
