// The Q3 figure: the hidden curve g for one test and the answer f built up wave by wave, with the scores.
// Needs app.js. Data from q3/data.json, written by q3/data.py, which lists the sources.
(async () => {
  const N = 100, W = 800, H = 300, PAD = 16, S = 20;  // cells, plot size, frames per wave
  let D;
  try { D = await (await fetch('q3/data.json')).json(); } catch { return status('Could not load q3/data.json', 'error'); }

  // Orthonormal Fourier basis on the 100 cell centres, as in solution.py: 1, cos 2πx, sin 2πx, cos 4πx, ...
  const h = (k, j) => k ? Math.SQRT2 * Math[k % 2 ? 'cos' : 'sin'](2 * Math.PI * ((k + 1) >> 1) * (j + 0.5) / N) : 1;
  const name = k => k ? `${k % 2 ? 'cos' : 'sin'} ${2 * ((k + 1) >> 1)}πx` : 'the constant';
  const wave = (i, k) => {  // the status line for wave k of test i, with its size in g's units, as drawn
    const A = Math.sqrt(2 * D.T[i]) * D.a[i][k] * (k ? Math.SQRT2 : 1), size = (A < 0 ? '−' : '') + Math.abs(A).toPrecision(2);
    if (!A) return `Wave ${k + 1}, ${name(k)}: too small for its 2 probes to read`;  // both probes scored 0
    return `Adding wave ${k + 1}: ${k ? `${size} × ${name(k)}` : `the constant ${size}`}, read from 2 probes`;
  };
  const stages = i => {  // f after 0, 1, .. 21 waves, then the final answer, which is g
    const e = Math.sqrt(2 * D.T[i]), F = [Array(N).fill(0)];
    D.a[i].forEach((c, k) => F.push(F[k].map((v, j) => v + e * c * h(k, j))));
    return [...F, D.g[i]];
  };
  // The recovered model: 20 * clip(payoff / target, 0, 1), payoff = mean(g f) - 0.5 mean(f^2), target = 0.5 mean(g^2),
  // the same as 20 * (1 - mean (g - f)^2 / mean g^2). The target comes from g, not the 4 decimal D.T: that matches the
  // measured stage scores to 0.06 points per test.
  const score = (i, f) => {
    const g = D.g[i], p = f.reduce((s, v, j) => s + g[j] * v - 0.5 * v * v, 0);
    return 20 * Math.min(1, Math.max(0, p / g.reduce((s, v) => s + 0.5 * v * v, 0)));
  };
  const all = D.T.map((_, i) => stages(i));
  const total = all[0].map((_, k) => all.reduce((s, F, i) => s + score(i, F[k]), 0));
  const sum = k => D.s[k].reduce((a, b) => a + b);

  // Progress strip: a mark per wave, then the final pass; tall marks where HackerRank measured the total
  const strip = $('strip'), K = Object.keys(D.s).map(Number);  // measured after 5, 11, 21 waves and 22, the final
  const segs = Array.from({length: 22}, () => strip.appendChild(document.createElement('i')));
  const tots = K.map((k, n) => {
    const e = strip.appendChild(document.createElement('span'));
    segs[k - 1].className = 'm';
    e.className = 'tot'; e.style.gridColumn = `${(K[n - 1] || 0) + 1} / ${k + 1}`; e.textContent = +sum(k).toFixed(2);
    return e;
  });

  const plot = $('plot');
  const zero = svgEl('line', {class: 'zero', x1: 0, x2: W}, plot);
  const [gap, gl, wl, fl] = ['gap', 'curve-g', 'wave', 'curve-f'].map(c => svgEl('path', {class: c}, plot));
  let y;
  const path = v => 'M0,' + v.map((x, j) => `${y(x).toFixed(1)}H${(j + 1) * W / N}`).join('V');
  const back = v => v.map((x, j) => `V${y(x).toFixed(1)}H${j * W / N}`).reverse().join('');  // path, right to left
  const at = (id, v) => $(id).style.top = y(v) / H * 100 + '%';  // an HTML label beside the plot, level with v

  let hold;  // the 5 s pause on the final frame before the loop restarts; every restart clears it, so one loop runs
  function show(i) {
    clearTimeout(hold);
    const F = all[i], g = F[22], d = F.slice(1).map((f, s) => f.map((v, j) => v - F[s][j]));
    const vals = [...F, ...d].flat(), lo = Math.min(...vals), hi = Math.max(...vals);
    y = v => PAD + (hi - v) / (hi - lo) * (H - 2 * PAD);
    zero.setAttribute('y1', y(0)); zero.setAttribute('y2', y(0));
    gl.setAttribute('d', path(g));
    at('y0', 0); at('lg', g[N - 1]);
    $('tval').textContent = (i / 50).toFixed(2);
    const draw = f => {  // f and the shaded gap; the two end labels sit on opposite sides, so they never overlap
      fl.setAttribute('d', path(f));
      gap.setAttribute('d', path(f) + back(g) + 'Z');
      at('lf', f[N - 1]);
      $('lf').classList.toggle('up', f[N - 1] >= g[N - 1]);
      $('lg').classList.toggle('up', f[N - 1] < g[N - 1]);
    };
    const readout = k => {  // k waves done, wave k next: the scores, the strip and the status, all in one step
      const m = D.s[k], tag = m ? 'measured' : 'model';
      metrics([['Waves in f', k < 22 ? `${k} of 21` : '21, then the final pass'],
               ['This test', `${(m ? m[i] : score(i, F[k])).toFixed(2)} of 20, ${tag}`, true],
               ['All 51 tests', `${(m ? sum(k) : total[k]).toFixed(2)} of 1020, ${tag}`, true]]);
      segs.forEach((e, s) => { e.classList.toggle('on', s < k); e.classList.toggle('cur', s === k); });
      tots.forEach((e, n) => e.classList.toggle('on', K[n] <= k));
      status(k < 21 ? wave(i, k) : k < 22 ? 'Final pass: 100 small corrections, 1 probe each' : 'Final answer: 20 of 20 on all 51 tests');
    };
    readout(0);
    draw(F[0]);
    play(22 * S, n => {
      const s = Math.floor(n / S), u = (n % S + 1) / S, e = u * u * (3 - 2 * u);
      if (n % S === 0) wl.setAttribute('d', path(d[s]));
      draw(F[s].map((v, j) => v + e * d[s][j]));
      wl.style.opacity = 0.5 * Math.sin(Math.PI * u);
      if (u === 1) readout(s + 1);
      if (n === 22 * S - 1 && !still.matches) hold = setTimeout(() => show(i), 5000);  // the last step, also after Skip
    }, () => show(i), 22 * 300);
  }
  $('t').oninput = e => show(+e.target.value);
  show(+$('t').value);
})();
