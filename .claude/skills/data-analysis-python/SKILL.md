---
name: data-analysis-python
description: End-to-end Python data analysis workflow from exploration through regression to publication-ready tables and figures
argument-hint: "[dataset path or description of analysis goal]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task"]
---

# Data Analysis Workflow (Python)

Run an end-to-end data analysis in Python: load, explore, analyze, and produce publication-ready output.

**Input:** `$ARGUMENTS` — a dataset path (e.g., `data/county_panel.csv`) or a description of the analysis goal (e.g., "regress wages on education with state fixed effects using CPS data").

---

## Constraints

- **Follow Python code conventions** in `.claude/rules/python-code-conventions.md`
- **Save all scripts** to `scripts/python/` with descriptive names
- **Save all outputs** (figures, tables, models) to `output/`
- **Use `to_parquet()`/`pickle.dump()`** for every computed object — notebooks may need them
- **Use project theme** for all figures (check for custom theme in `python-code-conventions.md`)
- **Run python-reviewer** on the generated script before presenting results

---

## Workflow Phases

### Phase 1: Setup and Data Loading

1. Read `.claude/rules/python-code-conventions.md` for project standards
2. Create Python script with proper header (title, author, purpose, inputs, outputs)
3. Import required packages at top (stdlib first, then third-party, then local)
4. Set seed once at top using YYYYMMDD format
5. Load and inspect the dataset

### Phase 2: Exploratory Data Analysis

Generate diagnostic outputs:
- **Summary statistics:** `describe()`, missingness rates, variable types
- **Distributions:** Histograms for key continuous variables
- **Relationships:** Scatter plots, correlation matrices
- **Time patterns:** If panel data, plot trends over time
- **Group comparisons:** If treatment/control, compare pre-treatment means

Save all diagnostic figures to `output/diagnostics/`.

### Phase 3: Main Analysis

Based on the research question:
- **Regression analysis:** Use `statsmodels` for OLS, `linearmodels` for panel data
- **Standard errors:** Cluster at the appropriate level (document why)
- **Multiple specifications:** Start simple, progressively add controls
- **Effect sizes:** Report standardized effects alongside raw coefficients

#### Common Model Types

| Model | Package | Call Pattern |
|-------|---------|-------------|
| OLS (robust SE) | `statsmodels.api` | `sm.OLS(y, sm.add_constant(X)).fit(cov_type='HC3')` |
| OLS (clustered SE) | `statsmodels.api` | `sm.OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': g})` |
| OLS (entity FE) | `statsmodels.api` | manual dummies + `sm.OLS(y, pd.concat([X, dummies])).fit(cov_type='cluster', ...)` |
| Logit | `statsmodels.api` | `sm.Logit(y, sm.add_constant(X)).fit()` |
| Probit | `statsmodels.api` | `sm.Probit(y, sm.add_constant(X)).fit()` |
| Ordered Logit | `statsmodels.miscmodels` | `OrderedModel(y, X).fit()` |
| DID | `statsmodels.api` | `sm.OLS(y, X[treat, post, treat×post]).fit(cov_type='HC3')` |
| RDD | `statsmodels.api` | `sm.OLS(y, X[running, treat, running×treat]).fit(cov_type='HC3')` |
| IV / 2SLS | `linearmodels.iv` | `IV2SLS(y, X_exog, Z_endog, Z_instr).fit(cov_type='robust')` |
| Panel FE | `linearmodels.panel` | `PanelOLS.from_formula("y ~ x + EntityEffects", data).fit(cov_type='clustered')` |

### Phase 4: Publication-Ready Output

**Tables:**
- Use `statsmodels.iolib.summary2` or custom LaTeX table export
- Include all standard elements: coefficients, SEs, significance stars, N, R-squared
- Export as `.tex` for LaTeX inclusion and `.csv` for quick viewing

**Figures:**
- Use `seaborn`/`matplotlib` with project theme
- Set `transparent=True` for LaTeX compatibility
- Include proper axis labels (sentence case, units)
- Export with explicit dimensions: `dpi=300`, `bbox_inches="tight"`
- Save as both `.pdf` and `.png`

**LaTeX Tables (Management Journal Style):**

Follow AMJ / SMJ / AMR conventions using the `booktabs` package.

**Layout:**
```latex
\begin{table}[htbp]
\centering
\caption{Descriptive Title}
\label{tab:label}
\begin{tabular}{l ccc}
\toprule
                 & (1)      & (2)      & (3)      \\
\midrule
Key variable     & 0.857*** & 0.642**  & 0.531*   \\
                 & (0.123)  & (0.201)  & (0.245)  \\
Control 1        &          & 0.334    & 0.298    \\
                 &          & (0.189)  & (0.192)  \\
Control 2        &          & -0.156   & -0.142   \\
                 &          & (0.134)  & (0.137)  \\
\midrule
Observations     & 256      & 256      & 256      \\
R²               & 0.18     & 0.23     & 0.24     \\
Adjusted R²      & 0.18     & 0.22     & 0.22     \\
\bottomrule
\multicolumn{4}{l}{\footnotesize Robust standard errors in (parentheses).}\\
\multicolumn{4}{l}{\footnotesize $\dagger p<0.10$, $*p<0.05$, $**p<0.01$, $***p<0.001$}\\
\end{tabular}
\end{table}
```

**Rules:**

| Element         | Convention                                                                                             |
| --------------- | ------------------------------------------------------------------------------------------------------ |
| Lines           | Only `\toprule`, `\midrule` (between sections), `\bottomrule` — never `\hline`                |
| Coefficients    | 3 decimal places + significance stars attached (e.g.,`0.857***`)                                     |
| Standard errors | Parentheses on the row below, same column alignment, no stars                                          |
| Variable labels | Human-readable names, not column names (e.g., "Management experience" not `mgmt_exp_yr`)             |
| Empty cells     | Blank when variable not in that specification                                                          |
| Column headers  | Sequential: (1), (2), (3)...                                                                           |
| Footer rows     | `Observations`, `R²`, `Adjusted R²` (or `Within R²` for FE models) — right-aligned numbers |
| Notes           | Two lines below `\bottomrule`: SE type, then significance levels                                     |

