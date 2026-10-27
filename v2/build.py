# APS docs v2: builds the docs website from the pages in content/ into _site/ (plain HTML, CSS and JS that GitHub Pages
# serves as they are). No packages to install: it runs on any Python 3.8+, including the one that ships with Unreal.
#   python build.py            ->  _site/  (open _site/index.html, or serve the folder)
#
# A page is a text file with a small header and Markdown-style body:
#   ---
#   title: Confidence
#   description: One line for search results and link previews.
#   layout: page            (or home)
#   ---
#   # Headings, **bold**, *italic*, `code`, [links](other-page.md), [[Key]] for a key cap
#   ![alt](media/clip.mp4 "caption")   on its own line: an image, or a looping video for .mp4
#   ::: fast            the 30-second version: what a busy reader needs (always open)
#   ::: deep Title      a closed "go deeper" section for readers who want the details
#   ::: steps           numbered steps, one per ### heading inside
#   ::: tip|info|warning Title
#   ::: grid            cards side by side, one ::: card Title | link | image per card
#   ::: split           two columns, separated by a line with +++
#   ::: try S2          "try it in the demo" box
#   Lines starting with < are raw HTML (for the home page's own layout).
import hashlib
import html
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "content")
THEME = os.path.join(ROOT, "theme")
MEDIA = os.path.join(ROOT, "media")
OUT = os.path.join(ROOT, "_site")

SITE = {"name": "APS Docs", "product": "Advanced Perception System",
        "url": "https://auragame33-sys.github.io/aps-docs/",
        "fab": "https://www.fab.com/", "support": "https://github.com/auragame33-sys/aps-docs/issues",
        "repo": "https://github.com/auragame33-sys/aps-docs"}

# The old MkDocs site's addresses (folder/ style), so links already out there land on the matching new page.
REDIRECTS = {
    "getting-started": "getting-started.html", "how-it-works": "how-it-works.html", "core-concepts": "how-it-works.html",
    "tutorial-complete-guard": "tutorial.html",
    "senses": "features/senses.html", "sound-system": "features/hearing.html", "memory-and-recall": "features/memory.html",
    "player-behavior-model": "features/memory.html#it-learns-how-you-play", "evidence-and-search": "features/search.html",
    "pain-and-damage": "features/emotions.html", "squad-and-relationships": "features/squads.html",
    "knowledge-and-comms": "features/knowledge.html", "environment-and-fairness": "features/world.html",
    "debugging": "features/visualizer.html", "explaining-and-recording": "features/visualizer.html#why-can-t-it-see-me",
    "archetype-cookbook": "guides/ready-made-ai.html", "how-to-guides": "guides/recipes.html",
    "behavior-trees": "guides/behavior-trees.html", "migrating-from-aiperception": "guides/from-ai-perception.html",
    "multiplayer": "guides/multiplayer.html", "profile-composition": "guides/profiles.html",
    "perception-profile": "reference/profile.html", "policies": "guides/policies.html",
    "adapters": "guides/policies.html#adapters", "custom-senses": "guides/custom-senses.html",
    "performance": "guides/performance.html", "scale-and-crowds": "guides/performance.html#many-ai-the-level-as-a-whole",
    "cheat-sheet": "reference/cheat-sheet.html", "blueprint-api": "reference/nodes.html", "events": "reference/events.html",
    "enum-reference": "reference/types.html", "troubleshooting": "help/troubleshooting.html",
}

REDIRECT_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Moved: %(title)s</title>
<meta http-equiv="refresh" content="0; url=%(to)s"><link rel="canonical" href="%(abs)s">
<meta name="robots" content="noindex"><script>var t = "%(to)s"; location.replace(t.indexOf("#") < 0 ? t + location.hash : t)</script></head>
<body style="font-family:system-ui,sans-serif;background:#0b0f14;color:#e6edf3;padding:40px">
<p>This page has moved: <a style="color:#4fd1c5" href="%(to)s">%(title)s</a>.</p></body></html>
"""

NOT_FOUND_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page not found | APS Docs</title><meta name="robots" content="noindex">
<link rel="icon" href="%(url)sassets/favicon.png"></head>
<body style="font-family:system-ui,sans-serif;background:#0b0f14;color:#e6edf3;margin:0;min-height:100vh;display:grid;place-items:center;text-align:center;padding:24px">
<div><p style="color:#4fd1c5;letter-spacing:.14em;font-weight:700;font-size:13px">404 &middot; LOST</p>
<h1 style="margin:.2em 0 .4em">It lost you.</h1><p style="color:#9fb0c0">This page doesn't exist, or it has moved.</p>
<p><a style="color:#0b0f14;background:#4fd1c5;padding:10px 18px;border-radius:10px;text-decoration:none;font-weight:700" href="%(url)s">Back to the APS docs</a></p></div></body></html>
"""

