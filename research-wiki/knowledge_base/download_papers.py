"""Populate the paper layer of the research knowledge base.

Downloads real arXiv PDFs (open access, arxiv.org only) and extracts full text with PyMuPDF.

Outputs
-------
research-wiki/papers/<slug>.pdf                      downloaded PDFs
research-wiki/knowledge_base/papers/<slug>.json      {"slug","full_text","num_pages","title","arxiv_id"}
research-wiki/knowledge_base/papers/_download_log.json

Usage: python download_papers.py
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

import fitz  # PyMuPDF

try:  # Windows consoles default to GBK; paper titles contain ligatures etc.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

ROOT = Path(__file__).resolve().parents[2]          # repo root
PDF_DIR = ROOT / "research-wiki" / "papers"
JSON_DIR = ROOT / "research-wiki" / "knowledge_base" / "papers"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 research-wiki-builder/1.0"
)
SLEEP_BETWEEN = 3.0
MAX_RETRIES = 2

# (arxiv_id, slug) - selected from domain_overview.md / metrics_and_baselines.md reference lists
PAPERS: list[tuple[str, str]] = [
    # --- foundational NV magnetometry / quantum sensing reviews ---
    ("0805.1367", "taylor2008_diamond_magnetometer_theory"),
    ("1611.02427", "degen2017_quantum_sensing"),
    ("1903.08176", "barry2020_sensitivity_optimization_nv"),
    # --- sensitivity / photon-budget hardware benchmarks ---
    ("2511.19831", "cavity_nanophotonic_ramsey_2025"),
    ("2311.06055", "cw_vs_pulsed_nv_dc_magnetometry_2024"),
    ("2608.28519", "leclerc2026_error_budgets_quantum_sensors"),
    ("2510.00913", "triple_tone_microwave_nv_magnetometers_2025"),
    # --- Bayesian / CRLB estimation with few photons on NV ---
    ("1807.09753", "santagati2019_one_photon_bayesian_nv"),
    ("2105.02327", "mcmichael2021_sequential_bayesian_ramsey"),
    ("2102.07212", "wu2021_continuous_sensing_cpt"),
    # --- learned estimators / ML controllers for NV ---
    ("2603.14144", "shang2026_nvrnet_physics_informed_ramsey"),
    ("2608.19582", "daniel2026_sim_to_real_nv_odmr"),
    ("2601.17465", "youssry2026_graybox_bayesian_quantum_sensing"),
    ("2603.14728", "yao2026_cnn_odmr_parameter_inference"),
    ("2311.15037", "varona2024_signal_to_image_nuclear_spins"),
    ("2409.12820", "haim2025_ml_high_bandwidth_magnetic_sensing"),
    ("2506.13469", "guo2025_two_stage_single_electron_sensing"),
    ("2606.02749", "rieckmann2026_nn_vector_magnetometry"),
    ("2403.05706", "belliardo2024_model_aware_rl_metrology"),
    # --- amortized inference / ML-scoping evidence ---
    ("2512.11300", "amortized_bnn_nv_sensing_2025"),
    ("2608.27632", "nn_vs_mle_nonmarkovian_nv_2026"),
    ("2608.23934", "bhowmik2026_qml_measurement_information_loss"),
]


def download(arxiv_id: str, dest: Path) -> tuple[bool, str]:
    """Download https://arxiv.org/pdf/<id> with retries. Returns (ok, reason)."""
    url = f"https://arxiv.org/pdf/{arxiv_id}"
    last = ""
    for attempt in range(1, MAX_RETRIES + 2):  # 1 initial try + MAX_RETRIES retries
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = resp.read()
            if not data.startswith(b"%PDF"):
                last = f"non-PDF payload ({len(data)} bytes, starts {data[:12]!r})"
            elif len(data) < 5000:
                last = f"PDF too small ({len(data)} bytes)"
            else:
                dest.write_bytes(data)
                return True, f"{len(data)} bytes"
        except Exception as exc:  # noqa: BLE001
            last = f"{type(exc).__name__}: {str(exc)[:120]}"
        if attempt <= MAX_RETRIES:
            time.sleep(SLEEP_BETWEEN * (attempt + 1))
    return False, last


