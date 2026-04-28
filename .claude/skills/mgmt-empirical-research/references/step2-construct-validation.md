# Step 2: Construct Development & Validation

## Branching Decision (MANDATORY at entry)

| Scale Status | Path | Stages |
|---|---|---|
| **Established** (validated in prior literature, used as-is) | Skip EFA → CFA directly | B → C → D |
| **Adapted** (modified from existing scale: items added/removed/translated) | CFA + invariance testing | B → C → D (emphasize D) |
| **New** (original development, no prior factor structure) | Full EFA → CFA pipeline | A → B → C → D |

---

## Stage A: EFA (Exploration) — NEW scales only

### When to use
Developing a new measure, or exploring dimensionality in a new context with no established factor structure.

### Procedure

**1. Sample splitting** — 50/50 random split, or independent samples. EFA on calibration sample, CFA on validation.

**2. Factorability checks**
```python
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity, calculate_kmo

chi_square, p = calculate_bartlett_sphericity(df[items])
kmo_all, kmo_model = calculate_kmo(df[items])
print(f"Bartlett χ² p={p:.4f}, KMO={kmo_model:.3f}")
# KMO > .60 required, > .80 preferred
```

**3. Factor number determination**
- Parallel analysis (Horn, 1965): gold standard. Compare real-data eigenvalues to random-data eigenvalues.
- Kaiser criterion (eigenvalue > 1): supplementary only — tends to over-extract.
- Scree plot: visual inspection for the "elbow."

**4. Factor extraction & rotation**
```python
from factor_analyzer import FactorAnalyzer

fa = FactorAnalyzer(n_factors=n_factors, rotation='oblimin')
fa.fit(df[items])
loadings = pd.DataFrame(fa.loadings_, index=items)
```
- Use **oblimin** (oblique) by default — management constructs are typically correlated.
- Varimax only if theory explicitly says factors are orthogonal.

**5. Item retention criteria**
- Primary loading ≥ .50
- Cross-loading gap ≥ .20 (primary minus highest cross-loading)
- Communality ≥ .40
- Items failing criteria: document removal, rerun EFA

**6. Sample size** — Minimum 5:1 ratio (N:items), ideally 10:1. N ≥ 200 minimum.

---

## Stage B: CFA (Confirmation)

### Model specification
```python
from semopy import Model

cfa_spec = '''
  factor1 =~ item1 + item2 + item3 + item4
  factor2 =~ item5 + item6 + item7 + item8
  factor3 =~ item9 + item10 + item11 + item12
'''

model = Model(cfa_spec)
result = model.fit(df)
stats = model.inspect()
```

### Estimator selection
| Estimator | When to Use | Notes |
|-----------|-------------|-------|
| **MLR** | Default for Likert data, N ≥ 200 | Satorra-Bentler scaled χ²; handles non-normality |
| **WLSMV** | Ordinal Likert ≤5 categories, small N | Does not assume continuous indicators |

### Fit criteria (Hu & Bentler, 1999)
| Index | Good | Acceptable | Notes |
|-------|------|------------|-------|
| χ²/df | < 2 | < 3 | Sensitive to N |
| CFI | ≥ .95 | ≥ .90 | For complex models, .90 acceptable |
| TLI | ≥ .95 | ≥ .90 | Penalizes model complexity |
| RMSEA | ≤ .06 | ≤ .08 | With 90% CI; test of close fit (p > .05) |
| SRMR | ≤ .08 | — | Less sensitive to N |

### Mplus CFA template
```
TITLE: CFA for [Construct Name]
DATA: FILE IS data.dat;
VARIABLE:
  NAMES ARE item1-item12;
  USEVARIABLES ARE item1-item12;
  MISSING ARE ALL (-99);
ANALYSIS: ESTIMATOR = MLR;
MODEL:
  f1 BY item1 item2 item3 item4;
  f2 BY item5 item6 item7 item8;
  f3 BY item9 item10 item11 item12;
OUTPUT: STANDARDIZED MODINDICES(3.84);
```

---

## Stage C: Reliability & Validity

