---
name: lit-read
description: Systematically read and extract structured knowledge from a batch of academic PDFs through 3 phases: semantic clustering (discover research threads and conversation maps), close reading (extract findings/methods/limitations per paper), and knowledge abstraction (propose updates to knowledge-base.md).
  Triggers: "read papers", "read literature", "read these PDFs", "精读文献", "读文献", "read this batch", "literature reading", "paper notes", "extract knowledge from papers", "analyze these papers", "读这些论文", "extract findings"
  Replaces: Manual paper-by-paper reading without structured extraction.
argument-hint: "[path/to/pdf/directory] --topic [topic-name]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "Agent"]
---
# Read-Lit: Structured Literature Reading

Systematically read a batch of academic PDFs through three phases — semantic clustering, close reading, and knowledge abstraction — turning raw papers into structured knowledge integrated into your project.

**Input:** `$ARGUMENTS` — a path to a directory containing PDF files. Optionally specify `--topic [name]` for the output subdirectory.

---

## How It Works

```
PDF Directory
    ↓
Phase 1: Semantic Clustering (语义聚类)
    → research-map.md (research conversation map)
    ↓
Phase 2: Close Reading (精读记录)
    → per-paper notes + knowledge-framework.md
    ↓
Phase 3: Knowledge Abstraction (知识抽象)
    → proposed updates to knowledge-base.md (user reviews)
```

Each phase builds on the previous one. You can stop after any phase if that's all you need.

---

## Phase 0: Setup

### 0a. Parse arguments

- `$ARGUMENTS` contains a path to a PDF directory (required)
- `--topic [name]` sets the output subdirectory name (default: `general`)
- Resolve the path relative to the project root

### 0b. Check for existing markdown, convert if needed

1. Use Glob to find all `.pdf` files in the input directory
2. **Check if markdown already exists:** Look for `.md` files in the input directory or a sibling `*_md` directory
3. **If markdown files exist:** Skip conversion — use the existing `.md` files directly. Proceed to Phase 1.
4. **If no markdown found:** Run the conversion script from lit-search:
   ```bash
   cd "$PROJECT_DIR" && PYTHONPATH=.claude/skills/lit-search \
     python3 -m scripts.convert_pdfs_to_md \
     --input "[pdf_directory]" \
     --output "[project_root]/docs/[topic]/pdf_markdown"
   ```

   The script skips already-converted files, so it's safe to re-run.
5. **For scanned PDFs**, the script automatically detects and uses OCR (requires pytesseract + tesseract). First-time setup:
   ```bash
   pip3 install pytesseract pillow --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
   brew install tesseract tesseract-lang
   ```
6. If the script fails (missing pymupdf), fall back to reading PDFs directly with the Read tool — it supports PDFs natively.

**If no PDFs found**, inform the user and stop.

### 0c. Read knowledge-base.md

Always read `.claude/rules/knowledge-base.md` before starting Phase 1. This gives the clustering context about your project's theoretical framework and helps identify relevant connections.

**Output path convention:** `docs/{topic}/` — all outputs from this session go here.

---

## Phase 1: Semantic Clustering

**Goal:** Discover the research conversation structure — who started what, who built on it, who challenged it, and where the field turned.

### 1a. Lightweight first pass

Read each paper's metadata + abstract + conclusion section (first 1-3 pages). For 15+ papers, this is a ~lightweight pass — you're mapping the territory, not analyzing deeply.

**For converted markdown files:** Read the first ~200 lines of each `.md` file.
**For direct PDF reading:** Read pages 1-3 of each PDF.

### 1b. Cluster papers into research threads

Group papers by their **research conversation**, not just topic similarity. A "conversation" is a line of inquiry where papers explicitly build on, extend, or challenge each other.

**Clustering signals to look for:**

- Same core construct or phenomenon being studied
- Explicit citations of each other (in references or text)
- Shared theoretical framework
- Methodological paradigm (same approach, different populations/settings)
- Direct agreements or disagreements in findings

### 1c. Assign roles within each thread

For each paper within a thread, classify its role:

| Role                    | Description                                      | Example                                |
| ----------------------- | ------------------------------------------------ | -------------------------------------- |
| **origin**        | Foundational work that started this conversation | "First to propose construct X"         |
| **extension**     | Builds directly on an origin, adds nuance        | "Extends X to new context Y"           |
| **critique**      | Challenges assumptions or findings               | "Questions the measurement of X"       |
| **turning-point** | Shifts the paradigm or opens new direction       | "Reconceptualizes X as Y instead of Z" |
| **synthesis**     | Integrates multiple prior threads                | "Meta-analysis of X across 20 studies" |

