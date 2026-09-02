#!/usr/bin/env python3
"""
Generate APS-Documentation-ALL-IN-ONE.md from docs/, in nav order.

The single-file version used to be maintained by hand alongside the site, which
meant two copies of twenty-eight pages and no mechanism keeping them honest. It
drifted, and the stale copy is the one somebody reads offline.

Run from the repo root:

    python tools/build_all_in_one.py

CI runs it with --check, which fails if the committed file does not match what
the sources would produce.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
OUTPUT = ROOT / "APS-Documentation-ALL-IN-ONE.md"

BANNER = """<!-- GENERATED FILE — DO NOT EDIT BY HAND.
     Produced by tools/build_all_in_one.py from the pages in docs/.
     Edit those, then re-run the script. -->

"""


def nav_order() -> list[tuple[str, str]]:
    """Read (section, filename) pairs out of mkdocs.yml's nav, in order.

    Deliberately parsed by hand rather than with a YAML library: mkdocs.yml uses
    Python-specific YAML tags for the emoji and superfences extensions, which a
    plain safe_load refuses to parse. The nav block is simple enough to read
    directly, and this keeps the script dependency-free.
    """
    text = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    nav_match = re.search(r"^nav:\s*$", text, re.MULTILINE)
    if not nav_match:
        sys.exit("mkdocs.yml has no nav: block")

    pages: list[tuple[str, str]] = []
    section = ""

    for line in text[nav_match.end():].splitlines():
        if line.strip() and not line.startswith((" ", "\t")):
            break  # dedented back to a top-level key; nav is over

        stripped = line.strip()
        if not stripped.startswith("- "):
            continue

        entry = stripped[2:]

        # "- Home: index.md"  /  '- "Tutorial: A Guard": tutorial.md'
        page = re.match(r'^(?:"([^"]+)"|([^:]+)):\s*(\S+\.md)\s*$', entry)
        if page:
            pages.append((section, page.group(3)))
            continue

        # "- Get started:" — a section header, no page attached
        header = re.match(r'^(?:"([^"]+)"|(.+)):\s*$', entry)
        if header:
            section = (header.group(1) or header.group(2)).strip()

    return pages


def demote(markdown: str) -> str:
    """Push every heading down one level, outside fenced code blocks.

    Each page owns an H1. Concatenated, that produces a document with 28 top-level
    headings and no hierarchy, so the page titles become H2 under a single H1.
    """
    out: list[str] = []
    in_fence = False
    fence_marker = ""

    for line in markdown.splitlines():
        fence = re.match(r"^(\s*)(`{3,}|~{3,})", line)
        if fence:
            marker = fence.group(2)[0]
            if not in_fence:
                in_fence, fence_marker = True, marker
            elif marker == fence_marker:
                in_fence = False

        if not in_fence and re.match(r"^#{1,5} ", line):
            line = "#" + line

        out.append(line)

    return "\n".join(out)


ICON = re.compile(r":(?:material|octicons|fontawesome)-[a-z0-9-]+:")
SVG = re.compile(r"<svg\b.*?</svg>", re.DOTALL)
SVG_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.DOTALL)
CAPTION = re.compile(r'<p class="aps-figure__caption">(.*?)</p>', re.DOTALL)
ATTR_LIST = re.compile(r"\{\s*[.#][^}]*\}")
HTML_WRAPPER = re.compile(r"^\s*</?(?:div|p|span)\b[^>]*>\s*$", re.IGNORECASE)
ADMONITION = re.compile(r'^(\s*)(?:!!!|\?\?\?\+?)\s+(\w+)(?:\s+"([^"]*)")?\s*$')
TAB = re.compile(r'^(\s*)===\s+"([^"]*)"\s*$')


def portable(markdown: str) -> str:
    """Convert mkdocs-material syntax to markdown that renders anywhere.

    The single-file build is read on GitHub and in plain editors, where an
    admonition is literal '!!! note' text, a content tab swallows its own body
    into an indented block, and an icon shortcode is visible punctuation. The
    site keeps all of it; only this output is flattened.
    """
    # The site draws its diagrams as inline SVG, which GitHub strips and a
    # plain editor shows as markup. Keep the figure's title as a one-line note
    # and let its caption stand as an ordinary paragraph.
    def figure_note(match: re.Match[str]) -> str:
        title = SVG_TITLE.search(match.group(0))
        label = title.group(1).strip() if title else "diagram"
        return f"*Figure: {label}.*"

    markdown = SVG.sub(figure_note, markdown)
    markdown = CAPTION.sub(r"\1", markdown)

    lines = markdown.splitlines()
    out: list[str] = []
    i = 0
    in_fence = False
    fence_marker = ""

    while i < len(lines):
        line = lines[i]

        fence = re.match(r"^(\s*)(`{3,}|~{3,})", line)
        if fence:
            marker = fence.group(2)[0]
            if not in_fence:
                in_fence, fence_marker = True, marker
            elif marker == fence_marker:
                in_fence = False

        if in_fence:
            out.append(line)
            i += 1
            continue

        admon = ADMONITION.match(line)
        tab = TAB.match(line)

        if admon or tab:
            indent = len(admon.group(1) if admon else tab.group(1))
            if admon:
                kind, title = admon.group(2), admon.group(3)
                label = title if title is not None else kind.capitalize()
                prefix = "> "
                header = f"> **{label}**" if label else None
            else:
                label = tab.group(2)
                prefix = ""
                header = f"**{label}**"

            # Collect the indented body that belongs to this block.
            i += 1
            body: list[str] = []
            while i < len(lines):
                nxt = lines[i]
                if not nxt.strip():
                    body.append("")
                    i += 1
                    continue
                if len(nxt) - len(nxt.lstrip()) <= indent:
                    break
                body.append(nxt[indent + 4:] if len(nxt) > indent + 4 else nxt.strip())
                i += 1

            while body and not body[-1].strip():
                body.pop()

            if header:
                out.append(header)
            if prefix:
                if header:
                    out.append(">")
                out.extend(f"{prefix}{b}".rstrip() for b in body)
            else:
                out.append("")
                out.extend(body)
            out.append("")
            continue

        if HTML_WRAPPER.match(line):
            i += 1
            continue

        line = ICON.sub("", line)
        line = ATTR_LIST.sub("", line)
        out.append(line.rstrip())
        i += 1

    # Collapse the blank runs the substitutions leave behind.
    collapsed: list[str] = []
    for line in out:
        if not line.strip() and collapsed and not collapsed[-1].strip():
            continue
        collapsed.append(line)

    return "\n".join(collapsed)


def rewrite_links(markdown: str) -> str:
    """Turn cross-page links into in-document anchors.

    `[Memory](memory-and-recall.md)` and `[Memory](memory-and-recall.md#limits)`
    both have to resolve inside one file. The page anchor is the filename slug,
    which matches the heading this script emits for each page.
    """
    def repl(match: re.Match[str]) -> str:
        label, target, fragment = match.group(1), match.group(2), match.group(3) or ""
        anchor = fragment[1:] if fragment else target
        return f"[{label}](#{anchor})"

    return re.sub(r"\[([^\]]+)\]\(([a-z0-9\-]+)\.md(#[^)]+)?\)", repl, markdown)


def build() -> str:
    parts = [BANNER]
    seen: set[str] = set()
    current_section = None

    for section, filename in nav_order():
        path = DOCS / filename
        if not path.exists():
            sys.exit(f"nav references {filename}, which does not exist")
        if filename in seen:
            continue
        seen.add(filename)

        if section and section != current_section:
            parts.append(f"\n\n# {section}\n")
            current_section = section

        body = path.read_text(encoding="utf-8")

        # The page's own H1 becomes its anchor target. Emitting the slug as an
        # explicit id keeps rewritten links working regardless of the title text.
        title = re.match(r"^#\s+(.+)$", body, re.MULTILINE)
        heading = title.group(1).strip() if title else filename
        if title:
            body = body[title.end():]

        slug = filename[:-3]
        parts.append(f'\n\n<a id="{slug}"></a>\n\n## {heading}\n')
        parts.append(rewrite_links(demote(portable(body))).strip())
        parts.append("\n\n---\n")

    return "".join(parts).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the committed file is out of date instead of rewriting it",
    )
    args = parser.parse_args()

    generated = build()

    if args.check:
        existing = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if existing.replace("\r\n", "\n") != generated:
            print(
                f"{OUTPUT.name} is out of date.\n"
                "Run: python tools/build_all_in_one.py",
                file=sys.stderr,
            )
            return 1
        print(f"{OUTPUT.name} is up to date.")
        return 0

    OUTPUT.write_text(generated, encoding="utf-8", newline="\n")
    pages = len(set(f for _, f in nav_order()))
    print(f"Wrote {OUTPUT.name} from {pages} pages ({len(generated):,} characters).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
