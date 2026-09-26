let step = 0, timer = null, held = false; // held: the reader paused; autoplay stays off
function apply() {
  for (let i = 0; i <= TOTAL; i++) root.classList.remove('is-step-' + i);
  root.classList.add('is-step-' + step);
  root.dispatchEvent(new CustomEvent('fg:step', { detail: { step } }));
}
const tl = {
  get step() { return step; },
  get playing() { return timer !== null; },
  go(n) { step = ((n % (TOTAL + 1)) + TOTAL + 1) % (TOTAL + 1); apply(); },
  next() { tl.go(step + 1); },
  prev() { tl.go(step - 1); },
  play() { if (!timer) { timer = setInterval(() => tl.next(), STEP_MS); root.classList.add('is-playing'); } },
  pause() { clearInterval(timer); timer = null; root.classList.remove('is-playing'); },
};
const btn = (name) => root.querySelector('[data-fg="' + name + '"]');
btn('prev').addEventListener('click', () => { held = true; tl.pause(); tl.prev(); });
btn('next').addEventListener('click', () => { held = true; tl.pause(); tl.next(); });
btn('play').addEventListener('click', () => { held = tl.playing; held ? tl.pause() : tl.play(); });
const counter = btn('counter');
function sync() {
  if (counter) counter.textContent = tl.step + ' / ' + TOTAL;
  btn('play').textContent = tl.playing ? '\u275A\u275A' : '\u25B6\uFE0E'; // FE0E: text glyph, not emoji
  btn('play').setAttribute('aria-pressed', String(tl.playing));
}
root.addEventListener('fg:step', sync);
root.querySelectorAll('.fg-controls button').forEach((b) => b.addEventListener('click', sync));
const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