A paper can have multiple roles across different threads.

### 1d. Map cross-thread connections

Identify relationships between threads:

- **Convergent**: Two threads arrive at similar conclusions from different angles
- **Divergent**: Two threads contradict each other
- **Sequential**: One thread logically follows from another
- **Parallel**: Independent threads studying the same phenomenon

### 1e. Write the research map

Save to `docs/{topic}/research-map.md`:

```markdown
# Research Conversation Map: [Topic]
**Papers**: N | **Threads**: K | **Date**: YYYY-MM-DD

## Thread 1: [Thread Name]
**Core question:** [What question does this conversation address?]
**Key construct:** [Main concept/debate]

### Origin
- [Author (Year)] — [Short Title]
  Role: origin | Why: [1 sentence on foundational contribution]

### Development
- [Author (Year)] — [Short Title]
  Role: extension | How: [1 sentence on what it adds]
- [Author (Year)] — [Short Title]
  Role: extension | How: ...

### Critique / Rebuttal
- [Author (Year)] — [Short Title]
  Role: critique | Challenge: [1 sentence on what it questions]

### Turning Point
- [Author (Year)] — [Short Title]
  Role: turning-point | Shift: [1 sentence on paradigm change]

## Thread 2: [Thread Name]
...

## Cross-Thread Connections
- **Thread 1 → Thread 2**: [relationship, 1 sentence]
- **Thread 1 ↔ Thread 3**: [tension, 1 sentence]

## Ungrouped Papers
- [Author (Year)] — [Title] | Reason: [why it doesn't fit a thread]
```

**Present the map to the user** and ask if the clustering looks right before proceeding to Phase 2. Adjust based on feedback.

---

## Phase 2: Close Reading

**Goal:** Read each paper fully, extract structured notes, and synthesize into a knowledge framework.

### 2a. Determine reading order

Follow the research map: origins first, then extensions, then critiques/turning points. This creates a natural narrative arc — you understand the foundation before seeing how others build on or challenge it.

### 2b. Batch processing for large sets

**For ≤5 papers:** Read all in sequence, no batching needed.
**For 6-15 papers:** Process in 2-3 batches of 3-5 papers each.
**For 15+ papers:** Process in batches of 3-5 papers. Use the Agent tool with `subagent_type: general-purpose` for parallel batches when possible.

**Batching strategy:**

- Group by thread (read one complete thread per batch)
- Each batch produces per-paper notes
- After all batches: synthesize into a cross-paper knowledge framework

### 2c. Read each paper and extract notes

For each paper, read the full text (PDF or markdown). Use the Read tool's `pages` parameter for PDFs (10-20 pages at a time).

Read the reading note template first:

```
.claude/skills/lit-read/references/reading-note-template.md
```

Then extract notes following the template structure. Save each note to:
`docs/{topic}/notes/{author}_{year}.md`

### 2d. Write the knowledge framework

After all per-paper notes are complete, synthesize into:
`docs/{topic}/knowledge-framework.md`

The knowledge framework goes beyond summarizing individual papers — it identifies patterns, tensions, and gaps across the entire set. See the template in `references/reading-note-template.md` for the exact format.

Key synthesis questions:

- Which theoretical constructs appear across multiple papers?
- Where do empirical findings converge or diverge?
- What methodological patterns emerge?
- What are the unresolved debates?
- How does this connect to the thesis Parts 1/2/3?

### 2e. Present summary to user

Show the user:

1. Number of papers read and notes generated
2. Key threads identified and how they relate
3. Most important findings and gaps discovered
4. Ask if they want to proceed to Phase 3 (knowledge abstraction)

---

## Phase 3: Knowledge Abstraction

**Goal:** Distill the most important new knowledge from the reading session and propose updates to the project's knowledge base.

### 3a. Identify candidate updates

Read both:

- `docs/{topic}/knowledge-framework.md` (new findings)
- `.claude/rules/knowledge-base.md` (current state)

Look for three types of updates:

**NEW — Concepts or findings not in knowledge-base.md:**

- New theoretical constructs relevant to Parts 1/2/3
- New methodological approaches or tools
- New empirical evidence that supports or challenges existing entries

**MODIFY — Existing entries that need refinement:**

- Findings that add nuance to existing constructs
- Evidence that strengthens or weakens existing claims
- Methodological insights that update prevention strategies

