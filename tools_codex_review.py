"""Submit the manuscript to the DashScope (qwen3.8-max) responses API for a strict
referee report. Bypasses the MCP wrapper, which was cancelling on long requests.

Builds a self-contained prompt: the manuscript with all LaTeX macros expanded to literal
numbers, plus the result tables the numbers come from.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))


def expand_macros(tex: str, numbers: str) -> str:
    macros = dict(re.findall(r"\\newcommand\{\\([a-zA-Z]+)\}\{([^}]*)\}", numbers))
    def rep(m):
        name = m.group(1)
        return macros.get(name, m.group(0))
    # repeat: values may reference other macros
    for _ in range(3):
        tex = re.sub(r"\\([a-zA-Z]+)", rep, tex)
    return tex


def main():
    tex = open(os.path.join(ROOT, "paper", "main.tex"), encoding="utf-8").read()
    nums = open(os.path.join(ROOT, "paper", "numbers.tex"), encoding="utf-8").read()
    tex = tex.replace("\\input{numbers}", "% numbers expanded inline")
    flat = expand_macros(tex, nums)

    a = json.load(open(os.path.join(ROOT, "results", "analysis_v2.json")))
    T = a["tables"]["cols7_40"]
    rows = []
    rows.append("r | lm_refine RMSE | joint_refine RMSE | partial_pool RMSE | "
                "lm eff | pool eff | pool bias")
    for k in sorted(T, key=lambda x: int(x[1:])):
        row = T[k]
        g = lambda m, f: row.get(m, {}).get(f, float("nan"))
        rows.append(f"{k[1:]} | {g('lm_refine','rmse'):.0f} | {g('joint_refine','rmse'):.0f} | "
                    f"{g('partial_pool','rmse'):.0f} | {g('lm_refine','efficiency'):.2f} | "
                    f"{g('joint_refine','efficiency'):.2f} | {g('joint_refine','bias'):+.0f}")
    ladder = "\n".join(rows)
    w = json.dumps(a.get("wilcoxon_cols7_40", {}), indent=1)[:2000]
    fl = json.dumps(a.get("floor_law", {}).get("cols7_40", {}), indent=1)[:1200]

    prompt = f"""You are a strict senior referee for a physics journal (Physical Review Applied /
Metrologia class). Below is a complete manuscript, followed by the raw result tables its
numbers come from. Review it adversarially and in detail.

=== MANUSCRIPT (LaTeX, macros already expanded to literal numbers) ===
{flat}

=== RESULT TABLE: RMSE per estimator per repetition level, real columns 7-40 ===
{ladder}

=== FLOOR LAW FIT (deltaB(r) = sqrt(A^2*(5000/r) + b^2)) ===
{fl}

=== PAIRED WILCOXON TESTS (cols 7-40, paired over columns) ===
{w}

ADDRESS EACH POINT WITH SPECIFIC NUMBERS:
1. TECHNICAL SOUNDNESS: Are the Cramer-Rao bound comparisons (free-envelope per trace vs
joint shared-envelope) correct and appropriate? Is comparing each estimator with its own
bound the right test? Is an RMSE-over-columns statistic valid given that all 40 columns come
from ONE session on ONE instrument (pseudo-replication)? Are the bootstrap CIs and
column-wise Wilcoxon tests defensible at this replication structure?
2. CENTRAL CLAIM: Could the crossover at r* ~ 9e4 be an artefact of (a) the ~50 nT
nominal-field systematic, (b) excluding columns 1-6, (c) estimating the envelope population
from the same 40 columns used for testing, (d) the synthetic control's construction?
Name the single most decisive additional analysis that would confirm or falsify it.
3. NEURAL COMPONENT: the network is worse than classical pooling at 5k-40k and best at
80k-320k. Meaningful budget-dependent behaviour, or undertrained-model artefact? What
evidence would distinguish these?
4. FIDELITY: check whether the numbers quoted in the text match the tables given above;
report mismatches.
5. OVERSTATEMENT AND GAPS: list every sentence that overstates the evidence, plus important
missing content (error budget, limitations, related work).
6. FIGURES: the manuscript has five figures (ladder+crossover law, estimator bias,
synthetic control, envelope histograms, sensitivity). Comment on whether they are the right
figures, whether any is misleading, and what would improve them.
7. RECOMMENDATION: Accept / Minor revision / Major revision / Reject, with a prioritised
list of required work, and whether this belongs in a physics journal or a metrology or
signal-processing venue.

Be adversarial and precise. Cite specific numbers for every criticism. If a claim is
correct, say so in one line; spend your effort on what is wrong or unproven."""

    key = os.environ.get("DASHSCOPE_API_KEY")
    if not key:
        print("DASHSCOPE_API_KEY not set"); sys.exit(1)
    body = json.dumps({"model": "qwen3.8-max", "input": prompt}).encode()
    req = urllib.request.Request(
        "https://dashscope.aliyuncs.com/compatible-mode/v1/responses",
        data=body, headers={"Authorization": f"Bearer {key}",
                            "Content-Type": "application/json"})
    print(f"submitting review ({len(prompt)} chars)...", flush=True)
    with urllib.request.urlopen(req, timeout=900) as r:
        out = json.load(r)
    text = []
    for item in out.get("output", []):
        if item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("type") == "output_text":
                    text.append(c["text"])
    review = "\n".join(text)
    os.makedirs(os.path.join(ROOT, "review-stage"), exist_ok=True)
    with open(os.path.join(ROOT, "review-stage", "CODEX_REVIEW.md"), "w",
              encoding="utf-8") as f:
        f.write("# Strict referee report (qwen3.8-max via DashScope responses API)\n\n")
        f.write(review)
    print("wrote review-stage/CODEX_REVIEW.md,", len(review), "chars")
    print(review[:3000])


if __name__ == "__main__":
    main()