# the sidebar: (section, [(title, page)]). A page whose file doesn't exist yet shows as "soon".
NAV = [
    ("Start here", [("Home", "index.md"), ("Get Started", "getting-started.md"), ("How APS thinks", "how-it-works.md"),
                    ("Tutorial: a complete guard", "tutorial.md")]),
    ("Features", [("Confidence", "features/confidence.md"), ("The senses", "features/senses.md"),
                  ("Hearing & sounds", "features/hearing.md"), ("Memory", "features/memory.md"),
                  ("Search & evidence", "features/search.md"), ("Emotions & pain", "features/emotions.md"),
                  ("Squads & teams", "features/squads.md"), ("Knowledge & witnesses", "features/knowledge.md"),
                  ("World & fairness", "features/world.md"), ("The Visualizer", "features/visualizer.md")]),
    ("Guides", [("Ready-made AI", "guides/ready-made-ai.md"), ("How-to recipes", "guides/recipes.md"),
                ("Behavior Trees", "guides/behavior-trees.md"), ("Coming from AI Perception", "guides/from-ai-perception.md"),
                ("Multiplayer", "guides/multiplayer.md"), ("Profiles: share & override", "guides/profiles.md"),
                ("Policies & adapters", "guides/policies.md"), ("Custom senses (C++)", "guides/custom-senses.md"),
                ("Performance & crowds", "guides/performance.md")]),
    ("Reference", [("Cheat sheet", "reference/cheat-sheet.md"), ("Components & assets", "reference/components.md"),
                   ("Blueprint nodes", "reference/nodes.md"), ("Events", "reference/events.md"),
                   ("Profile settings", "reference/profile.md"), ("Enums, types & console", "reference/types.md")]),
    ("Help", [("Troubleshooting", "help/troubleshooting.md"), ("FAQ", "help/faq.md")]),
]
NAV = [(sec, [(t, p if p and os.path.exists(os.path.join(CONTENT, p)) else None) for t, p in items]) for sec, items in NAV]
PAGES = [p for _, items in NAV for _, p in items if p]

KINDS_CALLOUT = {"tip": "Tip", "info": "Good to know", "warning": "Watch out", "note": "Note", "check": "Checkpoint"}


# ---- inline -------------------------------------------------------------------------------------------------------------
def slug(text):
    s = re.sub(r"<[^>]+>", "", text).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "section"


def link_target(url, page):
    """A link to another page (.md) becomes the built .html page."""
    if re.match(r"^[a-z]+:", url) or url.startswith("#"):
        return url
    path, _, anchor = url.partition("#")
    if path.endswith(".md"):
        target = os.path.normpath(os.path.join(os.path.dirname(page), path)).replace("\\", "/")
        if target not in PAGES:
            print("  warning: %s links to %s, which is not a page" % (page, target))
        path = path[:-3] + ".html"
    return path + ("#" + anchor if anchor else "")


def inline(text, page):
    out, pos = [], 0
    for m in re.finditer(r"`([^`]+)`", text):          # code spans first: nothing inside them is formatting
        out.append(_inline(text[pos:m.start()], page))
        out.append("<code>%s</code>" % html.escape(m.group(1)))
        pos = m.end()
    out.append(_inline(text[pos:], page))
    return "".join(out)


def _inline(t, page):
    t = html.escape(t, quote=False)
    t = re.sub(r"\[\[([^\]]+)\]\]", r'<kbd>\1</kbd>', t)
    t = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", lambda m: '<img src="%s" alt="%s" loading="lazy">' % (m.group(2), m.group(1)), t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
               lambda m: '<a href="%s"%s>%s</a>' % (link_target(m.group(2), page),
                                                   ' target="_blank" rel="noopener"' if m.group(2).startswith("http") else "",
                                                   m.group(1)), t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?!\w)", r"<em>\1</em>", t)
    t = t.replace(" -- ", " &ndash; ")
    return t


