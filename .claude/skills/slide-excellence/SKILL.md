---
name: slide-excellence
description: Comprehensive multi-agent slide review (visual + pedagogy + proofreading). Use before major milestones.
argument-hint: "[QMD or TEX filename]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task"]
context: fork
---

# Slide Excellence Review

Run comprehensive quality review on lecture slides. Three specialized agents analyze independently, then synthesize findings.

**Input:** `$ARGUMENTS` — path to `.qmd` or `.tex` file (e.g., `Quarto/Lecture01.qmd` or `Slides/Lecture01.tex`)

---

## Workflow

### Step 1: File Resolution

1. Parse `$ARGUMENTS` for filename
2. Search in `Quarto/` for `.qmd` files
3. Search in `Slides/` for `.tex` files
4. Abort if file not found

### Step 2: Parallel Agent Review

Launch 3 agents simultaneously (independent analysis):

| Agent | Subagent Type | Focus Area | Output |
|-------|--------------|------------|--------|
| Visual Audit | `slide-auditor` | Overflow, fonts, spacing, images | `quality_reports/[FILE]_visual.md` |
| Pedagogy Review | `pedagogy-reviewer` | Narrative, pacing, notation, examples | `quality_reports/[FILE]_pedagogy.md` |
| Proofreading | `proofreader` | Grammar, typos, consistency, citations | `quality_reports/[FILE]_proofread.md` |

### Step 3: Synthesize Report

Read all 3 agent reports and create combined summary:

```markdown
# Slide Excellence Review: [Filename]

**Date:** [Current date]
**File:** [File path]

## Overall Assessment: [EXCELLENT / GOOD / NEEDS WORK / POOR]

| Dimension | Critical Issues | Medium Issues | Low Issues |
|-----------|-----------------|---------------|------------|
| Visual/Layout | [count] | [count] | [count] |
| Pedagogical | [count] | [count] | [count] |
| Proofreading | [count] | [count] | [count] |
| **TOTAL** | **[sum]** | **[sum]** | **[sum]** |

---

## Critical Issues (Fix Before Presenting)
[From all agents, merged by priority]

## Medium Issues (Address in Next Revision)
[From all agents, merged by priority]

## Minor Suggestions (Future Improvements)
[From all agents, merged by priority]

---

## Agent Reports

### Visual Audit
[Summary of key findings]
→ Full report: `quality_reports/[FILE]_visual.md`

### Pedagogy Review
[Summary of key findings]
→ Full report: `quality_reports/[FILE]_pedagogy.md`

### Proofreading
[Summary of key findings]
→ Full report: `quality_reports/[FILE]_proofread.md`
```

Save to: `quality_reports/[FILE]_excellence.md`

---

## Quality Thresholds

| Rating | Critical | Medium | Action |
|--------|----------|--------|--------|
| **EXCELLENT** | 0-2 | 0-5 | Ready to present |
| **GOOD** | 3-5 | 6-15 | Minor polish recommended |
| **NEEDS WORK** | 6-10 | 16-30 | Significant revision needed |
| **POOR** | 11+ | 31+ | Major restructuring required |

---

## Important

- **Agents run in parallel** — use `Task` tool with `run_in_background: true`
- **Read all outputs before synthesizing** — don't guess agent findings
- **Preserve agent voice** — quote key issues directly from reports
- **File paths use `pathlib.Path`** — cross-platform compatible

---

## Gotchas

| Issue | Solution |
|-------|----------|
| Agent timeout | Increase `timeout` in Task call, default 300s may be insufficient for long slides |
| Output file conflicts | Use timestamp in filename: `[FILE]_excellence_[TIMESTAMP].md` |
| Missing agent reports | Check if agent failed; don't synthesize incomplete data |
| File path resolution | Handle both absolute and relative paths gracefully |

---

## Exit Conditions

**Success:** Combined report saved to `quality_reports/`

**Failure:**
- File not found → Report error to user
- All agents failed → Report system error
- Partial agent failure → Note in report, synthesize available data
