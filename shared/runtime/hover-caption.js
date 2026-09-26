// Targets carry data-info (plain text), optionally data-title (shown bold
// before it) and data-code (shown as inline code after it). Focus reaches
// the same readout as the pointer; fg:hover lets a diagram add its own
// highlight classes.
const hoverTargets = [...root.querySelectorAll('[data-info]')];
function hoverHtml(el) {
  const title = el.getAttribute('data-title');
  const code = el.getAttribute('data-code');
  return (title ? '<strong>' + escHtml(title) + '</strong> — ' : '') + escHtml(el.getAttribute('data-info')) +
    (code ? ' <code>' + escHtml(code) + '</code>' : '');
}
reserveCaption(hoverTargets.map(hoverHtml));
hoverTargets.forEach((el, index) => {
  el.setAttribute('tabindex', '0');
  const set = (on) => {
    setCaption(on ? hoverHtml(el) : captionInitial);
    if (caption) caption.classList.toggle('is-active', on);
    root.dispatchEvent(new CustomEvent('fg:hover', { detail: { el, index, on } }));
  };
  el.addEventListener('mouseenter', () => set(true));
  el.addEventListener('focus', () => set(true));
  el.addEventListener('mouseleave', () => set(false));
  el.addEventListener('blur', () => set(false));
});
