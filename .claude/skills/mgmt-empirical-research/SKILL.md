---
name: mgmt-empirical-research
description: >
  8-step empirical research pipeline for management studies covering survey and
  experimental data. Use when the user asks about CFA/SEM, scale validation (EFA,
  construct validity, measurement invariance), mediation analysis (bootstrap CI,
  Hayes PROCESS), moderation (interaction effects, simple slopes, Johnson-Neyman),
  conditional process analysis (moderated mediation), common method bias (Harman's,
  ULMC), hypothesis testing, structural equation modeling, multilevel modeling,
  AMJ-style publication tables and figures, or conducting quantitative management
  research. Also triggers on mentions of survey data analysis, experimental data
  analysis, research design, identification strategy, or endogeneity in management
  contexts. Use this skill even if the user just says "analyze my survey data",
  "run CFA", "test mediation", or "validate my scale" — these all belong here.
version: 2.0.0
---

# Management Empirical Research Pipeline

End-to-end empirical analysis workflow for management research: survey data and experimental data, with construct validation, hypothesis testing, and AMJ-style publication output.

## Cross-Cutting: Identification Framework

**This lens applies to every step.** Without explicit identification thinking, the pipeline becomes a descriptive toolkit rather than a research framework.

| Concern | Where Addressed | Key Action |
|---------|----------------|------------|
| Reverse causality | Step 1, Step 6 | Temporal design, cross-lagged models, reverse model test |
| Omitted variables | Step 5, Step 6 | Theory-driven controls, alternative specs, Oster δ |
| Common source bias | Step 1, Step 4, Step 6 | Multi-source design, CMB tests, single-source sensitivity |
| Endogeneity | Step 6 | IV, Heckman, fixed effects (see also stata-regression) |
| Alternative explanations | Step 5, Step 6 | Competing models, nested model comparison |

See `references/identification-framework.md` for the full framework with code examples.

## Pipeline Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│ Step 1  Data Preparation & Design Tagging                           │
│ Step 2  Construct Development & Validation                          │
│ Step 3  Descriptive Statistics & Correlations                       │
│ Step 4  Model Diagnostics, Respecification & Bias Assessment       │
│ Step 5  Hypothesis Testing: Main → Mechanism → Boundary             │
│ Step 6  Robustness & Identification                                 │
│ Step 7  Further Analysis                                            │
│ Step 8  Publication Output (5 tables + 4 figures)                   │
└──────────────────────────────────────────────────────────────────────┘
```

| Step | Deliverable | Reference |
|------|-------------|-----------|
| 1 | Clean dataset + design tag + quality report | `references/step1-data-preparation.md` |
| 2 | Validated measurement model | `references/step2-construct-validation.md` |
| 3 | Table 1 (correlations, AVE, CR) | `references/step3-descriptive-statistics.md` |
| 4 | Diagnostics report + respecification log | `references/step4-diagnostics-bias.md` |
| 5 | Hypothesis results table | `references/step5-hypothesis-testing.md` |
| 6 | Robustness summary table | `references/step6-robustness.md` |
| 7 | Supplementary analysis results | `references/step7-further-analysis.md` |
| 8 | 5 tables + 4 figures | `references/step8-publication-output.md` |

---

## Step 1: Data Preparation & Design Tagging

Two tracks: **(a) Survey** and **(b) Experimental**.

**Survey track:** Import → missing data analysis (Little's MCAR, MICE) → response quality (straight-lining, speeders) → non-response bias (Armstrong & Overton) → multi-source matching.

**Experimental track:** Manipulation checks → randomization balance (t-tests on demographics) → attention check exclusions.

**Design tagging (mandatory):** Assign ONE tag — `cross-sectional` | `time-lagged` | `panel` | `multilevel` | `experimental`. This tag determines downstream branching.

```python
# Quick quality check
missing_pct = df.isnull().mean()
print(f"Variables >15% missing: {(missing_pct > .15).sum()}")
sl = df[items].std(axis=1) == 0
print(f"Straight-liners: {sl.sum()} ({sl.mean()*100:.1f}%)")
```

→ Full code and decision criteria: `references/step1-data-preparation.md`

---

## Step 2: Construct Development & Validation

### Branching Decision (at entry)

| Scale Status | Execute |
|---|---|
| **Established** (validated, used as-is) | B → C → D |
| **Adapted** (modified from existing) | B → C → D (emphasize D) |
| **New** (original development) | **A →** B → C → D |

**Stage A: EFA** — Only for NEW scales. Parallel analysis → oblimin rotation → item retention (loading >.50, cross-loading <.30). Use independent calibration sample.

**Stage B: CFA** — semopy or Mplus. MLR estimator. Fit: CFI >.95, RMSEA <.06, SRMR <.08. Use independent validation sample.

**Stage C: Reliability & Validity** — CR >.70, AVE >.50, HTMT <.85.

**Stage D: Measurement Invariance** — Configural → metric → scalar across groups. ΔCFI ≤ .010.

```python
# Quick CFA via semopy
from semopy import Model
model = Model('''
  f1 =~ item1 + item2 + item3 + item4
  f2 =~ item5 + item6 + item7 + item8
''')
result = model.fit(df)
```

→ Full EFA/CFA pipeline, Mplus syntax, AVE/CR/HTMT functions: `references/step2-construct-validation.md`

---

## Step 3: Descriptive Statistics & Correlations

Management Table 1: construct means, SDs, correlations, **AVE√ on diagonal** (Fornell-Larcker check), CR and alpha in bottom rows.

```python
# AVE on diagonal for Fornell-Larcker
for i, name in enumerate(constructs):
    ave_sqrt = np.sqrt(ave_values[i])
    # Place on diagonal instead of 1.00