**Significance Stars:**

| Threshold | Symbol        |
| --------- | ------------- |
| p < 0.001 | `***`       |
| p < 0.01  | `**`        |
| p < 0.05  | `*`         |
| p < 0.10  | `$\dagger$` |

### Phase 5: Save and Review

1. Save all key objects (regression results, summary tables, processed data) using `to_parquet()` or `pickle.dump()`
2. Create `output/` subdirectories as needed with `Path.mkdir(parents=True, exist_ok=True)`
3. Run the python-reviewer agent on the generated script:

```
Delegate to the python-reviewer agent:
"Review the script at scripts/python/[script_name].py"
```

4. Address any Critical or High issues from the review.

---

## Script Structure

Follow this template:

```python
"""
============================================================
[Descriptive Title]
Author: [from project context]
Purpose: [What this script does]
Inputs: [Data files]
Outputs: [Figures, tables, data files]
============================================================
"""

# 0. Setup ----
from pathlib import Path
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.formula.api import ols

# Reproducibility
SEED = 20260301  # YYYYMMDD format
np.random.seed(SEED)
random.seed(SEED)

# Paths
DATA_DIR = Path("data/processed")
OUTPUT_DIR = Path("output/analysis")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Figure style
sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.2)


def main():
    """Main analysis workflow."""
    # 1. Data Loading ----
    # [Load and clean data]

    # 2. Exploratory Analysis ----
    # [Summary stats, diagnostic plots]

    # 3. Main Analysis ----
    # [Regressions, estimation]

    # 4. Tables and Figures ----
    # [Publication-ready output]

    # 5. Export ----
    # [Save all objects with to_parquet/pickle]


if __name__ == "__main__":
    main()
```

---

## Regression Export Function

Use this template to export regression results to AMJ-style LaTeX tables:

```python
def export_regression_latex(results, var_labels, model_labels, path,
                            caption="", label="", se_type="HC3"):
    """Build AMJ-style booktabs LaTeX table from statsmodels results.

    Args:
        results: list of fitted statsmodels regression results
        var_labels: ordered list of (col_name, display_name) tuples
        model_labels: list of column headers, e.g. ["(1)", "(2)", "(3)"]
        path: output path for .tex file
        caption: table caption
        label: LaTeX label for cross-reference
        se_type: description for notes (e.g., "HC3", "clustered by firm")
    """
    from pathlib import Path

    ncols = len(results)
    col_fmt = "l" + " c" * ncols
    lines = []

    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    if caption:
        lines.append(rf"\caption{{{caption}}}")
    if label:
        lines.append(rf"\label{{{label}}}")
    lines.append(rf"\begin{{tabular}}{{{col_fmt}}}")
    lines.append(r"\toprule")

    # Header row
    lines.append(" & ".join([""] + model_labels) + r" \\")
    lines.append(r"\midrule")

    # Variable rows
    for col_name, display_name in var_labels:
        coef_row = [display_name]
        se_row = [""]
        for res in results:
            if col_name in res.params.index:
                c = res.params[col_name]
                p = res.pvalues[col_name]
                se = res.bse[col_name]
                coef_row.append(f"{c:.3f}{sig_stars(p)}")
                se_row.append(f"({se:.3f})")
            else:
                coef_row.append("")
                se_row.append("")
        lines.append(" & ".join(coef_row) + r" \\")
        lines.append(" & ".join(se_row) + r" \\")

    # Footer
    lines.append(r"\midrule")
    for stat_name, getter in [
        ("Observations", lambda r: f"{int(r.nobs)}"),
        ("R$^2$", lambda r: f"{r.rsquared:.3f}"),
        ("Adjusted R$^2$", lambda r: f"{r.rsquared_adj:.3f}"),
    ]:
        row = [stat_name] + [getter(r) for r in results]
        lines.append(" & ".join(row) + r" \\")

    lines.append(r"\bottomrule")
    lines.append(rf"\multicolumn{{{ncols+1}}}{{l}}{{\footnotesize Robust standard errors ({se_type}) in parentheses.}}\\")
    lines.append(r"\multicolumn{" + str(ncols+1) + r"}{l}{\footnotesize $\dagger p<0.10$, $*p<0.05$, $**p<0.01$, $***p<0.001$}\\")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def sig_stars(p):
    """Return significance stars for p-value."""
    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    elif p < 0.10:
        return r"$\dagger$"
    return ""
```

---

## Important

- **Reproduce, don't guess.** If the user specifies a regression, run exactly that.
- **Show your work.** Print summary statistics before jumping to regression.
- **Check for issues.** Look for multicollinearity, outliers, perfect prediction.
- **Use relative paths.** All paths relative to repository root using `pathlib.Path`.
- **No hardcoded values.** Use variables for sample restrictions, date ranges, etc.
- **Handle edge cases.** Guard against division by zero, especially in financial metrics.

---

## Gotchas

| Issue | Solution |
|-------|----------|
| `SettingWithCopyWarning` | Use `.copy()` when slicing before assignment |
| Fixed effects via dummies | Report `Within R²` (compute from residuals), not OLS R² |
| Multicollinearity | Check VIF > 10 before interpreting; drop or combine collinear variables |
| LaTeX special chars in labels | Escape `_` → `\_`, `%` → `\%` in variable display names |
| Missing values differ across specs | Report exact N per model if sample sizes vary |
