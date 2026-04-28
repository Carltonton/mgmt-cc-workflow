---
paths:
  - "**/*.py"
  - "scripts/**/*.py"
  - "scripts/python/**/*.py"
---

# Python Code Standards

**Standard:** Production research code quality - PEP 8 + reproducibility

---

## 1. Reproducibility

- Seeds set ONCE at top of script using YYYYMMDD format
- All imports at top (standard library first, then third-party, then local)
- All paths relative to repository root using `pathlib.Path`
- Create output directories with `Path.mkdir(parents=True, exist_ok=True)`

```python
# Reproducibility setup
SEED = 20260301  # YYYYMMDD format
np.random.seed(SEED)
random.seed(SEED)
if torch_available:
    torch.manual_seed(SEED)
```

## 2. Function Design

- `snake_case` naming, verb-noun pattern
- Type hints for all function signatures (PEP 484)
- Google-style or NumPy-style docstrings
- Default parameters, no magic numbers
- Return type hints, explicit return statements

```python
def calculate_hazard_rate(
    data: pd.DataFrame,
    time_col: str = "tenure",
    event_col: str = "churned"
) -> pd.Series:
    """Calculate hazard rate for subscription data.

    Args:
        data: Input dataframe with subscription records
        time_col: Column name for time/tenure variable
        event_col: Column name for churn event indicator

    Returns:
        Series containing hazard rates by time period

    Raises:
        ValueError: If required columns are missing
    """
    # Implementation here
    return hazard_rates
```

## 3. Domain Correctness

<!-- Customize for your field's known pitfalls -->
- Verify numerical implementations match theoretical formulas
- Check for floating-point precision issues in probability calculations
- Validate survival analysis assumptions (censoring, independence)
- Document model assumptions in docstrings

## 4. Visual Identity (AMJ Management Journal Style)

```python
# --- AMJ-style grayscale palette ---
PALETTE = {
    "black": "#000000",
    "dark_gray": "#333333",
    "medium_gray": "#666666",
    "light_gray": "#999999",
    "pale_gray": "#CCCCCC",
}

# Line styles for series differentiation
LINE_STYLES = {"solid": "-", "dashed": "--", "dotted": ":", "dashdot": "-."}

# Markers for group differentiation
MARKERS = {"circle": "o", "square": "s", "triangle": "^", "diamond": "D"}

# Hatch patterns for bar charts
HATCHES = ["", "//", "\\\\", "xx", ".."]
```

### AMJ Figure Rules
1. **No color** — use black/white/gray only (journal print requirement)
2. **Differentiate series** by line style + marker, not by color
3. **No figure titles** — AMJ places captions below, not titles on figures
4. **Minimal chart junk** — light grid, clean axes

### Matplotlib Style Configuration
```python
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

GRAYSCALE_CYCLE = ["#000000", "#333333", "#666666", "#999999", "#CCCCCC"]

plt.style.use("seaborn-v0_8-whitegrid")
sns.set_context("paper", font_scale=1.2)

plt.rcParams.update({
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.transparent": True,
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
    "axes.labelsize": 12,
    "axes.titlesize": 14,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "axes.prop_cycle": mpl.cycler(color=GRAYSCALE_CYCLE),
})
```

### Figure Saving
```python
# Save with transparent background for LaTeX
fig.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight",
    transparent=True,
    format="png"
)
```

## 5. Data Persistence Pattern

**Heavy computations saved as Parquet/CSV/Pickle; scripts load pre-computed data.**

```python
import pandas as pd
import pickle
from pathlib import Path

# Save processed data
processed_path = Path("output/tables/table_name.parquet")
df.to_parquet(processed_path, index=False)

# Save model artifacts
model_path = Path("output/models/model.pkl")
with open(model_path, "wb") as f:
    pickle.dump(model, f)

# Save figures
fig_path = Path("output/figures/figure_name.png")
fig.savefig(fig_path, dpi=300, transparent=True)
```

## 6. Common Pitfalls

| Pitfall | Impact | Prevention |
|---------|--------|------------|
| Not setting seeds | Non-reproducible results | Set seeds at top of every script |
| Hardcoded paths | Breaks on other machines | Use `pathlib.Path` with relative paths |
| Missing type hints | Harder to debug/maintain | Add type hints to all functions |
| Not using virtual environment | Dependency conflicts | Always use `.venv` |
| Forgetting `transparent=True` | White boxes in LaTeX | Always include in `savefig()` |
| Pandas SettingWithCopy warning | Silent bugs | Use `.copy()` when creating subsets |
| Not handling missing data | Biased estimates | Explicitly handle NaN/NA values |

## 7. Pandas Best Practices

```python
# Use pathlib for paths
from pathlib import Path
DATA_DIR = Path("data/processed")
output_path = DATA_DIR / "processed_data.parquet"

# Use context managers for file operations
with open(output_path, "wb") as f:
    pickle.dump(data, f)

# Avoid chained assignment - use .loc[]
df.loc[df["column"] > threshold, "new_column"] = value

# Use .copy() to avoid SettingWithCopyWarning
df_subset = df[df["condition"]].copy()

# Use categorical dtype for low-cardinality strings
df["category_column"] = df["category_column"].astype("category")
```

## 8. Jupyter Notebook Conventions

```python
# Cell 1: Imports and setup
%load_ext autoreload
%autoreload 2
%matplotlib inline

# Cell 2: Configuration
SEED = 20260301
np.random.seed(SEED)

# Cell 3: Load data
# ... load and display basic info

# Cell 4+: Analysis
# ... exploratory analysis, modeling, etc.
```

## 9. Line Length & Mathematical Exceptions

**Standard:** Keep lines <= 100 characters (PEP 8).

**Exception: Mathematical Formulas** -- lines may exceed 100 chars **if and only if:**

1. Breaking the line would harm readability of the math
2. An inline comment explains the mathematical operation:
   ```python
   # Hazard function: h(t) = f(t) / S(t), ratio of density to survival
   hazard_rate = density_func(t) / survival_func(t)
   ```
3. The line is in a numerically intensive section (optimization loops, estimation routines)

## 10. Code Quality Checklist

```
[ ] Imports at top (stdlib, third-party, local)
[ ] Seeds set once at top
[ ] All paths relative using pathlib
[ ] Functions have type hints
[ ] Functions have docstrings
[ ] Figures: transparent bg, explicit dpi (300)
[ ] Heavy computations saved to disk
[ ] Comments explain WHY not WHAT
[ ] No hardcoded values or paths
[ ] Virtual environment activated
```

## 11. Environment Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Export environment (for reproducibility)
pip freeze > requirements.lock
```

## 12. Testing and Validation

```python
# Validate assumptions
assert not df.isnull().any().any(), "Data contains missing values"
assert df["tenure"].min() >= 0, "Negative tenure values found"
assert df["churned"].isin([0, 1]).all(), "Invalid churn indicator"

# Log key statistics
print(f"Sample size: {len(df)}")
print(f"Churn rate: {df['churned'].mean():.2%}")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
```
