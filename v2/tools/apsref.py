"""APS source model: reads the plugin's C++ headers (and constructors) into one JSON model of everything a user
can see in Unreal - components, Blueprint nodes, events, settings, enums and structs - with the names exactly as the
editor shows them and the developer's own doc comments.

The docs' reference pages are generated from this model and check_docs.py verifies every page against it, so a node,
setting or default named in the docs either exists in the plugin or the build says so.

    python -I apsref.py <plugin Source folder> <out model.json>
"""
import json
import os
import re
import sys

MACROS = re.compile(r"\b(UCLASS|USTRUCT|UENUM|UINTERFACE|UFUNCTION|UPROPERTY|DECLARE_DYNAMIC_MULTICAST_DELEGATE\w*|"
                    r"DECLARE_DYNAMIC_DELEGATE\w*)\s*\(")


# ---- Unreal's display names (FName::NameToDisplayString, UE 5.2) ---------------------------------------------------
ARTICLES = ["In", "As", "To", "Or", "At", "On", "If", "Be", "By", "The", "For", "And", "With", "When", "From"]


def display(name, is_bool=False):
    out, in_run, was_space, was_paren, was_number, was_minus = [], False, False, False, False, False
    n = len(name)
    for i, ch in enumerate(name):
        lower, upper, digit, under = ch.islower(), ch.isupper(), ch.isdigit(), ch == "_"
        if i == 0 and is_bool and ch == "b" and n > 1 and name[1].isupper():
            continue
        if (upper or (digit and not was_minus)) and not in_run and not was_paren and not was_number:
            if not was_space and out:
                out.append(" ")
                was_space = True
            in_run = True
        if lower:
            in_run = False
        if under:
            ch = " "
            in_run = True
        if not out:
            ch = ch.upper()
        elif not digit and (was_space or was_paren):
            article = False
            for a in ARTICLES:
                la = len(a)
                if n - i > la and not name[i + la].islower() and name[i:i + la] == a:
                    article = True
                    break
            ch = ch.lower() if article else ch.upper()
        was_space = ch == " "
        was_paren = ch == "("
        was_minus = ch == "-"
        was_number = digit or (was_number and (was_minus or ch == "."))
        out.append(ch)
    return "".join(out)


# ---- small parsing helpers --------------------------------------------------------------------------------------------
def balanced(text, start, open_ch="(", close_ch=")"):
    """Index just past the bracket matching text[start] (which is open_ch)."""
    depth, i, n = 0, start, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            i = text.index('"', i + 1) + 1 if '"' in text[i + 1:] else n
            while text[i - 2] == "\\" and text[i - 1] == '"':      # escaped quote inside a string
                i = text.index('"', i) + 1
            continue
        if c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return n


def split_top(text, sep=","):
    parts, depth, cur, quote = [], 0, [], False
    for c in text:
        if c == '"':
            quote = not quote
        if not quote:
            if c in "(<{[":
                depth += 1
            elif c in ")>}]":
                depth -= 1
            elif c == sep and depth == 0:
                parts.append("".join(cur).strip())
                cur = []
                continue
        cur.append(c)
    if "".join(cur).strip():
        parts.append("".join(cur).strip())
    return parts


def parse_specs(text):
    """UPROPERTY(EditAnywhere, Category = "X", meta = (A = 1, B)) -> ({flags}, {key: value}, {meta})."""
    flags, kv, meta = set(), {}, {}
    for part in split_top(text):
        if "=" in part:
            k, v = part.split("=", 1)
            k, v = k.strip(), v.strip()
            if k.lower() == "meta":
                inner = v.strip()[1:-1] if v.strip().startswith("(") else v
                for m in split_top(inner):
                    if "=" in m:
                        mk, mv = m.split("=", 1)
                        meta[mk.strip()] = mv.strip().strip('"')
                    elif m.strip():
                        meta[m.strip()] = True
            else:
                kv[k] = v.strip('"')
        elif part:
            flags.add(part.strip())
    return flags, kv, meta


def clean_comment(raw):
    raw = raw.strip()
    if raw.startswith("/*"):
        raw = re.sub(r"^/\*+!?", "", raw)
        raw = re.sub(r"\*+/$", "", raw)
        lines = [re.sub(r"^\s*\*\s?", "", l) for l in raw.split("\n")]
    else:
        lines = [re.sub(r"^\s*//+\s?", "", l) for l in raw.split("\n")]
    text = "\n".join(l.rstrip() for l in lines).strip()
    return text


