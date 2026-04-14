# Logic Action Detection Rules

## How to Classify `logic_action`

For each sentence, scan for connector words and discourse markers. Match the first applicable rule. If no rule matches, assign `progression` (default).

## Detection Rules by Action

### `define`
Signals the sentence introduces, defines, or delimits a concept.
- **EN:** "is defined as", "refers to", "can be understood as", "by definition", "the concept of", "we define", "means that", colon (`:`) introducing a term
- **ZH:** "指的是", "定义为", "是指", "可以被理解为", "概念上"

### `transition`
Signals a shift in direction, topic, or argument phase.
- **EN:** "However", "Furthermore", "Moreover", "Nevertheless", "Next", "Turning to", "Having discussed", "With respect to", "In this regard"
- **ZH:** "然而", "此外", "接下来", "另外", "另一方面", "关于", "在...方面"

### `progression` (default)
Advances the argument with new information, no clear connector.
- Applied when no other rule matches.
- Common in: restatements, elaborations, descriptions, narrations.

### `contrast`
Presents opposing, differing, or alternative views.
- **EN:** "In contrast", "Unlike", "whereas", "while", "conversely", "on the other hand", "differ", "distinguish"
- **ZH:** "与此不同", "相反", "与...不同", "区别于", "对比而言"
- **Note:** "while" and "whereas" can be `contrast` or `concession` — check if the sentence grants a point (concession) or sets up opposition (contrast).

### `concession`
Acknowledges a counter-point or limitation before a rebuttal.
- **EN:** "Although", "Even though", "Despite", "While it is true that", "Admittedly", "Granted", "To be sure"
- **ZH:** "尽管", "虽然", "不可否认", "诚然", "固然"
- **Distinguish from contrast:** Concession grants a point; contrast opposes. "Although X is true, Y" = concession. "X is A, whereas Y is B" = contrast.

### `causation`
States cause-effect or reason-consequence relationship.
- **EN:** "Because", "Therefore", "Thus", "Consequently", "As a result", "leads to", "results in", "causes", "drives", "due to", "owing to", arrows of implication (→)
- **ZH:** "因此", "由于", "导致", "造成", "因为", "所以", "结果是", "引发了"

### `comparison`
Draws parallel or similarity between two things.
- **EN:** "Similarly", "Likewise", "In the same way", "Like", "Analogous to", "Comparable to", "compared to", "Parallel to"
- **ZH:** "同样地", "类似于", "与...相似", "类比于", "同样"

### `example`
Provides illustrative instance, case, or evidence.
- **EN:** "For example", "For instance", "such as", "e.g.", "To illustrate", "Consider the case of", "as demonstrated by"
- **ZH:** "例如", "比如", "举例来说", "以...为例", "诸如"

### `qualification`
Narrows, conditions, or specifies the scope of a claim.
- **EN:** "Specifically", "In particular", "Under certain conditions", "To a certain extent", "Only when", "Provided that", "More precisely"
- **ZH:** "在特定条件下", "具体而言", "特别是", "在一定意义上", "仅当"

### `summary`
Recaps, concludes, or wraps up a line of argument.
- **EN:** "In summary", "To conclude", "In conclusion", "Overall", "Taken together", "These findings suggest", "Collectively", "In short"
- **ZH:** "总之", "综上所述", "总而言之", "概括而言", "总结来说", "这些发现表明"

---

## Ambiguity Resolution

When multiple rules could apply:

1. **"While"** — Check context: if granting a point → `concession`; if opposing → `contrast`; if temporal → `transition`
2. **"As"** — If causal → `causation`; if comparison → `comparison`; if temporal → `transition`
3. **Citation + claim** — The `logic_action` describes the discourse function, not the evidence. A sentence can be `example` + `evidence_kind: literature` (citing a source as an example).
4. **Multiple connectors** — Use the PRIMARY logical function. "However, because X..." → `contrast` dominates over `causation`.

## Chinese-English Mixed Text

For papers mixing both languages:
- Detect the primary language of each sentence
- Apply the corresponding trigger list
- Both trigger lists are exhaustive for common academic writing patterns
