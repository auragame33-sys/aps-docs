"""Writes the docs' Reference pages from the source model (tools/model.json, made by apsref.py):
components, Blueprint nodes, events, settings and types, every one of them, as the editor shows them.
Nothing here is typed by hand, so the reference cannot drift from the plugin: regenerate after a plugin change.

    python -I genref.py            (reads tools/model.json, writes content/reference/*.md)
"""
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "content", "reference")
M = json.load(open(os.path.join(HERE, "model.json"), encoding="utf-8"))
TYPES, ENUMS = M["types"], M["enums"]
VERSION = M.get("plugin", {}).get("VersionName", "?")

ENGINE_TYPES = {
    "float": ("Float", "float"), "double": ("Float", "float"), "int32": ("Integer", "int"), "int": ("Integer", "int"),
    "int64": ("Integer64", "int"), "uint8": ("Byte", "byte"), "bool": ("Boolean", "bool"), "FName": ("Name", "name"),
    "FString": ("String", "string"), "FText": ("Text", "text"), "FVector": ("Vector", "vector"), "FRotator": ("Rotator", "rotator"),
    "FTransform": ("Transform", "transform"), "FVector2D": ("Vector 2D", "struct"), "FLinearColor": ("Linear Color", "struct"),
    "FColor": ("Color", "struct"), "FGameplayTag": ("Gameplay Tag", "struct"), "FGameplayTagContainer": ("Gameplay Tag Container", "struct"),
    "FHitResult": ("Hit Result", "struct"), "FGuid": ("Guid", "struct"), "void": ("", ""),
}


def friendly_object(name):
    t = TYPES.get(name)
    if t:
        return t["display"]
    return re.sub(r"^[UAF](?=[A-Z])", "", name) if not name.startswith("E") else name


def pin(ctype):
    """A C++ type as the Blueprint editor names it, plus a colour class for its pin."""
    t = ctype.replace("const ", "").replace("class ", "").replace("struct ", "").replace("&", "").strip()
    t = re.sub(r"\bUPARAM\([^)]*\)\s*", "", t).strip()
    m = re.match(r"^(TArray|TSet)<(.+)>$", t)
    if m:
        inner, cls = pin(m.group(2))
        return ("Array of " if m.group(1) == "TArray" else "Set of ") + inner, cls + " container"
    m = re.match(r"^TMap<(.+?),\s*(.+)>$", t)
    if m:
        k, _ = pin(m.group(1))
        v, cls = pin(m.group(2))
        return "Map of %s to %s" % (k, v), cls + " container"
    m = re.match(r"^TSubclassOf<(.+)>$", t)
    if m:
        return friendly_object(m.group(1).strip()) + " Class", "class"
    m = re.match(r"^TSoftClassPtr<(.+)>$", t)
    if m:
        return friendly_object(m.group(1).strip()) + " Class (soft)", "class"
    m = re.match(r"^TSoftObjectPtr<(.+)>$", t)
    if m:
        return friendly_object(m.group(1).strip()) + " (soft)", "object"
    m = re.match(r"^(TObjectPtr|TWeakObjectPtr)<(.+)>$", t)
    if m:
        return pin(m.group(2) + "*")
    m = re.match(r"^TEnumAsByte<(.+)>$", t)
    if m:
        return pin(m.group(1))
    t = t.replace("*", "").strip()
    if t in ENGINE_TYPES:
        return ENGINE_TYPES[t]
    if t in ENUMS:
        return ENUMS[t]["display"], "enum"
    if t.startswith("E") and t[1:2].isupper():
        return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", t[1:]), "enum"
    if t.startswith("F") and t[1:2].isupper():
        return friendly_object(t) if t in TYPES else re.sub(r"(?<=[a-z])(?=[A-Z])", " ", t[1:]), "struct"
    return friendly_object(t), "object"


