# Claude Code Academic Workflow Template

A structured AI-assisted workflow for academic research, built on [Claude Code](https://claude.ai/code). Includes specialized agents, skills, rules, and hooks for slides, papers, data analysis, and literature review.

For the complete walkthrough, see the [**full workflow guide**](https://carltonton.github.io/mgmt-cc-workflow/Quarto/guide/workflow-guide.html).

**Author:** Lexuan Huang (based on Pedro Sant'Anna)
**License:** MIT

---

## Quick Start

### Step 1: Install Claude Code

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

1. Download and install [VS Code](https://code.visualstudio.com) (free, macOS/Windows/Linux)
2. Press `Cmd+Shift+X` (Mac) or `Ctrl+Shift+X` (Windows/Linux)
3. Search **"Claude Code"** → click **Install**
4. Open the Claude panel from the sidebar

</details>

### Step 2: Clone This Template

```bash
git clone https://github.com/`YOUR_USERNAME`/mgmt-cc-workflow.git my-project
cd my-project
```

Replace `YOUR_USERNAME` with your GitHub username.

### Step 3: Authenticate

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

### Step 4: Start Working

Run `claude` in your project directory and paste this starter prompt:

> I am starting to work on **[PROJECT NAME]** in this repo. **[Describe your project in 2–3 sentences — what you’re building, who it’s for, what tools you use (e.g., LaTeX/Beamer, R, Quarto).]**
>
> I want our collaboration to be structured, precise, and rigorous — even if it takes more time. When creating visuals, everything must be polished and publication-ready. I don’t want to repeat myself, so our workflow should be smart about remembering decisions and learning from corrections.
>
> I’ve set up the Claude Code academic workflow (forked from **`Carltonton/mgmt-cc-workflow`**). The configuration files are already in this repo (`.claude/`**,** `CLAUDE.md`, templates, scripts). Please read them, understand the workflow, and then **update all configuration files to fit my project** — fill in placeholders in `CLAUDE.md`, adjust rules if needed, and propose any customizations specific to my use case.
>
> After that, use the plan-first workflow for all non-trivial tasks. Once I approve a plan, switch to contractor mode — coordinate everything autonomously and only come back to me when there’s ambiguity or a decision to make. For our first few sessions, check in with me a bit more often so I can learn how the workflow operates.
>
> Enter plan mode and start by adapting the workflow configuration for this project.

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
| **Skills** | 21    | User-invocable commands for common academic tasks                       |
| **Rules**  | 20    | Workflow governance (always-on + path-scoped)                           |
| **Hooks**  | 8     | Automated triggers (context monitoring, verification reminders)         |

### Skill Categories

- **Research:** `/lit-search`, `/lit-read`, `/lit-review`, `/research-ideation`, `/interview-me`, `/mgmt-intro`, `/mgmt-theory-builder`, `/mgmt-empirical-research`, `/mgmt-qualitative-research`
- **Analysis:** `/stata-regression`, `/visualization`, `/jupyter-notebook`
- **Review:** `/review-python`, `/review-paper`, `/repo-audit`, `/slide-excellence`
- **Documents:** `/drawio`, `/extract-pdf`, `/obsidian-markdown`, `/obsidian-bases`, `/obsidian-cli`

---

## Obsidian Knowledge Base

The `knowledge-base/` folder doubles as an [Obsidian](https://obsidian.md) vault for research notes, literature tracking, and theoretical constructs.

### Setup

1. [Install Obsidian](https://obsidian.md) and open `knowledge-base/` as a vault
2. Install these **required plugins** (Settings → Community Plugins):
   - **[Dataview](https://github.com/blacksmithgu/obsidian-dataview)** — powers the dashboard queries and literature tracking tables
   - **[Templater](https://github.com/SilentVoid13/Templater)** — processes templates with dynamic values (dates, clipboard, file names)

### Folder Structure

| Folder                       | Purpose                                          |
| ---------------------------- | ------------------------------------------------ |
| `00-home/`                 | Dashboard and landing pages (Dataview-powered)   |
| `01-literature/notes/`     | Individual literature notes (one per paper)      |
| `01-literature/summaries/` | Condensed literature summaries                   |
| `01-literature/synthesis/` | Cross-paper synthesis and thematic reviews       |
| `02-theory/`               | Theoretical constructs, propositions, hypotheses |
| `03-methods/`              | Methodological notes and design decisions        |
| `04-project/`              | Project management, briefs, timelines            |
| `05-sources/`              | Source materials and raw data references         |
| `09-archive/`              | Archived or superseded notes                     |
| `_templates/`              | Note templates (used by Templater)               |

### Templates

Templates live in `_templates/` with the `tpl-` prefix. They use [Templater syntax](https://silentvoid13.github.io/Templater/) for dynamic values:

- `tpl-literature-note.md` — Literature notes with citekey, findings, relevance rating
- `tpl-literature-summary.md` — Condensed summaries of key papers
- `tpl-construct.md` — Theoretical construct definitions (bilingual fields)
- `tpl-study-note.md` — Study design and findings notes
- `tpl-research-log.md` — Daily research log with focus area and open questions
- `tpl-meeting.md` — Meeting notes with agenda and action items

---

## Directory Structure

```
my-project/
├── .claude/               # Claude Code infrastructure
│   ├── agents/            # 11 specialized review agents
│   ├── skills/            # 21 user-invocable skills
│   ├── hooks/             # 8 automation hooks
│   ├── rules/             # 20 governance rules
│   └── settings.json      # Hook configuration
├── Quarto/                # Quarto documents
│   └── guide/             # This workflow's full guide
├── data/                  # Research data (raw + processed)
├── docs/                  # Documents
├── knowledge-base/        # Knowledge base (Obsidian)
├── scripts/               # Analysis scripts (Python, Stata)
├── slides/                # Presentation slides
├── output/                # Generated outputs (figures, tables, models)
├── paper/                 # Paper drafts and sections
├── assets/                # Static assets (figures, tables)
├── references/            # Bibliography and reference files
├── quality_reports/       # Session logs, plans
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
