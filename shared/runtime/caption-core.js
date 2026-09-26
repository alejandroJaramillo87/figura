// Captions change at runtime. Every variant is stacked invisibly in one
// grid cell, so the box takes the tallest variant's height at any column
// width and changing the caption never reflows the post.
const caption = root.querySelector('[data-fg="caption"]');
const captionInitial = caption ? caption.innerHTML : '';
const captionText = document.createElement('span');
function reserveCaption(variants) {
  if (!caption) return;
  caption.textContent = '';
  caption.classList.add('fg-cap-grid');
  for (const html of [captionInitial, ...variants]) {
    const ghost = document.createElement('span');
    ghost.className = 'fg-cap-ghost';
    ghost.setAttribute('aria-hidden', 'true');
    ghost.innerHTML = html;
    caption.appendChild(ghost);
  }
  captionText.className = 'fg-cap-live';
  captionText.setAttribute('aria-live', 'polite');
  captionText.innerHTML = captionInitial;
  caption.appendChild(captionText);
}
function setCaption(html) { captionText.innerHTML = html; }
function escHtml(t) { const s = document.createElement('span'); s.textContent = t; return s.innerHTML; }
