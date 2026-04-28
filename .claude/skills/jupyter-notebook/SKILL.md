---
name: jupyter-notebook
description: Use when creating or editing Jupyter notebooks. All tunable parameters go in the first code cell; code is self-contained with no external imports.
---

# Jupyter Notebook Skill

## When to Use

- Creating a new `.ipynb` notebook
- Editing or refactoring an existing notebook
- Converting scripts into structured notebooks

## Self-Containment Rule

No imports from project `.py` files — notebooks run in environments where module paths are unavailable.

- ❌ `from scripts.python.module import function`
- ✅ Standard library and third-party packages only (`pandas`, `numpy`, `sklearn`, etc.)
- ✅ Define helper functions inside the notebook

## Cell Structure

### Cell 0 — Markdown Header

State purpose, inputs, outputs, date.

### Cell 1 — Environment Setup + All Tunable Parameters

Every tunable parameter lives here. Later cells **reference, never define**.

```python
# ============================================================================
# ENVIRONMENT SETUP & CENTRALIZED PARAMETERS
# ============================================================================

import warnings
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore')

# ============================================================================
# 📌 ALL PARAMETERS
# ============================================================================

# --- Reproducibility ---
RANDOM_SEED = 20260303
np.random.seed(RANDOM_SEED)

# --- Paths ---
DATA_PATH   = 'data/raw/...'
OUTPUT_PATH = 'data/processed/...'

# --- Analysis ---
SAMPLE_FRACTION = 0.05
CHUNK_SIZE      = 50000

# --- Visualization ---
COLOR_PALETTE = {
    "blue":  "#0072B2",
    "gold":  "#D55E00",
    "green": "#009E73",
    "pink":  "#CC79A7",
}
sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.2)

print(f"Seed: {RANDOM_SEED}")
print(f"Data: {DATA_PATH}")
```

### What Goes Where

| Cell 1 (parameters) ✅ | Later cells (logic) ❌ |
|---|---|
| File paths, output paths | Column name lists (STATIC_COLS, EXCLUDE_COLS) |
| Random seed | Data processing logic (agg_dict, impute rules) |
| Sample fraction, chunk size | Dynamically derived variables (FEATURE_COLS) |
| Econometric/ML params (caliper, bootstrap, alpha) | Intermediate computation results |
| Color palette, plot style | Function-local variables |

**Rule of thumb**: Would changing this value require re-running the whole notebook? If yes → Cell 1.

### Cell 2+ — Analysis Logic

One step per code cell. Use markdown cells to state purpose and expected output.

```python
# ❌ Wrong: defining a parameter in a logic cell
CONSOLIDATE_EVERY = 100

# ✅ Correct: reference the centralized parameter
for i in range(CONSOLIDATE_EVERY):
    ...
```

## Workflow

1. **Choose type**: `experiment` (exploratory analysis) or `tutorial` (teaching demo)
2. **Scaffold from template**:
   ```bash
   python .claude/skills/jupyter-notebook/scripts/new_notebook.py \
     --kind experiment --title "Churn Analysis" --out scripts/python/
   ```
3. **Fill content** following the Cell Structure above
4. **Validate**: run top-to-bottom, check outputs

## Templates & Scripts

- Templates: `assets/experiment-template.ipynb`, `assets/tutorial-template.ipynb`
- Generator: `scripts/new_notebook.py`
- References: `references/` directory

## Quality Checklist

- [ ] Cell 1 contains all tunable parameters
- [ ] No new parameters defined in later cells
- [ ] No imports from project `.py` files
- [ ] Runs top-to-bottom without hidden state
- [ ] Outputs are concise (short summaries over verbose dumps)
