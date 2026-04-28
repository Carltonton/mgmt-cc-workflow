---
name: review-paper
description: >
  Comprehensive manuscript review with logic-chain annotation and rewrite generation.
  Step A: per-sentence logic annotation at 4 levels (sentence/paragraph/section/full-text)
  + integrated referee evaluation (argument structure, identification, econometrics,
  literature, writing, presentation). Step B: scored rewrite generation with
  logic_consistency >= 90 gate. Supports PDF, DOCX, DOC, TXT, MD, QMD, TEX inputs.
argument-hint: "[file path] [--section N --paragraph M | \"targeted description\"]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task"]
version: 2.0.0
---
# Manuscript Review: Logic Chain + Referee Evaluation

Produce a thorough, constructive review of an academic manuscript — combining per-sentence logic-chain annotation with referee-style evaluation — then generate scored rewrites for flagged passages.

**Input:** `$ARGUMENTS` — path to a document (`.pdf`/`.docx`/`.doc`/`.txt`/`.md`/`.tex`/`.qmd`), optionally with scope flags or a natural-language targeting description.

---

## Step 0: Setup

### 0a. Parse arguments

Extract from `$ARGUMENTS`:

- `file_path`: first argument (required) — path to document
- `--section N`: restrict review to section N (optional)
- `--paragraph M`: further restrict to paragraph M within the section (optional)
- Quoted string: natural-language targeting (e.g., `"the logic in paragraph 2 feels off"`)
- Default scope: full paper

### 0b. Locate and load the file

Search in order:

1. Direct path from `file_path`
2. Glob for partial matches

**File handling by extension:**

| Extension                             | Method                                                                       |
| ------------------------------------- | ---------------------------------------------------------------------------- |
| `.pdf`                              | Read in chunks (5 pages at a time using `pages` parameter)                 |
| `.tex`, `.qmd`, `.md`, `.txt` | Read directly with Read tool                                                 |
| `.docx`, `.doc`                   | Attempt Read; if binary fails, inform user and suggest converting to PDF/TXT |

### 0c. Read reference schemas

Read the following reference files before starting Step A:

- `references/annotation-schema.md` — per-sentence annotation fields
- `references/logic-action-rules.md` — detection rules for `logic_action`
- `references/scoring-rubric.md` — scoring formula and gate criteria

### 0d. Segment text

If scope is targeted: extract the specified section/paragraph only.
If scope is full paper: segment into sections, paragraphs, and sentences.

Segmentation rules:

- Sections: headings (`#`/`##`/`###` in Markdown; `\section`/`\subsection` in LaTeX; numbered headings in PDF text)
- Paragraphs: blank lines, indentation patterns, or double newlines
- Sentences: period + space + capital letter, or explicit sentence boundaries

---

## Step A: Logic Chain Annotation + Referee Evaluation

### A1. Per-sentence annotation

For each sentence in scope, annotate with 4 fields (see `references/annotation-schema.md`):

| Field             | Description          | Example                                                     |
| ----------------- | -------------------- | ----------------------------------------------------------- |
| `logic_action`  | Discourse function   | `define`, `progression`, `contrast`, ...              |
| `targets`       | Intra-paragraph role | `opening·main-claim`, `internal-flow·follows[define]` |
| `evidence_kind` | Type of evidence     | `literature`, `data`, `none`                          |
| `certainty`     | Tone strength        | `strong`, `moderate`, `qualified`                     |

### A2. Build 4-level logic chain

**Sentence level:**
Annotated sequence with connectors. Flag sentences where:

- Logical unit is unclear (mixed purposes in one sentence)
- Transition to next sentence is abrupt or missing
- Evidence is absent for a strong claim

**Paragraph level:**
Detect the paragraph's progression pattern:

| Pattern          | Structure                 | Example                               |
| ---------------- | ------------------------- | ------------------------------------- |
| TSP              | Topic → Support → Point | Claim, evidence, analytical takeaway  |
| TP               | Transition → Progression | Shift direction, then develop         |
| CR               | Contrast → Resolution    | Present tension, then resolve         |
| SQ               | Sequential accumulation   | Related points building on each other |
| **broken** | No discernible pattern    | **Flagged for rewrite**         |

**Section level:**
Check whether each paragraph contributes to the section's stated topic. Detect **goal drift** — paragraphs serving a different purpose than the section heading suggests.

**Full-text level:**
Map the argument chain and narrative arc:

| Section           | Expected Role                   |
| ----------------- | ------------------------------- |
| Introduction      | State claim and motivation      |
| Literature Review | Position claim in existing work |
| Method            | Justify approach                |
| Results           | Present evidence                |
| Discussion        | Interpret findings              |
| Conclusion        | Resolve and contribute          |

Detect breaks in the narrative arc.

### A3. Integrated referee evaluation

Merge 6 referee dimensions into the logic analysis:

**1. Argument Structure**

- Is the research question clearly stated?
- Does the logic flow support it (sentence-level chain confirms or denies)?
- Are conclusions supported by evidence?