def default_text(v, ctype=""):
    if v is None:
        return ""
    v = v.strip()
    if v in ("nullptr", "NULL", "NAME_None", "FName()", "FString()", "FText()", "FText::GetEmpty()", "{}", "TEXT(\"\")", "\"\""):
        return "None" if v in ("nullptr", "NULL") else "empty"
    v = re.sub(r'^TEXT\("(.*)"\)$', r"\1", v)
    v = re.sub(r'^FName\(TEXT\("(.*)"\)\)$', r"\1", v)
    v = re.sub(r'^FName\("(.*)"\)$', r"\1", v)
    v = v.strip('"')
    if re.match(r"^-?\d+(\.\d*)?f?$", v) or re.match(r"^-?\.\d+f?$", v):
        num = float(v.rstrip("f"))
        return ("%g" % num) if abs(num) < 1e6 else ("%.0f" % num)
    if v in ("true", "false"):
        return "On" if v == "true" else "Off"
    m = re.match(r"^(E\w+)::(\w+)$", v)
    if m and m.group(1) in ENUMS:
        for val in ENUMS[m.group(1)]["values"]:
            if val["name"] == m.group(2):
                return val["display"]
        return m.group(2)
    m = re.match(r"^F(Vector|Rotator|Vector2D|LinearColor)\s*\((.*)\)$", v)
    if m:
        parts = [default_text(p) for p in m.group(2).split(",")]
        return "(%s)" % ", ".join(parts) if parts != ["empty"] else "(0, 0, 0)"
    if v in ("FVector::ZeroVector", "FRotator::ZeroRotator"):
        return "(0, 0, 0)"
    if v == "FVector::ForwardVector":
        return "(1, 0, 0)"
    # a class or asset by path: show its name, not the C++ that builds the path
    m = re.search(r'TEXT\("(/[^"]+)"\)', v)
    if m and ("SoftClassPtr" in v or "SoftObjectPtr" in v or "SoftObjectPath" in v):
        return m.group(1).rsplit("/", 1)[-1].split(".")[0]
    # a sense's loss settings: { Grace Time, Direct Cut, Confidence Decay Multiplier }
    m = re.match(r"^\{\s*([\d.]+)f?\s*,\s*(true|false)\s*,\s*([\d.]+)f?\s*\}$", v)
    if m:
        return "Grace %s s, %s, decay × %s" % (default_text(m.group(1)), "direct cut" if m.group(2) == "true" else "no direct cut",
                                               default_text(m.group(3)))
    # a list of enum values: their names
    if v.startswith("{") and v.endswith("}") and re.fullmatch(r"\{\s*(E\w+::\w+\s*,?\s*)+\}", v):
        return ", ".join(default_text(x.strip()) for x in v.strip("{} ").split(",") if x.strip())
    if v.startswith("FLinearColor::") or v.startswith("FColor::"):
        return v.split("::")[1]
    if re.match(r"^\d+\s*\*\s*\d+$", v):
        a, b = v.split("*")
        return str(int(a) * int(b))
    return v


def esc(s):
    return html.escape(s or "", quote=True)


# ---- descriptions: the source's doc comment, else a note written from the implementation (tools/notes.json)
NOTES = {k: re.sub(r"\s*\([\w./, ]+\.(?:h|cpp)(?:, [\w./]+\.(?:h|cpp))*\)\s*$", "", v)
         for k, v in json.load(open(os.path.join(HERE, "notes.json"), encoding="utf-8")).items() if not k.startswith("_")}
USED_OLD = []


