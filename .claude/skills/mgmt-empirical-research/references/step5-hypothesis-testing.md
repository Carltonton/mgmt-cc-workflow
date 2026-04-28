# Step 5: Hypothesis Testing

Three-stage ordered sequence: **(a) Main Effects → (b) Mechanisms (Mediation) → (c) Boundary Conditions (Moderation)**

---

## (a) Main Effects

### Direct Effects Testing
- SEM path analysis (preferred for latent variable models)
- OLS regression (for composite-score-based analysis)

### Model Building Sequence
Progressive entry to show incremental contribution:

| Model | Contents | Tests |
|-------|----------|-------|
| Model 0 | Controls only | Baseline R² |
| Model 1 | Controls + main IVs | ΔR² for IV contribution |
| Model 2 | Controls + IVs + mediators | Mediation (stage b) |
| Model 3 | Controls + IVs + mediators + interactions | Moderation (stage c) |

```python
import statsmodels.formula.api as smf
from scipy.stats import f as f_dist

def delta_r2_test(m_restricted, m_full):
    r2_f, r2_r = m_full.rsquared, m_restricted.rsquared
    n, k_f, k_r = m_full.nobs, m_full.df_model, m_restricted.df_model
    f_stat = ((r2_f - r2_r) / (k_f - k_r)) / ((1 - r2_f) / (n - k_f - 1))
    p_val = 1 - f_dist.cdf(f_stat, k_f - k_r, n - k_f - 1)
    return f_stat, p_val

m0 = smf.ols('Y ~ C1 + C2 + C3', data=df).fit()
m1 = smf.ols('Y ~ C1 + C2 + C3 + X', data=df).fit()
f_stat, p = delta_r2_test(m0, m1)
print(f"H1: X→Y ΔR²={m1.rsquared - m0.rsquared:.4f}, F={f_stat:.3f}, p={p:.4f}")
```

Report: coefficient, SE, p-value, standardized effect, R², ΔR².

---

## (b) Mechanisms — Mediation Analysis

### Methodological Context
- **Causal Steps (Baron & Kenny, 1986)**: Historical 4-step approach. Step 1 (significant total effect) is NOT required. Low statistical power. Cannot test indirect effect directly. **Use only as supplementary, not primary evidence.**
- **Modern Bootstrap Approach (Hayes, 2022)**: Current standard. Directly tests the indirect effect (a×b) with bootstrap CI. No requirement for significant total effect. Report: indirect effect, 95% bootstrap CI, if CI excludes zero → mediation established.

### Key Concepts Beyond "Run PROCESS"

