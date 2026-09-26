/*
 * Copy-source helpers for step-triggered effects.
 *
 * This file is never loaded at runtime. Timelines, hover and step captions,
 * toggles and per-copy ids are managed blocks under shared/runtime/, stamped
 * into each diagram by scripts/build.js; this file holds only the two
 * helpers a diagram copies by hand into its own IIFE when a step handler
 * needs them.
 *
 * Both assume they run inside the diagram's IIFE:
 *
 *   <script>(() => {
 *     const root = document.currentScript.closest('.fg-diagram');
 *     ...
 *   })();</script>
 */

/* Re-trigger a CSS animation: removing and re-adding a class only restarts
   its animation after a forced reflow. */
function restartAnimation(el, cls) {
  el.classList.remove(cls);
  void el.offsetWidth; // force reflow so the next add restarts the animation
  el.classList.add(cls);
}

/* Step-triggered comets (SMIL). Author each head's <animateMotion> with
   begin="indefinite" and chain its trails off it with syncbase timing
   (begin="xx-head.begin+0.1s"), which requires the instance-ids block. Hide
   comet groups outside their step and under prefers-reduced-motion, since
   SMIL ignores reduced motion.

   usage: root.addEventListener('fg:step', (e) => {
     if (e.detail.step === 1) launchComets(root, '.trl-comet-head');
   }); */
function launchComets(root, selector) {
  root.querySelectorAll(selector + ' animateMotion').forEach((m) => m.beginElement());
}
