"""Checks every docs page against the plugin source model (tools/model.json, made by apsref.py).

    python -I check_docs.py            (from the v2 folder, after the build)

What it checks, on every page in content/ (the generated reference pages are skipped: they ARE the source):
  names     Every `code` span and **bold** span that names an APS thing must be a real node, setting, event, enum
            value, component, asset or console command, spelled as the editor shows it. Unknown `code` names fail;
            unknown **bold** names are listed for review (bold is also used for menus and plain emphasis).
  bools     A setting written "b Something" fails: the editor drops the b (bUseEyeSocket shows as "Use Eye Socket").
  defaults  A table with a "Default" column, and a setting followed by a value in brackets - `Detect Threshold`
            (0.35) - must match the setting's default in the source.
  links     Links to other pages, and #anchors, must exist in the built site.
Exit code 1 when anything fails.
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONTENT = os.path.join(ROOT, "content")
SITE = os.path.join(ROOT, "_site")
M = json.load(open(os.path.join(HERE, "model.json"), encoding="utf-8"))

# ---- every name the editor shows ------------------------------------------------------------------------------------
NAMES = {}          # lower-cased display name -> kind
EXACT = {}          # lower-cased display name -> every exact spelling the editor uses


def add(name, kind):
    if name:
        NAMES.setdefault(name.lower(), kind)
        EXACT.setdefault(name.lower(), set()).add(name)


def case_problem(span):
    """The editor's spelling when the page's differs only in case (Unreal lowercases in, as, to, or, on...)."""
    spellings = EXACT.get(span.strip().lower())
    if spellings and span.strip() not in spellings:
        return sorted(spellings)[0]
    return None


for f in M["functions"]:
    if f["callable"] or f["event"]:
        add(f["display"], "node")
    elif "CallInEditor" in f.get("flags", []):
        add(f["display"], "button")          # Validate Profile, Show Budget: buttons in the Details panel
# the Details panel's group names (Ranges, Detection, Brain...), each part of a category path
for p in M["properties"]:
    if p["editable"] and p.get("category"):
        for part in p["category"].split("|"):
            if part and part != "APS":
                add(part, "category")
for p in M["properties"]:
    if p["editable"] or p["blueprint"] or p["assignable"] or p["visible"]:
        add(p["display"], "event" if p["assignable"] else "setting")
for e in M["enums"].values():
    add(e["display"], "enum")
    for v in e["values"]:
        add(v["display"], "enum value")
for t in M["types"].values():
    add(t["display"], "type")
for c in M.get("console", []):
    add(c["name"], "console")
# what Unreal itself names the nodes that get APS's subsystems, and the parameters of APS nodes and events
add("Get APSSubsystem", "node")
add("Get APSKnowledge Subsystem", "node")
for f in M["functions"]:
    for p in f["params"]:
        add(p["display"], "pin")
for d in M["delegates"].values():
    for p in d["params"]:
        add(re.sub(r"(?<=[a-z])(?=[A-Z])", " ", p["name"]), "pin")

# defaults, by display name (a name on several classes keeps every default)
DEFAULTS = {}
for p in M["properties"]:
    if p["default"] is not None:
        DEFAULTS.setdefault(p["display"].lower(), set()).add(p["default"])

# Unreal Engine and editor names the docs may use (not APS's): checked against this list instead of the source
ENGINE = {
    "is nearly zero", "get random reachable point in radius", "ai move to", "print string", "branch", "sequence", "delay",
    "spawn actor from class", "get actor location", "get player pawn", "get player character", "set timer by event",
    "event begin play", "event tick", "event any damage", "apply damage", "on component begin overlap",
    "on component hit", "on actor hit", "cast to", "get controlled pawn", "get owner", "set value as vector",
    "set value as object", "set value as bool", "set value as float", "set value as enum", "get blackboard",
    "run behavior tree", "move to", "is valid", "make literal name", "get display name", "concat", "append",
    "get all actors of class", "get game time in seconds", "set actor rotation", "rinterp to", "find look at rotation",
    "play sound at location", "get world delta seconds", "vector length", "normalize", "get velocity",
    "class defaults", "details", "components", "content browser", "blueprint class", "data asset", "add",
    "edit", "plugins", "project settings", "world settings", "play", "simulate", "my blueprint", "event graph",
    "blackboard", "behavior tree", "ai controller", "aicontroller", "character", "pawn", "actor", "generic team id",
    "physical material", "trace channel", "visibility", "camera", "get world", "eqs", "environment query",
    "ai perception", "ai perception component", "ai sense config", "on target perception updated",
    "on perception updated", "get currently perceived actors", "ai perception stimuli source",
    "register for sense", "report noise event", "make noise", "pawn noise emitter", "has line of sight to",
    "line trace by channel", "sphere overlap actors", "get distance to", "break hit result", "set focus",
    "clear focus", "finish execute", "receive execute ai", "receive tick ai", "service", "decorator", "task",
    "functions", "override", "variables", "compile", "save", "new", "miscellaneous", "install to engine",
    "library", "fab library", "epic games launcher", "enabled", "restart", "cmd", "output log", "console",
    "replicates", "net mode", "server", "client", "listen server", "dedicated server", "has authority",
    "switch has authority", "get game mode", "rep notify", "multicast", "run on server", "on rep",
    "anim notify", "anim montage", "socket", "skeletal mesh", "mesh", "capsule component", "head",
    "get socket location", "level blueprint", "directional light", "sky light", "exponential height fog",
    "post process volume", "box collision", "sphere collision", "trigger volume", "nav mesh bounds volume",
    "get controller", "possess", "unpossess", "on possess", "get ai controller", "use controller rotation yaw",
    "orient rotation to movement", "character movement", "max walk speed", "crouch", "un crouch", "is crouching",
    "simulation generates hit events", "generate overlap events", "ai moveto", "set focus", "clear focus",
    "apply point damage", "apply radial damage", "play sound at location", "spawn sound at location",
    "get value as bool", "set value as vector", "clear value", "get blackboard", "is equal to", "observer aborts",
}


# text the reader types or sees that is not a name: search words, asset and file names, JSON lines
LITERALS = {"advanced perception", "aps"}


def literal(span):
    s = span.strip()
    return (s.lower() in LITERALS or re.match(r"^(DA|BP|ABP|WBP|SK|SM|M|MI|T|L|NS|BT|BTT|BTS|BTD|BB|EQS|DT|S|PM)_\w+$", s) is not None
            or re.search(r"\.\w{2,7}$", s) is not None or s.endswith(".") or '"' in s or ":" in s or "/" in s or "\\" in s)


def known(name):
    n = name.strip().lower()
    return n in NAMES or n in ENGINE or n in LOCAL


# ---- page text, without code blocks or raw generated HTML -----------------------------------------------------------
LOCAL = set()      # names the reader makes on the current page (front matter "local: A, B"): their own assets and keys


def page_lines(path):
    text = open(path, encoding="utf-8").read().replace("\r\n", "\n")
    LOCAL.clear()
    if text.startswith("---\n"):
        head, _, text = text[4:].partition("\n---\n")
        for line in head.splitlines():
            if line.startswith("local:"):
                LOCAL.update(x.strip().lower() for x in line[6:].split(",") if x.strip())
    out, in_code = [], False
    for i, line in enumerate(text.split("\n"), 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            out.append((i, line))
    return out


NUM = re.compile(r"-?\d+(?:\.\d+)?")
FORMULA = re.compile(r"[=<>≥≤×÷±+*/^·]|−|\(|\)|\d+\s*(cm|s|m|%)\b")


def default_matches(value_text, src_values):
    """True / False, or None when the two can't be compared."""
    v = value_text.strip().lower().strip("`* ")
    srcs = {s.strip().lower() for s in src_values}
    bools = srcs & {"true", "false"}
    if bools:
        if v in ("on", "true", "yes", "ticked"):
            return "true" in bools
        if v in ("off", "false", "no", "unticked"):
            return "false" in bools
        return None
    m = NUM.search(v.replace(",", ""))
    if not m:
        return None
    dn = float(m.group())
    nums = []
    for s in srcs:
        sm = NUM.search(s.replace("f", ""))
        if sm and re.match(r"^-?[\d.]+f?$", s.strip()):
            nums.append(float(sm.group()))
    if not nums:
        return None
    return any(abs(dn - x) < 1e-4 for x in nums)


