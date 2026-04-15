# Claude Code Academic Workflow Template

A structured AI-assisted workflow for academic research, built on [Claude Code](https://claude.ai/code). Includes specialized agents, skills, rules, and hooks for slides, papers, data analysis, and literature review.

**Author:** Lexuan Huang (based on Pedro Sant'Anna)
**License:** MIT

---

## Quick Start

### Step 1: Install VS Code

Download from [code.visualstudio.com](https://code.visualstudio.com) (free, macOS/Windows/Linux).

### Step 2: Install Claude Code

Claude Code runs as both a **CLI tool** and a **VS Code extension** — same capabilities, different interface.

<details>
<summary><strong>Option A: CLI (Terminal)</strong></summary>

```bash
# Requires Node.js 18+ — check with: node --version
# If missing, install from https://nodejs.org

# Install Claude Code
curl -fsSL https://claude.ai/install.sh | bash

# Verify
claude --version
```

</details>

<details>
<summary><strong>Option B: VS Code Extension</strong></summary>

1. Open VS Code
2. Press `Cmd+Shift+X` (Mac) or `Ctrl+Shift+X` (Windows/Linux)
3. Search **"Claude Code"** → click **Install**
4. Open the Claude panel from the sidebar

</details>

### Step 3: Clone This Template

```bash
git clone https://github.com/Carltonton/mgmt-cc-workflow.git my-project
cd my-project
```

### Step 4: Authenticate

Run `claude` in your terminal — your browser will open for sign-in. You need a [Claude Pro or Max subscription](https://claude.ai), or an [Anthropic API key](https://console.anthropic.com).

<details>
<summary><strong>Using a third-party API? (GLM, OpenRouter, etc.)</strong></summary>

Edit your **user-level settings file** and add:

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "your-api-key",
    "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/paas/v4",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-4.7",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-5.1",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-5.1"
  },
  "model": "glm-5.1"
}
```

- **macOS/Linux:** `~/.claude/settings.json`
- **Windows:** `%APPDATA%\claude\settings.json`

</details>

### Step 5: Start Working

Run `claude` in your project directory and paste this starter prompt:

> I'm starting a project on **[YOUR TOPIC]** in this repo. Please read `CLAUDE.md` and all files in `.claude/`, then fill in the placeholders with my project details. After that, use the plan-first workflow for all tasks.

That's it — Claude will configure everything and you can start describing what you want to build.

> For the complete walkthrough, see the [**full workflow guide**](https://carltonton.github.io/mgmt-cc-workflow/Quarto/guide/workflow-guide.html).

---

## API Keys Configuration

Some skills require external API keys. Create a `.env` file in the root directory:

```bash
# Required for /lit-search (CrossRef, Semantic Scholar, Tavily)
TAVILY_API_KEY=tvly-your-key-here
CROSSREF_EMAIL=your-email@example.com

# Optional: Semantic Scholar (increases rate limits)
SEMANTIC_SCHOLAR_API_KEY=your-key-here

# Required: Anthropic API (if using API key auth instead of browser sign-in)
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

> **Note:** The `.env` file is already in `.gitignore` and will NOT be committed to your repository.

---

## What's Included

| Component        | Count | Description                                                             |
| ---------------- | ----- | ----------------------------------------------------------------------- |
| **Agents** | 11    | Specialized review agents (code, slides, pedagogy, visuals, literature) |
| **Skills** | 33    | User-invocable commands for common academic tasks                       |
| **Rules**  | 20    | Workflow governance (always-on + path-scoped)                           |
| **Hooks**  | 8     | Automated triggers (context monitoring, verification reminders)         |

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
