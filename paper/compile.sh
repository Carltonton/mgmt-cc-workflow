#!/bin/bash
# LaTeX compile script with automatic cleanup
# Usage: ./compile.sh [filename] (default: main)

FILE=${1:-main}
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== LaTeX Compilation (3-pass XeLaTeX + BibTeX) ==="

# Pass 1
echo "[1/3] XeLaTeX first pass..."
xelatex -interaction=nonstopmode "$FILE" 2>&1 | tail -3

# BibTeX
echo "[2/3] Running BibTeX..."
bibtex "$FILE" 2>&1 | tail -2

# Pass 2
echo "[3/3] XeLaTeX second pass..."
xelatex -interaction=nonstopmode "$FILE" 2>&1 | tail -2

# Pass 3
echo "[4/4] XeLaTeX third pass..."
xelatex -interaction=nonstopmode "$FILE" 2>&1 | tail -2

# Cleanup
echo ""
echo "=== Cleaning auxiliary files ==="
cd "$DIR" || exit
rm -f "${FILE}.aux" "${FILE}.bbl" "${FILE}.blg" "${FILE}.log" \
      "${FILE}.lof" "${FILE}.lot" "${FILE}.out" "${FILE}.synctex.gz" \
      "${FILE}.toc" "${FILE}.fls" "${FILE}.fdb_latexmk"

echo "✓ Cleanup complete"
echo "✓ Output: ${FILE}.pdf"
