# Claude Code Academic Workflow Template

A structured AI-assisted workflow for academic research, built on [Claude Code](https://claude.ai/code). Includes specialized agents, skills, rules, and hooks for slides, papers, data analysis, and literature review.

**Author:** Lexuan Huang (based on Pedro Sant'Anna)
**License:** MIT

---

## Quick Start

1. **Fork** this repo on GitHub
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/mgmt-cc-workflow.git my-project`
3. **Configure** `CLAUDE.md` — fill in the `[PLACEHOLDERS]` with your project details
4. **Start Claude Code**: open your terminal, run `claude`, and paste the starter prompt from the [workflow guide](https://carltonton.github.io/mgmt-cc-workflow/Quarto/guide/workflow-guide.html)

See the [full workflow guide](https://carltonton.github.io/mgmt-cc-workflow/Quarto/guide/workflow-guide.html) for detailed setup instructions.

---

## What's Included

| Component | Count | Description |
|-----------|-------|-------------|
| **Agents** | 11 | Specialized review agents (code, slides, pedagogy, visuals, literature) |
| **Skills** | 33 | User-invocable commands for common academic tasks |
| **Rules** | 20 | Workflow governance (always-on + path-scoped) |
| **Hooks** | 8 | Automated triggers (context monitoring, verification reminders) |

### Skill Categories

- **Presentation:** `/create-lecture`, `/deploy`, `/translate-to-quarto`, `/extract-tikz`, `/qa-quarto`, `/visual-audit`, `/pedagogy-review`, `/slide-excellence`, `/compile-latex`
- **Quality:** `/proofread`, `/review-python`, `/review-paper`, `/deep-audit`, `/devils-advocate`, `/context-status`
- **Research:** `/lit-search`, `/lit-read`, `/lit-review`, `/validate-bib`, `/research-ideation`, `/interview-me`, `/mgmt-*`
- **Analysis:** `/data-analysis-python`, `/python-regression`, `/stata-regression`, `/econ-visualization`, `/jupyter-notebook`
- **Workflow:** `/commit`, `/deploy`, `/learn`, `/simplify`, `/drawio`, `/defuddle`, `/obsidian-*`

---

## Directory Structure

```
my-project/
├── .claude/               # Claude Code infrastructure
│   ├── agents/            # 11 specialized review agents
│   ├── skills/            # 33 user-invocable skills
│   ├── hooks/             # 8 automation hooks
│   ├── rules/             # 20 governance rules
│   └── settings.json      # Hook configuration
├── Quarto/                # Quarto documents
│   └── guide/             # Workflow guide (this document)
├── data/                  # Research data (raw + processed)
├── scripts/               # Analysis scripts (Python, Stata)
├── output/                # Generated outputs (figures, tables, models)
├── paper/                 # Paper drafts and sections
├── assets/                # Static assets (figures, tables)
├── references/            # Bibliography and reference files
├── survey/                # Survey instruments
├── quality_reports/       # Session logs, plans, reviews
├── CLAUDE.md              # Project-specific Claude Code instructions
├── MEMORY.md              # Persistent memory across sessions
├── Bibliography_base.bib  # Bibliography database
└── requirements.txt       # Python dependencies
```

---

## Documentation

- **[Workflow Guide](https://carltonton.github.io/mgmt-cc-workflow/Quarto/guide/workflow-guide.html)** — Comprehensive guide covering all patterns, skills, and workflows
- **[CLAUDE.md](CLAUDE.md)** — Project configuration (fill in placeholders for your project)
- **[MEMORY.md](MEMORY.md)** — Persistent memory system for cross-session learning
- **[.claude/rules/](.claude/rules/)** — Detailed workflow protocols and conventions

---

## Origin

This workflow was extracted from **Econ 730: Causal Panel Data** at Emory University, developed by Pedro Sant'Anna. The econometrics origin is one application — the patterns are domain-agnostic and have been extended across fields including management, psychology, and computer science.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
