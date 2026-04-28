---
name: slide-excellence
description: >
  Comprehensive slide quality review covering visual layout, pedagogical design, and
  proofreading. Produces a synthesized report with severity-ranked issues and quality score.
  Use this skill whenever you need to review slides, check presentation quality, audit
  lecture materials, or verify slides before presenting — even if the user doesn't
  explicitly ask for a "review." Also use proactively before major milestones, before
  committing slide changes, or when the user says anything like "check these slides",
  "are these slides ready", "review my presentation", "any issues with my lecture",
  "polish my slides", or "final check on slides". Works with both .qmd
  (Quarto RevealJS) and .tex (Beamer LaTeX) files.
argument-hint: "[QMD or TEX filename]"
allowed-tools: ["Read", "Grep", "Glob", "Write"]
---
# Slide Excellence Review

Self-contained quality review for lecture slides. Three dimensions analyzed sequentially, then synthesized into one report.

**Input:** `$ARGUMENTS` — path to `.qmd` or `.tex` file (e.g., `Quarto/Lecture01.qmd` or `slides/main.tex`)

---

## Step 1: File Resolution

1. Parse `$ARGUMENTS` for filename
2. Search in order: `Quarto/`,  `slides/`, current directory
3. Abort if file not found

---

## Step 2: Visual Layout Review

Read the entire slide file and check:

### Overflow & Spacing

- Any content likely cut off or requiring scroll?
- Dense slides with too many items (more than 6 bullets, 3 boxes, or 2 large equations)?
- Font-size reductions below 0.85em (a sign of cramming)?
- Multiple large figures on one slide?

### Typography

- Consistent heading levels?
- Mixed font sizes without justification?
- Inconsistent bullet styles?

### Images & Figures

- All image references point to existing files?
- Images have `fig-align="center"` (QMD) or proper centering (TEX)?
- No PDF images referenced in QMD files (browsers can't render them)?

### Boxes & Containers

- Every opened container has a closing tag?
- Box colors/styles consistent within the same semantic type?

**Record all findings** with severity (Critical / Medium / Minor) and slide location.

---

## Step 3: Pedagogical Review

Read the slide file and evaluate:

### Narrative Arc

- Does the deck tell a coherent story (motivation → theory → evidence → conclusion)?
- Are transitions between sections smooth or abrupt?
- Is the progression accessible to the intended audience?

### Pacing & Density

- Are any slides overloaded (more than 3 key ideas per slide)?
- Is there a good balance of text, visuals, and whitespace?
- Are complex ideas broken across multiple slides with progressive disclosure?

### Notation & Examples

- Mathematical notation consistent across slides?
- Key terms defined before use?
- Concrete examples provided for abstract concepts?
- Are worked examples included where appropriate?

### Learning Objectives

- Can you infer the learning goals from the slide content?
- Does each section contribute to those goals?
- Is there a summary or take-away slide?

**Record all findings** with severity and slide location.

---

## Step 4: Proofreading Review

Read the slide file and check:

### Grammar & Typos

- Spelling errors, subject-verb agreement, tense consistency
- Missing or extra articles (a/an/the)
- Run-on sentences or sentence fragments

### Consistency

- Terminology used consistently (same term for same concept throughout)
- Acronyms defined on first use
- Numbering systems consistent (equations, figures, tables)

### Citations & References

- All citation keys resolve to valid bibliography entries?
- Citation format consistent throughout?
- No orphaned references (cited but not in bibliography)?

### Formatting

- No stray LaTeX/QMD markup visible in content
- No placeholder text (TODO, FIXME, XXX, [...])

**Record all findings** with severity and slide location.

---

## Step 5: Synthesize Report

Combine all findings into a single report:

```markdown
# Slide Excellence Review: [Filename]

**Date:** [YYYY-MM-DD]
**File:** [File path]
**Slides:** [Number of slides/frames]

## Overall Assessment: [EXCELLENT / GOOD / NEEDS WORK / POOR]

| Dimension | Critical | Medium | Minor |
|-----------|----------|--------|-------|
| Visual/Layout | [n] | [n] | [n] |
| Pedagogical | [n] | [n] | [n] |
| Proofreading | [n] | [n] | [n] |
| **TOTAL** | **[sum]** | **[sum]** | **[sum]** |

---

## Critical Issues (Fix Before Presenting)
1. **[Visual]** [Issue] — Slide [N]
2. **[Pedagogy]** [Issue] — Slide [N]

## Medium Issues (Address in Next Revision)
1. ...

## Minor Suggestions (Future Improvements)
1. ...
```

Save to: `quality_reports/[FILE]_excellence_[YYYY-MM-DD].md`

---

## Quality Thresholds

| Rating               | Critical | Medium | Action                       |
| -------------------- | -------- | ------ | ---------------------------- |
| **EXCELLENT**  | 0        | 0-3    | Ready to present             |
| **GOOD**       | 1-2      | 4-8    | Minor polish recommended     |
| **NEEDS WORK** | 3-5      | 9-15   | Significant revision needed  |
| **POOR**       | 6+       | 16+    | Major restructuring required |

---

## Gotchas

| Issue                          | Solution                                                                    |
| ------------------------------ | --------------------------------------------------------------------------- |
| Long file takes multiple reads | Read in chunks (200 lines at a time), process incrementally                 |
| Mixed QMD/TEX syntax           | Detect format from extension, apply appropriate checks                      |
| Ambiguous severity             | Default to Medium; only flag Critical if it breaks understanding or display |
