# Step 8: Publication Output

Every analysis MUST produce all 5 required tables and 4 required figures. Export to LaTeX (booktabs) + DOCX for tables, PDF (vector) + PNG (≥300 dpi) for figures.

---

## Required Tables

### T1: Descriptive Statistics, Correlations, AVE√, CR
See `step3-descriptive-statistics.md` for full LaTeX template.

### T2: CFA Factor Loadings, Reliability, Validity

```latex
\begin{table}[htbp]
\caption{Confirmatory Factor Analysis Results}
\label{tab:cfa}
\begin{tabular}{llcccccc}
\toprule
Construct & Item & Loading & SE & $t$ & AVE & CR & $\alpha$ \\
\midrule
\multirow{4}{*}{Factor 1}
  & item1 & .82 & .03 & 27.3 & \multirow{4}{*}{.64} & \multirow{4}{*}{.88} & \multirow{4}{*}{.87} \\
  & item2 & .79 & .03 & 24.1 & & & \\
  & item3 & .81 & .03 & 26.0 & & & \\
  & item4 & .77 & .04 & 22.1 & & & \\
\midrule
\multicolumn{8}{l}{Fit: $\chi^2$/df = 2.1, CFI = .96, TLI = .95, RMSEA = .04 [.03, .05], SRMR = .03} \\
\bottomrule
\end{tabular}
\end{table}
```

### T3: Measurement Invariance Tests

```latex
\begin{table}[htbp]
\caption{Measurement Invariance Tests}
\label{tab:invariance}
\begin{tabular}{lccccc}
\toprule
Model & $\chi^2$ & df & CFI & $\Delta$CFI & Decision \\
\midrule
Configural & 234.5 & 102 & .952 & --- & Baseline \\
Metric & 256.3 & 114 & .947 & .005 & Supported \\
Scalar & 289.1 & 126 & .938 & .009 & Supported \\
\bottomrule
\end{tabular}
\end{table}
```

### T4: Structural Model Results

```latex
\begin{table}[htbp]
\caption{Structural Model Results}
\label{tab:structural}
\begin{tabular}{lcccc}
\toprule
Hypothesis & Path & $\beta$ & $t$ & Result \\
\midrule
H1a & X $\to$ Y1 & .32*** & 4.85 & Supported \\
H1b & X $\to$ Y2 & .21**  & 3.12 & Supported \\
H2a & X $\to$ M1 $\to$ Y1 & .15  & --- & Supported$^a$ \\
H2b & X $\to$ M2 $\to$ Y2 & .09  & --- & Supported$^a$ \\
H3  & X $\times$ Expertise $\to$ Y2 & .18** & 2.95 & Supported \\
\midrule
\multicolumn{5}{l}{\small $R^2$: M1 = .28, M2 = .22, Y1 = .41, Y2 = .35} \\
\multicolumn{5}{l}{\small $^a$ Indirect effect tested via bootstrap 95\% CI} \\
\bottomrule
\end{tabular}
\end{table}
```

### T5: Mediation / Conditional Process Results

```latex
\begin{table}[htbp]
\caption{Mediation and Conditional Process Analysis}
\label{tab:mediation}
\begin{tabular}{lcccc}
\toprule
Effect & Estimate & SE & 95\% CI & Conclusion \\
\midrule
\multicolumn{5}{l}{\textit{Mediation (H2)}} \\
X $\to$ M1 $\to$ Y1 (indirect) & .15 & .04 & [.08, .22] & Significant \\
X $\to$ Y1 (direct) & .17 & .05 & --- & Partial mediation \\
\midrule
\multicolumn{5}{l}{\textit{Moderated Mediation (H3)}} \\
Index of moderated mediation & .06 & .02 & [.02, .11] & Significant \\
Conditional at Low Expertise & .08 & .03 & [.02, .15] & Significant \\
Conditional at High Expertise & .22 & .05 & [.12, .33] & Significant \\
\bottomrule
\end{tabular}
\end{table}
```

---

## Required Figures

### F1: Research Model (Path Diagram)
Use graphviz or matplotlib to draw the theoretical model with hypotheses labeled.

```python
import graphviz

dot = graphviz.Digraph(comment='Research Model')
dot.attr(rankdir='LR', size='8,4', dpi='300')

# Nodes
dot.node('X', 'Personality\nRefinement (X)')
dot.node('M1', 'Affect\nActivation (M1)')
dot.node('M2', 'Intent\nInference (M2)')
dot.node('Y1', 'Relational\nQuality (Y1)')
dot.node('Y2', 'Behavioral\nStrategy (Y2)')

# Edges with hypotheses
dot.edge('X', 'M1', label='a1')
dot.edge('M1', 'Y1', label='b1')
dot.edge('X', 'Y1', label="c'1")
dot.edge('X', 'M2', label='a2')
dot.edge('M2', 'Y2', label='b2')
dot.edge('X', 'Y2', label="c'2")

dot.render('figures/fig1_research_model', format='pdf', cleanup=True)
dot.render('figures/fig1_research_model', format='png', cleanup=True)
```

### F2: Structural Model Results
Same path diagram but with standardized coefficients and significance stars overlay. Highlight significant paths in a distinct color.

### F3: Interaction Plots (Moderation)
```python
import matplotlib.pyplot as plt
import numpy as np

def plot_interaction(x_range, b_x, b_w, b_xw, w_low, w_high, x_label, y_label, w_label):
    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)
    x = np.linspace(x_range[0], x_range[1], 100)

    for w_val, label, ls in [(w_low, f'Low {w_label}', '--'), (w_high, f'High {w_label}', '-')]:
        y = (b_x + b_xw * w_val) * x + b_w * w_val
        ax.plot(x, y, ls, linewidth=2, label=label)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.legend()
    fig.tight_layout()
    fig.savefig('figures/fig3_interaction.pdf')
    fig.savefig('figures/fig3_interaction.png', dpi=300)
```

### F4: Indirect Effect Plot (Mediation Visualization)
Forest plot showing bootstrap CIs for each indirect effect path.

```python
def plot_indirect_effects(effects, labels, ci_low, ci_high, filename='fig4_indirect'):
    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)
    y_pos = range(len(effects))

    ax.errorbar(effects, y_pos,
                xerr=[np.array(effects) - np.array(ci_low),
                       np.array(ci_high) - np.array(effects)],
                fmt='o', markersize=6, capsize=4, linewidth=1.5)

    ax.axvline(x=0, color='grey', linestyle=':', linewidth=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.set_xlabel('Indirect Effect (Bootstrap 95% CI)')
    fig.tight_layout()
    fig.savefig(f'figures/{filename}.pdf')
    fig.savefig(f'figures/{filename}.png', dpi=300)
```

---

## Export Conventions

| Output | Format | Specification |
|--------|--------|--------------|
| Tables | LaTeX | booktabs package, no vertical lines |
| Tables | DOCX | Via python-docx for reviewers who prefer Word |
| Figures | PDF | Vector format, no rasterization |
| Figures | PNG | ≥ 300 dpi, transparent background |
| All | Naming | `tables/table{N}_{description}.{ext}`, `figures/fig{N}_{description}.{ext}` |

---

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Tables without fit indices | Always include model fit in T2 and T4 |
| Figures at 72 dpi | Minimum 300 dpi for journal submission |
| Missing significance stars convention | Define: * p < .05, ** p < .01, *** p < .001 in table notes |
| Not reporting R² for each DV | Report R² for every endogenous variable |
| Forest plot without zero reference line | Always include vertical line at zero for indirect effects |
