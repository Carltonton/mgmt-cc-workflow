# Codex Delegation Skill

**Description:** Delegate well-specified, low-risk tasks to Codex CLI. Use when task is simple, repetitive, or batch-oriented.

---

## Decision Tree: Delegate or Do It Yourself?

Before starting ANY task, run this 3-question checklist:

```
Task received
  │
  Q1: Is the task FULLY SPECIFIED? (exact files, exact changes, clear success criteria)
  │   NO → Claude handles it (ambiguous tasks need judgment)
  │   YES ↓
  Q2: Is the risk of error LOW? (no academic content, no data analysis logic, no research decisions)
  │   NO → Claude handles it (high-risk tasks need oversight)
  │   YES ↓
  Q3: Is the task one of these MECHANICAL types?
  │   - Batch file operations (rename, move, restructure)
  │   - Code formatting (linting, import sorting, style normalization)
  │   - Repetitive text edits (find-replace across multiple files)
  │   - Script execution (compile, render, run tests, run pipelines)
  │   - Bibliography validation (format checking, field completeness)
  │   - Simple refactoring (rename variable, extract function, move imports)
  │   - Directory cleanup (remove temp files, organize outputs)
  │   NO → Claude handles it
  │   YES → DELEGATE TO CODEX
```

## NEVER Delegate

- Research design or methodological decisions
- Academic writing (arguments, interpretations, theory)
- Literature synthesis or gap identification
- Data analysis logic (statistical modeling choices, variable selection)
- Pedagogical design decisions
- Multi-step plans requiring judgment calls
- Any file containing research results or theoretical claims
- Creating new skills, rules, or agents

---

## Invocation

Always use non-interactive execution:

```bash
codex exec --profile seed-code --skip-git-repo-check "<prompt>"
```

The prompt MUST include all 4 elements:
1. **Project root** — always include the full project path
2. **Exact file paths** — list every file to be modified
3. **Exact changes** — describe the specific transformation
4. **Success criteria** — how to verify it worked

---

## Prompt Templates

### Template 1: Batch Find-Replace
```bash
codex exec --profile seed-code --skip-git-repo-check \
  "In the project at this directory, find all occurrences of 'OLD_TEXT' and replace with 'NEW_TEXT' in these files: file1.py, file2.py, file3.md. Do NOT modify any other files. Report what was changed."
```

### Template 2: Code Formatting
```bash
codex exec --profile seed-code --skip-git-repo-check \
  "Format all Python files in src/ according to PEP 8. Keep lines under 100 characters except for mathematical formulas and URLs. Do NOT change any logic, only formatting. Report which files were modified."
```

### Template 3: File Operations
```bash
codex exec --profile seed-code --skip-git-repo-check \
  "Perform the following file operations: (1) Move old_reports/ to quality_reports/archive/, (2) Delete all .tmp files in output/. Verify each operation succeeded and report results."
```

### Template 4: Script Execution
```bash
codex exec --profile seed-code --skip-git-repo-check \
  "Run the following command and report the output: python3 src/analysis.py --input data/survey.csv --output output/results/. Report success or failure with any error messages."
```

### Template 5: Bibliography Cleanup
```bash
codex exec --profile seed-code --skip-git-repo-check \
  "Validate the bibliography file at paper/references.bib. Check for: missing required fields (author, title, year, journal/booktitle), malformed author fields, encoding issues, duplicate entries. Report all issues found, do NOT modify the file."
```

---

## Verification Protocol

After Codex completes, Claude MUST verify:

1. **Exit code** — non-zero means failure; review error output
2. **Output files** — Read modified files to confirm changes are correct
3. **Scope** — Confirm no files were modified outside the intended scope
4. **Domain checks** —
   - Python: verify imports still resolve
   - LaTeX: check compilation succeeds
   - Data files: confirm no modification occurred

If verification fails at any step, Claude handles the task manually.

---

## Failure Handling

1. Check if the prompt was specific enough (most common cause of failure)
2. Retry once with a more specific prompt
3. If still fails, Claude does the task manually
4. Record in MEMORY.md: `[LEARN:codex] Codex failed on <task type>. Cause: <reason>. Resolution: <action>.`

---

## Quick Reference

| Task Type | Delegate? | Example |
|-----------|-----------|---------|
| Rename 20 files | YES | `codex exec ... "Rename all .bak files to .backup in output/"` |
| Fix imports in 10 files | YES | `codex exec ... "Update import paths from old_module to new_module"` |
| Write literature review | NO | Requires judgment and synthesis |
| Run analysis pipeline | YES | `codex exec ... "Run python3 src/pipeline.py"` |
| Choose statistical model | NO | Requires domain expertise |
| Format Python code | YES | `codex exec ... "Apply PEP 8 to all .py files in src/"` |
| Interpret regression results | NO | Requires domain knowledge |