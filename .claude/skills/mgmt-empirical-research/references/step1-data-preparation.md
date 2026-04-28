# Step 1: Data Preparation & Design Tagging

Two data tracks: Survey and Experimental. After cleaning, tag the data structure to determine downstream analysis branching.

---

## Track A: Survey Data

### Import & Inspection
```python
import pandas as pd
import numpy as np

df = pd.read_csv('survey_data.csv')
print(f"Shape: {df.shape}")
print(f"Response rate: {n_responses / n_invited * 100:.1f}%")
df.info()
df.describe()
```

### Missing Data Analysis

**1. Visualize missingness**
```python
missing_pct = df.isnull().mean().sort_values(ascending=False)
high_missing = missing_pct[missing_pct > 0.15]
print(f"Variables with >15% missing:\n{high_missing}")
```

**2. Little's MCAR test** — determines if Missing Completely At Random
- MCAR → listwise deletion is acceptable
- MAR → use multiple imputation (MICE)
- MNAR → sensitivity analysis + report as limitation

**3. Decision thresholds**
- >15% missing per variable → consider dropping the variable
- >10% missing per case → consider dropping the case
- If MCAR and missing rate < 5% → listwise deletion is fine

### Response Quality Flags

**Straight-lining** (SD=0 across scale items):
```python
def flag_straightliners(df, items):
    return df.index[df[items].std(axis=1) == 0].tolist()
```

**Speeders** (completion time < median/3): Flag for review.

**Attention checks**: Fail > 1 → exclude. Document exclusion rate.

**Inconsistent responses**: Check reverse-coded items. Flag contradictory pairs.

### Non-Response Bias
Armstrong & Overton (1977): compare early respondents (first 25%) vs. late (last 25%).
```python
from scipy.stats import ttest_ind

early = df[df['order'] <= df['order'].quantile(0.25)]
late = df[df['order'] >= df['order'].quantile(0.75)]

for var in key_vars:
    t, p = ttest_ind(early[var].dropna(), late[var].dropna())
    sig = '*' if p < .05 else ''
    print(f"{var}: t={t:.3f}, p={p:.4f} {sig}")
```
If significant differences → acknowledge non-response bias as limitation.

### Multi-Source Data Matching
For supervisor-employee, peer-ego, or multi-wave designs:
- Match by unique identifier
- Target match rate > 80%
- Test for systematic differences between matched and unmatched cases

---

## Track B: Experimental Data

### Manipulation Check
```python
from scipy.stats import ttest_ind
treat = df[df['condition'] == 'treatment']['manip_check']
ctrl = df[df['condition'] == 'control']['manip_check']
t, p = ttest_ind(treat, ctrl)
print(f"Manipulation check: t={t:.3f}, p={p:.4f}")
# p < .05 confirms manipulation worked
```

### Randomization Balance
```python
from scipy.stats import chi2_contingency

for var in ['age', 'gender', 'education', 'tenure']:
    t_grp = df[df['condition'] == 'treatment'][var]
    c_grp = df[df['condition'] == 'control'][var]
    if df[var].dtype in ['float64', 'int64']:
        t, p = ttest_ind(t_grp.dropna(), c_grp.dropna())
    else:
        ct = pd.crosstab(df[var], df['condition'])
        chi2, p, _, _ = chi2_contingency(ct)
    flag = '⚠ IMBALANCE' if p < .05 else ''
    print(f"{var}: p={p:.4f} {flag}")
```

### Attention Check Exclusions
Document: N excluded, reasons, and whether results differ with/without exclusions (report as sensitivity analysis in Step 6).

---

## Design Tagging (MANDATORY)

After cleaning, assign ONE primary design tag:

| Tag | Criteria | Downstream Implications |
|-----|----------|------------------------|
| `cross-sectional` | Single time point, all self-report | Weakest ID; full CMB checks; avoid causal language |
| `time-lagged` | ≥2 waves, temporal separation of X and Y | Moderate ID; test attrition bias |
| `panel` | ≥3 waves, repeated measures | Fixed effects applicable; within-person change |
| `multilevel` | Nested (employees in teams, dyadic) | Check ICC; use HLM/MSEM |
| `experimental` | Random assignment, manipulated IV | Strong ID; focus on ITT, effect sizes |

```python
design_tag = 'time-lagged'
metadata = {
    'design': design_tag,
    'n_waves': 3,
    'n_sources': 2,
    'response_rate': 0.42,
    'exclusions': {'straightliners': 12, 'attention': 8}
}
```

---

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Excluding without documenting rate | Report N at each step (flow chart) |
| Mean-imputing all missing | Use MICE for MAR; report with/without imputation |
| Skipping non-response bias test | Early-vs-late comparison is minimum standard |
| Assuming randomization worked | Always test balance on observables |
| Not tagging data structure | Tag determines correct downstream analysis path |
