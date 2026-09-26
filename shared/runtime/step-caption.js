// CAPTIONS[step] is plain text, or [title, text] shown as "N. title — text"
// with the caption marked active.
function stepCaptionHtml(s) {
  const c = CAPTIONS[s];
  return Array.isArray(c) ? '<strong>' + escHtml(s + '. ' + c[0]) + '</strong> \u2014 ' + escHtml(c[1]) : escHtml(c);
}
reserveCaption(CAPTIONS.map((c, s) => stepCaptionHtml(s)));
root.addEventListener('fg:step', (e) => {
  setCaption(stepCaptionHtml(e.detail.step));
  if (caption) caption.classList.toggle('is-active', Array.isArray(CAPTIONS[e.detail.step]));
});
