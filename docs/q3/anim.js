// The Q3 figure: the hidden curve g for one test and the answer f built up wave by wave, with the scores.
// Needs app.js. Data from q3/data.json, written by q3/data.py, which lists the sources.
(async () => {
  const N = 100, W = 800, H = 300, PAD = 12, S = 20;  // cells, plot size, frames per wave
  let D;
  try { D = await (await fetch('q3/data.json')).json(); } catch { return status('Could not load q3/data.json', 'error'); }

  // Orthonormal Fourier basis on the 100 cell centres, as in solution.py: 1, cos 2πx, sin 2πx, cos 4πx, ...
  const h = (k, j) => k ? Math.SQRT2 * Math[k % 2 ? 'cos' : 'sin'](2 * Math.PI * ((k + 1) >> 1) * (j + 0.5) / N) : 1;
  const name = k => k ? `${k % 2 ? 'cos' : 'sin'} ${2 * ((k + 1) >> 1)}πx` : 'the constant';
  const stages = i => {  // f after 0, 1, .. 21 waves, then the final answer, which is g
    const e = Math.sqrt(2 * D.T[i]), F = [Array(N).fill(0)];
    D.a[i].forEach((c, k) => F.push(F[k].map((v, j) => v + e * c * h(k, j))));
    return [...F, D.g[i]];
  };
  const score = (i, f) => {  // the recovered model: 20 * clip((mean(g f) - 0.5 mean(f^2)) / target, 0, 1)
    const p = f.reduce((s, v, j) => s + (D.g[i][j] * v - 0.5 * v * v) / N, 0);
    return 20 * Math.min(1, Math.max(0, p / D.T[i]));
  };
  const all = D.T.map((_, i) => stages(i));
  const total = all[0].map((_, k) => all.reduce((s, F, i) => s + score(i, F[k]), 0));

  const plot = $('plot');
  const zero = svgEl('line', {class: 'zero', x1: 0, x2: W}, plot);
  const [gl, wl, fl] = ['curve-g', 'wave', 'curve-f'].map(c => svgEl('path', {class: c}, plot));
  let y;
  const path = v => 'M0,' + v.map((x, j) => `${y(x).toFixed(1)}H${(j + 1) * W / N}`).join('V');

  function show(i) {
    const F = all[i], d = F.slice(1).map((f, s) => f.map((v, j) => v - F[s][j]));
    const vals = [...F, ...d].flat(), lo = Math.min(...vals), hi = Math.max(...vals);
    y = v => PAD + (hi - v) / (hi - lo) * (H - 2 * PAD);
    zero.setAttribute('y1', y(0)); zero.setAttribute('y2', y(0));
    gl.setAttribute('d', path(F[22]));
    $('tval').textContent = (i / 50).toFixed(2);
    const readout = k => {
      const m = D.s[k], tag = m ? 'measured' : 'model';
      metrics([['Waves in f', k < 22 ? `${k} of 21` : '21, then the residual pass'],
               ['This test', `${(m ? m[i] : score(i, F[k])).toFixed(2)} of 20, ${tag}`, true],
               ['All 51 tests', `${(m ? m.reduce((a, b) => a + b) : total[k]).toFixed(2)} of 1020, ${tag}`, true]]);
    };
    readout(0);
    play(22 * S, n => {
      const s = Math.floor(n / S), u = (n % S + 1) / S, e = u * u * (3 - 2 * u);
      if (n % S === 0) {
        status(s < 21 ? `Wave ${s + 1} of 21: ${name(s)}` : 'Residual pass: 100 small corrections, one probe each');
        wl.setAttribute('d', path(d[s]));
      }
      fl.setAttribute('d', path(F[s].map((v, j) => v + e * d[s][j])));
      wl.style.opacity = 0.5 * Math.sin(Math.PI * u);
      if (u === 1) readout(s + 1);
      if (n === 22 * S - 1) status('Final answer: 20 of 20 on all 51 tests');
    }, () => show(i), 22 * 300);
  }
  $('t').oninput = e => show(+e.target.value);
  show(+$('t').value);
})();
