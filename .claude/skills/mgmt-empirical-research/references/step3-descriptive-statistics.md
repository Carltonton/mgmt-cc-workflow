# Step 3: Descriptive Statistics & Correlations

## Goal
Produce the Management Table 1: construct-level means, SDs, correlations with AVE√ on diagonal and CR/alpha in bottom rows.

## Construct Score Computation

Before computing correlations, create construct-level scores. Two approaches:

### Latent Factor Scores (Preferred for new/adapted scales)
```python
# After CFA (Step 2), extract factor scores
from semopy import Model

model = Model(cfa_spec)
result = model.fit(df)
factor_scores = model.predict_factors(df)  # If supported
# Otherwise use regression-based factor scores from factor_analyzer
```

### Composite Means (Acceptable for established scales)
```python
# Simple mean of items for each construct
constructs = {
    'X': ['x1', 'x2', 'x3', 'x4'],
    'M1': ['m1_1', 'm1_2', 'm1_3'],
    'M2': ['m2_1', 'm2_2', 'm2_3'],
    'Y1': ['y1_1', 'y1_2', 'y1_3'],
    'Y2': ['y2_1', 'y2_2', 'y2_3'],
}

for name, items in constructs.items():
    df[name] = df[items].mean(axis=1)
```

## Correlation Matrix with Significance

```python
import numpy as np
from scipy.stats import pearsonr

construct_names = list(constructs.keys())
n = len(construct_names)
corr_matrix = np.zeros((n, n))
p_matrix = np.zeros((n, n))

for i, c1 in enumerate(construct_names):
    for j, c2 in enumerate(construct_names):
        r, p = pearsonr(df[c1], df[c2])
        corr_matrix[i, j] = r
        p_matrix[i, j] = p

# Significance stars
def stars(p):
    if p < .001: return '***'
    elif p < .01: return '**'
    elif p < .05: return '*'
    else: return ''
```

## Table 1 LaTeX Template

Management Table 1 format: means and SDs in first columns, correlation matrix below diagonal, AVE√ on diagonal (bold), significance stars.

```python
def generate_table1_latex(construct_names, means, sds, corr_matrix, p_matrix, ave_values, cr_values, alpha_values):
    """Generate LaTeX booktabs Table 1."""
    n = len(construct_names)
    lines = []
    lines.append(r'\begin{table}[htbp]')
    lines.append(r'\caption{Descriptive Statistics, Correlations, and Reliability}')
    lines.append(r'\label{tab:descriptive}')
    lines.append(r'\begin{tabular}{lccccccc}')
    lines.append(r'\toprule')
    
    # Header row
    header = 'Variable & $M$ & $SD$ & ' + ' & '.join(construct_names) + r' \\'
    lines.append(header)
    lines.append(r'\midrule')
    
    # Data rows
    for i, name in enumerate(construct_names):
        row = f'{name} & {means[i]:.2f} & {sds[i]:.2f}'
        for j in range(n):
            if j < i:
                # Correlation with stars
                sig = stars(p_matrix[i, j])
                row += f' & {corr_matrix[i,j]:.2f}{sig}'
            elif j == i:
                # AVE√ on diagonal (bold)
                row += f' & \\textbf{{{np.sqrt(ave_values[i]):.2f}}}'
            else:
                row += ' & '
        row += r' \\'
        lines.append(row)
    
    lines.append(r'\midrule')
    
    # Reliability row
    cr_row = 'CR & & & ' + ' & '.join([f'{cr:.2f}' for cr in cr_values]) + r' \\'
    lines.append(cr_row)
    alpha_row = r'$\alpha$ & & & ' + ' & '.join([f'{a:.2f}' for a in alpha_values]) + r' \\'
    lines.append(alpha_row)
    
    lines.append(r'\bottomrule')
    lines.append(r'\end{tabular}')
    lines.append(r'\begin{tablenotes}')
    lines.append(r'\small')
    lines.append(r'\item $n$ = XXX. Diagonal elements (bold) are square roots of AVE.')
    lines.append(r'\item Off-diagonal elements are correlations. * $p$ < .05, ** $p$ < .01, *** $p$ < .001.')
    lines.append(r'\item CR = Composite Reliability, $\alpha$ = Cronbach\'s alpha.')
    lines.append(r'\end{tablenotes}')
    lines.append(r'\end{table}')
    
    return '\n'.join(lines)
```

## Scale Range Reporting

Report both theoretical and observed ranges for each construct:

```python
for name, items in constructs.items():
    theoretical_min = 1  # e.g., 1 for 5-point Likert
    theoretical_max = 5
    observed_min = df[name].min()
    observed_max = df[name].max()
    print(f"{name}: {observed_min:.2f}-{observed_max:.2f} (theoretical: {theoretical_min}-{theoretical_max})")
```

## Key Checks

- AVE√ on diagonal should be LARGER than off-diagonal correlations → Fornell-Larcker criterion met
- All correlations < .85 → no multicollinearity concern (confirmed in Step 4 with VIF)
- Report N (may differ from total sample if listwise deletion applied)
- If any correlation > .70, check VIF in Step 4

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Reporting item-level correlations instead of construct-level | Compute construct scores first, then correlate |
| Forgetting AVE√ on diagonal | Management convention: put sqrt(AVE) on diagonal for Fornell-Larcker visual check |
| Not reporting scale ranges | Always show theoretical min-max vs. observed to demonstrate adequate variance |
| Using N from full sample when using listwise deletion | Report actual N used in correlation analysis |