# ---- media --------------------------------------------------------------------------------------------------------------
def figure(alt, src, caption, page):
    cap = '<figcaption>%s</figcaption>' % inline(caption, page) if caption else ""
    if src.lower().endswith((".mp4", ".webm")):
        poster = re.sub(r"\.(mp4|webm)$", ".jpg", src)          # media paths are written from the site's root
        has_poster = os.path.exists(os.path.join(ROOT, poster))
        if not os.path.exists(os.path.join(ROOT, src)):
            print("  warning: %s: missing %s" % (page, src))
        return ('<figure class="media video"><div class="frame"><video muted loop playsinline preload="none" data-src="%s"%s '
                'aria-label="%s"></video><button class="zoom" aria-label="Full size" title="Full size"></button></div>%s</figure>'
                % (src, ' poster="%s"' % poster if has_poster else "", html.escape(alt), cap))
    size = img_size(os.path.join(ROOT, src))
    if size is None:
        print("  warning: %s: missing or unreadable %s" % (page, src))
    w, h = size or (0, 0)
    # editor screenshots are taken at 150% Windows scaling: shown at most w / SHOT_SCALE wide, every screenshot's text
    # comes out the same size (a bit larger than the editor's own), whether the crop is a small menu or a wide panel
    style = ' style="--w:%dpx"' % round(w / SHOT_SCALE) if w else ""
    dims = ' width="%d" height="%d"' % (w, h) if w else ""
    return ('<figure class="media image"%s><div class="frame"><img src="%s" alt="%s"%s loading="lazy">'
            '<button class="zoom" aria-label="Full size" title="Full size"></button></div>%s</figure>'
            % (style, src, html.escape(alt), dims, cap))


SHOT_SCALE = 1.25


def img_size(path):
    """(width, height) of a .webp, .png or .jpg file, read from its header; None if it can't be read."""
    try:
        with open(path, "rb") as f:
            d = f.read(64 * 1024)
    except OSError:
        return None
    if d[:4] == b"RIFF" and d[8:12] == b"WEBP":
        kind = d[12:16]
        if kind == b"VP8 ":
            return (int.from_bytes(d[26:28], "little") & 0x3FFF, int.from_bytes(d[28:30], "little") & 0x3FFF)
        if kind == b"VP8L":
            b = int.from_bytes(d[21:25], "little")
            return ((b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1)
        if kind == b"VP8X":
            return (int.from_bytes(d[24:27], "little") + 1, int.from_bytes(d[27:30], "little") + 1)
    if d[:8] == b"\x89PNG\r\n\x1a\n":
        return (int.from_bytes(d[16:20], "big"), int.from_bytes(d[20:24], "big"))
    if d[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(d):
            if d[i] != 0xFF:
                i += 1
                continue
            m = d[i + 1]
            if m in (0xC0, 0xC1, 0xC2):
                return (int.from_bytes(d[i + 7:i + 9], "big"), int.from_bytes(d[i + 5:i + 7], "big"))
            i += 2 + int.from_bytes(d[i + 2:i + 4], "big")
    return None



FIG = re.compile(r'^!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)\s*$')


# ---- blocks -------------------------------------------------------------------------------------------------------------
class Doc:
    def __init__(self, page):
        self.page = page
        self.toc = []           # (level, id, text)
        self.ids = set()
        self.search = []        # (heading, id, text)
        self.toc_depth = 3      # deepest heading level listed in "On this page" (front matter: toc: 2)

    def anchor(self, text):
        base = slug(text)
        s, n = base, 2
        while s in self.ids:
            s, n = "%s-%d" % (base, n), n + 1
        self.ids.add(s)
        return s


def is_block_start(line):
    s = line.lstrip()
    return (s.startswith(("#", "```", ":::", "|", "> ", "<", "---")) or FIG.match(s) is not None
            or re.match(r"^([-*]|\d+\.)\s", s) is not None)


def render(lines, doc):
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1
            continue
        if s.startswith("```"):
            lang = s[3:].strip()
            j = i + 1
            body = []
            while j < n and not lines[j].strip().startswith("```"):
                body.append(lines[j])
                j += 1
            out.append('<div class="code"><pre><code%s>%s</code></pre><button class="copy" title="Copy">Copy</button></div>'
                       % (' class="lang-%s"' % lang if lang else "", html.escape("\n".join(body))))
            i = j + 1
            continue
        if s.startswith(":::"):
            head = s[3:].strip()
            depth, j, body = 1, i + 1, []
            while j < n:
                t = lines[j].strip()
                if t.startswith(":::") and t[3:].strip():
                    depth += 1
                elif t == ":::":
                    depth -= 1
                    if depth == 0:
                        break
                body.append(lines[j])
                j += 1
            out.append(custom(head, body, doc))
            i = j + 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            level, text = len(m.group(1)), m.group(2).strip()
            hid = doc.anchor(text)
            if 2 <= level <= doc.toc_depth:
                doc.toc.append((level, hid, re.sub(r"<[^>]+>", "", inline(text, doc.page))))
            # plain text: the search box escapes it when it shows it ("Search & evidence", not "Search &amp; evidence")
            doc.search.append([html.unescape(re.sub(r"<[^>]+>", "", inline(text, doc.page))), hid, ""])
            out.append('<h%d id="%s">%s<a class="anchor" href="#%s" aria-label="Link to this section">#</a></h%d>'
                       % (level, hid, inline(text, doc.page), hid, level))
            i += 1
            continue
        if s.startswith("---") and set(s) == {"-"}:
            out.append("<hr>")
            i += 1
            continue
        fm = FIG.match(s)
        if fm:
            out.append(figure(fm.group(1), fm.group(2), fm.group(3), doc.page))
            i += 1
            continue
        if s.startswith("|"):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append(table(rows, doc))
            continue
        if s.startswith("> "):
            quote = []
            while i < n and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].lstrip())
                i += 1
            out.append("<blockquote>%s</blockquote>" % render(quote, doc))
            continue
        if s.startswith("<"):
            raw = []
            while i < n and lines[i].strip():
                raw.append(lines[i])
                i += 1
            block = "\n".join(raw)
            # generated reference entries carry their own search entry: <... id="x" data-search="Title" data-text="...">
            for m in re.finditer(r'id="([^"]+)"\s+data-search="([^"]*)"\s+data-text="([^"]*)"', block):
                doc.search.append([html.unescape(m.group(2)), m.group(1), html.unescape(m.group(3))])
            out.append(block)
            continue
        if re.match(r"^([-*]|\d+\.)\s", s):
            items, i = collect_list(lines, i)
            out.append(list_html(items, doc))
            continue
        para = []
        while i < n and lines[i].strip() and not (para and is_block_start(lines[i])):
            para.append(lines[i].strip())
            i += 1
        text = " ".join(para)
        add_search_text(doc, text)
        out.append("<p>%s</p>" % inline(text, doc.page))
    return "\n".join(out)


