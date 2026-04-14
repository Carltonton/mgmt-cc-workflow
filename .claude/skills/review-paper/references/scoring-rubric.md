# Scoring Rubric: Rewrite Evaluation

## Hard Gate

A rewrite version **must** achieve `logic_consistency >= 90` to be considered. Versions below this threshold are never output to the user, regardless of their total score.

## Weighted Score Formula

```
Score = 0.40 × logic_consistency + 0.35 × information_density + 0.25 × style_match
```

Each dimension is scored 0-100. The final score is 0-100.

---

## Dimension Definitions

### `logic_consistency` (weight: 0.40)

**What it measures:** Whether each sentence maintains a clear, coherent logical unit and whether the paragraph's logical progression is sound.

**Evaluation criteria:**

| Criterion | Score Impact |
|-----------|-------------|
| Each sentence has a single clear logical purpose | -5 per sentence with mixed purposes |
| Transitions between sentences are natural | -5 per abrupt or missing transition |
| The paragraph follows a recognizable progression pattern (TSP/TP/CR/SQ) | -10 for broken pattern |
| No logical gaps or non-sequiturs | -15 per logical gap |
| Claims are properly supported or qualified | -5 per unsupported strong claim |

**Baseline:** Start at 100, deduct per criteria above. Floor at 0.

---

### `information_density` (weight: 0.35)

**What it measures:** Whether the rewrite preserves all factual content from the original without losing claims, weakening evidence, or introducing filler.

**Evaluation criteria:**

| Criterion | Score Impact |
|-----------|-------------|
| All factual claims from original are retained | -10 per lost claim |
| All citations/references preserved accurately | -10 per lost/mangled citation |
| All data/statistics preserved | -10 per lost data point |
| No new unsupported claims introduced | -5 per new unsupported claim |
| No unnecessary filler or wordiness | -5 per redundant sentence |
| Nuance level maintained (not over-simplified) | -5 per over-simplification |

**Baseline:** Start at 100, deduct per criteria above. Floor at 0.

---

### `style_match` (weight: 0.25)

**What it measures:** Whether the rewrite matches the academic register, language level, and voice of the surrounding text.

**Evaluation criteria:**

| Criterion | Score Impact |
|-----------|-------------|
| Academic register maintained | -10 for informal language |
| Complexity level matches surrounding text | -5 for over-simplification or over-complexification |
| Terminology consistent with paper's usage | -5 per terminology inconsistency |
| Sentence length variation matches paper style | -5 for jarring length change |
| Voice (active/passive) consistent with paper | -5 for voice inconsistency |

**Baseline:** Start at 100, deduct per criteria above. Floor at 0.

---

## Workflow

1. Generate 3 rewrite versions internally
2. Score each version on all 3 dimensions
3. Apply hard gate: reject any version with `logic_consistency < 90`
4. Among passing versions, rank by weighted score
5. Output the highest-scoring passing version

## Edge Cases

### No version passes the gate
- Report the best version's scores
- Explain what specifically caused `logic_consistency` to fall short
- Suggest manual revision strategies
- Ask user if they want to try a different approach

### Targeted single-sentence rewrite
- `logic_consistency` evaluates how well the rewritten sentence fits with the sentence before and after it
- Context window: 1 sentence before + rewritten sentence + 1 sentence after
- Score as normal, but context fit is the primary `logic_consistency` concern

### All versions have identical scores
- Output all tied versions with brief descriptions
- Let user choose based on preference
