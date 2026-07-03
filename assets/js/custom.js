/* ==========================================================================
   QuaRCS-lab Network — hero cinematic parallax
   Loaded after the theme's script.js. Vanilla JS, no dependencies.
   Ken Burns zoom is CSS; this adds a subtle scroll parallax on the media
   layer (translate only — the inner layer owns the scale, so no conflict).
   Fully disabled for users who prefer reduced motion.
   ========================================================================== */
(function () {
  'use strict';

  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) return;

  var hero = document.getElementById('hero-area');
  if (!hero) return;
  var media = hero.querySelector('.hero-media');
  if (!media) return;

  var ticking = false;

  function update() {
    ticking = false;
    var rect = hero.getBoundingClientRect();
    // Only do work while the hero is anywhere in the viewport.
    if (rect.bottom <= 0 || rect.top >= window.innerHeight) return;
    var offset = window.pageYOffset || document.documentElement.scrollTop || 0;
    media.style.transform = 'translate3d(0,' + (offset * 0.18) + 'px,0)';
  }

  function onScroll() {
    if (!ticking) {
      ticking = true;
      window.requestAnimationFrame(update);
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });
  update();
})();
