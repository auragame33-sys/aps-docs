"""Lists editable settings that no plugin code ever reads: candidates for "does nothing in this version".

A setting counts as read when its name appears in a .cpp or .h file anywhere other than its own declaration or a plain
assignment to it (constructor defaults and archetype presets write it; they don't read it). Every candidate is then
checked by hand before the docs say so (tools/inert.json).

    python -I find_inert.py <plugin Source folder>
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1]
M = json.load(open(os.path.join(HERE, "model.json"), encoding="utf-8"))
texts = {}
for root, _, files in os.walk(src):
    for f in files:
        if f.endswith((".cpp", ".h")):
            p = os.path.join(root, f)
            texts[os.path.relpath(p, src)] = open(p, encoding="utf-8", errors="replace").read()

owners = ("UPerceptionProfile", "USoundTypeDefinition", "USoundFilterProfile", "UPainTypeDefinition", "UAPSQualityProfile",
          "UPerceptionCore", "UAPSTargetComponent", "URelationshipComponent", "UAPSEnvironmentComponent", "UAPSSubsystem",
          "UAPSSignatureComponent", "UAPSObserverComponent", "UAPSEvidenceComponent", "UAPSSearchComponent",
          "UAPSKnowledgeSubsystem", "USenseUnit", "USenseUnit_Smell", "USenseUnit_Touch", "UAPSPerceptionListener")
for p in M["properties"]:
    if p["owner"] not in owners or not p["editable"]:
        continue
    name = p["name"]
    reads = 0
    for rel, t in texts.items():
        for m in re.finditer(r"\b%s\b" % re.escape(name), t):
            line_start = t.rfind("\n", 0, m.start()) + 1
            line_end = t.find("\n", m.end())
            line = t[line_start:line_end]
            after = t[m.end():m.end() + 6]
            if re.match(r"\s*=[^=]", after):                 # an assignment: a write
                continue
            if "UPROPERTY" in t[max(0, line_start - 300):line_start] and rel.endswith(".h") and re.search(r"\b%s\s*(=|;|\{)" % re.escape(name), line):
                continue                                     # the declaration
            if line.strip().startswith(("//", "*", "/*")):
                continue
            if "GET_MEMBER_NAME" in line:
                continue
            reads += 1
    if reads == 0:
        print("%-24s %-36s %s" % (p["owner"], p["display"], p["file"]))
