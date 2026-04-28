---
name: mgmt-lit-review
description: This skill should be used when the user asks about "literature review", "literature search", "research gap", "review paper", "systematic review", "meta-analysis", "theoretical contribution", "research conversation", or discusses conducting and writing literature reviews in management and business research. Provides guidance for effective literature review practices based on AMJ standards.
version: 1.2.0
argument-hint: "[research topic or question]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "WebSearch", "mcp__web_reader__webReader"]
---
# Management Literature Review

Guidance for conducting literature reviews, identifying research gaps, building theoretical conversations, and writing review papers in management research, following AMJ standards.

## When This Skill Applies

- Conducting a literature review
- Searching for relevant literature
- Identifying research gaps
- Writing a review paper or meta-analysis
- Building a theoretical conversation
- Synthesizing findings across multiple studies

---

## Steps

### 1. Parse the Topic

Extract the core research question or topic from `$ARGUMENTS`. Identify key constructs, research context, and theoretical domain.

### 2. Define Search Scope

Select databases (Web of Science, Scopus, Business Source Complete, PsycINFO, SSRN, Google Scholar). Build Boolean search strings.

→ See `references/search-strategy.md` for database coverage, Boolean operators, and search string construction.

### 3. Search Existing Project Resources

Check local resources first: `Bibliography_base.bib`, `quality_reports/lit_review_*.md`, `master_supporting_docs/`, `paper/sections/02_literature.tex`. Use `Grep` to search bibliography for relevant keywords.

### 4. Conduct External Search

Use `WebSearch` or `mcp__web_reader__webReader` to find recent publications. Prioritize recent work (5-10 years) unless seminal. Use snowballing for completeness.

→ See `references/search-strategy.md` for snowballing techniques.

### 5. Organize Findings by AMJ Research Canvas

Organize into four categories:

- **Theoretical Contributions** — models, frameworks, mechanisms, new constructs
- **Empirical Findings** — key results, effect sizes, data sources
- **Methodological Innovations** — new estimators, identification strategies, measurement
- **Dialogue Contribution** — counter-intuitive findings, challenges to conventional wisdom
- **Open Debates** — unresolved disagreements, conflicting findings, competing explanations

### 6. Identify Research Gaps

| Gap Type                            | Example                                 | AMJ Relevance                    |
| ----------------------------------- | --------------------------------------- | -------------------------------- |
| **Contradictory Findings**    | Studies find opposite results           | High — synthesis opportunity    |
| **Under-explored Context**    | No studies in emerging markets          | High — boundary condition       |
| **Missing Mechanism**         | Relationship exists but "why" unknown   | High — theoretical contribution |
| **New Construct**             | Construct never studied in this context | Medium — requires justification |
| **Methodological Limitation** | Existing studies have design flaws      | Medium — method contribution    |

### 7. Extract BibTeX Citations

Required: `author`, `title`, `year`, `journal`. Recommended: `volume`, `number`, `pages`, `doi`.

### 8. Save Structured Report

Save to: `docs/lit_review_[sanitized_topic].md`

---

## Output Format

```markdown
# Literature Review: [Topic]

**Date:** [YYYY-MM-DD]
**Query:** [Original query from user]

## Summary
[2-3 paragraph overview organized by AMJ Research Canvas categories]

## Key Papers

### [Author (Year)] — [Short Title]
- **Main contribution:** [1-2 sentences]
- **Method:** [Identification strategy / data]
- **Key finding:** [Result with effect size if available]
- **Relevance:** [Why it matters for our research]
- **AMJ Category:** [Theoretical/Empirical/Methodological/Dialogue]

[Repeat for 5-15 papers, ordered by relevance]

## Thematic Organization
### Theoretical Contributions / Empirical Findings / Methodological Innovations / Dialogue Contribution / Open Debates

## Research Gaps
1. **[Gap Type]** — [Description]
   - Why it matters: [Significance]
   - Potential approach: [How to address]

## Suggested Next Steps
## BibTeX Entries
```

---

## Integrity Guidelines

- **Be honest about uncertainty.** If you cannot verify a citation, say so explicitly.
- **Do NOT fabricate citations.** If unsure about a paper's details, flag it for the user to verify.
- **Prioritize recent work** (last 5-10 years) unless seminal papers are older.
- **Note working papers vs. published papers** — working papers may change before publication.

---

## Related Skills

- **[/mgmt-theory-builder](skill:mgmt-theory-builder)** — Constructing theoretical frameworks and articulating contributions
- **[/mgmt-empirical-research](skill:mgmt-empirical-research)** — Research design, measurement, and analysis
- **[/mgmt-qualitative-research](skill:mgmt-qualitative-research)** — Qualitative literature synthesis methods
- **[/validate-bib](skill:validate-bib)** — Cross-referencing citations against bibliography entries

---

## Reference Files

| File                                 | When to Read                                                                    |
| ------------------------------------ | ------------------------------------------------------------------------------- |
| `references/search-strategy.md`    | When building search strings or selecting databases                             |
| `references/evaluation-writing.md` | When evaluating papers, writing the review, or avoiding common pitfalls         |
| `references/reading-management.md` | When managing citations, planning reading strategy, or integrating with project |

---

## Self-Evaluation Checklist

- [ ] Purpose and scope clearly stated?
- [ ] Search strategy comprehensive and documented?
- [ ] Literature synthesized, not just listed?
- [ ] Research gap clearly identified?
- [ ] Connections between studies shown?
- [ ] Contradictory findings addressed?
- [ ] AMJ Research Canvas category specified for key contributions?
- [ ] Citations in BibTeX format?
- [ ] Report saved to `docs/`?

---

## Key References

- Webster, J., & Watson, R. T. (2002). Analyzing the Past to Prepare for the Future: Writing a Literature Review. *MIS Quarterly*.
- Cooper, H. M. (2016). *Research Synthesis and Meta-Analysis: A Step-by-Step Approach*. Sage.
- Boote, D. N., & Beile, P. (2005). Scholars Before Researchers. *Educational Researcher*.
- Dorobantu, S., et al. (2024). The AMJ Management Research Canvas. *Academy of Management Journal*.
- Thatcher, S. M. B., & Fisher, G. (2022). From the Editors—The Nuts and Bolts of Writing a Theory Paper. *Academy of Management Journal*.