def doc_before(text, pos):
    """The comment directly above pos (a /** */ block or a run of // lines), or ''."""
    j = pos
    while j > 0 and text[j - 1] in " \t":
        j -= 1
    if j > 0 and text[j - 1] == "\n":
        j -= 1
    while j > 0 and text[j - 1] in " \t\r":
        j -= 1
    head = text[:j]
    if head.endswith("*/"):
        s = head.rfind("/*")
        return clean_comment(head[s:])
    lines = head.split("\n")
    got = []
    while lines and lines[-1].strip().startswith("//"):
        line = lines.pop().strip()
        if re.match(r"^//\s*[─━-]{2,}", line) or re.search(r"[─━]{3,}", line):      # a section divider, not a doc
            break
        got.insert(0, line)
    return clean_comment("\n".join(got)) if got else ""


def strip_comments(s):
    s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)
    return re.sub(r"//[^\n]*", " ", s)


def norm_type(t):
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"\s*([<>*&,])\s*", r"\1", t).replace(",", ", ")
    return t


# ---- the model ------------------------------------------------------------------------------------------------------
def parse_file(path, rel, model):
    text = open(path, encoding="utf-8", errors="replace").read()
    text = text.replace("\r\n", "\n")
    # class / struct bodies, for knowing which one a member belongs to
    owners = []
    # an interface's functions live in its I-class, which has no macro of its own: file them under the U-class
    for im in re.finditer(r"\bclass\s+(?:\w+_API\s+)?I(\w+)\b[^;{]*\{", text):
        b0 = im.end() - 1
        owners.append((b0, balanced(text, b0, "{", "}"), "U" + im.group(1)))
    for m in MACROS.finditer(text):
        kind = m.group(1)
        p0 = m.end() - 1
        p1 = balanced(text, p0)
        specs = text[p0 + 1:p1 - 1]
        doc = doc_before(text, m.start())
        rest = text[p1:]
        if kind in ("UCLASS", "USTRUCT", "UINTERFACE"):
            dm = re.match(r"\s*(class|struct)\s+(?:\w+_API\s+)?(\w+)(?:\s*final)?\s*(?::\s*public\s+([\w:]+))?[^{;]*\{", rest)
            if not dm:
                continue
            name, parent = dm.group(2), dm.group(3) or ""
            body_open = p1 + dm.end() - 1
            body_close = balanced(text, body_open, "{", "}")
            flags, kv, meta = parse_specs(specs)
            entry = {"kind": kind[1:].lower(), "name": name, "parent": parent, "file": rel, "doc": doc,
                     "flags": sorted(flags), "meta": meta, "kv": kv,
                     "display": meta.get("DisplayName") or kv.get("DisplayName") or display(re.sub(r"^[UFAI](?=[A-Z])", "", name)),
                     "functions": [], "properties": [], "events": []}
            model["types"][name] = entry
            owners.append((body_open, body_close, name))
        elif kind == "UENUM":
            dm = re.match(r"\s*enum\s+(?:class\s+)?(\w+)\s*(?::\s*\w+)?\s*\{", rest)
            if not dm:
                continue
            name = dm.group(1)
            b0 = p1 + dm.end() - 1
            b1 = balanced(text, b0, "{", "}")
            body = text[b0 + 1:b1 - 1]
            values = []
            pos = 0
            for part in split_top_keep(body):
                seg, offset = part
                code = strip_comments(seg).strip()
                if not code:
                    continue
                vm = re.match(r"(\w+)\s*(?:=\s*([^U,]+?))?\s*(?:UMETA\s*\((.*)\))?\s*$", code, re.S)
                if not vm:
                    continue
                vflags, vkv, vmeta = parse_specs(vm.group(3) or "")
                vdoc = doc_before(body, offset + (len(seg) - len(seg.lstrip())))
                trailing = re.search(r"//\s*(.+)$", seg.strip().split("\n")[-1]) if "//" in seg else None
                if not vdoc:
                    # a trailing // comment after the value (it sits in the next segment's start)
                    nxt = body[offset + len(seg):offset + len(seg) + 200]
                    tm = re.match(r",?[ \t]*//\s*([^\n]+)", nxt)
                    vdoc = tm.group(1).strip() if tm else ""
                hidden = "Hidden" in vflags or vkv.get("Hidden") or vmeta.get("Hidden")
                values.append({"name": vm.group(1), "value": (vm.group(2) or "").strip(),
                               "display": vkv.get("DisplayName") or vmeta.get("DisplayName") or display(vm.group(1)),
                               "doc": vdoc, "hidden": bool(hidden or vm.group(1).endswith("_MAX") or vm.group(1) == "MAX" or vm.group(1) == "Count")})
            flags, kv, meta = parse_specs(specs)
            model["enums"][name] = {"name": name, "file": rel, "doc": doc, "blueprint": "BlueprintType" in flags,
                                    "display": meta.get("DisplayName") or display(re.sub(r"^E(?=[A-Z])", "", name)),
                                    "values": values}
        elif kind.startswith("DECLARE_DYNAMIC"):
            args = split_top(specs)
            dname, rest_args = args[0], args[1:]
            params = [{"type": norm_type(rest_args[i]), "name": rest_args[i + 1]} for i in range(0, len(rest_args) - 1, 2)]
            model["delegates"][dname] = {"name": dname, "params": params, "file": rel, "doc": doc}
        elif kind == "UFUNCTION":
            # the declaration: up to ';' or '{' at paren depth 0
            i, depth = p1, 0
            while i < len(text):
                c = text[i]
                if c == "(":
                    depth += 1
                elif c == ")":
                    depth -= 1
                elif depth == 0 and c in ";{":
                    break
                i += 1
            decl = strip_comments(text[p1:i]).strip()
            decl = re.sub(r"\b(virtual|static|FORCEINLINE|inline|UE_DEPRECATED\([^)]*\))\s+", lambda mm: ("static " if mm.group(1) == "static" else ""), decl)
            fm = re.match(r"(?:(static)\s+)?(.*?)\b(\w+)\s*\((.*)\)\s*(const)?\s*(override)?\s*(?:=\s*0)?\s*$", decl, re.S)
            if not fm:
                continue
            flags, kv, meta = parse_specs(specs)
            params = []
            for ptxt in split_top(fm.group(4)):
                if not ptxt or ptxt == "void":
                    continue
                default = None
                if "=" in ptxt and not re.search(r"[<>]=|==", ptxt):
                    ptxt, default = ptxt.split("=", 1)
                    default = default.strip()
                pm = re.match(r"(.*?)(\w+)\s*$", ptxt.strip(), re.S)
                if not pm:
                    continue
                ptype = norm_type(pm.group(1))
                out = ptype.endswith("&") and not ptype.startswith("const ") and "UPARAM(ref)" not in ptype
                params.append({"type": ptype, "name": pm.group(2), "default": default, "out": out,
                               "display": display(pm.group(2), ptype.startswith("bool"))})
            fname = fm.group(3)
            func = {"name": fname, "display": meta.get("DisplayName") or display(fname), "category": kv.get("Category", ""),
                    "doc": doc, "returns": norm_type(fm.group(2)), "params": params, "static": bool(fm.group(1)) or "static" in text[p1:i][:40],
                    "const": bool(fm.group(5)), "flags": sorted(flags), "meta": meta, "file": rel, "line": text[:m.start()].count("\n") + 1,
                    "pure": ("BlueprintPure" in flags) or (kv.get("BlueprintPure", "").lower() == "true"),
                    "callable": "BlueprintCallable" in flags or "BlueprintPure" in flags or "BlueprintPure" in kv,
                    "event": "BlueprintImplementableEvent" in flags or "BlueprintNativeEvent" in flags}
            if kv.get("BlueprintPure", "").lower() == "false":
                func["pure"] = False
            owner = owner_of(owners, m.start())
            func["owner"] = owner
            model["functions"].append(func)
        elif kind == "UPROPERTY":
            i = p1
            depth = 0
            while i < len(text):
                c = text[i]
                if c in "({":
                    depth += 1
                elif c in ")}":
                    depth -= 1
                elif c == ";" and depth == 0:
                    break
                i += 1
            decl = strip_comments(text[p1:i]).strip()
            default = None
            dm = re.match(r"(.*?)\b(\w+)\s*(?:\[[^\]]*\])?\s*(?::\s*1)?\s*(?:=\s*(.+)|(\{.*\}))?\s*$", decl, re.S)
            if not dm:
                continue
            ptype = norm_type(dm.group(1))
            pname = dm.group(2)
            default = (dm.group(3) or dm.group(4) or None)
            if default:
                default = re.sub(r"\s+", " ", default.strip())
            flags, kv, meta = parse_specs(specs)
            if not doc:                                   # a comment at the end of the declaration's line
                eol = text.find("\n", i)
                tail = text[i + 1:eol if eol >= 0 else len(text)]
                tm = re.match(r"\s*//+\s*(.+)$", tail)
                if tm:
                    doc = tm.group(1).strip()
            is_bool = ptype in ("bool", "uint8") and pname.startswith("b") and len(pname) > 1 and pname[1].isupper()
            prop = {"name": pname, "type": ptype, "default": default, "doc": doc, "category": kv.get("Category", ""),
                    "display": meta.get("DisplayName") or display(pname, is_bool), "flags": sorted(flags), "meta": meta,
                    "file": rel, "line": text[:m.start()].count("\n") + 1, "owner": owner_of(owners, m.start()),
                    "editable": any(f.startswith("Edit") for f in flags), "visible": any(f.startswith("Visible") for f in flags),
                    "blueprint": any(f.startswith("BlueprintRead") for f in flags), "assignable": "BlueprintAssignable" in flags}
            model["properties"].append(prop)