```

Report scale ranges (theoretical vs. observed). If any correlation > .70, flag for VIF check in Step 4.

→ Full LaTeX template: `references/step3-descriptive-statistics.md`

---

## Step 4: Model Diagnostics, Respecification & Bias

This is about **model quality**, not assumptions. Normality is NOT a gatekeeper (MLR handles it).

**Check:** VIF < 5 | Mahalanobis outliers | CMB (Harman's, marker, ULMC) | Fit indices

**Model Respecification:** Review modification indices (MI > 3.84). Only free parameters with theoretical justification. Document every change in a respecification log.

**Model Building Sequence:**
- Model 0: Controls only
- Model 1: + main IVs
- Model 2: + mediators
- Model 3: + interactions

```python
# VIF check
from statsmodels.stats.outliers_influence import variance_inflation_factor
vif = pd.DataFrame({'VIF': [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]})
```

→ Full diagnostic functions, ULMC Mplus syntax, respecification log template: `references/step4-diagnostics-bias.md`

---

## Step 5: Hypothesis Testing

Three-stage ordered sequence:

### (a) Main Effects
Direct paths X→Y. Progressive model building (Model 0→1→2→3). Report coefficient, SE, p, standardized β, R², ΔR².

### (b) Mechanisms — Mediation
Bootstrap CI for indirect effect (5,000+ resamples). Know the concepts beyond "run PROCESS":
- **Inconsistent mediation**: indirect and direct effects in opposite signs — not a failure, reveals opposing mechanisms
- **Suppression effects**: adding mediator increases direct effect
- **Sequential mediation**: X→M1→M2→Y (multi-step chain)
- **Parallel vs. serial**: theory determines which to specify

```python
# Bootstrap mediation (simplified)
def bootstrap_mediation(df, x, m, y, controls, n_boot=5000):
    # ... resample, estimate a×b, return mean + 95% CI
    pass
# CI excludes zero → mediation established
```

### (c) Boundary Conditions — Moderation

| Path | Method | When |
|------|--------|------|
| Regression | Interaction + simple slopes + Johnson-Neyman | Composite scores, single-level |
| SEM | Latent interaction, multi-group SEM | Latent variables |
| Multilevel | Cross-level interaction (HLM) | Nested data, ICC >.05 |

→ Full bootstrap mediation code, three moderation paths, conditional process analysis: `references/step5-hypothesis-testing.md`

---

## Step 6: Robustness & Identification

Each robustness check ties to a specific identification concern (see cross-cutting framework):

- **Alternative specifications**: Progressive controls (no controls → demographics → full)
- **Competing models**: Reverse causality model, alternative mediator, non-linear
- **Endogeneity**: IV (stata-regression), Heckman, fixed effects (panel)
- **Subsample**: By expertise, data source, time period
- **CMB post-hoc**: ULMC-corrected vs. original
- **Latent vs. composite**: Compare scoring approaches

```python
# Coefficient stability across specifications
for spec_name, formula in specs.items():
    m = smf.ols(formula, data=df).fit()
    print(f"{spec_name}: b_X={m.params['X']:.3f}, p={m.pvalues['X']:.4f}")