### Reliability
```python
def cronbach_alpha(items_df):
    k = items_df.shape[1]
    item_vars = items_df.var(axis=0, ddof=1)
    total_var = items_df.sum(axis=1).var(ddof=1)
    return (k / (k - 1)) * (1 - item_vars.sum() / total_var)

def composite_reliability(loadings):
    """CR = (Σλ)² / [(Σλ)² + Σ(1-λ²)]"""
    sum_l = sum(loadings)
    sum_e = sum(1 - l**2 for l in loadings)
    return sum_l**2 / (sum_l**2 + sum_e)

def ave(loadings):
    """AVE = mean(λ²)"""
    return sum(l**2 for l in loadings) / len(loadings)
```

**Thresholds:** α ≥ .70, CR ≥ .70 (both preferred ≥ .80)

### Convergent validity
- AVE ≥ .50
- Standardized loadings ≥ .70 (≥ .60 acceptable for established scales)
- All loadings significant (t > 1.96)

### Discriminant validity
**HTMT** (Henseler et al., 2015) — the current gold standard:
```python
def htmt_ratio(df, items_f1, items_f2):
    """HTMT = mean(corr(f1_items, f2_items))² / sqrt(mean(corr_within_f1) * mean(corr_within_f2))"""
    cross = df[items_f1].corrwith(df[items_f2]).values
    between = np.sqrt(np.mean(cross**2))
    within1 = df[items_f1].corr().values
    within1 = within1[np.triu_indices_from(within1, k=1)]
    within2 = df[items_f2].corr().values
    within2 = within2[np.triu_indices_from(within2, k=1)]
    within = np.sqrt(np.mean(within1) * np.mean(within2))
    return between / within
```
- HTMT < .85 (strict) or < .90 (liberal)
- Bootstrap CI: if CI includes 1, discriminant validity is questionable

**Fornell-Larcker criterion**: √AVE of each construct > its correlations with other constructs. Report alongside HTMT (still expected by many reviewers).

---

## Stage D: Measurement Invariance

### When required
- Comparing groups (gender, expertise, culture)
- Multi-wave studies (ensure measurement stability over time)

### Testing sequence
1. **Configural**: Same factor structure across groups (baseline)
2. **Metric**: Equal factor loadings (required for comparing structural paths)
3. **Scalar**: Equal intercepts (required for comparing latent means)

### Evaluation criteria (Chen, 2007)
- ΔCFI ≤ .010 (most reliable for MLR)
- ΔRMSEA ≤ .015
- Satorra-Bentler scaled χ² difference test

### Partial invariance
If full metric/scalar invariance fails: free non-invariant parameters, test partial model. Still valid if majority of parameters are invariant.

### Mplus invariance template
```
TITLE: Invariance Test - [Groups]
DATA: FILE IS data.dat;
VARIABLE:
  NAMES ARE item1-item12 group;
  USEVARIABLES ARE item1-item12;
  GROUPING IS group (1=g1, 2=g2);
  MISSING ARE ALL (-99);
ANALYSIS: ESTIMATOR = MLR;
MODEL:
  f1 BY item1 item2 item3 item4;
  f2 BY item5 item6 item7 item8;
! Metric: loadings constrained by default in multi-group
! For scalar, add: [item1] (m1); [item2] (m2); ...
OUTPUT: STANDARDIZED;
```

---

## Common Pitfalls

| Pitfall | Why It's Wrong | Correct Approach |
|---------|----------------|------------------|
| EFA and CFA on same sample | Overfits, inflates fit indices | Split sample or use independent samples |
| Varimax for correlated constructs | Forces orthogonality where it doesn't exist | Default to oblimin |
| Good CFA fit with weak items | Model-level fit masks item-level problems | Check every loading ≥ .50 |
| Freeing error covariances to improve fit | Capitalizes on chance | Only with theoretical justification |
| Trusting Kaiser over parallel analysis | Kaiser over-extracts | Parallel analysis is the standard |
| Ignoring modification indices entirely | Misses genuine misspecification | Review MI > 3.84, free only with theory |
| No invariance testing for group comparisons | Invalid to compare paths across groups | Test configural → metric → scalar before structural comparisons |