ARXIV_STAMP = re.compile(r"arXiv:\d{4}\.\d{4,5}(v\d+)?\s*\[", re.I)
JUNK_LINE = re.compile(r"^(\d+\s*)?(\[?(cond-mat|quant-ph|physics|astro-ph)[^\]]*\]?\s*\d|\d{1,2}\s+\w+\s+20\d\d)", re.I)


def extract_title(doc: "fitz.Document", fallback: str) -> str:
    """Best-effort title: PDF metadata, else largest-font text near the top of page 1."""
    meta = (doc.metadata or {}).get("title") or ""
    meta = " ".join(meta.split())
    if (len(meta) > 12 and not ARXIV_STAMP.search(meta)
            and not meta.lower().startswith(("untitled", "microsoft word", "latex", "powerpoint"))):
        return meta
    try:
        page = doc[0]
        height = page.rect.height
        lines: list[tuple[float, float, str]] = []  # (size, y0, text)
        for blk in page.get_text("dict")["blocks"]:
            for line in blk.get("lines", []):
                spans = line.get("spans", [])
                txt = " ".join(" ".join(s["text"].split()) for s in spans).strip()
                if not txt or ARXIV_STAMP.search(txt) or JUNK_LINE.match(txt):
                    continue
                size = max((s["size"] for s in spans), default=0.0)
                y0 = line.get("bbox", (0, 0, 0, 0))[1]
                lines.append((size, y0, txt))
        if not lines:
            return fallback
        top = [ln for ln in lines if ln[1] < 0.42 * height] or lines
        max_size = max(ln[0] for ln in top)
        title_lines = [ln for ln in top if ln[0] >= max_size - 0.6]
        title_lines.sort(key=lambda ln: ln[1])
        # stop at the first large line that follows a > 1.6x line-gap (authors/affiliations block)
        keep = [title_lines[0]]
        for prev, cur in zip(title_lines, title_lines[1:]):
            if cur[1] - prev[1] > 1.8 * max_size:
                break
            keep.append(cur)
        cand = " ".join(re.sub(r"^\d+\s+", "", ln[2]) for ln in keep)
        cand = " ".join(cand.split())
        if len(cand) > 8:
            return cand[:300]
    except Exception:  # noqa: BLE001
        pass
    return fallback


def main() -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    succeeded, failed = [], []

    for i, (arxiv_id, slug) in enumerate(PAPERS, 1):
        pdf_path = PDF_DIR / f"{slug}.pdf"
        json_path = JSON_DIR / f"{slug}.json"
        print(f"[{i}/{len(PAPERS)}] {arxiv_id} -> {slug}", flush=True)

        if pdf_path.exists() and pdf_path.stat().st_size > 5000:
            ok, reason = True, "cached"
        else:
            ok, reason = download(arxiv_id, pdf_path)
            time.sleep(SLEEP_BETWEEN)  # politeness delay between arxiv requests

        if not ok:
            print(f"    FAILED: {reason}", flush=True)
            failed.append({"arxiv_id": arxiv_id, "slug": slug, "reason": reason})
            continue

        try:
            doc = fitz.open(pdf_path)
            num_pages = doc.page_count
            full_text = "\n".join(page.get_text() for page in doc)
            title = extract_title(doc, slug)
            doc.close()
        except Exception as exc:  # noqa: BLE001
            print(f"    EXTRACT FAILED: {exc}", flush=True)
            failed.append({"arxiv_id": arxiv_id, "slug": slug, "reason": f"extract: {type(exc).__name__}: {str(exc)[:120]}"})
            continue

        record = {
            "slug": slug,
            "full_text": full_text,
            "num_pages": num_pages,
            "title": title,
            "arxiv_id": arxiv_id,
        }
        json_path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
        print(f"    ok: {num_pages} pages, {len(full_text)} chars | {title[:80]}", flush=True)
        succeeded.append({"slug": slug, "arxiv_id": arxiv_id, "pages": num_pages,
                          "chars": len(full_text), "title": title})

    log = {
        "source": "arxiv.org (open access)",
        "downloaded_at": time.strftime("%Y-%m-%d"),
        "requested": len(PAPERS),
        "succeeded": succeeded,
        "failed": failed,
    }
    (JSON_DIR / "_download_log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDONE: {len(succeeded)} succeeded, {len(failed)} failed", flush=True)


if __name__ == "__main__":
    main()