def add_search_text(doc, text):
    plain = re.sub(r"[`*\[\]]", "", re.sub(r"\]\([^)]*\)", "]", text))
    if doc.search:
        if len(doc.search[-1][2]) < 600:
            doc.search[-1][2] = (doc.search[-1][2] + " " + plain).strip()
    else:
        doc.search.append(["", "", plain[:600]])


def collect_list(lines, i):
    """List items with their indentation; continuation lines belong to the item above."""
    items, n = [], len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            if i + 1 < n and re.match(r"^\s*([-*]|\d+\.)\s", lines[i + 1]):
                i += 1
                continue
            break
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line)
        if m:
            items.append([len(m.group(1).replace("\t", "    ")), m.group(2)[0].isdigit(), m.group(3)])
        elif items and line.startswith(" "):
            items[-1][2] += " " + line.strip()
        else:
            break
        i += 1
    return items, i


def list_html(items, doc, base=None):
    if not items:
        return ""
    indent = items[0][0] if base is None else base
    ordered = items[0][1]
    out = ["<ol>" if ordered else "<ul>"]
    k = 0
    while k < len(items):
        ind, _, text = items[k]
        add_search_text(doc, text)
        sub = []
        k += 1
        while k < len(items) and items[k][0] > indent:
            sub.append(items[k])
            k += 1
        out.append("<li>%s%s</li>" % (inline(text, doc.page), list_html(sub, doc, sub[0][0]) if sub else ""))
    out.append("</ol>" if ordered else "</ul>")
    return "".join(out)


