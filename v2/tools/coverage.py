# Coverage check: is everything the old docs named still covered by the new site?
#
# Takes every **bold** and `code` name in the old MkDocs pages (docs/*.md) that is a real APS name
# (a node, setting, event, enum value or type in tools/model.json), and looks for it in the new
# hand-written pages first, then in the generated reference. A name only in the reference is
# documented but not explained anywhere; a name in neither is a gap.
#
#   python -I tools/coverage.py [old docs folder]
#
# The old pages were removed from the repo on 2026-10-26, after this check last said 0 missing. To run it again,
# take them from the history first:  git archive -o old_docs.tar 47bfbe3 docs  then  tar -x -f old_docs.tar -C <folder>
# (then pass <folder>/docs).
import io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OLD = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(ROOT), "docs")
if not os.path.isdir(OLD):
    sys.exit("No old docs at %s: take them from the history first (see the top of this file)." % OLD)
M = json.load(open(os.path.join(HERE, "model.json"), encoding="utf-8"))

names = {}
for f in M["functions"]:
    if f["callable"] or f["event"] or "CallInEditor" in f.get("flags", []):
        names[f["display"].lower()] = f["display"]
for p in M["properties"]:
    if p["editable"] or p["blueprint"] or p["assignable"] or p["visible"]:
        names[p["display"].lower()] = p["display"]
for e in M["enums"].values():
    for v in e["values"]:
        names[v["display"].lower()] = v["display"]
for t in M["types"].values():
    names[t["display"].lower()] = t["display"]


def norm(s):
    s = re.sub(r"\s*\(.*$", "", s.strip())          # "Report Pain (Def, Amount)" -> "Report Pain"
    s = re.sub(r"^b\s+(?=[A-Z])", "", s)            # the old docs' "b Use Per Target Light"
    return s.strip(" .:").lower()


def text_of(folder, skip=()):
    out = {}
    for dp, _, fs in os.walk(folder):
        for f in fs:
            if f.endswith(".md"):
                rel = os.path.relpath(os.path.join(dp, f), folder).replace("\\", "/")
                if any(rel.startswith(s) for s in skip):
                    continue
                out[rel] = io.open(os.path.join(dp, f), encoding="utf-8").read().lower()
    return out


content = os.path.join(ROOT, "content")
pages = text_of(content, skip=("reference/nodes", "reference/events", "reference/profile",
                               "reference/types", "reference/components"))
ref = text_of(os.path.join(content, "reference"))
pages_all = "\n".join(pages.values())
ref_all = "\n".join(ref.values())

old = {}
for f in sorted(os.listdir(OLD)):
    if not f.endswith(".md"):
        continue
    t = io.open(os.path.join(OLD, f), encoding="utf-8").read()
    for m in re.finditer(r"\*\*([^*\n]{2,60})\*\*|`([^`\n]{2,60})`", t):
        n = norm(m.group(1) or m.group(2))
        if n in names:
            old.setdefault(n, set()).add(f)

explained, ref_only, missing = [], [], []
for n in sorted(old):
    if n in pages_all:
        explained.append(n)
    elif n in ref_all:
        ref_only.append(n)
    else:
        missing.append(n)

print("old docs name %d APS names: %d explained on a page, %d only in the reference, %d missing"
      % (len(old), len(explained), len(ref_only), len(missing)))
for title, group in (("ONLY IN THE REFERENCE", ref_only), ("MISSING", missing)):
    if group:
        print("\n" + title)
        for n in group:
            print("  %-40s from %s" % (names[n], ", ".join(sorted(old[n]))))
sys.exit(1 if missing else 0)