def md_inline(t):
    t = esc(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    return t


def described(owner, name, display_name, doc):
    """(html, plain) for a member: its doc comment, or a fallback."""
    if (doc or "").strip():
        return doc_html(doc), one_line(doc)
    note = NOTES.get("%s.%s" % (owner, name))
    if note:
        return "<p>%s</p>" % esc(note), note
    return "", ""


def doc_html(text):
    """A doc comment as short HTML paragraphs (Unreal-style tooltips; blank lines split paragraphs)."""
    text = (text or "").strip()
    if not text:
        return ""
    paras = [re.sub(r"\s*\n\s*", " ", p).strip() for p in re.split(r"\n\s*\n", text)]
    out = []
    for p in paras:
        p = esc(p)
        p = re.sub(r"`([^`]+)`", r"<code>\1</code>", p)
        out.append("<p>%s</p>" % p)
    return "".join(out)


def one_line(text):
    text = re.sub(r"\s+", " ", (text or "").strip())
    return text


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def owner_display(owner):
    t = TYPES.get(owner)
    return t["display"] if t else owner


def is_component(t):
    return "BlueprintSpawnableComponent" in t["meta"] or t["parent"] == "UActorComponent" and t["kind"] == "class"


# ---- node cards -----------------------------------------------------------------------------------------------------
def pin_html(label, ctype, default=None, exec_pin=False, side="in"):
    if exec_pin:
        return '<span class="pin exec"><i></i></span>'
    tname, cls = pin(ctype)
    d = default_text(default, ctype) if default is not None else ""
    dv = ' <em>%s</em>' % esc(d) if d and d != "empty" else ""
    return '<span class="pin %s" title="%s"><i></i><b>%s</b><small>%s</small>%s</span>' % (cls, esc(tname), esc(label), esc(tname), dv)


def node_card(f, anchor):
    hidden = set()
    wc = f["meta"].get("WorldContext")
    if wc:
        hidden.add(wc)
    for k in ("HidePin", "InternalUseParam"):
        if k in f["meta"]:
            hidden.update(x.strip() for x in str(f["meta"][k]).split(","))
    kind = "event" if f["event"] else ("pure" if f["pure"] else "call")
    ins, outs = [], []
    if kind == "call":
        ins.append(pin_html("", "", exec_pin=True))
        outs.append(pin_html("", "", exec_pin=True))
    if not f["static"] and kind != "event" and f["owner"]:
        ins.append(pin_html("Target", f["owner"] + "*"))
    for p in f["params"]:
        if p["name"] in hidden:
            continue
        (outs if p["out"] else ins).append(pin_html(p["display"], p["type"], p["default"] if not p["out"] else None))
    if f["returns"] and f["returns"] != "void":
        outs.append(pin_html(f["meta"].get("ReturnDisplayName", "Return Value"), f["returns"]))
    badges = []
    if f["static"]:
        badges.append("library")
    if "DevelopmentOnly" in f["meta"]:
        badges.append("development builds only")
    if "DeprecatedFunction" in f["meta"]:
        badges.append("deprecated")
    if f["event"]:
        badges.append("override in Blueprint")
    target = "" if f["static"] else owner_display(f["owner"])
    dhtml, dplain = described(f["owner"], f["name"], f["display"], f["doc"])
    head_kind = {"pure": "Pure", "call": "Callable", "event": "Event to override"}[kind]
    return ('<div class="bpn %s" id="%s" data-search="%s" data-text="%s">'
            '<div class="bpn-head"><span class="bpn-icon"></span><b>%s</b>%s</div>'
            '<div class="bpn-meta"><span>%s</span>%s%s</div>'
            '<div class="bpn-pins"><div class="bpn-in">%s</div><div class="bpn-out">%s</div></div>'
            '<div class="bpn-doc">%s</div></div>'
            % (kind, anchor, esc(f["display"]), esc(dplain[:300]), esc(f["display"]),
               "".join('<span class="badge">%s</span>' % esc(b) for b in badges),
               esc(head_kind), (' <span>Target is <b>%s</b></span>' % esc(target)) if target else "",
               ' <span class="cat">%s</span>' % esc(f["category"].replace("|", " › ")) if f["category"] else "",
               "".join(ins), "".join(outs), dhtml or "<p class=\"nodoc\">No description in the source.</p>"))


def event_card(p, anchor):
    dhtml, dplain = described(p["owner"], p["name"], p["display"], p["doc"])
    outs = [pin_html("", "", exec_pin=True)] + [pin_html(re.sub(r"(?<=[a-z])(?=[A-Z])", " ", x["name"]), x["type"]) for x in p.get("params", [])]
    return ('<div class="bpn event" id="%s" data-search="%s" data-text="%s">'
            '<div class="bpn-head"><span class="bpn-icon"></span><b>%s</b></div>'
            '<div class="bpn-meta"><span>Event</span> <span>on <b>%s</b></span> <span class="cat">%s</span></div>'
            '<div class="bpn-pins"><div class="bpn-in"></div><div class="bpn-out">%s</div></div>'
            '<div class="bpn-doc">%s</div></div>'
            % (anchor, esc(p["display"]), esc(dplain[:300]), esc(p["display"]), esc(owner_display(p["owner"])),
               esc(p["category"].replace("|", " › ")), "".join(outs),
               dhtml or "<p class=\"nodoc\">No description in the source.</p>"))


# ---- settings -------------------------------------------------------------------------------------------------------
INERT = {k: v for k, v in json.load(open(os.path.join(HERE, "inert.json"), encoding="utf-8")).items() if not k.startswith("_")}


# Defaults too structured to print from their C++ initializer (checked against the constructor).
DEFAULT_SHOWN = {
    "UAPSTargetComponent.VisibilitySamples": "5 points: head socket (weight 1), chest (0.9), pelvis (0.7), "
                                             "clavicle_l and clavicle_r sockets (0.6 each)",
}


def setting_row(p, anchor):
    dhtml, dplain = described(p["owner"], p["name"], p["display"], p["doc"])
    why = INERT.get("%s.%s" % (p["owner"], p["name"]))
    if why:
        dhtml = ('<p class="inert-why"><b>Does nothing in APS %s.</b> %s</p>' % (esc(VERSION), esc(why))) + dhtml
    tname, cls = pin(p["type"])
    d = DEFAULT_SHOWN.get("%s.%s" % (p["owner"], p["name"])) or default_text(p["default"], p["type"])
    if p["type"] == "bool" and not d:
        d = "Off"
    meta = p["meta"]
    rng = []
    lo, hi = meta.get("ClampMin", meta.get("UIMin")), meta.get("ClampMax", meta.get("UIMax"))
    if lo is not None and hi is not None:
        rng.append("%s to %s" % (default_text(str(lo)), default_text(str(hi))))
    elif lo is not None:
        rng.append("at least %s" % default_text(str(lo)))
    elif hi is not None:
        rng.append("at most %s" % default_text(str(hi)))
    units = meta.get("Units") or meta.get("ForceUnits")
    if units:
        rng.append(str(units).lower())
    cond = meta.get("EditCondition")
    when = ""
    if cond:
        cm = re.match(r"^\s*(!)?\s*(\w+)\s*(==\s*(.+))?$", str(cond))
        if cm:
            other = next((q for q in M["properties"] if q["owner"] == p["owner"] and q["name"] == cm.group(2)), None)
            od = other["display"] if other else cm.group(2)
            if cm.group(3):
                when = "only when %s is %s" % (od, default_text(cm.group(4).strip()))
            else:
                when = ("only when %s is off" if cm.group(1) else "only when %s is on") % od
        else:
            when = "only when " + str(cond)
    return ('<div class="set" id="%s" data-search="%s" data-text="%s">'
            '<div class="set-head"><b>%s</b><span class="pin %s"><i></i><small>%s</small></span>%s</div>'
            '<div class="set-facts">%s%s%s%s</div><div class="set-doc">%s</div></div>'
            % (anchor, esc(p["display"]), esc(dplain[:300]), esc(p["display"]), cls, esc(tname),
               '<span class="adv">advanced</span>' if "AdvancedDisplay" in p["flags"] else "",
               '<span>Default <b>%s</b></span>' % esc(d) if d else "",
               # The name Overrides, Set Profile Number/Flag and aps.Tune take: the C++ name, not
               # the Details label (a tickbox keeps its b, some keep an underscore).
               '<span title="The name Overrides, Set Profile Number and aps.Tune take">Override name <code>%s</code></span>'
               % esc(p["name"]) if p["owner"] == "UPerceptionProfile" else "",
               "".join('<span>%s</span>' % esc(r) for r in rng),
               '<span class="when">%s</span>' % esc(when) if when else "",
               dhtml or "<p class=\"nodoc\">No description in the source.</p>"))


def cat_title(cat, strip_prefix="APS|"):
    c = cat[len(strip_prefix):] if cat.startswith(strip_prefix) else cat
    return c.replace("|", " › ") or "General"


# ---- pages ----------------------------------------------------------------------------------------------------------
HEADER = ("<!-- Generated by tools/genref.py from the APS %s source. Do not edit by hand: change the plugin's comments "
          "and run tools/apsref.py, then tools/genref.py. -->" % VERSION)


def write(name, front, body):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write("---\n%s\n---\n%s\n\n%s\n" % (front.strip(), HEADER, body.strip()))


def source_note():
    return ('<div class="gen-note">Generated from the APS %s source code: every name, pin, default and description '
            'below is read from the plugin itself, so it matches what you see in the editor.</div>' % esc(VERSION))


def ordered_owners():
    """Where Blueprint nodes live, in the order a user meets them."""
    first = ["UPerceptionCore", "UAPSPerceptionListener", "UAPSTargetComponent", "URelationshipComponent", "UAPSEnvironmentComponent",
             "UAPSSubsystem", "UPerceptionSoundSystem", "UAPSViewLibrary", "UAPSDebugHelper", "UPerceptionProfile",
             "USenseUnit_Pain", "USenseUnit_Touch", "USenseUnit_Vibration", "USenseUnit_Smell", "USenseUnit",
             "UAPSSignatureComponent", "UAPSObserverComponent", "UAPSEvidenceComponent", "UAPSSearchComponent",
             "UAPSKnowledgeSubsystem", "UAPSDescriptorLibrary",
             "UAPSFusionPolicy", "UAPSThreatPolicy", "UAPSAttentionPolicy", "UAPSSignificancePolicy", "UAPSHealthProvider", "UAPSStanceProvider"]
    seen = {f["owner"] for f in M["functions"] if f["callable"] or f["event"]}
    return [o for o in first if o in seen] + sorted(seen - set(first))


OWNER_INTRO = {
    "UPerceptionCore": "The component on every AI. Its nodes read what the AI believes and change how it behaves. Drag from an APS Core reference, or right-click in its owner's graph and type the node's name.",
    "UAPSPerceptionListener": "Put your reactions in a Blueprint made from APS Perception Listener and add it to every AI that should share them. These are the events you implement there.",
    "UAPSSubsystem": "World-wide APS settings and lookups. Get it with **Get APSSubsystem** (any Blueprint) and drag from it.",
    "UAPSKnowledgeSubsystem": "The Knowledge module's world-wide memory of identities, factions and dispatch. Get it with **Get APSKnowledge Subsystem**.",
    "UAPSViewLibrary": "Read-only data for drawing what an AI perceives (the APS Visualizer is built only from these). Callable from any Blueprint.",
    "UPerceptionSoundSystem": "Make noises the AI can hear. Callable from any Blueprint.",
    "UAPSDebugHelper": "Tools for inspecting squads while you play. Callable from any Blueprint.",
    "UAPSDescriptorLibrary": "Build and compare descriptors (what a witness says about someone). Callable from any Blueprint.",
    "UAPSFusionPolicy": "Make a Blueprint child of this class and set it on the profile's Fusion Policy to decide how senses combine.",
    "UAPSThreatPolicy": "Make a Blueprint child and set it on the profile's Threat Policy to score threats your way.",
    "UAPSAttentionPolicy": "Make a Blueprint child and set it on the profile's Attention Policy to choose what the AI attends to.",
    "UAPSSignificancePolicy": "Make a Blueprint child and set it on the APS subsystem to rank which AI get full-quality updates.",
    "UAPSHealthProvider": "An interface: implement it on your character so APS can read its health without knowing your health system.",
    "USenseUnit_Touch": "<p class=\"inert-why\"><b>Not reachable from Blueprint in APS 3.0.</b> These are on the Touch Sense object the APS Core creates, and no node returns it. Use the APS Core's <b>Report Touch Contact</b>, <b>Report Touch Contact with Impulse</b> and <b>End Touch Contact</b>, which do the same.</p>",
    "USenseUnit_Vibration": "<p class=\"inert-why\"><b>Not reachable from Blueprint in APS 3.0.</b> This is on the Vibration Sense object the APS Core creates, and no node returns it. Use the APS Core's <b>Report Vibration Event</b>, which does the same.</p>",
    "USenseUnit_Smell": "<p class=\"inert-why\"><b>Not reachable from Blueprint in APS 3.0.</b> This is on the Smell Sense object the APS Core creates, and no node returns it. For one kind of AI with its own wind, set <b>Wind Direction</b> in the Class Defaults of a Blueprint child of Smell Sense; for everyone, <b>Set Wind State</b> on the APS Subsystem.</p>",
    "USenseUnit_Pain": "<p class=\"inert-why\"><b>Not reachable from Blueprint in APS 3.0.</b> These are on the Pain Sense object the APS Core creates, and no node returns it. Use the APS Core's pain nodes of the same names; Set Health Ratio, Get Health Ratio and Get Pain State are for C++ only (the core's GetSenseInstances). From Blueprint, give APS health with the APSHealth Provider interface.</p>",
    "UAPSStanceProvider": "An interface: implement it on your character so APS can read its stance (standing, crouching, prone) from your own movement code.",
}


def nodes_page():
    owners = ordered_owners()
    body = [source_note(), "",
            "Every APS node you can place in a Blueprint graph, grouped by where it lives. **Green** nodes are pure "
            "(no white execution pins: they only read), **blue** nodes do something, **red** ones are events you "
            "override. Pins are coloured as in the editor. Search this page with [[Ctrl]] + [[F]], or the site search "
            "above: every node is in it.", ""]
    counts = {}
    for o in owners:
        fs = [f for f in M["functions"] if f["owner"] == o and (f["callable"] or f["event"])]
        if not fs:
            continue
        counts[o] = len(fs)
        body.append("## %s" % owner_display(o))
        if o in OWNER_INTRO:
            body.append(OWNER_INTRO[o])
            body.append("")
        cats = []
        for f in fs:
            if f["category"] not in cats:
                cats.append(f["category"])
        for c in cats:
            group = [f for f in fs if f["category"] == c]
            if len(cats) > 1:
                body.append("### %s" % cat_title(c))
            body.append('<div class="bpn-list">' + "".join(node_card(f, "n-" + slug(owner_display(o) + "-" + f["name"])) for f in group) + "</div>")
            body.append("")
    write("nodes.md", "title: Blueprint nodes\ndescription: Every APS Blueprint node, with its pins, defaults and description, generated from the plugin source.\ntoc: 2",
          "# Blueprint nodes\n\n" + "\n".join(body))
    return counts


def events_page():
    body = [source_note(), "",
            "Two kinds of events. **Bind** the first kind: select the component, and at the bottom of its Details click "
            "**+** next to the event. **Override** the second kind in a Blueprint made from the class (a Listener, a "
            "policy, a sense), from the **Functions** list's **Override** menu.", ""]
    bind = [p for p in M["properties"] if p["assignable"]]
    owners = []
    for p in bind:
        if p["owner"] not in owners:
            owners.append(p["owner"])
    n = 0
    body.append("## Events you bind")
    for o in owners:
        body.append("### %s" % owner_display(o))
        group = [p for p in bind if p["owner"] == o]
        body.append('<div class="bpn-list">' + "".join(event_card(p, "e-" + slug(owner_display(o) + "-" + p["name"])) for p in group) + "</div>")
        body.append("")
        n += len(group)
    body.append("## Events you override")
    over = [f for f in M["functions"] if f["event"]]
    for o in ordered_owners():
        group = [f for f in over if f["owner"] == o]
        if not group:
            continue
        body.append("### %s" % owner_display(o))
        if o in OWNER_INTRO:
            body.append(OWNER_INTRO[o])
            body.append("")
        body.append('<div class="bpn-list">' + "".join(node_card(f, "o-" + slug(owner_display(o) + "-" + f["name"])) for f in group) + "</div>")
        body.append("")
        n += len(group)
    write("events.md", "title: Events\ndescription: Every APS event you bind or override, with its pins, generated from the plugin source.\ntoc: 3",
          "# Events\n\n" + "\n".join(body))
    return n


def settings_block(owner, props, prefix):
    cats = []
    for p in props:
        if p["category"] not in cats:
            cats.append(p["category"])
    out = []
    for c in cats:
        group = [p for p in props if p["category"] == c]
        out.append("### %s" % cat_title(c))
        out.append('<div class="set-list">' + "".join(setting_row(p, prefix + slug(p["display"])) for p in group) + "</div>")
        out.append("")
    return out


def editable(owner):
    return [p for p in M["properties"] if p["owner"] == owner and (p["editable"] or (p["visible"] and p["blueprint"])) and not p["assignable"]]


def profile_page():
    props = editable("UPerceptionProfile")
    body = [source_note(), "",
            "Everything an AI perceives, and how sharply, is set on its **Perception Profile** (a Data Asset). These are all "
            "of its settings, in the order and groups of its Details panel. A new profile works as it is: every setting "
            "has a working default.", ""]
    cats = []
    for p in props:
        top = p["category"].split("|")[0]
        if top not in cats:
            cats.append(top)
    for top in cats:
        group = [p for p in props if p["category"].split("|")[0] == top]
        body.append("## %s" % top)
        sub = []
        for p in group:
            if p["category"] not in sub:
                sub.append(p["category"])
        for c in sub:
            g2 = [p for p in group if p["category"] == c]
            if c != top:
                body.append("### %s" % cat_title(c).split(" › ", 1)[-1])
            body.append('<div class="set-list">' + "".join(setting_row(p, "s-" + slug(p["display"])) for p in g2) + "</div>")
            body.append("")
    write("profile.md", "title: Profile settings\ndescription: Every Perception Profile setting with its default, range and description, generated from the plugin source.\ntoc: 2",
          "# Profile settings\n\n" + "\n".join(body))
    return len(props)


# One or two sentences per class for the reader, instead of the source's class comment, which is
# written for whoever maintains the plugin (history, "WHY IT EXISTS", pipeline notes) or is empty.
CLASS_DOC = {
    "UPerceptionCore": 'The component that makes an AI perceive. Put it on the AI\'s <b>Pawn</b> (never its controller), assign a Perception Profile, and handle its events. <a href="../getting-started.html">Getting started</a>',
    "UAPSPerceptionListener": 'Optional. Make a Blueprint from it, implement the APS events there, and add it to every AI that should share those reactions. It must sit on the same actor as the APS Core.',
    "UAPSTargetComponent": 'Optional, on anything AI look at (the player, NPCs, vehicles): where its sample points are, its stance, a light level from your own light gem, camouflage, and registration for non-Pawns. <a href="../features/confidence.html">Confidence</a>',
    "URelationshipComponent": 'Optional, on an AI beside its APS Core: who is an enemy, a friend, feared or neutral, by class, by team or per actor. <a href="../features/squads.html#teams-and-relationships">Squads &amp; teams</a>',
    "UAPSEnvironmentComponent": 'Makes a sphere around its actor where light, rain, wind, indoors or sense ranges are different: fog, smoke, a cellar, a market. <a href="../features/world.html#places-with-their-own-conditions">World &amp; fairness</a>',
    "UAPSSignatureComponent": 'What a witness could describe about this actor: traits like a red coat or a white van. <a href="../features/knowledge.html">Knowledge &amp; witnesses</a>',
    "UAPSObserverComponent": 'On an AI beside its APS Core: reports what it perceives to its faction, as a description, and discovers evidence. <a href="../features/knowledge.html#the-observer-a-guard-that-reports">Knowledge &amp; witnesses</a>',
    "UAPSEvidenceComponent": 'Turns its actor into something AI can find and draw a conclusion from: a body, a forced lock, blood. <a href="../features/search.html#evidence">Search &amp; evidence</a>',
    "UAPSSearchComponent": 'Hands an AI the best place to look next while it searches, spreading at the target\'s speed and staying on the navmesh. <a href="../features/search.html#search">Search &amp; evidence</a>',
    "UPerceptionProfile": 'Every setting for how one kind of AI perceives. <a href="../guides/profiles.html">Profiles</a>',
    "UAPSQualityProfile": 'Makes an AI cheaper or dearer without changing what it does: update rates, sample points, the light trace. Nothing it believes is reset. <a href="../guides/performance.html#2-quality-profiles">Performance &amp; crowds</a>',
    "USoundTypeDefinition": 'One kind of noise (a footstep, a gunshot): how loud, how far, how alarming. Emit it with Emit Sound. <a href="../features/hearing.html">Hearing</a>',
    "USoundFilterProfile": 'Which sounds an AI reacts to, by category, alert level and team, and how loud each seems to it. <a href="../features/hearing.html#6-filters-hear-only-what-matters">Hearing</a>',
    "UPainTypeDefinition": 'One kind of pain (a flash, burning, bleeding): which senses it dulls and how fast it fades. <a href="../features/emotions.html#pain-senses-that-stop-working">Emotions &amp; pain</a>',
    "USenseUnit": 'The parent of every sense, and of your own: a sense made directly from it sets these in its Class Defaults. The built-in senses ignore them. <a href="../guides/custom-senses.html">Custom senses</a>',
    "USenseUnit_Vision": 'Sight: five points per target, cones, the head\'s direction, light, cover and see-through surfaces. <a href="../features/senses.html#vision">Senses</a>',
    "USenseUnit_Hearing": 'Hears only the sounds your game emits, muffled by walls, building up with repeats. <a href="../features/hearing.html">Hearing</a>',
    "USenseUnit_Smell": 'Scent carried by the wind, in the dark and around corners; places a target only roughly. <a href="../features/senses.html#smell">Senses</a>',
    "USenseUnit_Touch": 'Contact: bumps, grabs, hits and blasts, wired automatically; the only sense that knows exactly where you are. <a href="../features/senses.html#touch">Senses</a>',
    "USenseUnit_Vibration": 'Footsteps through the floor, through walls, faster movement felt more. <a href="../features/senses.html#vibration">Senses</a>',
    "USenseUnit_Echolocation": 'Sonar pulses: no light or line of sight needed, precise up close. <a href="../features/senses.html#echolocation">Senses</a>',
    "USenseUnit_Damage": 'Being hurt tells the AI who did it, at any range, from every Unreal damage call. <a href="../features/emotions.html#damage-knowing-who-hurt-it">Emotions &amp; pain</a>',
    "USenseUnit_Pain": 'Pain you report, and low health, dull the AI\'s other senses. <a href="../features/emotions.html#pain-senses-that-stop-working">Emotions &amp; pain</a>',
}


def class_doc(t):
    return CLASS_DOC.get(t["name"]) or doc_html(t["doc"]) or ""


def components_page():
    comps = [t for t in TYPES.values() if t["kind"] == "class" and "BlueprintSpawnableComponent" in t["meta"]]
    order = ["UPerceptionCore", "UAPSPerceptionListener", "UAPSTargetComponent", "URelationshipComponent", "UAPSEnvironmentComponent",
             "UAPSSignatureComponent", "UAPSObserverComponent", "UAPSEvidenceComponent", "UAPSSearchComponent"]
    comps.sort(key=lambda t: order.index(t["name"]) if t["name"] in order else 99)
    assets = [TYPES[n] for n in ("UPerceptionProfile", "UAPSQualityProfile", "USoundTypeDefinition", "USoundFilterProfile", "UPainTypeDefinition") if n in TYPES]
    senses = [t for t in TYPES.values() if t["kind"] == "class" and t["parent"] == "USenseUnit"]
    body = [source_note(), "",
            "Every APS component you can add to an actor, every asset type you can create, and every sense, with all "
            "their settings. All components are listed under **Add** in the Components panel: type `aps`.", "",
            "## Components"]
    n = 0
    for t in comps:
        props = editable(t["name"])
        n += len(props)
        nodes = sum(1 for f in M["functions"] if f["owner"] == t["name"] and (f["callable"] or f["event"]))
        events = sum(1 for p in M["properties"] if p["owner"] == t["name"] and p["assignable"])
        body.append("### %s" % t["display"])
        body.append('<div class="comp-doc">%s</div>' % class_doc(t))
        facts = []
        if nodes:
            facts.append("[%d Blueprint nodes](nodes.md#%s)" % (nodes, slug(t["display"])))
        if events:
            facts.append("[%d events](events.md#%s)" % (events, slug(t["display"])))
        if facts:
            body.append("It has " + " and ".join(facts) + ".")
            body.append("")
        if props:
            body.append('<div class="set-list">' + "".join(setting_row(p, "c-" + slug(t["display"] + "-" + p["display"])) for p in props) + "</div>")
        else:
            body.append("*No settings of its own: add it and it works.*")
        body.append("")
    body.append("## Assets")
    body.append("Create these in the Content Browser: right-click, **Miscellaneous → Data Asset**, and pick the class.")
    body.append("")
    for t in assets:
        props = editable(t["name"])
        body.append("### %s" % t["display"])
        body.append('<div class="comp-doc">%s</div>' % class_doc(t))
        if t["name"] == "UPerceptionProfile":
            body.append("Its %d settings have [their own page](profile.md)." % len(props))
            body.append("")
            continue
        n += len(props)
        body.append('<div class="set-list">' + "".join(setting_row(p, "a-" + slug(t["display"] + "-" + p["display"])) for p in props) + "</div>")
        body.append("")
    body.append("## Senses")
    body.append("A profile lists the senses its AI has in **Sense Classes**. Settings shared by every sense live on the "
                "profile; the settings below belong to one sense: to change them, make a Blueprint child of the sense "
                "(right-click it in the class picker, or **Blueprint Class** and search its name), set them in its Class "
                "Defaults, and put your child class in the profile's Sense Classes instead.")
    body.append("")
    base = TYPES.get("USenseUnit")
    if base:
        props = editable("USenseUnit")
        body.append("### Every sense")
        body.append('<div class="comp-doc">%s</div>' % class_doc(base))
        if props:
            body.append('<div class="set-list">' + "".join(setting_row(p, "x-sense-" + slug(p["display"])) for p in props) + "</div>")
        body.append("")
        n += len(props)
    for t in sorted(senses, key=lambda t: t["display"]):
        props = editable(t["name"])
        n += len(props)
        body.append("### %s" % t["display"])
        body.append('<div class="comp-doc">%s</div>' % class_doc(t))
        if props:
            body.append('<div class="set-list">' + "".join(setting_row(p, "x-" + slug(t["display"] + "-" + p["display"])) for p in props) + "</div>")
        else:
            body.append("*All of this sense's settings are on the Perception Profile.*")
        body.append("")
    write("components.md", "title: Components & assets\ndescription: Every APS component, asset and sense with all its settings, generated from the plugin source.\ntoc: 3",
          "# Components & assets\n\n" + "\n".join(body))
    return n


def types_page():
    body = [source_note(), "",
            "The choices (enums) and data (structs) APS nodes and events pass around, with every value and field.", "",
            "## Enums"]
    ne = 0
    for e in sorted(ENUMS.values(), key=lambda e: e["display"]):
        if not e["blueprint"]:
            continue
        ne += 1
        vals = [v for v in e["values"] if not v["hidden"]]
        body.append("### %s" % e["display"])
        if e["doc"]:
            body.append('<div class="comp-doc">%s</div>' % doc_html(e["doc"]))
        rows = "".join('<tr id="%s" data-search="%s" data-text="%s"><td><b>%s</b></td><td>%s</td></tr>'
                       % ("v-" + slug(e["display"] + "-" + v["display"]), esc(v["display"]), esc(e["display"]),
                          esc(v["display"]), doc_html(v["doc"]) or "") for v in vals)
        body.append('<div class="table"><table class="enum"><thead><tr><th>Value</th><th>Meaning</th></tr></thead><tbody>%s</tbody></table></div>' % rows)
        body.append("")
    body.append("## Structs")
    ns = 0
    for t in sorted(TYPES.values(), key=lambda t: t["display"]):
        if t["kind"] != "struct" or "BlueprintType" not in t["flags"]:
            continue
        fields = [p for p in M["properties"] if p["owner"] == t["name"] and (p["blueprint"] or p["editable"])]
        ns += 1
        body.append("### %s" % t["display"])
        if t["doc"]:
            body.append('<div class="comp-doc">%s</div>' % doc_html(t["doc"]))
        if fields:
            body.append('<div class="set-list">' + "".join(setting_row(p, "f-" + slug(t["display"] + "-" + p["display"])) for p in fields) + "</div>")
        body.append("")
    body.append("## Console commands")
    body.append("Type these in the console ([[`]] while playing, or the editor's **Cmd** box).")
    body.append("")
    for c in M.get("console", []):
        body.append("### %s" % c["name"])
        body.append(c["help"] + (" (default `%s`)" % c["default"] if c["default"] else ""))
        body.append("")
    write("types.md", "title: Enums, types & console\ndescription: Every APS enum value, struct field and console command, generated from the plugin source.\ntoc: 2",
          "# Enums, types & console\n\n" + "\n".join(body))
    return ne, ns


if __name__ == "__main__":
    c = nodes_page()
    e = events_page()
    p = profile_page()
    s = components_page()
    t = types_page()
    with open(os.path.join(HERE, "used_old_descriptions.txt"), "w", encoding="utf-8", newline="\n") as fh:
        for o, d, fname, text in sorted(set(USED_OLD)):
            fh.write("%s | %s | %s | %s\n" % (o, d, fname, text))
    print("descriptions from the old docs: %d (listed in tools/used_old_descriptions.txt)" % len(set(USED_OLD)))
    print("nodes %d in %d groups, events %d, profile settings %d, component/asset/sense settings %d, enums %d, structs %d"
          % (sum(c.values()), len(c), e, p, s, t[0], t[1]))
