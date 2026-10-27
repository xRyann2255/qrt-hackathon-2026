// The background dots under the pointer light up yellow. One fixed layer, moved with a transform at most once a frame;
// its pattern is shifted to line up with the page's 22px dot grid. Mouse and trackpad only.
if (matchMedia('(hover: hover) and (pointer: fine)').matches) {
  const R = 170, STEP = 22, g = document.body.appendChild(document.createElement('div'));
  g.className = 'glow';
  let x = 0, y = 0, queued = false;
  const mod = v => ((v % STEP) + STEP) % STEP;
  const paint = () => {
    queued = false;
    const left = x - R, top = y - R;
    g.style.transform = `translate3d(${left}px, ${top}px, 0)`;
    g.style.backgroundPosition = `${-mod(left + scrollX)}px ${-mod(top + scrollY)}px`;
  };
  const queue = () => { if (!queued) { queued = true; requestAnimationFrame(paint); } };
  addEventListener('pointermove', e => { x = e.clientX; y = e.clientY; g.classList.add('on'); queue(); }, {passive: true});
  addEventListener('scroll', queue, {passive: true});
  document.addEventListener('mouseout', e => { if (!e.relatedTarget) g.classList.remove('on'); });
}