def table(rows, doc):
    if len(rows) > 1 and all(re.match(r"^:?-{2,}:?$", c) for c in rows[1]):
        head, body = rows[0], rows[2:]
    else:
        head, body = None, rows
    out = ['<div class="table"><table>']
    if head:
        out.append("<thead><tr>%s</tr></thead>" % "".join("<th>%s</th>" % inline(c, doc.page) for c in head))
    out.append("<tbody>")
    for r in body:
        add_search_text(doc, " ".join(r))
        out.append("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c, doc.page) for c in r))
    out.append("</tbody></table></div>")
    return "".join(out)


def custom(head, body, doc):
    kind, _, arg = head.partition(" ")
    arg = arg.strip()
    if kind == "fast":
        return ('<section class="fast"><div class="fast-label"><span class="bolt"></span>%s</div>%s</section>'
                % (inline(arg or "The 30-second version", doc.page), render(body, doc)))
    if kind == "deep":
        return ('<details class="deep"><summary><span class="deep-label">Go deeper</span><span class="deep-title">%s</span>'
                '</summary><div class="deep-body">%s</div></details>' % (inline(arg, doc.page), render(body, doc)))
    if kind in KINDS_CALLOUT:
        return ('<aside class="callout %s"><div class="callout-title">%s</div>%s</aside>'
                % (kind, inline(arg or KINDS_CALLOUT[kind], doc.page), render(body, doc)))
    if kind == "steps":
        parts, cur = [], None
        for line in body:
            m = re.match(r"^###\s+(.*)$", line.strip())
            if m:
                cur = [m.group(1), []]
                parts.append(cur)
            elif cur is not None:
                cur[1].append(line)
        lis = []
        for k, (title, lines) in enumerate(parts, 1):
            hid = doc.anchor(title)
            if doc.toc_depth >= 3:
                doc.toc.append((3, hid, title))
            doc.search.append([title, hid, ""])
            lis.append('<li class="step" id="%s"><div class="step-num">%d</div><div class="step-body"><h3>%s</h3>%s</div></li>'
                       % (hid, k, inline(title, doc.page), render(lines, doc)))
        return '<ol class="steps">%s</ol>' % "".join(lis)
    if kind == "grid":
        return '<div class="grid">%s</div>' % render(body, doc)
    if kind == "card":
        title, link, image = (arg.split("|") + ["", ""])[:3]
        title, link, image = title.strip(), link.strip(), image.strip()
        img = ('<div class="card-media"><img src="%s" alt="" loading="lazy"></div>' % image) if image else ""
        go = '<span class="card-go">Open</span>' if link else ""
        inner = '%s<div class="card-body"><h4>%s</h4>%s%s</div>' % (img, inline(title, doc.page), render(body, doc), go)
        if link:
            return '<a class="card" href="%s">%s</a>' % (link_target(link, doc.page), inner)
        return '<div class="card">%s</div>' % inner
    if kind == "split":
        cols, cur = [[]], 0
        for line in body:
            if line.strip() == "+++":
                cols.append([])
            else:
                cols[-1].append(line)
        return '<div class="split">%s</div>' % "".join('<div class="col">%s</div>' % render(c, doc) for c in cols)
    if kind == "try":
        return ('<aside class="try"><div class="try-icon"></div><div><div class="try-title">Try it in the demo%s</div>%s</div></aside>'
                % (": room " + html.escape(arg) if arg else "", render(body, doc)))
    print("  warning: %s: unknown block ::: %s" % (doc.page, kind))
    return render(body, doc)


# ---- pages --------------------------------------------------------------------------------------------------------------
def read_page(page):
    text = open(os.path.join(CONTENT, page), encoding="utf-8").read().replace("\r\n", "\n")
    meta = {}
    if text.startswith("---\n"):
        head, _, text = text[4:].partition("\n---\n")
        for line in head.splitlines():
            k, _, v = line.partition(":")
            v = v.strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]     # a quoted value, as in YAML: title: "Tutorial: a complete guard"
            meta[k.strip()] = v
    return meta, text


def rel(page, target):
    """The path from page to a file at the site root."""
    depth = page.count("/")
    return "../" * depth + target


def nav_html(page):
    out = []
    for section, items in NAV:
        out.append('<div class="nav-section"><div class="nav-title">%s</div><ul>' % section)
        for title, p in items:
            if p is None:
                out.append('<li><span class="nav-soon">%s<em>soon</em></span></li>' % title)
            else:
                cls = ' class="active" aria-current="page"' if p == page else ""
                out.append('<li><a href="%s"%s>%s</a></li>' % (rel(page, p[:-3] + ".html"), cls, title))
        out.append("</ul></div>")
    return "".join(out)


def toc_html(doc):
    if len(doc.toc) < 2:
        return ""
    items = "".join('<li class="l%d"><a href="#%s">%s</a></li>' % (lvl, hid, txt) for lvl, hid, txt in doc.toc)
    return '<nav class="toc" aria-label="On this page"><div class="toc-title">On this page</div><ul>%s</ul></nav>' % items