**NO CHANGE — Confirmed existing knowledge:**

- Findings that align with what's already in the knowledge base
- Not worth adding (too niche, not relevant to this thesis)

### 3b. Generate proposed diff

Create a structured proposal showing exactly what would change. Save to:
`docs/{topic}/knowledge-base-diff.md`

```markdown
# Proposed Updates to Knowledge Base
**Source**: [topic] reading session | **Date**: YYYY-MM-DD

## ADD

### [Target Section in knowledge-base.md]
**Content to add:**
[new content with rationale]

### [Another Target Section]
**Content to add:**
[new content]

---

## MODIFY

### [Existing Section/Entry]
**Current:** [quote or summarize what's there]
**Proposed change:** [what to change]
**Reason:** [evidence from reading session]

### [Another Entry]
**Current:** [...]
**Proposed change:** [...]
**Reason:** [...]

---

## NO CHANGE

- [Existing entry]: Confirmed by [Paper (Year)]
- [Existing entry]: Still accurate, no new evidence
```

### 3c. Review with user

Present the diff to the user. For each proposed change:

- Explain what would change and why
- Cite the specific papers that support the change
- Ask the user to approve, reject, or modify each item

### 3d. Apply approved changes

For each approved update:

- Read the current `.claude/rules/knowledge-base.md`
- Apply the change using the Edit tool
- Ensure formatting consistency with the existing file

**Be conservative:** Only add knowledge that is directly relevant to the thesis Parts 1/2/3. The knowledge base should stay focused and scannable.

---

## Output Summary

| Phase           | Output                        | Location                                      |
| --------------- | ----------------------------- | --------------------------------------------- |
| 0 - Setup       | Converted markdown + manifest | `docs/{topic}/pdf_markdown/`          |
| 1 - Clustering  | Research conversation map     | `docs/{topic}/research-map.md`        |
| 2 - Reading     | Per-paper reading notes       | `docs/{topic}/notes/`                 |
| 2 - Synthesis   | Knowledge framework           | `docs/{topic}/knowledge-framework.md` |
| 3 - Abstraction | Proposed KB updates           | `docs/{topic}/knowledge-base-diff.md` |
| 3 - Applied     | Updated knowledge base        | `.claude/rules/knowledge-base.md`           |

---

## Important

- **Theory-driven reading:** When extracting knowledge, always relate findings back to the theoretical framework in knowledge-base.md. Don't just summarize — ask "how does this change what we know?"
- **Honest limitations:** Note both what authors acknowledge and what they don't. Missing limitations are often more informative than stated ones.
- **Incremental sessions:** If context runs out mid-reading, save progress and resume. The research map and per-paper notes are designed to be incrementally updatable.
- **Respect paper boundaries:** Don't conflate findings across papers. Each note should clearly attribute findings to specific papers.

---

## Gotchas

### Configuration

| Issue                   | Solution                                                                          |
| ----------------------- | --------------------------------------------------------------------------------- |
| pymupdf not installed   | Run `pip install pymupdf`, or fall back to reading PDFs directly with Read tool |
| PDF directory not found | Check the path; try both absolute and relative to project root                    |

### Data/Input

| Issue                          | Solution                                                                               |
| ------------------------------ | -------------------------------------------------------------------------------------- |
| PDF text extraction is garbled | Scanned PDFs need OCR; try reading with Read tool which handles some formatting better |
| 15+ papers overwhelm context   | Use batching (3-5 papers per batch) and Agent tool for parallel processing             |
| Papers are in mixed languages  | Extract in the paper's primary language; add English summary for Chinese papers        |

### Processing

| Issue                                  | Solution                                                         |
| -------------------------------------- | ---------------------------------------------------------------- |
| Can't determine paper's role in thread | Default to "extension"; flag for user review in the map          |
| Abstracts too short for clustering     | Read introduction + literature review section (first 5-10 pages) |
| Two papers seem to be the same         | Check DOI and page counts; deduplicate in manifest               |

### Output/Export

| Issue                              | Solution                                                                      |
| ---------------------------------- | ----------------------------------------------------------------------------- |
| knowledge-base.md getting too long | Summarize existing entries before adding; suggest restructuring if >300 lines |
| Notes directory cluttered          | Follow naming convention strictly:`{last_author}_{year}.md`                 |

### Environment

| Issue                             | Solution                                                                       |
| --------------------------------- | ------------------------------------------------------------------------------ |
| Long session, context compressing | Save research-map.md and current batch progress to disk; resume in new session |
