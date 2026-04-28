# Step 6: Robustness & Identification

This is where the identification framework (see `identification-framework.md`) manifests concretely. Every robustness check should be tied to a specific identification concern.

---

## Alternative Model Specifications

### Progressive Controls
Test whether results hold with different control variable sets:
```python
# Specification 1: No controls
m1 = smf.ols('Y ~ X', data=df).fit()
# Specification 2: Demographics only
m2 = smf.ols('Y ~ X + age + gender + education', data=df).fit()
# Specification 3: Full controls
m3 = smf.ols('Y ~ X + age + gender + education + tenure + industry', data=df).fit()
# Specification 4: Alternative controls
m4 = smf.ols('Y ~ X + age + gender + ai_self_efficacy', data=df).fit()

for i, m in enumerate([m1, m2, m3, m4], 1):
    print(f"Spec {i}: b_X={m.params['X']:.3f}, p={m.pvalues['X']:.4f}, R²={m.rsquared:.3f}")
```
If X coefficient is stable across specifications → robust to omitted variable concerns.

---

## Competing Models

Test theoretically plausible alternative explanations:

### Reverse Causality Model
```python
# Forward: X → Y (your model)
m_forward = smf.ols('Y ~ X + C1 + C2', data=df).fit()
# Reverse: Y → X (alternative explanation)
m_reverse = smf.ols('X ~ Y + C1 + C2', data=df).fit()
```
For longitudinal data: use cross-lagged models (see `identification-framework.md`).

### Alternative Mediator
If another variable could explain X→Y, test it:
```python
# Your mediator
_, ci_lo, ci_hi = bootstrap_mediation(df, 'X', 'M1', 'Y', controls)
# Alternative mediator
_, ci_lo2, ci_hi2 = bootstrap_mediation(df, 'X', 'M_alt', 'Y', controls)
```
Report both. If your mediator's indirect effect remains significant → more credible.

### Non-linear Alternative
```python
m_linear = smf.ols('Y ~ X', data=df).fit()
m_quad = smf.ols('Y ~ X + I(X**2)', data=df).fit()
# Compare with F-test or AIC
```

---

## Endogeneity Sensitivity

### Instrumental Variable (if instrument available)
Delegate to `stata-regression` skill for IV/2SLS.

### Heckman Correction (selection bias)
If sample selection is a concern (e.g., only motivated employees respond):
```
* Stata: Heckman two-step
heckman Y X C1 C2, select(selection_eq = Z C1 C2)
```
Where Z is an exclusion restriction (variable affecting selection but not outcome).

### Fixed Effects (panel data)
If design tag = `panel`:
```python
# Entity fixed effects
m_fe = smf.ols('Y ~ X + C(entity)', data=df).fit()
# Or use linearmodels
from linearmodels.panel import PanelOLS
m_fe = PanelOLS(df['Y'], df[['X']], entity_effects=True).fit()
```

---

## Subsample Analysis

### By Key Moderator
```python
for group_name, group_df in df.groupby('expertise_median'):
    m = smf.ols('Y ~ X + C1 + C2', data=group_df).fit()
    print(f"{group_name}: b_X={m.params['X']:.3f}, p={m.pvalues['X']:.4f}, n={len(group_df)}")
```

### By Data Source
If multi-source: test with single-source vs. multi-source subsamples.

### By Time Period
If multi-wave: test each wave separately for stability.

---

## CMB Post-Hoc Correction

If CMB was detected in Step 4:
1. Report original (uncorrected) results
2. Report ULMC-corrected results
3. Compare key coefficients — if they remain similar, CMB is not driving findings

```python
# Compare substantive coefficients before/after ULMC correction
print(f"Original X→Y: b={b_orig:.3f}, p={p_orig:.4f}")
print(f"ULMC-corrected X→Y: b={b_ulmc:.3f}, p={p_ulmc:.4f}")
print(f"Difference: {abs(b_orig - b_ulmc):.3f}")
```

---

## Latent vs. Composite Sensitivity

```python
# Composite scores
m_comp = smf.ols('Y ~ X_composite + C1', data=df).fit()
# Latent factor scores (from CFA)
m_latent = smf.ols('Y ~ X_factor_score + C1', data=df).fit()

print(f"Composite: b={m_comp.params['X_composite']:.3f}")
print(f"Latent:    b={m_latent.params['X_factor_score']:.3f}")
```
If both approaches yield similar results → findings are robust to measurement approach.

---

## Robustness Summary Table Template

| Robustness Check | Key Coefficient | Change from Main Model | Conclusion |
|-----------------|-----------------|----------------------|------------|
| No controls | .XX | ±.XX | Robust / Sensitive |
| Alternative mediator | .XX | ±.XX | Robust / Attenuated |
| Subsample: High expertise | .XX | ±.XX | Robust / Weaker |
| ULMC correction | .XX | ±.XX | CMB not driving |
| Latent vs. composite | .XX | ±.XX | Measurement-robust |

---

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Running robustness only as "add more controls" | Test specific identification threats, not just add controls |
| Ignoring failed robustness checks | Report honestly; discuss why effect might be fragile |
| Not connecting robustness to identification | Each check should address a specific identification concern |
| Over-claiming robustness | "Robust" means consistent, not proof of causality |
