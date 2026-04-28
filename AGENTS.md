# Project Context for Codex

**Project:** [YOUR PROJECT NAME]
**Researcher:** [YOUR NAME] ([YOUR INSTITUTION])

## Safety Guardrails (NEVER violate)

1. NEVER modify files in `.claude/` — this is infrastructure, not content
2. NEVER modify research data files (CSV, Excel, Parquet in `data/` or `survey/`)
3. NEVER modify academic arguments, theoretical claims, or research conclusions
4. NEVER create or delete files unless explicitly instructed
5. Report exactly what you changed and what you did NOT change

## Directory Access

| Directory | Access | Notes |
|-----------|--------|-------|
| `scripts/` | Read-Write | Python source code |
| `paper/` | Read-Write | LaTeX paper drafts (formatting only, not arguments) |
| `Slides/` | Read-Write | Beamer lecture slides (formatting only) |
| `Quarto/` | Read-Write | Quarto slide sources (formatting only) |
| `output/` | Read-Write | Generated figures and tables |
| `docs/` | Read-Write | Rendered documentation |
| `quality_reports/` | Read-Write | Session logs, plans, reviews |
| `references/` | Read-Write | Reference materials |
| `assets/` | Read-Write | Static assets |
| `data/` | **READ ONLY** | Research data |
| `survey/` | **READ ONLY** | Survey instruments and responses |
| `.claude/` | **READ ONLY** | Infrastructure |
| `.codex/` | **READ ONLY** | Codex configuration |

## Code Standards

### Python
- Seeds set ONCE at top in YYYYMMDD format
- Type hints on all functions
- `pathlib.Path` for all paths (relative to project root)
- Figures: 300 DPI, transparent background
- Save heavy computations to disk (Parquet/Pickle)
- snake_case filenames
- PEP 8 style, lines under 100 characters

### File Naming
- Python: snake_case | Documentation: kebab-case | Dates: YYYY-MM-DD

### LaTeX & Bibliography
- XeLaTeX only (never pdflatex)
- BibTeX key format: `AuthorYear` or `AuthorYearWord`
- UTF-8 encoding for all text files

## Environment

```bash
source .venv/bin/activate
python3 script.py
```

## General Rules

- Use relative paths from project root
- Preserve existing file structure — do not reorganize
- Do not add dependencies or install packages
- If uncertain about a change, skip it and report
