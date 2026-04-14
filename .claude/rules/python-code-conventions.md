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
def calculate_reliability(
    data: pd.DataFrame,
    items: list[str],
    method: str = "cronbach"
) -> float:
    """Calculate internal consistency reliability for scale items.

    Args:
        data: Input dataframe with survey responses
        items: Column names for scale items
        method: Reliability method ("cronbach" or "omega")

    Returns:
        Reliability coefficient (0-1)

    Raises:
        ValueError: If required columns are missing
    """
    # Implementation here
    return reliability
```

## 3. Domain Correctness

<!-- Customize for your field's known pitfalls -->
- Verify numerical implementations match theoretical formulas
- Check for floating-point precision issues in probability calculations
- Validate statistical assumptions (normality, independence, measurement invariance)
- Document model assumptions in docstrings

## 4. Visual Identity

```python
# --- Research palette for publication figures ---
PALETTE = {
    "primary_blue": "#012169",
    "primary_gold": "#f2a900",
    "accent_gray": "#525252",
    "positive_green": "#15803d",
    "negative_red": "#b91c1c",
}
```

### Matplotlib Style Configuration
```python
import matplotlib.pyplot as plt
import seaborn as sns

# Set publication-quality defaults
plt.style.use("seaborn-v0_8-whitegrid")
sns.set_context("paper", font_scale=1.2)

# Custom figure style
def setup_figure_style():
    """Configure matplotlib for publication-quality figures."""
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
   # Composite reliability: CR = (sum λ)^2 / [(sum λ)^2 + sum δ]
   composite_reliability = (sum_loadings ** 2) / (sum_loadings ** 2 + sum_errors)
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
assert df["item1"].min() >= 1, "Values below scale minimum found"
assert df["item1"].max() <= 7, "Values above scale maximum found"

# Log key statistics
print(f"Sample size: {len(df)}")
print(f"Missing rate: {df.isnull().mean().mean():.2%}")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
```