def split_top_keep(body):
    """Enum body split at top-level commas, keeping each segment's offset."""
    out, depth, start, i, quote = [], 0, 0, 0, False
    clean = re.sub(r"/\*.*?\*/", lambda m: " " * len(m.group(0)), body, flags=re.S)
    clean = re.sub(r"//[^\n]*", lambda m: " " * len(m.group(0)), clean)
    while i < len(body):
        c = clean[i]
        if c == '"':
            quote = not quote
        elif not quote:
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            elif c == "," and depth == 0:
                out.append((body[start:i], start))
                start = i + 1
        i += 1
    out.append((body[start:], start))
    return out


def owner_of(owners, pos):
    best = None
    for a, b, name in owners:
        if a <= pos < b and (best is None or a > best[0]):
            best = (a, name)
    return best[1] if best else ""


def constructor_defaults(source, model):
    """Defaults assigned in constructors (Foo::Foo() { X = 1; }), for members with no inline initialiser."""
    names = {t for t in model["types"]}
    found = {}
    for root, _, files in os.walk(source):
        for f in files:
            if not f.endswith(".cpp"):
                continue
            text = open(os.path.join(root, f), encoding="utf-8", errors="replace").read().replace("\r\n", "\n")
            for m in re.finditer(r"\b(\w+)::(\w+)\s*\([^)]*\)\s*(?::[^{]*)?\{", text):
                if m.group(1) != m.group(2) or m.group(1) not in names:
                    continue
                b0 = m.end() - 1
                body = strip_comments(text[b0:balanced(text, b0, "{", "}")])
                for am in re.finditer(r"^\s*(\w+)\s*=\s*([^;]+);", body, re.M):
                    found.setdefault(m.group(1), {})[am.group(1)] = re.sub(r"\s+", " ", am.group(2).strip())
    for p in model["properties"]:
        if p["default"] is None and p["owner"] in found and p["name"] in found[p["owner"]]:
            p["default"] = found[p["owner"]][p["name"]]
            p["default_from"] = "constructor"


