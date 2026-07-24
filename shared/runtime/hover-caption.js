const caption = root.querySelector('[data-fg="caption"]');
const captionDefault = caption.textContent;
root.querySelectorAll('[data-info]').forEach((el) => {
  el.addEventListener('mouseenter', () => {
    caption.textContent = el.getAttribute('data-info');
    caption.classList.add('is-active');
  });
  el.addEventListener('mouseleave', () => {
    caption.textContent = captionDefault;
    caption.classList.remove('is-active');
  });
});
