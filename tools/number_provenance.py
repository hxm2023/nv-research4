"""Emit the number-provenance table for the submission bundle.

Every LaTeX macro in paper/numbers.tex is classified into one of three buckets:

  MATCHED   the macro's value equals a numeric leaf of some results/*.json, within the
            rounding implied by how the macro is printed (so a value displayed as -10
            matches a stored -9.7);
  DERIVED   the macro is computed by src/make_numbers.py from other result values
            (sensitivities eta, ratios, crossovers, p-values, fit residuals);
  UNMATCHED everything else --- these must be protocol constants or text macros, and
            anything else is a number with no provenance.

Usage: python tools/number_provenance.py  > submission/NUMBER_PROVENANCE.txt
"""
from __future__ import annotations

import json
import os
import re

BS = chr(92)
MACRO_RE = re.compile(r"\\newcommand\{\\([a-zA-Z]+)\}\{([^}]*)\}")

DERIVED_PREFIXES = ("eta", "ratio", "crlb", "pJoint", "pPart", "pNet", "crossoverReps",
                    "photonGainFactor", "lawFit", "crossoverCI", "crossoverMedian",
                    "rmseGB", "biasGB", "rmseAbl", "attrib", "addback", "floor", "env",
                    "sys")
CONSTANTS = {"nTau", "nCols", "nSheets", "rMinK", "rMaxK", "tauOffNs", "tauOffSigmaNs",
             "tauStep", "bStep", "nBins", "WResid", "netSteps", "nSeedsNetSet",
             "nSeedsAblation"}


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


def parse(v):
    """(value, display ulp) for a macro body that encodes a number, else (None, None)."""
    t = (v.replace(BS + "ensuremath{", "").replace(BS + "times10^{", "e")
          .replace("}", "").replace("{", "").replace(BS + "%", "").strip().lstrip("+"))
    try:
        x = float(t)
    except ValueError:
        return None, None
    if "e" in t:
        mant, _, exp = t.partition("e")
        dec = len(mant.split(".")[1]) if "." in mant else 0
        return x, 10.0 ** (int(exp) - dec)
    dec = len(t.split(".")[1]) if "." in t else 0
    return x, 10.0 ** (-dec)


def main():
    macros = load_macros()
    leaves = numeric_leaves()
    print("# Number provenance for paper/numbers.tex")
    print("#   MATCHED   value equals a numeric leaf of results/*.json, within the rounding")
    print("#             implied by how the macro is printed (a displayed -10 matches -9.7)")
    print("#   DERIVED   computed by src/make_numbers.py from other result values")
    print("#   UNMATCHED must be a protocol constant or a text macro; anything else has no")
    print("#             provenance and needs attention\n")
    unmatched, derived, matched = [], [], 0
    for k, v in sorted(macros.items()):
        x, ulp = parse(v)
        if x is None:
            unmatched.append((k, v, "text / non-numeric"))
            continue
        tol = max(5e-3 * abs(x), 0.5 * ulp)
        hits = [p for y, p in leaves if abs(y - x) <= tol]
        if hits:
            matched += 1
            print(f"MATCHED   {k:30s} {v:>14s}   {sorted(hits)[0]}")
        elif k.startswith(DERIVED_PREFIXES):
            derived.append((k, v))
        else:
            unmatched.append((k, v, "no leaf within the display rounding"))
    print(f"\n# MATCHED: {matched}   DERIVED: {len(derived)}   UNMATCHED: {len(unmatched)}")
    print("\n# DERIVED macros (recomputed by src/make_numbers.py from the result files):")
    for k, v in derived:
        print(f"#   {k:30s} {v}")
    print("\n# UNMATCHED macros:")
    for k, v, why in unmatched:
        tag = "protocol constant" if k in CONSTANTS else why
        print(f"#   {k:30s} {v:>14s}   {tag}")


if __name__ == "__main__":
    main()