def console_commands(source, model):
    """Console variables and commands the plugin registers (aps.*), with their help text."""
    model["console"] = []
    for root, _, files in os.walk(source):
        for f in files:
            if not f.endswith(".cpp"):
                continue
            text = open(os.path.join(root, f), encoding="utf-8", errors="replace").read()
            for m in re.finditer(r"(TAutoConsoleVariable<(\w+)>|FAutoConsoleCommand\w*|FAutoConsoleVariableRef)\s+\w+\s*\(", text):
                p1 = balanced(text, m.end() - 1)
                args = split_top(text[m.end():p1 - 1])
                strings = [re.sub(r'"\s*\n\s*TEXT\("|"\s+"', "", a) for a in args]
                name = re.search(r'TEXT\("([^"]+)"\)', strings[0]) if strings else None
                if not name:
                    continue
                helptext = ""
                for a in args[1:]:
                    lits = re.findall(r'TEXT\("((?:[^"\\]|\\.)*)"\)|"((?:[^"\\]|\\.)*)"', a)
                    if lits:
                        helptext = "".join(x or y for x, y in lits)
                        break
                default = args[1].strip() if m.group(2) and len(args) > 1 else ""
                model["console"].append({"name": name.group(1), "kind": "variable" if m.group(2) else "command",
                                         "type": m.group(2) or "", "default": default, "help": helptext.replace("\\n", " ")})


def build(source):
    model = {"types": {}, "enums": {}, "delegates": {}, "functions": [], "properties": []}
    for root, _, files in os.walk(source):
        for f in sorted(files):
            if f.endswith(".h"):
                path = os.path.join(root, f)
                parse_file(path, os.path.relpath(path, source).replace("\\", "/"), model)
    constructor_defaults(source, model)
    console_commands(source, model)
    # events: BlueprintAssignable properties get their delegate's parameters
    for p in model["properties"]:
        if p["assignable"]:
            d = model["delegates"].get(p["type"])
            p["params"] = d["params"] if d else []
    # plugin version
    up = os.path.join(os.path.dirname(source.rstrip("/\\")), "APS.uplugin")
    if os.path.exists(up):
        model["plugin"] = json.load(open(up, encoding="utf-8-sig"))
    return model


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    model = build(src)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(model, fh, indent=1, ensure_ascii=False)
    fx = model["functions"]
    pr = model["properties"]
    print("types %d, enums %d, delegates %d, functions %d (Blueprint %d), properties %d (editable %d, events %d)" % (
        len(model["types"]), len(model["enums"]), len(model["delegates"]), len(fx), sum(1 for f in fx if f["callable"] or f["event"]),
        len(pr), sum(1 for p in pr if p["editable"]), sum(1 for p in pr if p["assignable"])))
