apply();
if (reduced) {
  tl.go(TOTAL); // show final state, manual stepping still available
} else {
  const io = new IntersectionObserver(
    // The first callback reports any overlap as intersecting, so test the
    // ratio; a reader who paused keeps control until they press play.
    (entries) => entries.forEach((e) => {
      if (e.intersectionRatio < 0.3) tl.pause();
      else if (!held) tl.play();
    }),
    { threshold: 0.3 }
  );
  io.observe(root);
}
