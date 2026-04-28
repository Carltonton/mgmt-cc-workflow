# Identification Framework (Cross-Cutting)

This framework is a lens, not a step. It applies to every stage of the empirical pipeline to ensure causal claims are defensible. Without explicit identification thinking, the pipeline becomes a "descriptive SEM toolkit" rather than an empirical research framework.

## Five Core Identification Concerns

### 1. Reverse Causality
The direction of X→Y may actually be Y→X. Common in cross-sectional survey studies where all variables are measured simultaneously.

**Detection:** Temporal ordering in design (T1 predictor → T2 outcome); cross-lagged panel models for longitudinal data.

**Remedy:** Longitudinal design with temporal separation; experimental manipulation of X; instrumental variables (if valid instrument exists).

**Where in pipeline:** Step 1 (design tagging — time-lagged/panel designs mitigate this), Step 6 (competing reverse-causality model comparison).

### 2. Omitted Variable Bias
Unmeasured confounders correlated with both X and Y create spurious or biased relationships.

**Detection:** Sensitivity analysis (Oster's δ — how much selection on unobservables would be needed to eliminate the effect); comparison of estimates with/without controls (large coefficient changes suggest omitted variables).

**Remedy:** Theory-driven covariate selection (not "kitchen sink"); fixed effects for panel data (absorbs time-invariant confounders); instrumental variables; propensity score matching.

**Where in pipeline:** Step 5 (control variable justification via theory, not just statistics), Step 6 (robustness with alternative control sets).

### 3. Common Source Bias vs. True Causality
When predictor and criterion come from the same source at the same time, correlations are inflated by shared method variance — this is NOT the same as a true causal relationship.

**Detection:** Harman's single-factor test, marker variable technique, ULMC (covered in Step 4).

**Design remedy:** Multi-source data (e.g., employee self-report on attitudes, supervisor rates performance); temporal separation (T1 predictors, T2 outcomes); different scale formats for X and Y.

**Where in pipeline:** Step 1 (multi-source matching), Step 4 (CMB assessment), Step 6 (single-source sensitivity analysis).

### 4. Experimental vs. Observational Identification
Not all designs have the same identification strength. Be honest about what your design can and cannot establish.

**Where in pipeline:** Step 1 (design tag determines identification strength), Step 5 (method choice must match design), Step 6 (identification sensitivity appropriate to design).

### 5. Alternative Explanations
Always ask: what else could explain this pattern? A good paper rules out the most plausible alternatives.

**Remedy:** Competing models — test theoretically plausible alternatives (e.g., reversed paths, different mediators); null model comparison — show your model fits better than alternatives; boundary condition tests — if effect holds only under certain conditions, it's more credible.

**Where in pipeline:** Step 5 (nested model comparison in model building sequence), Step 6 (competing models, alternative specifications).

## Identification Strength Matrix

| Design | Identification Strength | Key Threats | Minimum Robustness Required |
|--------|------------------------|-------------|----------------------------|
| Lab experiment | Strong | External validity, demand effects | Replication, field follow-up |
| Field experiment | Strong–Moderate | Contamination, attrition | ITT analysis, attrition bias test |
| Quasi-experimental | Moderate | Selection bias | PSM, IV, DID — see stata-regression |
| Longitudinal survey | Moderate–Weak | Attrition, common method | Cross-lagged models, fixed effects |
| Cross-sectional survey | Weak | All of the above | Full robustness battery (Step 6) |

## Pipeline Mapping

| Concern | Step 1 | Step 4 | Step 5 | Step 6 |
|---------|--------|--------|--------|--------|
| Reverse causality | Design tag | — | — | Reverse model test |
| Omitted variables | — | — | Theory-driven controls | Alt. control sets, Oster δ |
| Common source bias | Multi-source matching | CMB tests | — | Single-source sensitivity |
| Alt. explanations | — | — | Nested model comparison | Competing models |
| Identification honesty | Design tag | — | Method matches design | Endogeneity sensitivity |

## Cross-Lagged Panel Check (Python)

For longitudinal data, test reverse causality:

```python
import statsmodels.api as sm

# Cross-lagged model: X1→Y2 and Y1→X2
df['X1_c'] = df['X_t1'] - df['X_t1'].mean()
df['Y1_c'] = df['Y_t1'] - df['Y_t1'].mean()

# Forward path: X1 → Y2 (controlling Y1)
m_forward = sm.OLS(df['Y_t2'], sm.add_constant(df[['Y1_c', 'X1_c', 'C1']])).fit()

# Reverse path: Y1 → X2 (controlling X1)
m_reverse = sm.OLS(df['X_t2'], sm.add_constant(df[['X1_c', 'Y1_c', 'C1']])).fit()

print(f"Forward X1→Y2: b={m_forward.params['X1_c']:.3f}, p={m_forward.pvalues['X1_c']:.4f}")
print(f"Reverse Y1→X2: b={m_reverse.params['Y1_c']:.3f}, p={m_reverse.pvalues['Y1_c']:.4f}")
```

If forward path is significant but reverse is not → evidence for X→Y direction.
If both significant → bidirectional relationship (acknowledge in discussion).
If reverse is stronger → revisit theoretical rationale.
