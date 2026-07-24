apply();
if (reduced) {
  tl.go(TOTAL); // show final state, manual stepping still available
} else {
  const io = new IntersectionObserver(
    (entries) => entries.forEach((e) => (e.isIntersecting ? tl.play() : tl.pause())),
    { threshold: 0.3 }
  );
  io.observe(root);
}
