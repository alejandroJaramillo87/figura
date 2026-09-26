const toggles = [...root.querySelectorAll('[data-fg="toggle"]')];
const segmented = toggles.length > 1; // one button per state, else one button cycles
reserveCaption(STATES.map((s) => s.cap || ''));
let state = 0;
function show(n) {
  STATES.forEach((s) => s.cls && root.classList.remove(s.cls));
  state = n;
  const s = STATES[n];
  if (s.cls) root.classList.add(s.cls);
  if (s.cap) setCaption(s.cap);
  if (segmented) toggles.forEach((b, i) => b.setAttribute('aria-pressed', String(i === n)));
  else if (s.label) toggles[0].textContent = s.label;
  else if (STATES.length === 2) toggles[0].setAttribute('aria-pressed', String(n === 1));
  root.dispatchEvent(new CustomEvent('fg:toggle', { detail: { state: n } }));
}
const tg = {
  get state() { return state; },
  show,
  next() { show((state + 1) % STATES.length); },
};
toggles.forEach((b, i) => b.addEventListener('click', () => (segmented ? show(i) : tg.next())));
show(0);