def prevnext(page):
    k = PAGES.index(page)
    titles = {p: t for _, items in NAV for t, p in items if p}
    out = []
    if k > 0:
        p = PAGES[k - 1]
        out.append('<a class="prev" href="%s"><span>Previous</span>%s</a>' % (rel(page, p[:-3] + ".html"), titles[p]))
    else:
        out.append("<span></span>")
    if k + 1 < len(PAGES):
        p = PAGES[k + 1]
        out.append('<a class="next" href="%s"><span>Next</span>%s</a>' % (rel(page, p[:-3] + ".html"), titles[p]))
    return '<nav class="prevnext">%s</nav>' % "".join(out)


def build():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "assets"))
    for f in os.listdir(THEME):
        src = os.path.join(THEME, f)
        if f.endswith(".html"):
            continue
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(OUT, "assets", f))
        else:
            shutil.copy2(src, os.path.join(OUT, "assets", f))
    shutil.copy2(os.path.join(THEME, "favicon.ico"), OUT)      # browsers ask the site's root for it, whatever the page says
    if os.path.isdir(MEDIA):
        shutil.copytree(MEDIA, os.path.join(OUT, "media"))
    template = open(os.path.join(THEME, "page.html"), encoding="utf-8").read()
    # browsers (and GitHub Pages) cache the stylesheet and scripts: a version from the theme's and pages' contents makes
    # every change reach readers on their next visit
    ver = hashlib.sha1()
    for folder in (THEME, CONTENT):
        for base, _, files in sorted(os.walk(folder)):
            for f in sorted(files):
                with open(os.path.join(base, f), "rb") as fh:
                    ver.update(fh.read())
    for name in ("style.css", "app.js", "search.js"):
        template = template.replace('assets/%s"' % name, 'assets/%s?v=%s"' % (name, ver.hexdigest()[:10]))
    index = []
    for page in PAGES:
        meta, text = read_page(page)
        doc = Doc(page)
        if meta.get("toc", "").isdigit():
            doc.toc_depth = int(meta["toc"])
        body = render(text.split("\n"), doc)
        root = rel(page, "")
        layout = meta.get("layout", "page")
        values = {
            "title": html.escape(meta.get("title", "APS")),
            "page_title": html.escape(meta.get("title", "APS") + " | " + SITE["name"]) if page != "index.md"
            else html.escape(SITE["name"] + ": " + SITE["product"]),
            "description": html.escape(meta.get("description", "")),
            "root": root, "layout": layout, "content": body,
            "nav": nav_html(page), "toc": toc_html(doc) if layout != "home" else "",
            "prevnext": prevnext(page) if layout != "home" else "",
            "fab": SITE["fab"], "support": SITE["support"], "repo": SITE["repo"],
        }
        out = template
        for k, v in values.items():
            out = out.replace("{{%s}}" % k, v)
        out = out.replace('src="media/', 'src="%smedia/' % root).replace('data-src="media/', 'data-src="%smedia/' % root) \
                 .replace('poster="media/', 'poster="%smedia/' % root).replace('href="media/', 'href="%smedia/' % root)
        dst = os.path.join(OUT, page[:-3] + ".html")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "w", encoding="utf-8", newline="\n") as f:
            f.write(out)
        url = page[:-3] + ".html"
        for h, hid, txt in doc.search:
            index.append({"p": meta.get("title", ""), "u": url + ("#" + hid if hid else ""), "h": h, "t": txt[:400]})
        print("  %-28s %6d bytes, %d sections" % (page, len(out), len(doc.toc)))
    with open(os.path.join(OUT, "assets", "search.js"), "w", encoding="utf-8", newline="\n") as f:
        f.write("window.APS_SEARCH=%s;\n" % json.dumps(index, ensure_ascii=False))
    titles = {p[:-3] + ".html": read_page(p)[0].get("title", "APS") for p in PAGES}
    for old, new in REDIRECTS.items():
        to = "../" + new
        page_file = new.split("#")[0]
        if page_file not in titles:
            raise SystemExit("redirect %s/ points at %s, which is not a page" % (old, new))
        os.makedirs(os.path.join(OUT, old), exist_ok=True)
        with open(os.path.join(OUT, old, "index.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(REDIRECT_PAGE % {"to": to, "abs": SITE["url"] + new, "title": html.escape(titles[page_file])})
    with open(os.path.join(OUT, "404.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(NOT_FOUND_PAGE % {"url": SITE["url"]})
    print("built %d pages, %d redirects from the old addresses, and a 404 page into %s" % (len(PAGES), len(REDIRECTS), OUT))


if __name__ == "__main__":
    build()
