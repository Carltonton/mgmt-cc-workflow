# Orchestrator Protocol: Contractor Mode

**After a plan is approved, the orchestrator takes over autonomously.**

## The Loop

```
Plan approved → orchestrator activates
  │
  Step 1: IMPLEMENT — Execute plan steps
  │
  For each implementation subtask:
  │
  1a. Delegation check — Run the 3-question checklist (see codex skill)
      - Fully specified + low risk + mechanical type?
        YES → Delegate to Codex: codex exec --profile seed-code --skip-git-repo-check "<prompt>"
        NO  → Claude implements directly
  │
  1b. If delegated to Codex:
      - Verify exit code (0 = success)
      - Read modified files to confirm correctness
      - Check scope (no unintended modifications)
      - If verification fails → Claude redoes manually
  │
  1c. If Claude implements directly:
      - Execute per plan
      - Standard verification applies
  │
  Step 2: VERIFY — Compile, render, check outputs
  │         If verification fails → fix → re-verify
  │
  Step 3: REVIEW — Run review agents (by file type)
  │
  Step 4: FIX — Apply fixes (critical → major → minor)
  │
  Step 5: RE-VERIFY — Confirm fixes are clean
  │
  Step 6: SCORE — Apply quality-gates rubric
  │
  └── Score >= threshold?
        YES → Present summary to user
        NO  → Loop back to Step 3 (max 5 rounds)
              After max rounds → present with remaining issues
```

## Limits

- **Main loop:** max 5 review-fix rounds
- **Critic-fixer sub-loop:** max 5 rounds
- **Verification retries:** max 2 attempts
- **Codex delegation retries:** max 1 retry, then Claude takes over
- Never loop indefinitely

## "Just Do It" Mode

When user says "just do it" / "handle it":
- Skip final approval pause
- Auto-commit if score >= 80
- Still run the full verify-review-fix loop
- Still present the summary
