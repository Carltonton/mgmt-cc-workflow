# Management Empirical Research Standards

**Applies when:** Using `mgmt-empirical-research` skill or any quantitative management research analysis (survey, experimental, or mixed).

---

## Survey / CFA-SEM Standards

### CFA/SEM Quality Gates

| Metric | Threshold | Reject If |
|--------|-----------|-----------|
| CFI | > .95 | < .93 |
| RMSEA | < .06 | > .08 |
| SRMR | < .08 | > .10 |
| CR (composite reliability) | > .70 | < .60 |
| AVE | > .50 | < .40 |
| HTMT | < .85 | > .90 |
| Measurement invariance ΔCFI | ≤ .010 | > .020 |

### Survey Reporting Requirements

- **Effect sizes mandatory:** Report Cohen's f² (.02/.15/.35), κ², or standardized effects alongside p-values
- **Bootstrap over Sobel:** Indirect effects tested with bootstrap CI (5,000+ resamples)
- **Table 1 diagonal:** Must show AVE√ (Fornell-Larcker), NOT 1.00
- **Model building sequence:** Model 0 (controls) → Model 1 (+IVs) → Model 2 (+mediators) → Model 3 (+interactions)
- **Respecification log:** Document every model change with theoretical rationale

### Required Outputs (Survey/CFA-SEM)

| Output | Format |
|--------|--------|
| T1: Descriptives/correlations/AVE√/CR | LaTeX booktabs + DOCX |
| T2: CFA loadings | LaTeX booktabs |
| T3: Measurement invariance | LaTeX booktabs |
| T4: Structural model | LaTeX booktabs |
| T5: Mediation/conditional process | LaTeX booktabs |
| F1: Research model diagram | PDF vector |
| F2: Structural model results | PDF vector + PNG 300dpi |
| F3: Interaction plots | PDF vector + PNG 300dpi |
| F4: Indirect effect forest plot | PDF vector + PNG 300dpi |

---

## Experimental Design Standards

### Pre-Analysis Checks

- [ ] **Manipulation checks:** Report ANOVA/t-test confirming manipulation worked (F/t, p, η²)
- [ ] **Randomization balance:** t-tests/χ² on demographics across conditions
- [ ] **Attention checks:** Document exclusions and final N per condition
- [ ] **Power analysis:** Report a priori power (G*Power) or minimum detectable effect; if post-hoc, label clearly

### Treatment Effect Estimation

| Method | When to Use | Key Requirements |
|--------|-------------|------------------|
| OLS regression | Simple between-subjects | Robust SE, covariates justified by theory |
| ANOVA/ANCOVA | Factorial designs | Report F, df, p, partial η²; ANCOVA covariates pre-specified |
| Logistic/probit | Binary outcomes | Report odds ratios or marginal effects, not just coefficients |
| Mixed-effects | Nested/clustered experiments | Random intercepts for clusters; report ICC |

### Effect Size Reporting (Experiments)

| Effect Size | Context | Thresholds (small/medium/large) |
|-------------|---------|-------------------------------|
| Cohen's d | 2-group comparison | .20 / .50 / .80 |
| Partial η² | ANOVA/ANCOVA | .01 / .06 / .14 |
| Cohen's f | Multi-group | .10 / .25 / .40 |
| Odds ratio | Logistic regression | 1.5 / 2.5 / 4.3 |

### Multiple Comparison Corrections

- **Planned contrasts:** Bonferroni or Holm-Bonferroni
- **Post-hoc pairwise:** Tukey HSD (equal N) or Games-Howell (unequal N)
- **False Discovery Rate:** Benjamini-Hochberg when testing many effects
- **Do NOT apply correction** to orthogonal planned contrasts (reduces power unnecessarily)

### Experimental Reporting Requirements

- Report cell means, SDs, and N per condition
- Report exact p-values (not just < .05)
- Include balance/randomization table
- mediation in experiments: bootstrap CI (same as survey), but leverage experimental variation for identification

### Required Outputs (Experiments)

| Output | Content |
|--------|---------|
| T-bal: Randomization balance table | Demographics by condition, test statistics |
| T-manip: Manipulation check results | ANOVA/t-test for each manipulation |
| T-main: Main treatment effects | Coefficient, SE, p, d/η², 95% CI |
| T-mech: Mediation (if applicable) | Indirect effect, bootstrap CI |
| F-interact: Interaction plots | Simple slopes or marginal means by condition |

---

## Regression Model Standards

### OLS Diagnostics (Before Trusting Results)

| Check | Method | Red Flag |
|-------|--------|----------|
| Linearity | Residual plots, RESET test | Systematic pattern in residuals |
| Homoscedasticity | Breusch-Pagan, White test | p < .05 → use robust SE (HC1 or HC3) |
| Normality of residuals | Q-Q plot, Shapiro-Wilk | Severe skew → bootstrap SE |
| Multicollinearity | VIF | VIF > 5 (some say > 10) |
| Outlier influence | Cook's distance, leverage | D > 4/N or > 1 |
| Model specification | RESET test, added variable plots | Omitted non-linear terms |

### Standard Error Strategy

| Data Structure | SE Type | When |
|----------------|---------|------|
| Cross-sectional, homoscedastic | Classical OLS | Breusch-Pagan p > .05 |
| Cross-sectional, heteroscedastic | HC1 (White) robust | Breusch-Pagan p < .05 |
| Clustered (teams, classes) | Cluster-robust | ICC > .05 or design-based |
| Panel (repeated measures) | Cluster by entity + Driscoll-Kraay | T > N panels |
| Multilevel | Random effects variance components | ICC > .05 |

### Panel Data Standards

- **Hausman test:** FE vs. RE (p < .05 → FE preferred)
- **Fixed effects:** Report within-R², entity/time FE, clustered SE
- **Random effects:** Report overall/between/within R², GLS weights
- **Dynamic panel:** Arellano-Bond GMM for lagged DV (check Hansen J, AR(2))

### Multilevel Model Standards

- **ICC justification:** ICC > .05 justifies multilevel over OLS
- **Level specification:** Variables at correct level (Level 1 = individual, Level 2 = group)
- **Centering:** Group-mean centering for Level 1 effects; grand-mean for cross-level interactions
- **Random slopes:** Test if slope variance is significant before adding cross-level interactions

### Regression Reporting Requirements

- Report β (unstandardized), SE, p, standardized β, 95% CI
- Report R² and ΔR² for nested models
- Report F-statistic and overall model significance
- For panel: report N entities, T periods, total observations

---

## Cross-Cutting Standards (All Designs)

### Identification Framework

Every analysis step must address:
- [ ] Reverse causality
- [ ] Omitted variables
- [ ] Common source bias (survey) / demand characteristics (experiment)
- [ ] Endogeneity
- [ ] Alternative explanations

### Missing Data

- Flag variables with >15% missing
- Document handling method (FIML, MI, listwise deletion) with justification
- For experiments: report attrition by condition and test for differential attrition

### Power & Sample Size

| Design | Minimum | Recommended |
|--------|---------|-------------|
| Between-subjects experiment | 30/cell | 50+/cell for medium effects |
| CFA/SEM | 10:1 items-to-cases | 200+ total |
| Multilevel | 20 groups, 5/group | 30+ groups, 20+/group |
| Panel regression | T ≥ 3 | T ≥ 5, N ≥ 30 |
