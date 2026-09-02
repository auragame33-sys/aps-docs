#!/usr/bin/env python3
"""Check the docs against the APS plugin source.

The site claims every default value and node name was read out of the source
rather than inferred from property names. This is what makes that claim checkable
instead of a promise.

    python tools/check_against_source.py --source "C:/path/to/Advanced Perception System/Source"

Three checks:

  defaults  Every value in a table that declares a "Default" column is compared
            against the initialiser in the header. Recipe tables in tutorials and
            field-description tables are skipped, because a recommended value is
            not a claim about a default.

  nodes     Every node named in a table that declares a "Node" column must exist
            as a UFUNCTION. The docs write nodes in Unreal's display form -
            "Get Attention Target" - which is the C++ name with spaces inserted,
            so comparing with spaces removed is exact rather than fuzzy.

  members   Every property named in a settings table must exist at all, even if
            it has no inline initialiser to compare.

This cannot run in CI: the plugin source lives in a separate repository. Run it
locally before opening a sync PR.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"

# Members carrying an inline initialiser. Underscores are stripped from the name
# because Unreal removes them for the Details panel, which is what the docs quote.
INITIALISED = re.compile(
    r"(?:TObjectPtr<[^>]+>|TArray<[^>]+>|TMap<[^>]+>|TSubclassOf<[^>]+>|TSet<[^>]+>"
    r"|int32|int64|uint8|uint32|float|double|bool|FName|FString|FVector"
    r"|FRotator|FGameplayTag|FGameplayTagContainer|E[A-Za-z]+)\s+"
    r"(?P<name>[A-Za-z_]\w*)\s*=\s*(?P<value>[^;{]+);"
)
# Any declared member, initialised or not.
#
# Two things this has to get right. The type part must allow nested angle
# brackets, or TArray<TEnumAsByte<ECollisionChannel>> is missed. And the
# whitespace must be horizontal only: allowing \s lets a single match run across
# many lines to reach a semicolon, and finditer then resumes past every
# declaration it swallowed on the way, silently reporting them as absent.
DECLARED = re.compile(
    r"^[^\S\n]*"
    r"(?:[\w:]+(?:<[^;\n]*>)?[*&]*[^\S\n]+[*&]*)+"
    r"(?P<name>[A-Za-z_]\w*)"
    r"[^\S\n]*(?:\[[^\]\n]*\])?"
    r"[^\S\n]*(?:=[^;\n]*)?;",
    re.MULTILINE,
)


def read_headers(source: Path) -> list[str]:
    return [p.read_text(encoding="utf-8", errors="replace") for p in source.rglob("*.h")]


def source_defaults(headers: list[str]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = defaultdict(set)
    for text in headers:
        for m in INITIALISED.finditer(text):
            out[m.group("name").replace("_", "")].add(m.group("value").strip())
    return out


def source_members(headers: list[str]) -> set[str]:
    names: set[str] = set()
    for text in headers:
        for m in DECLARED.finditer(text):
            names.add(m.group("name").replace("_", ""))
    return names


def source_callables(headers: list[str]) -> set[str]:
    names: set[str] = set()
    for text in headers:
        for m in re.finditer(r"UFUNCTION\([^)]*\)\s*(.{0,400}?)[;{]", text, re.DOTALL):
            fn = re.search(r"\b([A-Za-z_]\w*)\s*\(", m.group(1))
            if fn:
                names.add(fn.group(1))
        for m in re.finditer(
            r"UPROPERTY\([^)]*BlueprintAssignable[^)]*\)\s*[\w<>:]+\s+(\w+)", text
        ):
            names.add(m.group(1))
    return {n.replace("_", "").lower() for n in names}


def table_rows(column: str) -> list[tuple[str, str, str]]:
    """(page, first cell, named column) for tables declaring that column."""
    rows: list[tuple[str, str, str]] = []
    for page in sorted(DOCS.glob("*.md")):
        index = None
        for line in page.read_text(encoding="utf-8").splitlines():
            if not line.startswith("|"):
                index = None
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            lowered = [c.lower() for c in cells]
            if column in lowered:
                index = lowered.index(column)
                continue
            if set("".join(cells)) <= set("-: ") or index is None or len(cells) <= index:
                continue
            rows.append((page.name, cells[0], cells[index]))
    return rows


NUM = re.compile(r"-?\d+(?:\.\d+)?")


def numeric(text: str):
    m = NUM.search(text.replace(",", ""))
    return float(m.group()) if m else None


def compare(doc_val: str, src_vals: set[str]):
    """True match, False mismatch, None not comparable."""
    d = doc_val.strip().lower().strip("`")

    bools = {v.lower() for v in src_vals} & {"true", "false"}
    if bools:
        if d in {"true", "on", "yes"} or d == "\u2705":
            return "true" in bools
        if d in {"false", "off", "no"} or d == "\u274c":
            return "false" in bools
        return None

    if not d or "empty" in d or d in ("none", "zero", "-", "\u2014"):
        return None

    dn = numeric(doc_val)
    if dn is None:
        return None
    src_numbers = [numeric(v) for v in src_vals]
    if not any(n is not None for n in src_numbers):
        return None
    return any(n is not None and abs(dn - n) < 1e-4 for n in src_numbers)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True, type=Path,
                    help="path to the plugin's Source directory")
    args = ap.parse_args()

    if not args.source.is_dir():
        sys.exit(f"not a directory: {args.source}")

    headers = read_headers(args.source)
    defaults = source_defaults(headers)
    members = source_members(headers)
    callables = source_callables(headers)

    print(f"source: {len(headers)} headers, {len(defaults)} initialised members, "
          f"{len(callables)} Blueprint-callable names\n")

    failures = 0

    # ── defaults ─────────────────────────────────────────────────────────────
    compared = 0
    mismatches: list[str] = []
    absent: list[str] = []
    ambiguous: list[str] = []

    for page, first, value in table_rows("default"):
        prop = re.match(r"^(?:\u26a0\s*)?`([^`]+)`$", first)
        if not prop:
            continue
        key = prop.group(1).strip().replace(" ", "").replace("\\", "")

        if key not in members:
            absent.append(f"{page}: `{prop.group(1)}`")
            continue
        if key not in defaults:
            continue  # exists, but has no inline initialiser to compare

        verdict = compare(value, defaults[key])
        if verdict is None:
            continue
        compared += 1
        if verdict:
            if len(defaults[key]) > 1:
                ambiguous.append(f"{page}: `{prop.group(1)}` -> {sorted(defaults[key])}")
        else:
            mismatches.append(
                f"{page}: `{prop.group(1)}` documented '{value}', "
                f"source {sorted(defaults[key])}"
            )

    print(f"defaults: {compared} compared")
    for m in mismatches:
        print(f"  MISMATCH  {m}")
    failures += len(mismatches)

    if absent:
        print(f"\nsettings named in docs with no such member: {len(absent)}")
        for a in absent:
            print(f"  MISSING  {a}")
        failures += len(absent)

    # ── nodes ────────────────────────────────────────────────────────────────
    # Several API tables head their first column something other than "Node" —
    # "Button / setting" on the workbench table, for one. Missing those means a
    # misspelt node name in them goes unchecked, so accept the variants too.
    unknown: list[str] = []
    seen: set[tuple[str, str]] = set()
    node_count = 0
    for header in ("node", "function", "event", "button / setting"):
        for page, first, _ in table_rows(header):
            m = re.match(r"^\*\*([A-Za-z][A-Za-z0-9 ]+?)\*\*", first)
            if not m or (page, m.group(1)) in seen:
                continue
            seen.add((page, m.group(1)))
            node_count += 1
            if m.group(1).replace(" ", "").lower() not in callables:
                unknown.append(f"{page}: **{m.group(1)}**")

    print(f"\nnodes: {node_count} checked")
    for u in unknown:
        print(f"  NO SUCH UFUNCTION  {u}")
    failures += len(unknown)

    # Reported, not failed: a shared name is not automatically wrong.
    if ambiguous:
        print(f"\nnames that exist on more than one class ({len(ambiguous)}) — "
              f"matched one of them, worth an eye:")
        for a in ambiguous:
            print(f"  {a}")

    print()
    if failures:
        print(f"FAILED: {failures} problem(s)")
        return 1
    print("PASSED: docs agree with the source")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