**2. Identification Strategy**

- Are causal claims credible?
- Key identifying assumptions stated explicitly?
- Threats to identification flagged?

**3. Econometric Specification**

- Correct standard errors?
- Appropriate functional form?
- Sample selection issues?
- Multiple testing concerns?

**4. Literature Positioning**

- Key papers cited (`evidence_kind: literature` coverage)?
- Contribution differentiated from existing work?

**5. Writing Quality**

- Clarity and concision
- Academic tone
- Notation consistency

**6. Presentation**

- Tables and figures well-designed?
- Typos, grammatical errors?
- Paper length appropriate for contribution?

### A4. Citation format check

Verify citations against:

- **APA 7th edition** standard
- **GB/T 7713.2-2022** (Chinese academic paper standard)

Flag any format inconsistencies.

### A5. Generate 3-5 referee objections

Tough questions a top-journal referee would raise, grounded in the logic chain analysis.

### A5b. Domain review (optional, for management/social science papers)

For papers in organizational psychology, management, or related domains, spawn the `domain-reviewer` agent as a parallel review pass:

```
Agent tool → subagent_type: "domain-reviewer"
Prompt: "Review [file_path] for substantive correctness. Focus on assumption sufficiency, derivation correctness, citation fidelity, code-theory alignment, and backward logic."
```

Merge the domain-reviewer report into the Step A findings before presenting to the user.

### A6. Present Step A report

Present the full report to the user. **Wait for user confirmation** before proceeding to Step B.

The user may respond with:

- "OK" / "continue" / "proceed" → go to Step B
- Specific questions about flagged areas → address before Step B
- Scope adjustment → re-run with new scope

---

## Step B: Rewrite Generation

**Only triggered after user confirms Step A report.**

### B1. Identify rewrite targets

Sentences/paragraphs flagged in Step A as:

- `broken` progression pattern
- Abrupt transitions
- Goal drift
- Unsupported strong claims
- User-specified targets

### B2. Generate 3 rewrite versions

For each target, generate 3 alternative versions **internally** (not shown to user yet).

### B3. Score each version

Apply scoring rubric (see `references/scoring-rubric.md`):

**Hard gate:** `logic_consistency >= 90` — versions below this are rejected.

**Weighted score:**

```
Score = 0.40 × logic_consistency + 0.35 × information_density + 0.25 × style_match
```

| Dimension               | Weight | What it measures                                                                 |
| ----------------------- | ------ | -------------------------------------------------------------------------------- |
| `logic_consistency`   | 0.40   | Sentence logical unit consistency, paragraph progression, transition naturalness |
| `information_density` | 0.35   | Factual content preservation, evidence retention, no claims lost                 |
| `style_match`         | 0.25   | Academic register, language level, paper voice                                   |

### B4. Output the best passing version

If at least one version passes the gate, output the highest-scoring version with:

1. **Rewritten text** (the recommended version)
2. **Scoring summary** (all 3 versions):

| Version | logic_consistency | information_density | style_match | Weighted Score | Pass?  |
| ------- | ----------------- | ------------------- | ----------- | -------------- | ------ |
| V1      | N/100             | N/100               | N/100       | N              | Yes/No |
| V2      | N/100             | N/100               | N/100       | N              | Yes/No |
| V3      | N/100             | N/100               | N/100       | N              | Yes/No |

3. **Key changes** — what was changed and why
4. **Trade-offs** — any information restructured or nuance shifted
5. **Citation verification** — confirm citation formats comply with APA 7 + GB/T 7713.2-2022

### B5. Edge cases

**No version passes the gate:**

- Report the best version's scores
- Explain what caused `logic_consistency` to fall short
- Suggest manual revision strategies
- Ask user if they want to try a different approach

**Single-sentence targeted rewrite:**

- Evaluate fit with surrounding context (1 sentence before + after)
- `logic_consistency` measures context integration, not just internal coherence

---

## Output Format

Save to `quality_reports/paper_reviews/logic_review_[sanitized_name].md`.

Both Step A and Step B go in the same file. Step B is appended under a `## Rewrites` heading.

### Step A Output Template

