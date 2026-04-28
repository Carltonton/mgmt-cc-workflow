#!/bin/bash
# LaTeX compile guard + compiler
# Dual-purpose: acts as PreToolUse guard (blocks direct xelatex)
#               and as compile script when called directly with arguments

# --- Mode detection ---
# Hook mode: JSON on stdin from Claude Code's hook system
# Compile mode: called with filename argument

if [ $# -gt 0 ]; then
  # ============================================================
  # COMPILE MODE: 3-pass XeLaTeX + BibTeX with cleanup
  # Usage: bash .claude/hooks/latex-compile-guard.sh [filename]
  # ============================================================
  FILE=${1:-main}
  DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

  # Find the paper directory (contains .tex files)
  TEX_DIR=$(find "$DIR" -name "*.tex" -maxdepth 3 -not -path "*/.*" | head -1 | xargs dirname 2>/dev/null)
  if [ -z "$TEX_DIR" ]; then
    echo "ERROR: No .tex files found" >&2
    exit 1
  fi

  cd "$TEX_DIR" || exit 1
  echo "=== LaTeX Compilation (3-pass XeLaTeX + BibTeX) ==="
  echo "Working dir: $(pwd)"
  echo "File: ${FILE}"

  echo "[1/4] XeLaTeX first pass..."
  xelatex -interaction=nonstopmode "$FILE" 2>&1 | tail -3

  echo "[2/4] Running BibTeX..."
  bibtex "$FILE" 2>&1 | tail -2

  echo "[3/4] XeLaTeX second pass..."
  xelatex -interaction=nonstopmode "$FILE" 2>&1 | tail -2

  echo "[4/4] XeLaTeX third pass..."
  xelatex -interaction=nonstopmode "$FILE" 2>&1 | tail -2

  echo ""
  echo "=== Cleaning auxiliary files ==="
  rm -f "${FILE}.aux" "${FILE}.bbl" "${FILE}.blg" "${FILE}.log" \
        "${FILE}.lof" "${FILE}.lot" "${FILE}.out" "${FILE}.synctex.gz" \
        "${FILE}.toc" "${FILE}.fls" "${FILE}.fdb_latexmk"
  echo "✓ Cleanup complete"
  echo "✓ Output: ${FILE}.pdf"
  exit 0
fi

# ============================================================
# GUARD MODE: PreToolUse hook — block direct LaTeX commands
# ============================================================
INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name')

if [ "$TOOL" != "Bash" ]; then
  exit 0
fi

COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$COMMAND" ]; then
  exit 0
fi

# Allow if using a shell script (compile.sh, this script, etc.)
if echo "$COMMAND" | grep -qE '\.sh\b'; then
  exit 0
fi

# Block direct LaTeX compilation commands
if echo "$COMMAND" | grep -qE '\b(xelatex|pdflatex|latexmk|lualatex)\b'; then
  echo "BLOCKED: Direct LaTeX compilation detected. Use the compile script instead:" >&2
  echo "  bash .claude/hooks/latex-compile-guard.sh [filename]" >&2
  echo "" >&2
  echo "This ensures proper 3-pass XeLaTeX + BibTeX compilation and cleanup." >&2
  exit 2
fi

exit 0
