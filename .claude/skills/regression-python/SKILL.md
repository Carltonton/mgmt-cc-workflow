---
name: regression-python
description: Run regression analyses in Python with publication-ready LaTeX tables following management journal conventions.
version: 2.0.0
argument-hint: "model type, DV, key regressors, controls, SE type, output path"
---
# Python Regression

## Workflow

1. **Ask** — DV, key regressors, controls, clustering level, output path
2. **Build** — Fit models with `statsmodels`, use robust or clustered SEs
3. **Export** — Write `.tex` table following the specification below
4. **Verify** — Check coefficients, stars, N, R² match model summaries

---

## Common Models

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

---

## LaTeX Table Specification (Management Journal Style)

Follow AMJ / SMJ / AMR conventions using the `booktabs` package.

### Layout

```
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

### Rules

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

### Significance Stars

| Threshold | Symbol        |
| --------- | ------------- |
| p < 0.001 | `***`       |
| p < 0.01  | `**`        |
| p < 0.05  | `*`         |
| p < 0.10  | `$\dagger$` |

Use `sig_stars(p)` from `tebao.utils` to generate these consistently.

---

## Python Code Template

```python
import statsmodels.api as sm
from pathlib import Path


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
    from tebao.utils import sig_stars

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
```

---

## Gotchas

| Issue                              | Solution                                                                |
| ---------------------------------- | ----------------------------------------------------------------------- |
| `SettingWithCopyWarning`         | Use `.copy()` when slicing before assignment                          |
| Fixed effects via dummies          | Report `Within R²` (compute from residuals), not OLS R²             |
| Multicollinearity                  | Check VIF > 10 before interpreting; drop or combine collinear variables |
| LaTeX special chars in labels      | Escape `_` → `\_`, `%` → `\%` in variable display names       |
| Missing values differ across specs | Report exact N per model if sample sizes vary                           |
