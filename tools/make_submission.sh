#!/usr/bin/env bash
# Submission bundle: clean-room build + hash manifest + number-provenance table.
#
#   1. refuse to run on a dirty working tree (the bundle must correspond to a commit)
#   2. copy the paper sources into a fresh directory and compile there, so the PDF
#      cannot depend on stray files in the working tree
#   3. write SHA-256 manifests for the sources and the result files
#   4. write the provenance table: every LaTeX macro -> the JSON field it came from
#
# Usage: bash tools/make_submission.sh [outdir]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
OUT="${1:-submission}"
STAMP="$(git rev-parse --short HEAD)"

if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: working tree is dirty; commit first so the bundle matches a revision" >&2
  git status --short >&2
  exit 1
fi

rm -rf "$OUT"
mkdir -p "$OUT/paper"
cp -r paper/main.tex paper/numbers.tex paper/figures "$OUT/paper/"

echo "== clean-room build ($STAMP) =="
( cd "$OUT/paper" && pdflatex -interaction=nonstopmode main.tex >/dev/null 2>&1 \
  && pdflatex -interaction=nonstopmode main.tex >build.log 2>&1 )
grep -q "Output written" "$OUT/paper/build.log" || { echo "BUILD FAILED" >&2; tail -20 "$OUT/paper/build.log" >&2; exit 1; }
if grep -qi "undefined" "$OUT/paper/build.log"; then
  echo "ERROR: undefined references in the clean-room build" >&2; grep -i undefined "$OUT/paper/build.log" >&2; exit 1
fi
echo "  $(grep 'Output written' "$OUT/paper/build.log")"

echo "== hash manifest =="
{ echo "# revision $STAMP  ($(date -u +%Y-%m-%dT%H:%MZ))"
  echo "# paper sources"
  find "$OUT/paper" -name '*.tex' -o -name 'main.pdf' | sort | while read -r f; do
      echo "$(sha256sum "$f" | cut -c1-16)  ${f#$OUT/}"
  done
  echo "# result files the numbers come from"
  find results -name '*.json' | sort | while read -r f; do
      echo "$(sha256sum "$f" | cut -c1-16)  $f"
  done
} > "$OUT/MANIFEST.txt"
echo "  $(grep -c json "$OUT/MANIFEST.txt") result files hashed"

echo "== number provenance =="
python tools/number_provenance.py > "$OUT/NUMBER_PROVENANCE.txt"
echo "  $(wc -l < "$OUT/NUMBER_PROVENANCE.txt") lines"

echo
echo "bundle at $OUT/ : paper/main.pdf, MANIFEST.txt, NUMBER_PROVENANCE.txt"