```

→ Full robustness battery template, summary table format: `references/step6-robustness.md`

---

## Step 7: Further Analysis

- **Conditional process**: Index of moderated mediation, conditional indirect effects at moderator levels
- **Multi-group SEM**: Structural invariance after measurement invariance (Step 2D)
- **Effect sizes**: Cohen's f² (.02/.15/.35), κ² for indirect effects, standardized effects
- **Variance modeling** (thesis-specific): Quantile regression, location-scale model for heterogeneous effects
- **Post-hoc power**: Observed power analysis

→ Full code for each: `references/step7-further-analysis.md`

---

## Step 8: Publication Output

### 5 Required Tables
| Table | Content |
|-------|---------|
| T1 | Descriptive statistics, correlations, AVE√, CR |
| T2 | CFA factor loadings, reliability, validity |
| T3 | Measurement invariance test results |
| T4 | Structural model results (paths, R²) |
| T5 | Mediation / conditional process (indirect effects, bootstrap CIs) |

### 4 Required Figures
| Figure | Content |
|--------|---------|
| F1 | Research model (path diagram with hypotheses) |
| F2 | Structural model results (significant paths highlighted) |
| F3 | Interaction plots (simple slopes for moderation) |
| F4 | Indirect effect plot (forest plot of bootstrap CIs) |

Export: LaTeX booktabs + DOCX (tables), PDF vector + PNG ≥300dpi (figures).

→ Full LaTeX templates, graphviz path diagram, interaction plot code: `references/step8-publication-output.md`

---

## Related Skills

| Skill | Use When |
|-------|----------|
| mgmt-theory-builder | Building hypotheses and theoretical arguments |
| mgmt-lit-review | Literature search and gap identification |
| mgmt-qualitative-research | Grounded theory, interview coding, scale item generation |
| data-analysis-python | Basic OLS/logit regression, panel data, basic regression tables |
| stata-regression | Causal inference (IV, DID, PSM, Heckman) |
| mgmt-intro | Writing abstracts and introductions |
| econ-visualization | Publication-quality charts and graphs |

---

## Self-Evaluation Checklist

- [ ] Data cleaned and quality documented with design tag (Step 1)
- [ ] Measurement model validated: appropriate path (EFA→CFA) with acceptable fit (Step 2)
- [ ] Reliability (CR >.70) and validity (AVE >.50, HTMT <.85) established (Step 2)
- [ ] Table 1 complete with means, SDs, correlations, AVE√, CR (Step 3)
- [ ] Model diagnostics: VIF, CMB assessed with at least two methods (Step 4)
- [ ] Respecification decisions documented with theoretical rationale (Step 4)
- [ ] All hypotheses tested: main effects → mediation → moderation (Step 5)
- [ ] Indirect effects tested with bootstrap CI (not Sobel) (Step 5)
- [ ] Robustness checked with alternative specifications (Step 6)
- [ ] Identification concerns explicitly addressed (Step 6)
- [ ] Effect sizes reported (f², κ², standardized) (Step 7)
- [ ] All 5 tables and 4 figures produced (Step 8)

---

## Key References

- Hair, J. F., et al. (2019). Multivariate Data Analysis. 8th ed.
- Hayes, A. F. (2022). Introduction to Mediation, Moderation, and Conditional Process Analysis. 3rd ed.
- Podsakoff, P. M., et al. (2003). Common method biases in behavioral research. JAP, 88, 879-903.
- Fornell, C., & Larcker, D. F. (1981). Evaluating structural equation models. JMR, 18, 39-50.
- Henseler, J., et al. (2015). A new criterion for assessing discriminant validity. JAMS, 43, 115-135.
- Hu, L., & Bentler, P. M. (1999). Cutoff criteria for fit indexes. SEM, 6, 1-55.
- Chen, F. F. (2007). Sensitivity of goodness of fit indexes to lack of measurement invariance. SEM, 14, 464-504.
- Dorobantu, S., et al. (2024). The AMJ Management Research Canvas. AMJ.

---

## Gotchas

### Processing

| Issue | Solution |
|-------|----------|
| CFA fit looks great but items cross-load | Check modification indices; resist freeing parameters without theory |
| Bootstrap CI includes zero for indirect effect | Report the CI anyway; discuss as "directionally consistent" |
| Ignoring measurement error in composite scores | Use latent variables in SEM; composites introduce attenuation |
| VIF inflated by interaction term | Mean-center variables BEFORE creating interaction |
| Treating CMB as "assumption test" | CMB is a design/validity issue — address in design and assess statistically |

### Data/Input

| Issue | Solution |
|-------|----------|
| Likert treated as interval without justification | Check normality; use WLSMV if ordinal assumption needed |
| EFA and CFA on same sample | Always split or use independent samples |
| Missing data imputed without checking MCAR | Run Little's test first; choose method accordingly |

### Output/Export

| Issue | Solution |
|-------|----------|
| Table 1 diagonal shows 1.00 not AVE√ | Management convention: put √AVE on diagonal |
| Only reporting p-values without effect sizes | Journals increasingly require f², κ², standardized effects |
