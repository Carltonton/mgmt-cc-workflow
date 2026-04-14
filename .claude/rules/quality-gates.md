---
paths:
  - "Slides/**/*.tex"
  - "Quarto/**/*.qmd"
  - "scripts/**/*.R"
  - "scripts/**/*.py"
  - "scripts/python/**/*.py"
  - "paper/**/*.tex"
---

# Quality Gates & Scoring Rubrics

## Thresholds

- **80/100 = Commit** -- good enough to save
- **90/100 = PR** -- ready for deployment
- **95/100 = Excellence** -- aspirational

## Quarto Slides (.qmd)

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | Compilation failure | -100 |
| Critical | Equation overflow | -20 |
| Critical | Broken citation | -15 |
| Critical | Typo in equation | -10 |
| Major | Text overflow | -5 |
| Major | TikZ label overlap | -5 |
| Major | Notation inconsistency | -3 |
| Minor | Font size reduction | -1 per slide |
| Minor | Long lines (>100 chars) | -1 (EXCEPT documented math formulas) |

## R Scripts (.R)

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | Syntax errors | -100 |
| Critical | Domain-specific bugs | -30 |
| Critical | Hardcoded absolute paths | -20 |
| Major | Missing set.seed() | -10 |
| Major | Missing figure generation | -5 |

## Python Scripts (.py)

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | Syntax errors / import failures | -100 |
| Critical | Domain-specific bugs (wrong formula, logic) | -30 |
| Critical | Hardcoded absolute paths | -20 |
| Major | Missing seeds (np.random.seed, etc.) | -10 |
| Major | Missing type hints on functions | -5 |
| Major | Missing docstrings on functions | -3 |
| Minor | PEP 8 style violations | -2 per violation |
| Minor | Long lines (>100 chars) | -1 per line (EXCEPT documented math) |
| Minor | Figures without transparent background | -3 |
| Minor | Low DPI figures (<300) | -2 |

## LaTeX Research Papers (paper/*.tex)

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | XeLaTeX compilation failure | -100 |
| Critical | Undefined citation | -15 |
| Critical | Overfull hbox > 10pt | -10 |
| Major | Missing references in bibliography | -5 |
| Major | Figure resolution issues | -3 |
| Minor | Formatting inconsistencies | -1 per instance |

## Beamer Slides (.tex)

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | XeLaTeX compilation failure | -100 |
| Critical | Undefined citation | -15 |
| Critical | Overfull hbox > 10pt | -10 |

## Enforcement

- **Score < 80:** Block commit. List blocking issues.
- **Score < 90:** Allow commit, warn. List recommendations.
- User can override with justification.

## Quality Reports

Generated **only at merge time**. Use `templates/quality-report.md` for format.
Save to `quality_reports/merges/YYYY-MM-DD_[branch-name].md`.

## Tolerance Thresholds (Research)

<!-- Customize for your domain -->

| Quantity | Tolerance | Rationale |
|----------|-----------|-----------|
| Model fit indices (CFI, RMSEA) | 1e-3 | Numerical precision |
| Reliability coefficients (alpha, CR) | 1e-2 | Bootstrap variability |
| Regression coefficients | 1e-3 | Standard error scale |
| Factor loadings | 1e-3 | Optimization convergence |