**Inconsistent (Competitive) Mediation**
- Indirect effect (a×b) and direct effect (c') have **opposite signs**
- Total effect may be near zero (they cancel out) — this is NOT a failure
- Reveals opposing mechanisms operating simultaneously
- MUST use bootstrap CI, cannot rely on total effect significance

**Suppression Effects**
- Adding mediator **increases** the direct effect: |c'| > |c|
- Mediator suppresses irrelevant variance in X, clarifying the X→Y relationship
- Signal: direct and indirect effects have same sign, but direct becomes larger

**Sequential (Serial) Mediation**
- X → M1 → M2 → Y (multi-step chain)
- Test each specific indirect path separately via bootstrap
- Use Hayes PROCESS Model 6 or Mplus MODEL INDIRECT

**Parallel vs. Serial — NOT interchangeable**
- **Parallel**: X simultaneously affects multiple mediators (X→M1→Y, X→M2→Y)
- **Serial**: X affects mediator chain (X→M1→M2→Y)
- **Theory determines specification** — never test both and pick the better one

### Bootstrap CI Implementation
```python
import numpy as np
import statsmodels.api as sm

def bootstrap_mediation(df, x, m, y, controls, n_boot=5000, seed=42):
    np.random.seed(seed)
    n = len(df)
    indirect = []
    for _ in range(n_boot):
        idx = np.random.choice(n, n, replace=True)
        boot = df.iloc[idx]
        # Path a: X → M
        Xa = sm.add_constant(boot[controls + [x]])
        a = sm.OLS(boot[m], Xa).fit().params[x]
        # Path b: M → Y (controlling for X)
        Xb = sm.add_constant(boot[controls + [x, m]])
        b = sm.OLS(boot[y], Xb).fit().params[m]
        indirect.append(a * b)
    ie = np.array(indirect)
    ci_lo, ci_hi = np.percentile(ie, [2.5, 97.5])
    return np.mean(ie), ci_lo, ci_hi
```

### Mplus Mediation Syntax
```
MODEL:
  M1 ON X (a1);
  Y1 ON M1 (b1) X (cp1);
MODEL CONSTRAINT:
  NEW(ind1);
  ind1 = a1*b1;
OUTPUT: CINTERVAL(BOOTSTRAP);
```

### Reporting Template
- Indirect effect: ab = .XX, 95% CI [.XX, .XX]
- Direct effect: c' = .XX, p = .XX
- Total effect: c = .XX, p = .XX
- Effect size: κ² = .XX
- Status: full / partial / inconsistent / none

---

## (c) Boundary Conditions — Moderation

### Three Paths

#### Path 1: Regression-Based Moderation
For composite scores, single-level data.

```python
df['X_c'] = df['X'] - df['X'].mean()
df['W_c'] = df['W'] - df['W'].mean()
df['XW'] = df['X_c'] * df['W_c']

model = smf.ols('Y ~ X_c + W_c + XW', data=df).fit()

# Simple slopes at ±1 SD
for label, w_val in [('Low (-1SD)', -df['W'].std()), ('Mean', 0), ('High (+1SD)', df['W'].std())]:
    slope = model.params['X_c'] + model.params['XW'] * w_val
    print(f"Simple slope at {label}: {slope:.4f}")
```

#### Path 2: SEM-Based Moderation
For latent variables where measurement error matters.

**Latent interaction** (matched-pair indicator product):
```python
model = '''
  X =~ x1 + x2 + x3
  W =~ w1 + w2 + w3
  Y =~ y1 + y2 + y3
  XW =~ x1w1 + x2w2 + x3w3
  Y ~ X + W + XW
'''
```

**Multi-group SEM** for categorical moderators:
```
MODEL:
  Y ON X (slope);
MODEL group2:
  Y ON X (slope2);
MODEL TEST:
  slope = slope2;  ! Test if slopes differ across groups
```

#### Path 3: Multilevel-Based Moderation
For nested data (employees in teams, students in classes). Cross-level interactions where Level-2 W moderates Level-1 X→Y.

```python
import statsmodels.regression.mixed_linear_model as mlm

df['X_gmc'] = df.groupby('group')['X'].transform(lambda x: x - x.mean())
model = mlm.MixedLM.from_formula(
    'Y ~ X_gmc + W + X_gmc:W',
    groups=df['group'], data=df
).fit()
```
- ICC > .05 justifies multilevel approach
- Random intercept + cross-level interaction

### Conditional Process (Moderated Mediation)
When the indirect effect itself depends on a moderator.

- **Index of moderated mediation**: If bootstrap CI excludes zero → moderated mediation confirmed
- **Conditional indirect effects**: Report at moderator levels (-1 SD, mean, +1 SD)
- Hayes PROCESS Model 7 (first-stage), Model 14 (second-stage), Model 8 (both)

### Reporting Template for Moderation
- Interaction: b = .XX, SE = .XX, p = .XX
- Simple slope at Low W: b = .XX, p = .XX
- Simple slope at High W: b = .XX, p = .XX
- Johnson-Neyman transition point: W = .XX
- Include interaction plot (see Step 8)

---

## Common Pitfalls

| Pitfall | Why It's Wrong | Correct Approach |
|---------|----------------|------------------|
| Not mean-centering before interaction | Inflated VIF, uninterpretable main effects | Always center X and W before XW |
| Only reporting interaction significance | Readers can't see where effect exists | Follow with simple slopes + plot |
| Using Baron & Kenny as sufficient | Low power, requires total effect | Bootstrap CI is the standard |
| Requiring significant total effect for mediation | Inconsistent mediation makes total non-significant | Test indirect effect directly |
| Serial when theory says parallel | Tests wrong causal chain | Match mediation type to theory |
| Ignoring nested data structure | Inflates Type I error | Check ICC > .05 → use multilevel |
