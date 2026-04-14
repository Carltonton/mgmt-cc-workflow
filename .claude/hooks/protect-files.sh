#!/bin/bash
# Block accidental edits to protected files
# Customize PROTECTED_PATTERNS below for your project
INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name')
FILE=""

# Extract file path based on tool type
if [ "$TOOL" = "Edit" ] || [ "$TOOL" = "Write" ]; then
  FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
fi

# No file path = not a file operation, allow
if [ -z "$FILE" ]; then
  exit 0
fi

# ============================================================
# CUSTOMIZE: Add patterns for files you want to protect
# Uses basename matching — add full paths for more precision
# ============================================================
PROTECTED_PATTERNS=(
  "Bibliography_base.bib"
  "settings.json"
  "data/raw"
)

BASENAME=$(basename "$FILE")
for PATTERN in "${PROTECTED_PATTERNS[@]}"; do
  # Check basename match
  if [[ "$BASENAME" == "$PATTERN" ]]; then
    echo "Protected file: $BASENAME. Edit manually or remove protection in .claude/hooks/protect-files.sh" >&2
    exit 2
  fi
  # Check path/directory match (for patterns containing /)
  if [[ "$PATTERN" == */* ]] && [[ "$FILE" == */"$PATTERN"/* ]] || [[ "$FILE" == "$PATTERN"/* ]]; then
    echo "Protected path: $PATTERN. Edit manually or remove protection in .claude/hooks/protect-files.sh" >&2
    exit 2
  fi
done

exit 0
