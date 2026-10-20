// APS docs v2: theme switch, phone menu, search, "on this page" highlight, videos that play when they're on screen,
// full-size view for pictures and clips, copy buttons. No libraries.
(function () {
  "use strict";
  var root = document.documentElement;

  // ---- light / dark ------------------------------------------------------------------------------------------------
  var themeBtn = document.querySelector(".theme-btn");
  if (themeBtn) themeBtn.addEventListener("click", function () {
    var next = root.dataset.theme === "light" ? "dark" : "light";
    root.dataset.theme = next;
    try { localStorage.setItem("aps-theme", next); } catch (e) {}
  });

  // ---- phone menu --------------------------------------------------------------------------------------------------
  var menuBtn = document.querySelector(".menu-btn"), scrim = document.querySelector(".scrim");
  function setMenu(open) {
    document.body.classList.toggle("nav-open", open);
    if (scrim) scrim.hidden = !open;
    if (menuBtn) menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
  }
  if (menuBtn) menuBtn.addEventListener("click", function () { setMenu(!document.body.classList.contains("nav-open")); });
  if (scrim) scrim.addEventListener("click", function () { setMenu(false); });

  // ---- search -------------------------------------------------------------------------------------------------------
  var input = document.getElementById("search"), box = document.querySelector(".results");
  var index = window.APS_SEARCH || [];
  var base = (document.querySelector('link[rel="stylesheet"]').getAttribute("href") || "").replace(/assets\/style\.css(\?.*)?$/, "");
  var sel = -1;
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function mark(s, words) {
    var out = esc(s);
    words.forEach(function (w) { if (w.length > 1) out = out.replace(new RegExp("(" + w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig"), "<mark>$1</mark>"); });
    return out;
  }
  function search(q) {
    var words = q.toLowerCase().split(/\s+/).filter(Boolean);
    if (!words.length) return [];
    var hits = [];
    index.forEach(function (e) {
      var h = (e.h || "").toLowerCase(), p = (e.p || "").toLowerCase(), t = (e.t || "").toLowerCase(), score = 0, all = true;
      words.forEach(function (w) {
        var s = 0;
        if (h.indexOf(w) >= 0) s += h.indexOf(w) === 0 ? 12 : 8;
        if (p.indexOf(w) >= 0) s += 4;
        if (t.indexOf(w) >= 0) s += 2;
        if (!s) all = false;
        score += s;
      });
      if (all && score) hits.push({ e: e, s: score });
    });
    hits.sort(function (a, b) { return b.s - a.s; });
    return hits.slice(0, 12).map(function (x) { return x.e; });
  }
  function show() {
    var q = input.value.trim();
    if (!q) { box.hidden = true; return; }
    var words = q.toLowerCase().split(/\s+/).filter(Boolean), hits = search(q);
    sel = -1;
    box.innerHTML = hits.length ? hits.map(function (e, i) {
      var snippet = e.t || "";
      var at = words.length ? snippet.toLowerCase().indexOf(words[0]) : -1;
      if (at > 60) snippet = "…" + snippet.slice(at - 40);
      return '<a href="' + base + e.u + '" data-i="' + i + '"><div class="r-page">' + esc(e.p) + '</div><div class="r-head">' +
        mark(e.h || e.p, words) + '</div><div class="r-text">' + mark(snippet, words) + "</div></a>";
    }).join("") : '<div class="r-none">Nothing found for “' + esc(q) + '”. Try a sense, a node name or a setting.</div>';
    box.hidden = false;
  }
  if (input && box) {
    input.addEventListener("input", show);
    input.addEventListener("focus", show);
    input.addEventListener("keydown", function (ev) {
      var links = box.querySelectorAll("a");
      if (ev.key === "ArrowDown" || ev.key === "ArrowUp") {
        ev.preventDefault();
        if (!links.length) return;
        sel = (sel + (ev.key === "ArrowDown" ? 1 : -1) + links.length) % links.length;
        links.forEach(function (a, i) { a.classList.toggle("sel", i === sel); });
        links[sel].scrollIntoView({ block: "nearest" });
      } else if (ev.key === "Enter" && links.length) {
        ev.preventDefault();
        window.location.href = links[sel >= 0 ? sel : 0].href;
      } else if (ev.key === "Escape") {
        box.hidden = true;
        input.blur();
      }
    });
    document.addEventListener("click", function (ev) { if (!ev.target.closest(".search")) box.hidden = true; });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "/" && document.activeElement !== input && !/input|textarea/i.test(document.activeElement.tagName)) {
        ev.preventDefault();
        input.focus();
      }
    });
  }

  // ---- "on this page": highlight the section being read ---------------------------------------------------------
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll(".toc a"));
  if (tocLinks.length && "IntersectionObserver" in window) {
    var targets = tocLinks.map(function (a) { return document.getElementById(a.getAttribute("href").slice(1)); }).filter(Boolean);
    var current = null;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) current = en.target.id; });
      tocLinks.forEach(function (a) { a.classList.toggle("on", a.getAttribute("href") === "#" + current); });
    }, { rootMargin: "-80px 0px -70% 0px" });
    targets.forEach(function (t) { io.observe(t); });
  }

  // ---- videos: load and play only while on screen (pages stay light) ------------------------------------------
  var vids = document.querySelectorAll("video[data-src]");
  function load(v) { if (!v.src) { v.src = v.dataset.src; } }
  if ("IntersectionObserver" in window) {
    var vio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var v = en.target;
        if (en.isIntersecting) { load(v); var p = v.play(); if (p && p.catch) p.catch(function () {}); }
        else if (!v.paused) v.pause();
      });
    }, { rootMargin: "120px 0px", threshold: 0.25 });
    vids.forEach(function (v) { vio.observe(v); });
  } else vids.forEach(function (v) { load(v); v.autoplay = true; });
  document.querySelectorAll(".media.video video").forEach(function (v) {
    v.addEventListener("click", function () { if (v.paused) v.play(); else v.pause(); });
  });

  // ---- full size view ------------------------------------------------------------------------------------------------
  var lb = document.querySelector(".lightbox"), stage = lb && lb.querySelector(".lightbox-stage");
  function closeLb() { if (!lb) return; lb.hidden = true; stage.innerHTML = ""; }
  document.querySelectorAll(".media .zoom").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var frame = btn.parentNode, img = frame.querySelector("img"), vid = frame.querySelector("video");
      if (img) {
        stage.innerHTML = '<img src="' + img.currentSrc + '" alt="">';
        // a phone shows the screenshot at its readable size, scrolling sideways, instead of shrunk to the screen
        var w = getComputedStyle(frame.parentNode).getPropertyValue("--w").trim();
        if (w) stage.firstChild.style.setProperty("--w", w);
      }
      else if (vid) { load(vid); stage.innerHTML = '<video src="' + vid.src + '" controls autoplay loop muted playsinline></video>'; }
      lb.classList.toggle("is-image", !!img);
      lb.hidden = false;
    });
    var pic = btn.parentNode.querySelector("img");
    if (pic) pic.addEventListener("click", function () { btn.click(); });
  });
  if (lb) {
    lb.addEventListener("click", function (ev) { if (ev.target === lb || ev.target.classList.contains("lightbox-close")) closeLb(); });
    document.addEventListener("keydown", function (ev) { if (ev.key === "Escape") closeLb(); });
  }

  // ---- copy buttons ------------------------------------------------------------------------------------------------
  document.querySelectorAll(".code .copy").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var text = btn.parentNode.querySelector("code").innerText;
      function done() { btn.textContent = "Copied"; btn.classList.add("done"); setTimeout(function () { btn.textContent = "Copy"; btn.classList.remove("done"); }, 1400); }
      if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, function () {});
      else {
        var ta = document.createElement("textarea"); ta.value = text; document.body.appendChild(ta); ta.select();
        try { document.execCommand("copy"); done(); } catch (e) {}
        document.body.removeChild(ta);
      }
    });
  });

  // ==== motion ===========================================================================================================
  // Everything below only decorates and explains: the page reads the same without it, "reduce motion" gets still
  // frames, and nothing animates while it is off screen or the tab is hidden.
  var still = !!(window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches);
  var hasIO = "IntersectionObserver" in window;
  var MONO = '"Cascadia Code", Consolas, "SFMono-Regular", Menlo, monospace';

  // ---- the lifecycle every live meter plays (17 s): it grows sure of you, then loses you and forgets ------------------
  var NAMES = ["Undetected", "Suspected", "Detected", "Tracked", "Lost", "Remembered", "Expired"];
  var WHY = ["not seen yet", "“What was that?”", "“There you are.”", "full chase",
             "senses silent: it searches", "stays alert near where you were", "memory gone"];
  var DARK = ["#9fb1c1", "#f4d27a", "#ffb454", "#ff6b5e", "#a78bfa", "#64a8ff", "#7f8fa1"];
  var LIGHT = ["#66768a", "#9a6a00", "#b35c00", "#c8372b", "#7c5cd6", "#1f6fd1", "#66768a"];
  var LOOP = 17;
  function ease(u) { return u < .5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2; }
  function life(t) {
    t = t % LOOP;
    var v = 0, s = 0, sight = 0, hear = 0, mem = 0, u, step = Math.abs(Math.sin(t * 4.2));
    if (t < 1.2) { /* nothing yet */ }
    else if (t < 6.4) { u = (t - 1.2) / 5.2; v = 86 * ease(u); s = v < 15 ? 0 : v < 35 ? 1 : v < 60 ? 2 : 3; sight = Math.min(1, .2 + u * 1.1); hear = .3 + .35 * step; mem = v / 160; }
    else if (t < 8.6) { v = 86 + 2 * Math.sin((t - 6.4) * 3); s = 3; sight = .94 + .06 * Math.sin(t * 7); hear = .3 + .35 * step; mem = .55; }
    else if (t < 10.6) { u = (t - 8.6) / 2; v = 86 - 28 * u; s = 4; sight = Math.max(0, .9 - u * 3); hear = .2 * step * (1 - u); mem = .55 + .45 * u; }
    else if (t < 14.2) { u = (t - 10.6) / 3.6; v = 9 + 49 * Math.pow(1 - u, 1.4); s = 5; mem = 1 - .5 * u; }
    else if (t < 15.6) { u = (t - 14.2) / 1.4; v = 9 * (1 - u); s = 6; mem = .5 * (1 - u); }
    return { v: v, s: s, sight: sight, hear: hear, mem: mem };
  }
  // calls frame(seconds) every animation frame while el is on screen; a single still frame for "reduce motion"
  function whileVisible(el, frame, stillAt) {
    if (still) { frame(stillAt); return; }
    var on = !hasIO, raf = 0, t0 = performance.now();
    function tick(now) { raf = 0; if (!on || document.hidden) return; frame((now - t0) / 1000); raf = requestAnimationFrame(tick); }
    function start() { if (!raf && on && !document.hidden) raf = requestAnimationFrame(tick); }
    if (hasIO) new IntersectionObserver(function (en) { on = en[en.length - 1].isIntersecting; start(); }).observe(el);
    document.addEventListener("visibilitychange", start);
    start();
  }

  // the home hero's APS panel
  var hud = document.querySelector(".hero-hud");
  if (hud) {
    var hState = hud.querySelector(".hud-state"), hN = hud.querySelector(".hud-pct .n"), hBar = hud.querySelector(".meter"),
        hRows = hud.querySelectorAll(".hud-rows div"), hWhy = hud.querySelector(".why"), hLast = -1;
    whileVisible(hud, function (t) {
      var L = life(t);
      if (L.s !== hLast) { hLast = L.s; hState.textContent = NAMES[L.s].toUpperCase(); hWhy.textContent = WHY[L.s]; hud.style.setProperty("--c", DARK[L.s]); }
      hN.textContent = Math.round(L.v);
      hBar.style.setProperty("--v", L.v.toFixed(1));
      [L.sight, L.hear, L.mem].forEach(function (x, i) {
        hRows[i].style.setProperty("--v", Math.round(x * 100));
        hRows[i].querySelector("em").textContent = Math.round(x * 100);
      });
    }, 7.4);
  }

  // the Confidence page's seven states, played live: a meter on top lights each state as the AI passes through it
  var strip = document.querySelector(".states");
  if (strip) {
    var cards = strip.querySelectorAll(".state");
    var cm = document.createElement("div");
    cm.className = "cmeter";
    cm.setAttribute("aria-hidden", "true");
    cm.innerHTML = '<div class="cm-top"><span class="cm-state"></span><span class="cm-why"></span><span class="cm-pct"></span></div>' +
      '<div class="meter"><i></i><s style="left:15%"></s><s style="left:35%"></s><s style="left:60%"></s></div>' +
      '<div class="cm-marks"><span style="left:15%">15</span><span style="left:35%">35</span><span style="left:60%">60</span></div>';
    strip.insertBefore(cm, strip.firstChild);
    var cmS = cm.querySelector(".cm-state"), cmW = cm.querySelector(".cm-why"), cmP = cm.querySelector(".cm-pct"),
        cmB = cm.querySelector(".meter"), cmLast = -1, cmTheme = "";
    whileVisible(strip, function (t) {
      var L = life(t), theme = root.dataset.theme || "dark";
      if (L.s !== cmLast || theme !== cmTheme) {
        cmLast = L.s; cmTheme = theme;
        cmS.textContent = NAMES[L.s]; cmW.textContent = WHY[L.s];
        var pal = theme === "light" ? LIGHT : DARK;
        cm.style.setProperty("--c", pal[L.s]);
        cards.forEach(function (c, i) { c.style.setProperty("--c", pal[i]); c.classList.toggle("lit", i === L.s); });
      }
      cmP.textContent = Math.round(L.v) + "%";
      cmB.style.setProperty("--v", L.v.toFixed(1));
    }, 7.4);
  }

  // ---- scrolling: the reading progress line, the steps' line filling up, the hero clip drifting slower ------------
  var bar = document.querySelector(".progress"), stepEls = document.querySelectorAll(".steps .step"),
      heroVid = document.querySelector(".hero video"), ticking = false;
  function onScroll() {
    ticking = false;
    var max = document.documentElement.scrollHeight - innerHeight, mid = innerHeight * .55;
    if (bar) bar.style.setProperty("--p", max > 0 ? Math.min(1, Math.max(0, scrollY / max)).toFixed(4) : "0");
    stepEls.forEach(function (s) {
      var r = s.getBoundingClientRect(), f = (mid - (r.top + 48)) / Math.max(1, r.height - 48);
      s.style.setProperty("--fill", Math.max(0, Math.min(1, f)).toFixed(3));
      s.classList.toggle("now", r.top < mid && r.bottom > mid);
    });
    if (heroVid && !still && scrollY < innerHeight * 1.3) heroVid.style.transform = "translate3d(0," + (scrollY * .3).toFixed(1) + "px,0)";
  }
  addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  addEventListener("resize", onScroll);
  onScroll();

  // ---- things slide softly into place as they come on screen --------------------------------------------------------
  if (hasIO && !still) {
    var rvEls = document.querySelectorAll([".band-head", ".path", ".pillar", ".showcase > *", ".anyai figure", ".versus .row", ".cta",
      "article > h2", "article > .media", "article > .fast", "article > .table", "article > .callout", "article > .deep",
      "article > .try", "article > .states", "article > .split", ".steps > .step", ".grid > .card", ".prevnext a"].join(","));
    root.classList.add("anim");
    var rio = new IntersectionObserver(function (entries) {
      var k = 0;
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target;
        rio.unobserve(el);
        el.style.setProperty("--d", Math.min(k++ * .07, .42) + "s");
        el.classList.add("in", "seen");
      });
    }, { rootMargin: "0px 0px -6% 0px", threshold: .06 });
    rvEls.forEach(function (el) {
      el.classList.add("rv");
      el.addEventListener("transitionend", function done(ev) {
        if (ev.target !== el || ev.propertyName !== "opacity" || !el.classList.contains("in")) return;
        el.classList.remove("rv", "in");          // hand the element its own hover motion back
        el.style.removeProperty("--d");
        el.removeEventListener("transitionend", done);
      });
      rio.observe(el);
    });
  }

  // ---- a light that follows the cursor across cards ----------------------------------------------------------------
  document.querySelectorAll(".card, .path, .pillar, .prevnext a").forEach(function (el) { el.classList.add("glow"); });
  if (window.matchMedia && matchMedia("(hover: hover)").matches) {
    document.addEventListener("pointermove", function (ev) {
      var el = ev.target.closest && ev.target.closest(".glow");
      if (!el) return;
      var r = el.getBoundingClientRect();
      el.style.setProperty("--mx", (ev.clientX - r.left).toFixed(0) + "px");
      el.style.setProperty("--my", (ev.clientY - r.top).toFixed(0) + "px");
    }, { passive: true });
  }

  // ---- the perception field: the page's background is a tiny APS world ----------------------------------------------
  // Guards sweep their view cones (which stop at walls, like the Visualizer's). Whatever wanders into a cone, the mouse
  // included, makes that guard surer: teal, then gold (Suspected), orange (Detected), red (Tracked). It turns to watch
  // what it has detected, pings when it does, and marks the last known spot when it loses it.
  (function () {
    var cv = document.querySelector(".bg-field");
    if (!cv || !cv.getContext) return;
    var ctx = cv.getContext("2d"), W = 0, H = 0, dpr = 1, seed = 1;
    var walls = [], guards = [], movers = [], pings = [], ghosts = [], T = [], col = null;
    var ptr = { x: 0, y: 0, t: -1e9 }, mouse = !!(window.matchMedia && matchMedia("(pointer: fine)").matches);
    function rnd() {          // a fixed sequence, so the little world is laid out the same on every page
      seed = seed + 0x6D2B79F5 | 0;
      var t = Math.imul(seed ^ seed >>> 15, 1 | seed);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    }
    function hex(v) {
      v = (v || "").trim();
      if (v.charAt(0) !== "#") return [128, 128, 128];
      if (v.length === 4) v = "#" + v[1] + v[1] + v[2] + v[2] + v[3] + v[3];
      return [parseInt(v.slice(1, 3), 16), parseInt(v.slice(3, 5), 16), parseInt(v.slice(5, 7), 16)];
    }
    function colors() {
      var cs = getComputedStyle(root), light = root.dataset.theme === "light";
      col = { k: light ? 1.35 : 1, ink: hex(cs.getPropertyValue("--text")), mem: hex(cs.getPropertyValue("--info")),
              ramp: ["--accent", "--gold", "--warn", "--danger"].map(function (n) { return hex(cs.getPropertyValue(n)); }) };
      guards.forEach(function (g) { g.c = col.ramp[0].slice(); });
    }
    function rgba(c, a) {
      return "rgba(" + Math.round(c[0]) + "," + Math.round(c[1]) + "," + Math.round(c[2]) + "," + Math.max(0, Math.min(1, a * col.k)).toFixed(3) + ")";
    }
    function angDiff(a, b) { var d = (a - b) % 6.2832; if (d > 3.1416) d -= 6.2832; if (d < -3.1416) d += 6.2832; return d; }
    // how far a ray from (x, y) along (dx, dy) gets before a wall, up to maxd (the slab test, one wall at a time)
    function hit(x, y, dx, dy, maxd) {
      var best = maxd;
      for (var i = 0; i < walls.length; i++) {
        var w = walls[i], lo = 0, hi = best, t1, t2, s;
        if (Math.abs(dx) < 1e-9) { if (x < w.x || x > w.x + w.w) continue; }
        else { t1 = (w.x - x) / dx; t2 = (w.x + w.w - x) / dx; if (t1 > t2) { s = t1; t1 = t2; t2 = s; } lo = Math.max(lo, t1); hi = Math.min(hi, t2); if (lo > hi) continue; }
        if (Math.abs(dy) < 1e-9) { if (y < w.y || y > w.y + w.h) continue; }
        else { t1 = (w.y - y) / dy; t2 = (w.y + w.h - y) / dy; if (t1 > t2) { s = t1; t1 = t2; t2 = s; } lo = Math.max(lo, t1); hi = Math.min(hi, t2); if (lo > hi) continue; }
        if (lo < best) best = lo;
      }
      return best;
    }
    function world() {
      seed = 1337;
      var n = W > 1300 ? 5 : W > 760 ? 4 : 3, range = Math.max(150, Math.min(320, Math.min(W, H) * .36)), i, k;
      guards = []; walls = []; movers = []; pings = []; ghosts = [];
      for (i = 0; i < n; i++) {
        var g = { x: W * (i + .5) / n + (rnd() - .5) * W / n * .5, y: H * (.16 + rnd() * .68), base: rnd() * 6.2832, amp: .45 + rnd() * .5,
                  per: 9 + rnd() * 8, ph: rnd() * 6.28, range: range * (.85 + rnd() * .3), fov: .5 + rnd() * .12,
                  c: col.ramp[0].slice(), conf: [], seen: [], best: 0 };
        g.a = g.base;
        guards.push(g);
      }
      for (i = 0, k = 0; i < (W > 900 ? 6 : 3) && k < 60; k++) {
        var horiz = rnd() < .55, len = 70 + rnd() * 120, th = 10 + rnd() * 6;
        var w = { x: rnd() * (W - len), y: H * .06 + rnd() * H * .86, w: horiz ? len : th, h: horiz ? th : len * .8 };
        var clear = guards.every(function (g) {
          return g.x < w.x - 36 || g.x > w.x + w.w + 36 || g.y < w.y - 36 || g.y > w.y + w.h + 36;
        });
        if (clear) { walls.push(w); i++; }
      }
      for (i = 0; i < 2; i++) movers.push({ f1: .035 + rnd() * .02, f2: .028 + rnd() * .02, p1: rnd() * 6.28, p2: rnd() * 6.28 });
    }
    function targets(t, now) {
      T = movers.map(function (m) { return { x: W * (.5 + .44 * Math.sin(t * m.f1 + m.p1)), y: H * (.5 + .4 * Math.sin(t * m.f2 + m.p2)) }; });
      T.push({ x: ptr.x, y: ptr.y, me: true, gone: !(mouse && now - ptr.t < 3500) });
    }
    function step(t, dt) {
      guards.forEach(function (g) {
        var best = 0, bestI = -1, anySeen = false;
        T.forEach(function (p, i) {
          var dx = p.x - g.x, dy = p.y - g.y, d = Math.sqrt(dx * dx + dy * dy), seen = false, c = g.conf[i] || 0;
          if (!p.gone && d < g.range && d > 1 && Math.abs(angDiff(Math.atan2(dy, dx), g.a)) < g.fov && hit(g.x, g.y, dx / d, dy / d, d) >= d - .5) seen = true;
          if (seen) c = Math.min(1, c + dt * (.16 + .5 * (1 - d / g.range)) * (p.me ? 1.5 : 1));
          else c = Math.max(0, c - dt * (c > .35 ? .07 : .12));
          if (seen && c >= .35 && (g.conf[i] || 0) < .35) pings.push({ x: p.x, y: p.y, t: t, c: col.ramp[2] });
          if (!seen && g.seen[i] && c >= .35 && !p.gone) ghosts.push({ x: p.x, y: p.y, t: t });
          g.conf[i] = c; g.seen[i] = seen;
          if (seen) anySeen = true;
          if (c > best) { best = c; bestI = i; }
        });
        var want = g.base + g.amp * Math.sin(t * 6.2832 / g.per + g.ph);
        if (bestI >= 0 && best >= .35 && g.seen[bestI]) want = Math.atan2(T[bestI].y - g.y, T[bestI].x - g.x);
        var turn = 1.4 * dt;
        g.a += Math.max(-turn, Math.min(turn, angDiff(want, g.a)));
        g.best = best; g.anySeen = anySeen;
        var tc = col.ramp[best < .15 ? 0 : best < .35 ? 1 : best < .6 ? 2 : 3], u = Math.min(1, dt * 3);
        for (var k = 0; k < 3; k++) g.c[k] += (tc[k] - g.c[k]) * u;
      });
      pings = pings.filter(function (p) { return t - p.t < 1.4; });
      ghosts = ghosts.filter(function (p) { return t - p.t < 6; });
    }
    function draw(t) {
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, W, H);
      ctx.lineWidth = 1;
      walls.forEach(function (w) {                       // cover: little blocks, like the demo's grey walls seen from above
        ctx.beginPath();
        if (ctx.roundRect) ctx.roundRect(w.x + .5, w.y + .5, w.w - 1, w.h - 1, 3); else ctx.rect(w.x + .5, w.y + .5, w.w - 1, w.h - 1);
        ctx.fillStyle = rgba(col.ink, .06); ctx.fill();
        ctx.strokeStyle = rgba(col.ink, .17); ctx.stroke();
        ctx.strokeStyle = rgba(col.ink, .07);
        ctx.beginPath();
        if (w.w > w.h) { ctx.moveTo(w.x + 4, w.y + w.h / 2); ctx.lineTo(w.x + w.w - 4, w.y + w.h / 2); }
        else { ctx.moveTo(w.x + w.w / 2, w.y + 4); ctx.lineTo(w.x + w.w / 2, w.y + w.h - 4); }
        ctx.stroke();
      });
      guards.forEach(function (g) {
        var c = g.c, N = 32, a0 = g.a - g.fov, da = 2 * g.fov / N, i, a, dx, dy, r;
        ctx.beginPath(); ctx.moveTo(g.x, g.y);
        for (i = 0; i <= N; i++) { a = a0 + da * i; dx = Math.cos(a); dy = Math.sin(a); r = hit(g.x, g.y, dx, dy, g.range); ctx.lineTo(g.x + dx * r, g.y + dy * r); }
        ctx.closePath();
        var gr = ctx.createRadialGradient(g.x, g.y, 0, g.x, g.y, g.range);
        gr.addColorStop(0, rgba(c, .2 + g.best * .14)); gr.addColorStop(.65, rgba(c, .06)); gr.addColorStop(1, rgba(c, 0));
        ctx.fillStyle = gr; ctx.fill();
        ctx.strokeStyle = rgba(c, .13); ctx.stroke();
        T.forEach(function (p, i) {                       // sight lines to whatever it can see
          if (!g.seen[i]) return;
          var cf = g.conf[i];
          ctx.setLineDash(cf < .35 ? [3, 5] : []);
          ctx.strokeStyle = rgba(c, .22 + cf * .5);
          ctx.beginPath(); ctx.moveTo(g.x, g.y); ctx.lineTo(p.x, p.y); ctx.stroke();
        });
        ctx.setLineDash([]);
        ctx.fillStyle = rgba(c, .9); ctx.beginPath(); ctx.arc(g.x, g.y, 3.5, 0, 6.2832); ctx.fill();
        ctx.strokeStyle = rgba(c, .35); ctx.beginPath(); ctx.arc(g.x, g.y, 9, 0, 6.2832); ctx.stroke();
        var name = g.anySeen ? (g.best < .15 ? "" : g.best < .35 ? "SUSPECTED" : g.best < .6 ? "DETECTED" : "TRACKED")
                             : (g.best >= .35 ? "LOST" : g.best >= .08 ? "REMEMBERED" : "");
        if (name) {
          ctx.font = "600 10px " + MONO;
          ctx.fillStyle = g.anySeen ? rgba(c, .8) : rgba(col.mem, .7);
          ctx.fillText(name + " " + Math.round(g.best * 100) + "%", g.x + 13, g.y - 11);
        }
      });
      T.forEach(function (p) {                           // the wanderers (the mouse needs no dot: it's your cursor)
        if (p.me) return;
        ctx.fillStyle = rgba(col.ink, .7); ctx.beginPath(); ctx.arc(p.x, p.y, 3, 0, 6.2832); ctx.fill();
        ctx.strokeStyle = rgba(col.ink, .16); ctx.beginPath(); ctx.arc(p.x, p.y, 7.5, 0, 6.2832); ctx.stroke();
      });
      pings.forEach(function (p) {
        var u = (t - p.t) / 1.4;
        ctx.strokeStyle = rgba(p.c, .6 * (1 - u)); ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.arc(p.x, p.y, 6 + 54 * ease(Math.min(1, u)), 0, 6.2832); ctx.stroke();
      });
      ctx.lineWidth = 1;
      ghosts.forEach(function (p) {
        var u = (t - p.t) / 6;
        ctx.setLineDash([3, 4]); ctx.strokeStyle = rgba(col.mem, .55 * (1 - u));
        ctx.beginPath(); ctx.arc(p.x, p.y, 11, 0, 6.2832); ctx.stroke(); ctx.setLineDash([]);
        ctx.font = "600 9.5px " + MONO; ctx.fillStyle = rgba(col.mem, .6 * (1 - u));
        ctx.fillText("LAST KNOWN", p.x + 15, p.y + 3);
      });
    }
    var lastW = 0;
    function size() {
      dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      W = innerWidth; H = innerHeight;
      cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
      if (W !== lastW) { lastW = W; world(); }        // phones change height while scrolling: keep the world then
    }
    colors(); size();
    if (window.MutationObserver) new MutationObserver(colors).observe(root, { attributes: true, attributeFilter: ["data-theme"] });
    addEventListener("resize", function () { size(); if (still) { targets(6, 0); draw(6); } });
    addEventListener("pointermove", function (e) { if (e.pointerType === "mouse") { ptr.x = e.clientX; ptr.y = e.clientY; ptr.t = performance.now(); } }, { passive: true });
    if (still) {                                       // one calm frame, a few seconds into the story
      for (var s = 0; s < 6; s += .05) { targets(s, 0); step(s, .05); }
      draw(6);
      return;
    }
    var t0 = performance.now(), last = 0, raf = 0;
    function frame(now) {
      raf = 0;
      if (document.hidden) return;
      var t = (now - t0) / 1000;
      if (t - last >= 1 / 45) {                        // slow motion needs no more than ~45 frames a second
        var dt = Math.min(.05, t - last); last = t;
        targets(t, now); step(t, dt); draw(t);
      }
      raf = requestAnimationFrame(frame);
    }
    document.addEventListener("visibilitychange", function () { if (!document.hidden && !raf) raf = requestAnimationFrame(frame); });
    raf = requestAnimationFrame(frame);
  })();
})();