def fix_case(pages):
    """Rewrite `code` and **bold** names whose case differs from the editor's (python check_docs.py --fix-case)."""
    for page in pages:
        path = os.path.join(CONTENT, page)
        text = open(path, encoding="utf-8").read()

        def code(m):
            exact = case_problem(m.group(1))
            return "`%s`" % exact if exact else m.group(0)

        def bold(m):
            span = m.group(1)
            words = span.split()
            if (all(w[:1].isupper() for w in words) or (len(words) > 1 and span[:1].isupper())) and not span.isupper():
                exact = case_problem(span)
                if exact:
                    return "**%s**" % exact
            return m.group(0)

        new = re.sub(r"`([^`\n]+)`", code, text)
        new = re.sub(r"\*\*([^*\n]+)\*\*", bold, new)
        if new != text:
            open(path, "w", encoding="utf-8", newline="\n").write(new)
            print("fixed case in", page)


def main():
    pages = []
    for base, _, files in os.walk(CONTENT):
        for f in files:
            if f.endswith(".md"):
                rel = os.path.relpath(os.path.join(base, f), CONTENT).replace("\\", "/")
                if not rel.startswith("reference/") or rel == "reference/cheat-sheet.md":
                    pages.append(rel)
    pages.sort()
    if "--fix-case" in sys.argv:
        fix_case(pages)
    errors, review = [], []
    for page in pages:
        lines = page_lines(os.path.join(CONTENT, page))
        table_default_col = None
        for ln, line in lines:
            raw = line.strip()
            # --- tables with a Default column
            if raw.startswith("|"):
                cells = [c.strip() for c in raw.strip("|").split("|")]
                low = [c.lower() for c in cells]
                if "default" in low:
                    table_default_col = low.index("default")
                elif table_default_col is not None and not set("".join(cells)) <= set("-: ") and len(cells) > table_default_col:
                    nm = re.match(r"^`([^`]+)`", cells[0]) or re.match(r"^\*\*([^*]+)\*\*", cells[0])
                    if nm:
                        name = nm.group(1).strip()
                        src = DEFAULTS.get(name.lower())
                        if src:
                            ok = default_matches(cells[table_default_col], src)
                            if ok is False:
                                errors.append("%s:%d  default of `%s` is %s in the source, the page says %s"
                                              % (page, ln, name, "/".join(sorted(src)), cells[table_default_col]))
            else:
                table_default_col = None
            if raw.startswith("<") and "data-search" in raw:
                continue
            text = re.sub(r"<[^>]+>", " ", line)
            # --- code spans
            for m in re.finditer(r"`([^`]+)`", text):
                span = m.group(1).strip()
                if re.match(r"^b [A-Z]", span):
                    errors.append("%s:%d  `%s`: the editor shows bools without the b: `%s`" % (page, ln, span, span[2:]))
                    continue
                if FORMULA.search(span) or not re.search(r"[A-Za-z]", span) or span.startswith(("aps.", "Stimulus.", "Sound.", "Evidence.")) and not known(span):
                    if span.startswith("aps.") and not known(span.split()[0]):
                        errors.append("%s:%d  `%s`: no such console command" % (page, ln, span))
                    continue
                if re.match(r"^[a-z][a-z0-9_.]*$", span) or literal(span):     # a value, a socket name, an asset, a file
                    continue
                if not known(span):
                    errors.append("%s:%d  `%s`: no node, setting, event or value of that name in the source" % (page, ln, span))
                    continue
                exact = case_problem(span)
                if exact and span.lower() not in LOCAL:
                    errors.append("%s:%d  `%s`: the editor writes it `%s`" % (page, ln, span, exact))
                # --- a value in brackets right after a setting: `Detect Threshold` (0.35)
                after = text[m.end():m.end() + 40]
                vm = re.match(r"\s*\((-?[\d.]+)\s*(%|s|cm|cm/s|m|°)?[^)]*\)", after)
                if vm and span.lower() in DEFAULTS:
                    val = vm.group(1)
                    if vm.group(2) == "%":
                        val = str(float(val) / 100)
                    ok = default_matches(val, DEFAULTS[span.lower()])
                    if ok is False:
                        errors.append("%s:%d  `%s` (%s): the source default is %s" % (page, ln, span, vm.group(0).strip(), "/".join(sorted(DEFAULTS[span.lower()]))))
            # --- bold spans
            for m in re.finditer(r"\*\*([^*]+)\*\*", text):
                span = m.group(1).strip()
                if re.match(r"^b [A-Z]", span):
                    errors.append("%s:%d  **%s**: the editor shows bools without the b" % (page, ln, span))
                    continue
                words = span.split()
                looks_like_name = 1 <= len(words) <= 7 and all(w[:1].isupper() or w.lower() in ("in", "as", "to", "or", "at", "on", "if", "be", "by", "the", "for", "and", "with", "when", "from", "of", "a") for w in words) and re.search(r"[A-Z]", span)
                if looks_like_name and not known(span) and not re.search(r"[.!?:;,]$|\d", span):
                    review.append("%s:%d  **%s**" % (page, ln, span))
                elif (looks_like_name or (len(words) > 1 and span[:1].isupper())) and not span.isupper() \
                        and span.lower() in NAMES and span.lower() not in ENGINE:
                    exact = case_problem(span)
                    if exact:
                        errors.append("%s:%d  **%s**: the editor writes it **%s**" % (page, ln, span, exact))
    # --- links and anchors in the built site
    ids = {}
    for base, _, files in os.walk(SITE):
        for f in files:
            if f.endswith(".html"):
                rel = os.path.relpath(os.path.join(base, f), SITE).replace("\\", "/")
                ids[rel] = set(re.findall(r'\sid="([^"]+)"', open(os.path.join(base, f), encoding="utf-8").read()))
    for rel in sorted(ids):
        src = open(os.path.join(SITE, rel), encoding="utf-8").read()
        body = src.split('<main id="main"', 1)[-1]
        for href in re.findall(r'href="([^"]+)"', body):
            if href.startswith(("http", "mailto:", "assets/", "../assets/", "media/", "../media/")) or href.endswith((".png", ".jpg", ".webp", ".mp4")):
                continue
            path, _, anchor = href.partition("#")
            target = rel if not path else os.path.normpath(os.path.join(os.path.dirname(rel), path)).replace("\\", "/")
            if target not in ids:
                errors.append("site %s  links to %s: no such page" % (rel, href))
            elif anchor and anchor not in ids[target]:
                errors.append("site %s  links to %s: no such anchor" % (rel, href))
    print("checked %d pages against %d names from the source" % (len(pages), len(NAMES)))
    for e in errors:
        print("  FAIL  " + e)
    if review:
        print("\nbold names not in the source (menus or emphasis? review):")
        for r in review:
            print("  ?     " + r)
    print("\n%s: %d problem(s), %d to review" % ("FAILED" if errors else "PASSED", len(errors), len(review)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
