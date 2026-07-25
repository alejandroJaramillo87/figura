const root = document.currentScript.closest('.fg-diagram');
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
if (reduced) {
  root.classList.add('is-settled'); // final composition, no motion
} else {
  let started = false;
  const io = new IntersectionObserver((entries) => entries.forEach((e) => {
    if (!started) {
      if (!e.isIntersecting) return;
      started = true; // intro plays once per page load
      root.classList.add('is-live');
      setTimeout(() => root.classList.add('is-settled'), INTRO_MS);
    } else {
      root.classList.toggle('is-paused', !e.isIntersecting);
    }
  }), { threshold: 0.3 });
  io.observe(root);
}
