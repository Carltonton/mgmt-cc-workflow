# Step 4: Model Diagnostics, Respecification & Bias Assessment

This step is about model quality, not statistical assumptions. The key insight: normality is NOT a gatekeeper (robust estimators handle non-normality). Focus on multicollinearity, outliers, common method bias, fit evaluation, and model respecification.

---

## Multicollinearity

```python
from statsmodels.stats.outliers_influence import variance_inflation_factor

def compute_vif(df, predictors):
    X = df[predictors].dropna()
    vif_data = pd.DataFrame({
        'variable': predictors,
        'VIF': [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    })
    return vif_data

vif = compute_vif(df, ['X', 'M1', 'M2', 'C1', 'C2'])
print(vif)
# VIF < 5: good, < 10: acceptable, > 10: problematic
```

**Note:** After mean-centering and creating interaction terms (Step 5), re-check VIF. Interaction terms can inflate VIF if centering was skipped.

---

## Outliers

### Mahalanobis Distance (multivariate outliers)
```python
from scipy.stats import chi2

def mahalanobis_outliers(df, variables, alpha=0.001):
    X = df[variables].dropna()
    cov = X.cov().values
    inv_cov = np.linalg.inv(cov)
    mean = X.mean().values
    diff = X.values - mean
    md = np.sqrt(np.sum(diff @ inv_cov * diff, axis=1))
    threshold = chi2.ppf(1 - alpha, df=len(variables))
    outliers = md > np.sqrt(threshold)
    return df.index[outliers]

outlier_idx = mahalanobis_outliers(df, items)
print(f"Multivariate outliers: {len(outlier_idx)} cases")
```

### Cook's Distance (regression outliers)
```python
import statsmodels.api as sm

model = sm.OLS(df['Y'], sm.add_constant(df[['X', 'M', 'C1']])).fit()
influence = model.get_influence()
cooks = influence.cooks_distance[0]
high_influence = np.where(cooks > 4/len(df))[0]
print(f"High-influence cases (Cook's d): {len(high_influence)}")
```

**Decision:** Don't automatically remove outliers. Investigate first. If legitimate extreme values, use robust methods. If data entry errors, correct or remove.

---

## Common Method Bias (Design Issue, NOT Assumption)

CMB is a validity threat arising from measuring predictors and outcomes with the same method/source at the same time. Three detection approaches:

### 1. Harman's Single-Factor Test
```python
from factor_analyzer import FactorAnalyzer

# Force single factor
fa = FactorAnalyzer(n_factors=1, rotation=None)
fa.fit(df[all_items])
variance_explained = fa.get_factor_variance()[1][0]
print(f"Single factor explains: {variance_explained*100:.1f}%")
# Must be < 50% to pass
```
**Limitation:** Weak test — easily passes but doesn't prove CMB is absent.

### 2. CFA Marker Variable Technique
Include a theoretically unrelated "marker" variable in the CFA. If it correlates with substantive constructs, method variance is present.

```
! Mplus: Marker variable model
MODEL:
  f_substantive BY item1-item8;
  f_marker BY marker1-marker3;
  f_marker WITH f_substantive@0;  ! Uncorrelated by theory
```
If model fit improves when allowing correlation → method variance detected.

### 3. Unmeasured Latent Method Construct (ULMC)
Add an orthogonal method factor to the CFA. All items load on both their substantive factor and the method factor.

```
! Mplus: ULMC model
MODEL:
  f1 BY item1-item4;
  f2 BY item5-item8;
  f_method BY item1-item8;  ! All items also load on method factor
  f_method WITH f1@0 f2@0;  ! Orthogonal to substantive factors
  f_method BY item1-item8@1;  ! Constrain method loadings equal
```
Compare model fit with and without ULMC. If substantive relationships change substantially → CMB is a concern.

---

## Model Respecification (SEM-Specific)

### Modification Indices (MI)
MI > 3.84 suggests a path or covariance that, if freed, would significantly improve fit.

```python
# semopy: after model fit
mi = model.modification_indices()
print(mi[mi['MI'] > 3.84].sort_values('MI', ascending=False).head(10))
```

**Rules for respecification:**
1. NEVER free parameters just to improve fit — every change needs theoretical rationale
2. Error covariances: only between items with similar wording, same scale, or same method
3. Item deletion: only if loading < .40 AND theoretical justification for removal
4. Cross-loadings: only if theory supports dual-factor membership
5. Document every respecification in a log (what changed, why, MI value)

### Respecification Log Template
| Action | MI Value | Theoretical Rationale | Impact on Fit |
|--------|----------|----------------------|---------------|
| Added e1↔e3 covariance | 12.4 | Same scale, reverse-coded pair | CFI: .92→.95 |

---

## Fit Indices Review

Re-assess model fit after any respecification. Track progressive fit:

| Model | χ²/df | CFI | TLI | RMSEA [90% CI] | SRMR | Decision |
|-------|-------|-----|-----|----------------|------|----------|
| Initial CFA | 4.2 | .89 | .87 | .09 [.08, .10] | .07 | Below threshold |
| + Error cov | 2.8 | .93 | .91 | .06 [.05, .07] | .05 | Acceptable |
| + Item removed | 2.1 | .96 | .95 | .04 [.03, .05] | .04 | Good |

---

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Treating CMB as "assumption test" | CMB is a design/validity issue — address in design (multi-source, temporal separation) and assess statistically |
| Freeing error covariances liberally | Only with theoretical justification — document every one |
| Blocking pipeline on normality tests | MLR handles non-normality; don't gatekeep on Shapiro-Wilk |
| Removing outliers without investigation | Check if data entry error first; use robust methods for legitimate extremes |
| Reporting only final model fit | Show progressive fit through respecification steps |
