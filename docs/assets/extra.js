/* ═══════════════════════════════════════════════════════════════════════════
   APS documentation — behaviour layer

   Two things only:
     1. Opt in to page-load animation (so content is fully visible without JS)
     2. A reading-progress bar

   Deliberately NOT here: scroll-triggered reveals. They hide content that
   Ctrl+F and anchor links jump to, which is a genuine regression in docs.
   ═══════════════════════════════════════════════════════════════════════════ */

(function () {
  "use strict";

  var reduced = window.matchMedia &&
                window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ── 1. Enable animations ───────────────────────────────────────────────
     CSS only animates under .js-anim, so with JS off or reduced motion on,
     everything renders plainly and instantly. No flash of hidden content. */
  if (!reduced) {
    document.documentElement.classList.add("js-anim");
  }

  /* ── 2. Reading progress ─────────────────────────────────────────────── */
  if (reduced) return;

  var bar = document.createElement("div");
  bar.className = "aps-progress";
  bar.setAttribute("aria-hidden", "true");

  function mount() {
    if (!document.body.contains(bar)) document.body.appendChild(bar);
    update();
  }

  var ticking = false;

  function update() {
    var doc = document.documentElement;
    var scrollable = doc.scrollHeight - doc.clientHeight;
    var ratio = scrollable > 0 ? doc.scrollTop / scrollable : 0;
    bar.style.transform = "scaleX(" + Math.min(Math.max(ratio, 0), 1) + ")";
    ticking = false;
  }

  function onScroll() {
    if (!ticking) {
      ticking = true;
      window.requestAnimationFrame(update);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll, { passive: true });
})();
