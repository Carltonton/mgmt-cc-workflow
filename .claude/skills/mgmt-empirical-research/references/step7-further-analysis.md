# Step 7: Further Analysis

Supplementary analyses beyond core hypothesis testing: conditional process, effect sizes, variance modeling, and multi-group comparisons.

---

## Conditional Process Analysis (Deep Dive)

Full moderated mediation analysis after establishing basic mediation (Step 5b) and moderation (Step 5c).

### Index of Moderated Mediation
Quantifies how the indirect effect changes per unit change in the moderator.
```python
def moderated_mediation_index(df, x, m, y, w, controls, n_boot=5000, seed=42):
    """Bootstrap CI for the index of moderated mediation."""
    np.random.seed(seed)
    n = len(df)
    indices = []

    for _ in range(n_boot):
        idx = np.random.choice(n, n, replace=True)
        boot = df.iloc[idx]

        # Path a: X → M (may depend on W)
        X_a = sm.add_constant(boot[controls + [x, w, x + '_x_' + w]])
        a = boot_m_a_model.params[x]
        a_w = boot_m_a_model.params[x + '_x_' + w]  # Interaction on path a

        # Path b: M → Y
        X_b = sm.add_constant(boot[controls + [x, m]])
        b = boot_y_model.params[m]

        # Index = a_w * b
        indices.append(a_w * b)

    indices = np.array(indices)
    ci_lo, ci_hi = np.percentile(indices, [2.5, 97.5])
    return np.mean(indices), ci_lo, ci_hi
```

If CI excludes zero → moderated mediation confirmed (the mechanism strength varies with the moderator).

### Conditional Indirect Effects Table
Report indirect effect at moderator levels:
| Moderator Level | Indirect Effect | 95% CI | Significant? |
|----------------|-----------------|--------|-------------|
| Low W (-1 SD) | .XX | [.XX, .XX] | Yes/No |
| Mean W | .XX | [.XX, .XX] | Yes/No |
| High W (+1 SD) | .XX | [.XX, .XX] | Yes/No |

---

## Multi-Group SEM

Test structural invariance across groups (after establishing measurement invariance in Step 2D).

### Procedure
1. Confirm measurement invariance (configural + metric at minimum)
2. Test structural path equality across groups
3. If paths differ → moderation by group membership confirmed

```
! Mplus: structural invariance test
MODEL:
  Y ON X (slope);
  Y ON M (path_b);
MODEL group2:
  Y ON X (slope2);
  Y ON M (path_b2);
MODEL TEST:
  slope = slope2;  ! Test: is X→Y the same across groups?
```

---

## Effect Size Reporting

Required for all hypothesis tests. Management journals increasingly demand effect sizes alongside p-values.

### Cohen's f² for SEM Paths
```python
def cohens_f_squared(r_squared_full, r_squared_reduced):
    """f² = (R²_full - R²_reduced) / (1 - R²_full)"""
    return (r_squared_full - r_squared_reduced) / (1 - r_squared_full)
```
| f² | Size |
|----|------|
| .02 | Small |
| .15 | Medium |
| .35 | Large |

### κ² for Indirect Effects (MacKinnon, 2008)
Proportion of maximum possible indirect effect that is realized. More interpretable than raw indirect effect magnitude.

### Completely Standardized Effects
For SEM: report standardized path coefficients so readers can compare effect sizes across paths.

### Variance Explained (R²)
Report R² for each endogenous variable:
```python
# In SEM, compute R² for each endogenous variable
for var in ['M1', 'M2', 'Y1', 'Y2']:
    r2 = 1 - (model.inspect().query(f"op == '~" and f"target == '{var}'")['Estimate'].var())
    print(f"R²({var}) = {r2:.3f}")
```

---

## Variance Modeling (Thesis-Specific)

For research questions involving heterogeneous effects (e.g., personality refinement amplifies outcome variance).

### Quantile Regression
Test whether X→Y relationship differs across the outcome distribution:
```python
import statsmodels.formula.api as smf

for q in [0.25, 0.50, 0.75]:
    mq = smf.quantreg('Y ~ X + C1 + C2', data=df).fit(q=q)
    print(f"Q={q:.2f}: b_X={mq.params['X']:.3f}, SE={mq.bse['X']:.3f}")
```
If the coefficient increases at higher quantiles → effect is stronger for higher-Y individuals (variance amplification).

### Location-Scale Model
Simultaneously model mean AND variance of Y as functions of X:
```
* Stata: location-scale model
reg Y X C1 C2
predict residuals, r
gen abs_resid = abs(residuals)
reg abs_resid X C1 C2
```
Or use `hetregress` in Stata for formal heteroskedasticity modeling.

If X significantly predicts the variance (scale) of Y → variance amplification confirmed.

---

## Post-Hoc Power Analysis

Report observed power after analysis:
```python
from statsmodels.stats.power import TTestPower

power_analysis = TTestPower()
observed_power = power_analysis.power(
    effect_size=cohen_d, nobs=len(df), alpha=0.05, alternative='two-sided'
)
print(f"Observed power: {observed_power:.3f}")
```

---

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Reporting only p-values for effects | Always include effect size (f², κ², standardized β) |
| Running conditional process without basic mediation | Establish mediation first, then test moderation of it |
| Treating quantile regression as confirmatory | Use as supplementary — main tests should be OLS/SEM |
| Over-interpreting small effect sizes | f² = .02 is statistically significant but practically small — discuss both |
