/*
 * snippets.js — reference helper patterns for slide-animator diagrams.
 *
 * This file is NEVER loaded at runtime. It is a copy source: when generating
 * a new diagram, copy the snippets you need into the diagram's inline IIFE
 * and adapt names. Keeping helpers copied (not linked) keeps every diagram
 * file a frozen, fully self-contained artifact that survives build-time
 * inlining into the blog.
 *
 * Every snippet assumes it runs inside the diagram's IIFE:
 *
 *   <script>(() => {
 *     const root = document.currentScript.closest('.sa-diagram');
 *     ...
 *   })();</script>
 */

/* ------------------------------------------------------------------ */
/* 1. Step timeline: drive a diagram through numbered states.          */
/*    Convention: root gets class `is-step-N`; CSS does the rest.      */
/* ------------------------------------------------------------------ */
function makeTimeline(root, totalSteps, stepMs) {
  let step = 0;
  let timer = null;

  function apply() {
    for (let i = 0; i <= totalSteps; i++) root.classList.remove('is-step-' + i);
    root.classList.add('is-step-' + step);
    root.dispatchEvent(new CustomEvent('sa:step', { detail: { step } }));
  }

  const tl = {
    get step() { return step; },
    get playing() { return timer !== null; },
    go(n) { step = ((n % (totalSteps + 1)) + totalSteps + 1) % (totalSteps + 1); apply(); },
    next() { tl.go(step + 1); },
    prev() { tl.go(step - 1); },
    play() {
      if (timer) return;
      timer = setInterval(() => tl.next(), stepMs);
      root.classList.add('is-playing');
    },
    pause() {
      clearInterval(timer);
      timer = null;
      root.classList.remove('is-playing');
    },
  };
  apply();
  return tl;
}

/* ------------------------------------------------------------------ */
/* 2. Control bar: prev / play-pause / next / step counter.            */
/*    Expects markup (keeps DOM authored, not generated):              */
/*      <div class="sa-controls">                                      */
/*        <button data-sa="prev" aria-label="Previous step">‹</button> */
/*        <button data-sa="play" aria-label="Play or pause">▶</button> */
/*        <button data-sa="next" aria-label="Next step">›</button>     */
/*        <span data-sa="counter"></span>                              */
/*      </div>                                                         */
/* ------------------------------------------------------------------ */
function wireControls(root, tl, totalSteps) {
  const btn = (name) => root.querySelector('[data-sa="' + name + '"]');
  const counter = btn('counter');
  btn('prev').addEventListener('click', () => { tl.pause(); tl.prev(); });
  btn('next').addEventListener('click', () => { tl.pause(); tl.next(); });
  btn('play').addEventListener('click', () => (tl.playing ? tl.pause() : tl.play()));
  function sync() {
    if (counter) counter.textContent = tl.step + ' / ' + totalSteps;
    btn('play').textContent = tl.playing ? '❚❚' : '▶';
  }
  root.addEventListener('sa:step', sync);
  root.querySelectorAll('.sa-controls button').forEach((b) => b.addEventListener('click', sync));
  sync();
}

/* ------------------------------------------------------------------ */
/* 3. Autoplay on visibility: start when ~30% visible, pause when      */
/*    scrolled away. Skip autoplay entirely under reduced motion.      */
/* ------------------------------------------------------------------ */
function autoplayWhenVisible(root, tl) {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return; // static + manual step controls only
  }
  const io = new IntersectionObserver(
    (entries) => entries.forEach((e) => (e.isIntersecting ? tl.play() : tl.pause())),
    { threshold: 0.3 }
  );
  io.observe(root);
}

/* ------------------------------------------------------------------ */
/* 4. Hover-to-inspect caption: blocks carry data-info; a caption box  */
/*    shows details for the hovered block.                             */
/*      <g class="sa-block" data-info="...">…</g>                      */
/*      <div class="sa-caption" data-sa="caption">default text</div>   */
/* ------------------------------------------------------------------ */
function wireHoverCaption(root, defaultText) {
  const caption = root.querySelector('[data-sa="caption"]');
  root.querySelectorAll('[data-info]').forEach((el) => {
    el.addEventListener('mouseenter', () => {
      caption.textContent = el.getAttribute('data-info');
      caption.classList.add('is-active');
    });
    el.addEventListener('mouseleave', () => {
      caption.textContent = defaultText;
      caption.classList.remove('is-active');
    });
  });
}
