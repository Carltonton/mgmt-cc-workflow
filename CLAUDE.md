# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**ALWAYS start responses with:** "Claude engine ready ✅"

---

## Project Context

**Project:** [YOUR PROJECT NAME]

**Researcher:** [YOUR NAME] ([YOUR INSTITUTION]) | **Supervisor:** [YOUR SUPERVISOR]
**Discipline:** [YOUR DISCIPLINE]

### Project Structure

| Phase | Focus | Outcome |
| ----- | ----- | ------- |
| **1** | [Phase 1 description] | [Phase 1 outcome] |
| **2** | [Phase 2 description] | [Phase 2 outcome] |
| **3** | [Phase 3 description] | [Phase 3 outcome] |

See [README.md](README.md) for complete project overview.

---

## Workflow Principles

1. **No compatibility code** unless explicitly requested, and always use .venv environment
2. **Plan first, execute smartly**: Use `EnterPlanMode` for non-trivial tasks. For complex tasks (>3 files), split into subtasks and use Agent Team. Always start from first principles—don't assume I know exactly what I want. If goals or paths seem unclear or suboptimal, discuss before proceeding
3. **Clarify before coding**: If requirements are vague, ask via `AskUserQuestion`
4. **After code**: List edge cases and test cases (brief checklist)
5. **After corrections**: Record reflections in MEMORY.md
6. **Orchestrator Loop** — IMPLEMENT → VERIFY → REVIEW → FIX → RE-VERIFY → SCORE (max 5 rounds)

See `.claude/rules/` for detailed protocols.

---

## Common Skills

### Literature & Research

- `/lit-search` — Academic literature search, reference lookup, and metadata collection (CrossRef, Semantic Scholar, Tavily)
- `/lit-review` — Literature synthesis with gap identification
- `/validate-bib` — Validate bibliography entries
- `/review-paper` — Comprehensive manuscript review
- `/research-ideation` — Generate research questions and hypotheses
- `/interview-me` — Formalize research idea into specification
- `/mgmt-*` — Management research guides (theory, empirical, qualitative, intro)

### Quality Reviews

- `/proofread` — Grammar, typos, consistency
- `/slide-excellence` — Multi-agent slide review
- `/pedagogy-review` — Holistic pedagogical review
- `/visual-audit` — Adversarial visual audit
- `/qa-quarto` — Quarto vs Beamer QA
- `/review-python` — Python code quality

### Analysis & Documentation

- `/data-analysis-python` — End-to-end Python workflow
- `/python-regression` — Python regression with publication tables
- `/stata-regression` — Stata regression analysis
- `/econ-visualization` — Publication-quality charts
- `/create-lecture` — Create Beamer lectures
- `/deploy` — Render and sync Quarto slides
- `/translate-to-quarto` — Beamer to Quarto conversion

### Development

- `/commit` — Stage, commit, create PR, merge
- `/simplify` — Review and improve code
- `/learn` — Extract session knowledge into skill

---

## Domain Context

**[YOUR DOMAIN] Research** — [key concepts and theories]

**See:** [`.claude/rules/knowledge-base.md`](.claude/rules/knowledge-base.md)

---

## Key Directories

Full structure: See [README.md](README.md)

---

## Session Management

- **Logs:** `quality_reports/session_logs/YYYY-MM-DD_description.md`
- **Memory:** Record learnings in `MEMORY.md` with `[LEARN:workflow|domain|technical]` tags
- **Context:** Before compression, update MEMORY.md and session log

---

## Codex Integration

**Synergy Pattern: Claude leads, Codex executes**

```
Task received → Delegation check (3-question checklist)
                    ↓                    ↓
             Codex executes        Claude handles
                    ↓
             Claude verifies
```

**Delegation Protocol:**
1. Before each implementation subtask, run the delegation checklist (see `codex` skill)
2. Fully specified + low risk + mechanical → Codex
3. Ambiguous + judgment-required + high risk → Claude
4. ALWAYS verify Codex output before proceeding (exit code + file read + scope check)

**Invocation:**

```bash
# Non-interactive (always use this)
codex exec --profile seed-code --skip-git-repo-check "prompt"

# Interactive (only for exploratory debugging)
codex --profile seed-code
```

**Task Allocation:**

| Claude Handles | Codex Handles |
|---------------|---------------|
| Research design & ideation | Batch file operations |
| Literature synthesis & writing | Code formatting & linting |
| Pedagogical design decisions | Repetitive find-replace edits |
| Data analysis interpretation | Script execution (compile, render) |
| Multi-agent coordination | Bibliography validation |
| Domain-specific judgment | Simple refactoring & cleanup |

---

## Edge Cases & Test Checklist

After code changes:

- [ ] All imports resolve (no missing dependencies)
- [ ] Seeds set correctly for reproducibility
- [ ] Paths are relative (no hardcoded paths)
- [ ] Domain-specific assumptions validated
- [ ] Quality score >= 80 before commit
