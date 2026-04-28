# Academic Visualization Standards (AMJ Style)

**Applies when:** Creating charts, figures, or plots for management research papers or presentations.

## Grayscale-Only Policy

**ALL publication figures must be grayscale.** No color exceptions.

### Palette

| Name | Hex | Usage |
|------|-----|-------|
| black | #000000 | Primary series |
| dark_gray | #333333 | Second series |
| medium_gray | #666666 | Third series |
| light_gray | #999999 | Fourth series |
| pale_gray | #CCCCCC | Backgrounds/fills |

### Differentiation Rules

Series must be distinguished by **BOTH** line style AND markers, never color alone:

| Series | Line Style | Marker |
|--------|-----------|--------|
| 1st | solid (-) | circle (o) |
| 2nd | dashed (--) | square (s) |
| 3rd | dotted (:) | triangle (^) |
| 4th | dash-dot (-.) | diamond (D) |

### Bar Charts

- Hatch patterns: `["", "//", "\\", "xx", ".."]`
- `edgecolor='black'` always
- No color fills

### Heatmaps

- Sequential gray colormaps only (e.g., `Greys`)

## Export Standards

| Property | Requirement |
|----------|-------------|
| DPI | ≥ 300 |
| Background | Transparent |
| Format | PDF for LaTeX, PNG for slides |
| Figure titles | **None** — journals use captions below |

## Font & Style

- **Font:** Times New Roman (serif)
- **Grid:** Light (alpha=0.3), minimal chart junk
- **Legend:** Inside plot area when possible, no box shadow
- **Axis labels:** Include units, descriptive names

## Python Configuration

```python
import matplotlib.pyplot as plt
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman'],
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.transparent': True,
    'savefig.bbox': 'tight',
})
```

## R Configuration

```r
amj_grays  <- c("#000000", "#333333", "#666666", "#999999", "#CCCCCC")
amj_lines  <- c("solid", "dashed", "dotted", "dotdash")
amj_shapes <- c(16, 15, 17, 18)  # circle, square, triangle, diamond
```
