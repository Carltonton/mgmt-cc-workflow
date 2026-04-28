---
name: visualization
description: >
  Create publication-quality charts and graphs for management journal papers
  (AMJ, AMR, SMJ, ASQ) using AMJ-style black/white/gray palette with line-style
  and marker differentiation. Use this skill whenever generating any figure, chart,
  plot, or visualization — including survival curves, coefficient plots, bar charts,
  scatter plots, heatmaps, event studies, state transition diagrams, or descriptive
  EDA plots. Also use when the user mentions matplotlib, seaborn, ggplot2, figures,
  charts, plots, or asks to visualize data. Do NOT use for slide design or layout.
version: 2.0.0
tags:
  - visualization
  - matplotlib
  - seaborn
  - ggplot2
  - grayscale
---

# Visualization (AMJ Management Journal Style)

## Purpose

Generate publication-quality figures for management journal papers using **black/white/gray** styling. Series are differentiated by line style + marker, not by color — matching AMJ print requirements.

## AMJ Style Rules

These are non-negotiable for journal submission:

1. **Grayscale only** — no color in figures
2. **Differentiate series** by line style (solid/dashed/dotted/dash-dot) + markers (circle/square/triangle/diamond), never by color alone
3. **No figure titles on the plot** — journals place captions below, not titles on figures
4. **Minimal chart junk** — light grid, clean axes, no decorative backgrounds
5. **Bar charts** use gray fills with hatch patterns for distinction
6. **Heatmaps** use sequential gray colormaps (`Greys`)

## Style Constants

Reference these when generating code. They are also defined in `scripts/python/config.py`.

### Grayscale Palette

| Name | Hex | Usage |
|------|-----|-------|
| black | `#000000` | Primary series, axes |
| dark_gray | `#333333` | Second series |
| medium_gray | `#666666` | Third series |
| light_gray | `#999999` | Fourth series |
| pale_gray | `#CCCCCC` | Fifth series, backgrounds |

### Line Styles

| Style | Matplotlib | ggplot2 | Use for |
|-------|-----------|---------|---------|
| Solid | `-` | `solid` | Primary/baseline series |
| Dashed | `--` | `dashed` | Second series |
| Dotted | `:` | `dotted` | Third series |
| Dash-dot | `-.` | `dotdash` | Fourth series |

### Markers

| Marker | Matplotlib | ggplot2 shape | Use for |
|--------|-----------|---------------|---------|
| Circle | `o` | 16 | Group 1 |
| Square | `s` | 15 | Group 2 |
| Triangle | `^` | 17 | Group 3 |
| Diamond | `D` | 18 | Group 4 |

### Hatch Patterns (Bar Charts)

`["", "//", "\\\\", "xx", ".."]`

## Instructions

### Step 1: Ask the user

Before generating code, clarify:

- What data and key variables?
- Chart type (line, bar, scatter, event study, heatmap, survival curve)?
- Output format (PDF preferred for LaTeX, PNG for slides) and dimensions?

### Step 2: Generate the code

When writing visualization code:

1. Import style constants from `scripts/python/config.py` when in the project repo, otherwise define them inline
2. Set up the grayscale color cycle in matplotlib rcParams
3. Differentiate every multi-series plot by **both** gray shade AND line style + marker
4. Add `edgecolor='black'` to bar charts so gray fills are distinguishable
5. Export at 300 DPI with transparent background
6. Omit figure titles — use axis labels only

### Step 3: Verify

After generating, confirm:

- No color is used (only black/white/gray hex codes)
- Each series has a distinct line style or marker
- Bar charts use hatch patterns
- Figure has no title (axis labels only)

## Example: Python (matplotlib/seaborn)

```python
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

# AMJ style constants
GRAYSCALE = ["#000000", "#333333", "#666666", "#999999", "#CCCCCC"]
LINES = ["-", "--", ":", "-."]
MARKS = ["o", "s", "^", "D"]

sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.2)
plt.rcParams.update({
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.transparent": True,
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
    "axes.prop_cycle": mpl.cycler(color=GRAYSCALE),
})

df = pd.read_csv("data.csv")
fig, ax = plt.subplots(figsize=(7, 4))

for i, group in enumerate(df["group"].unique()):
    subset = df[df["group"] == group]
    ax.plot(
        subset["x"], subset["y"],
        label=group,
        color=GRAYSCALE[i % len(GRAYSCALE)],
        linestyle=LINES[i % len(LINES)],
        marker=MARKS[i % len(MARKS)],
        markevery=5,
        linewidth=1.5,
        markersize=5,
    )

ax.set_xlabel("X Label")
ax.set_ylabel("Y Label")
ax.legend(loc="lower right")
ax.grid(True, alpha=0.3)
fig.savefig(Path("output/figures/figure.png"), dpi=300, transparent=True)
plt.close()
```

## Example: R (ggplot2)

```r
library(tidyverse)

amj_grays  <- c("#000000", "#333333", "#666666", "#999999", "#CCCCCC")
amj_lines  <- c("solid", "dashed", "dotted", "dotdash")
amj_shapes <- c(16, 15, 17, 18)

df <- read_csv("data.csv")

ggplot(df, aes(x = x, y = y, linetype = group, shape = group)) +
  geom_line(linewidth = 0.8) +
  geom_point(size = 2) +
  scale_linetype_manual(values = amj_lines) +
  scale_shape_manual(values = amj_shapes) +
  labs(x = "X Label", y = "Y Label", linetype = "Group", shape = "Group") +
  theme_minimal(base_size = 12) +
  theme(
    legend.position = "bottom",
    panel.grid.minor = element_blank(),
    axis.text = element_text(color = "black")
  )

ggsave("figures/figure.pdf", width = 7, height = 4, dpi = 300)
```

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Using color to differentiate series | Use line style + marker instead |
| Adding a figure title | Remove — journals use captions below |
| Overlapping lines indistinguishable | Combine different gray + different line style + different marker |
| Bar chart bars hard to tell apart | Add hatch patterns + `edgecolor='black'` |
| Heatmap with color gradient | Use `cmap='Greys'` (Python) or `scale_fill_gradient(low="white", high="black")` (R) |
| Seaborn overriding grayscale palette | Set `sns.set_palette(GRAYSCALE)` or use `axes.prop_cycle` |

## References

- AMJ Author Guidelines: https://aom.org/research/publishing/amj
- ggplot2: https://ggplot2.tidyverse.org/
- Tufte (2001) *The Visual Display of Quantitative Information*

## Changelog

### v2.0.0 (2026-04-28)

- Switched to AMJ management journal style: grayscale palette, line style + marker differentiation
- Removed all color palettes
- Added hatch patterns for bar charts
- Added heatmap guidance
- Renamed from `econ-visualization` to `visualization`

### v1.0.0

- Initial release