```markdown
# Logic Review: [Paper Title]

**Date:** [YYYY-MM-DD]
**Scope:** [Full paper / Section N / Section N, Paragraph M]
**File:** [path to document]

---

## Section [N]: [Section Title]

### Paragraph [M]

**Progression Pattern:** [TSP / TP / CR / SQ / broken]
**Section Goal Alignment:** [on-target / mild-drift / significant-drift]

| # | Sentence (abbreviated) | logic_action | targets | evidence_kind | certainty | Flag |
|---|------------------------|-------------|---------|---------------|-----------|------|
| 1 | [First 40 chars]... | define | opening·main-claim | theory | strong | |
| 2 | [First 40 chars]... | progression | internal-flow·follows[define] | literature | moderate | |
| 3 | [First 40 chars]... | transition | internal-flow·follows[progression] | none | qualified | ⚠ |
| 4 | [First 40 chars]... | summary | closing·wrap-up | none | moderate | |

**Logic Chain Diagram:**
define → progression → transition⚠ → summary

**Flags:**
- ⚠ S3: [Explanation of why this sentence is flagged]
  - Issue: [Specific problem]
  - Suggestion: [What kind of fix might help]

---

## Full-Text Logic Summary

### Argument Chain
[S1.define] → [S2.progression] → ... → [SN.summary]

### Narrative Arc Check

| Section | Expected Role | Actual Pattern | Status |
|---------|--------------|---------------|--------|
| Introduction | State claim | [detected] | [OK / DRIFT] |
| Lit Review | Position claim | [detected] | [OK / DRIFT] |
| Method | Justify approach | [detected] | [OK / DRIFT] |
| Results | Present evidence | [detected] | [OK / DRIFT] |
| Discussion | Interpret | [detected] | [OK / DRIFT] |
| Conclusion | Resolve | [detected] | [OK / DRIFT] |

### Referee Objections

#### RO1: [Question]
**Why it matters:** [Why this could be fatal]
**How to address:** [Suggested response or analysis]

[Repeat for 3-5 objections]

### Citation Issues

| Location | Current Format | Required Format | Standard |
|----------|---------------|----------------|----------|
| [location] | [current] | [corrected] | APA 7 / GB/T |

### Flagged Items Summary

| # | Location | Issue | Severity |
|---|----------|-------|----------|
| 1 | S2§P3 | Broken transition | Major |
| 2 | S4§P1 | Goal drift | Minor |

---

**Action Required:** Review the flags above. Reply "OK" or "continue" to proceed with rewrite generation, or specify which items to discuss.
```

### Step B Output Template (appended under `## Rewrites`)

```markdown
## Rewrites

### Rewrite 1: [Location Description]

**Original (flagged):**

> [Original text]

**Issue:** [Description from Step A]

**Recommended Rewrite:**

> [Rewritten version — highest-scoring passing version]

**Scoring Summary:**

| Version | logic_consistency | information_density | style_match | Score | Pass? |
|---------|------------------|--------------------|-------------|-------|-------|
| V1 | N/100 | N/100 | N/100 | N | Yes |
| V2 | N/100 | N/100 | N/100 | N | No |
| V3 | N/100 | N/100 | N/100 | N | Yes |

**Selected:** V[N] (highest score among passing versions)

**Key Changes:**
1. [Change 1]: [Why]
2. [Change 2]: [Why]

**Trade-offs:**
- [Any information restructured, with rationale]

**Citation Check:** [OK / Issues: details]
```

---

## Principles

- **Logic first.** Sentence-level logical connections are the most important prerequisite for paper revision.
- **Be constructive.** Every criticism comes with a suggestion.
- **Be specific.** Reference exact sentences, paragraphs, sections.
- **Think like a top-journal referee.** What would make them reject?
- **Distinguish fatal from minor.** Not everything is equally important.
- **Gate strictly.** No rewrite version with `logic_consistency < 90` is output as "approved."
- **Do NOT fabricate details.** If a section cannot be read clearly, say so.

---

## Gotchas

### Configuration

| Issue                       | Solution                                                                  |
| --------------------------- | ------------------------------------------------------------------------- |
| Reference schemas not found | Check `.claude/skills/review-paper/references/` exists with all 3 files |

### Data/Input

| Issue                                                               | Solution                                                                                       |
| ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `.docx` binary read failure                                       | Suggest converting to PDF or plain text                                                        |
| Scanned PDFs have no extractable text                               | Suggest OCR conversion or providing `.md`/`.tex` version                                   |
| Mixed Chinese/English text                                          | Detect language per sentence; apply appropriate connector rules from `logic-action-rules.md` |
| Targeted scope not found (e.g.,`--section 5` but only 3 sections) | Report error with list of available sections                                                   |

### Processing

| Issue                                         | Solution                                                          |
| --------------------------------------------- | ----------------------------------------------------------------- |
| Long papers overwhelm context for full review | Process section by section; save intermediate results to disk     |
| Ambiguous `logic_action` classification     | Default to `progression`; flag for user review                  |
| No version passes rewrite gate                | Report best scores, explain shortcomings, suggest manual revision |
| Rewrite gate fails repeatedly (2+ attempts)   | Switch to advisory mode: provide analysis rather than rewrites    |

### Output/Export

| Issue                          | Solution                                                                                   |
| ------------------------------ | ------------------------------------------------------------------------------------------ |
| Logic chain table too wide     | Use abbreviated sentence display (first 40 chars); full sentences available in report file |
| Output directory doesn't exist | Create `quality_reports/paper_reviews/` automatically                                    |

### Environment

| Issue                                  | Solution                                           |
| -------------------------------------- | -------------------------------------------------- |
| Context compression during long review | Save Step A results to disk before starting Step B |
