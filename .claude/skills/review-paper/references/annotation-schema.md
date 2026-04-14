# Annotation Schema: Per-Sentence Logic Annotation

## Fields

Each sentence receives 4 annotation fields:

### 1. `logic_action` — Discourse Function

What logical role the sentence plays in the argument.

| Value | Meaning | Default? |
|-------|---------|----------|
| `define` | Introduces or defines a concept/term | |
| `transition` | Shifts direction or connects to a new sub-topic | |
| `progression` | Advances the argument with new information | **Yes** |
| `contrast` | Presents opposing or differing view | |
| `concession` | Acknowledges a counter-point before rebuttal | |
| `causation` | States cause-effect relationship | |
| `comparison` | Draws parallel between two things | |
| `example` | Provides illustrative instance | |
| `qualification` | Narrows or conditions a claim | |
| `summary` | Recaps or wraps up a line of argument | |

**Detection:** Use connector words and discourse markers (see `logic-action-rules.md`). If no clear connector is present, default to `progression`.

---

### 2. `targets` — Intra-Paragraph Role

The sentence's structural role within its paragraph.

| Value | When Applied |
|-------|-------------|
| `opening·main-claim` | First sentence that states the paragraph's topic/claim |
| `internal-flow·follows[X]` | Subsequent sentences; `[X]` = previous sentence's `logic_action` |
| `closing·wrap-up` | Last sentence that summarizes or transitions out |

**Auto-detection rules:**
- Sentence position 1 in paragraph → `opening·main-claim`
- Sentence position N (not last) → `internal-flow·follows[logic_action of sentence N-1]`
- Last sentence + contains summary/conclusion connector → `closing·wrap-up`
- Last sentence + no summary connector → `internal-flow·follows[logic_action of sentence N-1]`

---

### 3. `evidence_kind` — Evidence Type

What kind of backing the sentence relies on.

| Value | Detection Signals |
|-------|------------------|
| `literature` | Citation present: (Author, Year), [N], \cite{}, footnotes with sources |
| `data` | Statistics, percentages, N=, p<, confidence intervals, regression coefficients |
| `case` | Named organizations, specific incidents, case descriptions, vignettes |
| `theory` | References to models, frameworks, theoretical constructs, mechanisms |
| `none` | No evidence; proceeds from reasoning, assertion, or logical deduction |

---

### 4. `certainty` — Tone Strength

How strongly the claim is stated.

| Value | Detection Signals |
|-------|------------------|
| `strong` | "demonstrates", "proves", "clearly", "must", "will", "establishes" |
| `moderate` | "suggests", "indicates", "shows", "finds", "supports" |
| `qualified` | "may", "might", "could", "appears to", "seems to", "it is possible that" |

---

## Example Annotation

Original paragraph:

> Distributed leadership refers to a shared influence process where team members collectively guide strategic direction. Prior work suggests that leadership distribution significantly impacts team outcomes (Carson et al., 2007). However, the mechanisms through which distributed leadership emerges remain poorly understood. For example, Hiller (2006) found that collective leadership was associated with team effectiveness, yet the underlying process differed substantially across contexts. These findings indicate that leadership effectiveness likely depends on interaction dynamics rather than structural design alone.

| # | Sentence (abbreviated) | logic_action | targets | evidence_kind | certainty |
|---|------------------------|-------------|---------|---------------|-----------|
| 1 | Distributed leadership refers to... | define | opening·main-claim | none | strong |
| 2 | Prior work suggests... | progression | internal-flow·follows[define] | literature | moderate |
| 3 | However, the mechanisms... | contrast | internal-flow·follows[progression] | none | qualified |
| 4 | For example, Hiller (2006)... | example | internal-flow·follows[contrast] | literature | strong |
| 5 | These findings indicate... | summary | closing·wrap-up | none | qualified |
