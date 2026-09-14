"""Emit the number-provenance table for the submission bundle.

Every LaTeX macro in paper/numbers.tex is matched, by value, against every numeric leaf of
every file in results/. Macros with no match are listed separately; they should be protocol
constants, text macros, or values quoted directly in the manuscript text.

Usage: python tools/number_provenance.py  > submission/NUMBER_PROVENANCE.txt
"""
from __future__ import annotations

import json
import os
import re

BS = chr(92)
MACRO_RE = re.compile(re.escape(BS) + r"newcommand\{" + re.escape(BS) + r"([a-zA-Z]+)\}"
                      + re.escape(BS) + r"\{([^}]*)\}")


def load_macros(path="paper/numbers.tex"):
    return dict(MACRO_RE.findall(open(path, encoding="utf-8").read()))


def numeric_leaves(root="results"):
    leaves = []

    def walk(node, path, fname):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}" if path else k, fname)
        elif isinstance(node, list):
            for i, v in enumerate(node[:400]):
                walk(v, f"{path}[{i}]", fname)
        elif isinstance(node, (int, float)) and not isinstance(node, bool):
            leaves.append((float(node), f"{fname}:{path}"))

    for name in sorted(os.listdir(root)):
        if name.endswith(".json"):
            walk(json.load(open(os.path.join(root, name), encoding="utf-8")), "", name)
    return leaves


def as_float(v):
    """Parse a LaTeX macro body into a float when it encodes one."""
    t = (v.replace(BS + "ensuremath{", "").replace(BS + "times10^{", "e")
          .replace(BS + "%", "").replace("}", "").replace("{", "").replace("+", "", 1)
         if v.startswith("+") else v.replace(BS + "ensuremath{", "")
          .replace(BS + "times10^{", "e").replace("}", "").replace("{", ""))
    try:
        return float(t)
    except ValueError:
        return None


def main():
    macros = load_macros()
    leaves = numeric_leaves()
    print("# Number provenance: every LaTeX macro in paper/numbers.tex matched by value")
    print("# against every numeric leaf of every results/*.json (relative tolerance 0.5%,")
    print("# which covers the rounding applied when the macros are emitted).")
    print("# Macros with no match are listed at the end; they must be protocol constants,")
    print("# text macros, or numbers quoted directly in the manuscript.\n")
    orphans = []
    for k, v in sorted(macros.items()):
        x = as_float(v)
        if x is None:
            orphans.append((k, v, "text/non-numeric"))
            continue
        tol = 5e-3 * max(abs(x), 1e-12)
        hits = [p for y, p in leaves if abs(y - x) <= tol]
        if hits:
            print(f"{k:28s} {v:>12s}   {sorted(hits)[0]}")
        else:
            orphans.append((k, v, "no result-file value within 0.5%"))
    print(f"\n# {len(orphans)} macros with no numeric match:")
    for k, v, why in orphans:
        print(f"#   {k:28s} {v:>12s}   {why}")


if __name__ == "__main__":
    main()
