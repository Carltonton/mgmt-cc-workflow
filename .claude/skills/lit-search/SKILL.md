---
name: lit-search
description: Academic literature search, reference lookup, and metadata collection using OpenAlex, CrossRef, Semantic Scholar, Tavily, SSRN, and Unpaywall APIs. Automatically collects paper metadata after each search.
  Triggers: "search for papers", "literature search", "find publications", "DOI lookup", "paper references", "extract references", "reference extraction"
  Replaces: WebSearch for academic queries (saves MCP quota).
version: 2.0.0
argument-hint: "[query] --source [openalex|crossref|semantic-scholar|google-scholar|ssrn|all] --references [path.md] --doi [DOI] --topic [topic-dir] --abs-rating [3|4|4*|all] --field [Management|Psychology|etc] --expand --chain [DOI1,DOI2]"
allowed-tools: ["Read", "Write", "Bash"]
---
# Academic Literature Search

Search academic literature using direct API calls to OpenAlex, CrossRef, Semantic Scholar, Tavily, and SSRN. Bypasses WebSearch to save MCP quota and provides richer academic metadata. **Automatically persists paper metadata to `docs/{topic}/metadata.json` after each search, then screens abstracts for relevance.**

## Workflow Overview

The skill supports a cyclic literature discovery workflow:

```
Step 1: API Search
  /lit-search "query" → metadata.json → screen abstracts → paper-list.md

Step 2: Manual PDF Processing
  Download PDFs → references/articles_pdf → auto-convert to references/articles_md

Step 3: Reference Extraction
  /lit-search --references references/articles_md/Paper.md → extract refs → re-run Step 1 logic
```

Each cycle expands the reference collection. Papers from reference extraction go through the same screening pipeline as API search results.

## Execution Protocol

When this skill is invoked, follow these three steps **in order**:

### Step 1: Mode Judgment

Parse `$ARGUMENTS` to determine the search mode:

| Flag Present             | Mode                 | Action                                  |
| ------------------------ | -------------------- | --------------------------------------- |
| `--references path.md` | Reference extraction | Extract references from a markdown file |
| `--chain DOI1,DOI2`    | Citation chaining    | Find papers cited by seed DOIs          |
| `--doi DOI`            | Single DOI lookup    | Fetch metadata for one paper            |
| Query string only        | Topic search         | Search by keyword across APIs           |

### Step 2: Execute Search

#### Protocol A: API Search (Topic Search / DOI Lookup)

1. Build the CLI command from parsed arguments
2. Run via Bash:
   ```bash
   python3 .claude/skills/lit-search/lit-search.py --query "..." --source all --max-results 10
   ```
3. The script outputs results as Markdown and persists ALL results to `docs/{topic}/metadata.json`
4. Read and display the Markdown output to the user

#### Protocol B: Reference Extraction (`--references path.md`)

1. Run the conversion and extraction script:
   ```bash
   python3 .claude/skills/lit-search/scripts/convert_pdfs_to_md.py --input path.md --extract-references --topic coaching-papers
   ```
2. This extracts all references from the markdown file and saves them to `docs/{topic}/metadata.json`
3. **Follow up with DOI/abstract enrichment** (CrossRef first, then S2):
   ```bash
   cd "$PROJECT_DIR" && PYTHONPATH=.claude/skills/lit-search \
     python3 -m scripts.s2_enrich --topic coaching-papers --source markdown_reference --crossref-only
   ```
4. Read and display the extracted references to the user

#### Protocol C: Citation Chaining (`--chain DOI1,DOI2`)

1. Build the CLI command:
   ```bash
   python3 .claude/skills/lit-search/lit-search.py --chain "DOI1,DOI2" --topic coaching-papers
   ```
2. This uses Semantic Scholar's `get_references()` to find papers cited by the seed DOIs
3. Results go through the same merge and metadata pipeline

**If no results found**, stop here and inform the user.

### Step 3: Relevance Screening

**After every successful search (Step 2), screen the results for relevance.**

#### 3a. Read metadata

Read `docs/{topic}/metadata.json` — focus on papers from the current search (papers with the most recent `added_date`).

#### 3b. Screen each paper

##### Step 0: ABS Journal Hard Filter

Read `.claude/skills/lit-search/scripts/abs_journals.json` and extract all journal names strings from the `journals` → `4*` / `4` / `3` sections.
For each paper from the current search:

1. **ABS Journal Check**: Compare the paper's `journal` field against the ABS journal name list.
   - Normalize both names (lowercase, strip punctuation).
   - A match occurs when:
     - **Exact match** (any length), OR
     - **Substring match** for ABS names with ≥ 3 words (e.g., "Human Resource Development International" matches even if stored with slight variation). Short ABS names (1-2 words like "Management Science", "Omega") require exact match to avoid false positives.
   - Journal matches an ABS entry → proceed to Step 1 (relevance screening)
   - Journal does NOT match → **SKIP** with reason: "Non-ABS journal: [journal name]"

##### Step 1: Relevance Screening (only for papers that passed ABS filter)

- If the paper has an **abstract**: read title + abstract + journal + year, then judge KEEP or SKIP
- If the paper has **no abstract**: auto-keep with `[AUTO-KEEP]` tag

**Relevance judgment** — infer the research domain from the search query + topic name:

- **KEEP**: Papers directly relevant to the search intent, or methodologically relevant
- **SKIP**: Papers clearly unrelated to the research domain
- **BORDERLINE → KEEP**: When uncertain, prefer keeping for manual review

#### 3c. Write paper-list.md

Append results to `docs/{topic}/paper-list.md`.

**If the file exists**: read it first, deduplicate by DOI against existing entries, then append a new dated section.
**If the file doesn't exist**: create it with a header.

Use this format for the new section:

```markdown
---

## Search: "query string" — YYYY-MM-DD

**Source**: OpenAlex + CrossRef + Semantic Scholar | **Kept**: N / **Skipped**: M / **Auto-kept (no abstract)**: K

### Kept Papers

1. **Paper Title**

   - **Authors**: Author One, Author Two
   - **Year**: 2024
   - **DOI**: 10.xxxx/xxxxx
   - **Journal**: Journal Name
   - **Focus**: 1-line summary from abstract
   - **Relevance**: 1-line reason for keeping

2. **Another Paper Title**

   ...

### Skipped Papers

- **Paper Title** (DOI: 10.xxxx/yyyy) — Reason: 1-line skip reason

### Auto-Kept (No Abstract — Manual Review Needed)

- **Paper Title** (DOI: 10.xxxx/zzzz) — No abstract available
```

#### 3d. Print summary

After writing the file, print a one-line summary:

```
Screening: 8 kept / 4 skipped / 2 auto-kept (no abstract) → docs/{topic}/paper-list.md
```

---

## API Sources

| Source                     | Best For                     | Requires Key                 | Rate Limit          |
| -------------------------- | ---------------------------- | ---------------------------- | ------------------- |
| **OpenAlex** | Abstracts, ISSN batch filtering, concept search | No (mailto for polite pool) | 10 req/sec (polite) |
| **CrossRef**         | Journal metadata, DOI lookup | No (email recommended)       | 1 req/sec           |
| **Semantic Scholar** | Citation counts, abstracts, citation chaining | Optional (100→300 req/5min) | 20 req/5min free    |
| **Google Scholar** (via Tavily) | Academic web search across publisher sites | Yes (1000 req/month free) | Returns actual paper pages from publisher domains |
| **SSRN** (via Tavily) | Management working papers, preprints | Yes (Tavily key) | Via Tavily limits |
| **Unpaywall** | OA status enrichment (not search) | No (email) | 100K req/day |

**Merge priority**: OpenAlex > CrossRef > Semantic Scholar > Google Scholar > SSRN

## Usage Examples

### Example 1: Search ABS 4* Management Journals

```bash
/lit-search "board governance" --field Management --abs-rating 4* --max-results 10
```

**Output**: Papers from Academy of Management Journal, Journal of Management, etc.

### Example 2: OpenAlex Search (abstracts + ISSN filtering)

```bash
/lit-search "AI coaching performance" --source openalex --abs-rating 4* --max-results 20
```

**Output**: Papers with abstracts from ABS 4* journals. OpenAlex filters all ISSNs in a single API call.

### Example 3: Citation Chaining

```bash
/lit-search --chain "10.1177/00218863241283919,10.5465/amj.2023.1308" --topic coaching-papers
```

**Output**: Papers cited by the two seed papers, using Semantic Scholar's reference graph.

### Example 4: Query Expansion

```bash
/lit-search "coaching effectiveness" --expand --source all --topic coaching-papers
```

**Output**: Searches multiple query variants (e.g., "mentoring effectiveness", "development intervention effectiveness") for broader coverage.

### Example 5: DOI Lookup

```bash
/lit-search --doi 10.1287/mksc.2018.0886 --source semantic-scholar
```

**Output**: Paper metadata with abstract.

### Example 6: Reference Extraction from Markdown

```bash
/lit-search --references references/articles_md/AMJ_kilduff_2015.md --topic coaching-papers
```

**Output**: Extracts all references from the markdown file, saves to metadata.json. Run CrossRef DOI lookup as a follow-up to enrich with DOIs.

---

## Automatic Metadata Collection

Every search automatically persists structured paper metadata to `docs/{topic}/metadata.json`.

### How It Works

- After each search, results are normalized and deduplicated by DOI
- New papers are appended; existing entries are updated with any new fields
- `last_updated` timestamp tracks the most recent write
- Metadata collection is **non-fatal** — if it fails, search results are unaffected

### Topic Configuration

```bash
# Default topic (coaching-papers)
/lit-search "coaching" --topic coaching-papers

# Different topic
/lit-search "machine learning interpretability" --topic ml-interpretability
```

### Metadata Schema

Standard fields per paper entry:

```json
{
  "_meta": {
    "topic": "coaching-papers",
    "last_updated": "2026-04-27T14:00:00Z",
    "total_entries": 42,
    "created_date": "2026-03-30T12:00:00Z"
  },
  "papers": {
    "journal_Author_year": {
      "title": "...",
      "authors": ["Author One", "Author Two"],
      "year": 2024,
      "journal": "Academy of Management Journal",
      "doi": "10.5465/amj.2023.1308",
      "abstract": "...",
      "keywords": [],
      "source": "openalex",
      "added_date": "2026-04-27T14:00:00Z"
    }
  }
}
```

**Key format**: `journal_Author_year` (matches PDF naming in `references/articles_pdf/`)

**Standard fields**: `title`, `authors`, `year`, `journal`, `doi`, `abstract`, `keywords`, `source`, `added_date`

---

## ABS Journal Filtering

The module includes 468 ABS-rated journals (3+) with filtering capability:

### Available Ratings

- **4*** Elite journals (AMJ, AMR, JAP)
- **4** Excellent journals
- **3** Good journals
- **all** All 3+ journals

### Available Fields

- Management
- Psychology
- Marketing
- Finance
- Economics
- Sociology
- And more...

### Filter Logic

- **OpenAlex**: Uses pipe-separated ISSN filtering in a single API call (most efficient)
- **CrossRef**: Uses ISSN filtering (batch mode searches all target journals)
- **Semantic Scholar**: Screening-time filtering (ABS check happens after search)
- **Google Scholar** (Tavily): Uses `include_domains` restricted to academic publisher sites
- **SSRN** (Tavily): Domain-restricted to ssrn.com

---

## Behind the Scenes

This skill includes a self-contained scripts module:

```
.claude/skills/lit-search/
├── scripts/
│   ├── __init__.py                # Public API
│   ├── shared_types.py            # Paper dataclass + matching
│   ├── search_orchestrator.py     # Main search logic
│   ├── query_expander.py          # Query expansion strategies
│   ├── metadata_manager.py        # Metadata persistence & deduplication
│   ├── openalex_client.py         # OpenAlex API (abstracts + ISSN batch)
│   ├── unpaywall_client.py        # Unpaywall OA enrichment
│   ├── ssrn_client.py             # SSRN search (via Tavily)
│   ├── crossref_client.py          # CrossRef API
│   ├── semantic_scholar_client.py  # Semantic Scholar API
│   ├── tavily_client.py            # Google Scholar (via Tavily include_domains)
│   ├── doi_utils.py                # DOI utilities
│   ├── api_base.py                 # Base client class
│   ├── exceptions.py               # Custom exceptions
│   ├── abs_journals.json            # ABS journal database
│   ├── config.py                   # Configuration
│   ├── convert_pdfs_to_md.py       # PDF→Markdown conversion + reference extraction
│   ├── s2_enrich.py                # S2 + Unpaywall enrichment
│   └── temp/                       # Search results cache
└── SKILL.md                        # This file
```

### How It Works

1. Parse query and parameters from `$ARGUMENTS`
2. Determine search mode (topic search vs. reference extraction vs. DOI lookup vs. citation chaining)
3. Execute via appropriate protocol (API search, reference extraction, or citation chain)
4. API clients query OpenAlex, CrossRef, Semantic Scholar, Tavily, SSRN
5. Results deduplicated by DOI, persisted to `metadata.json`
6. Claude screens abstracts for relevance
7. Kept papers appended to `paper-list.md`

---

## Gotchas

### Configuration

| Issue            | Solution                                             |
| ---------------- | ---------------------------------------------------- |
| Module not found | Ensure `.claude/` exists in project root           |
| API key errors   | Check `.env` file format (no quotes around values) |

### Data/Input

| Issue            | Solution                              |
| ---------------- | ------------------------------------- |
| No results found | Try broader query or different source |

### Processing

| Issue            | Solution                                                   |
| ---------------- | ---------------------------------------------------------- |
| Slow search      | Multiple sources take time; use single source for speed    |
| Duplicate papers | Normal across sources; deduplication happens automatically |

### S2 Rate Limiting

During interactive sessions, S2 **fails fast** on rate limits — other sources return immediately.
To enrich papers with S2 data between sessions, run in background:

```bash
cd "$PROJECT_DIR" && PYTHONPATH=.claude/skills/lit-search \
  python3 -m scripts.s2_enrich --topic coaching-papers
```

### Environment

| Issue                      | Solution                                                                 |
| -------------------------- | ------------------------------------------------------------------------ |
| Virtual environment issues | Activate venv:`source .venv/bin/activate`                              |
| macOS proxy issues         | Unset proxy vars:`unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY` |

---

## References

- **Module README**: `.claude/skills/lit-search/scripts/README.md`
- **ABS Journal Database**: `.claude/skills/lit-search/scripts/abs_journals.json`
- **Hook Configuration**: `.claude/settings.json` (PreToolUse hooks)

---

## Version History

- **v2.0.0** (2026-04-27): Major upgrade — OpenAlex client (ISSN batch, abstracts, concepts), Unpaywall OA enrichment, SSRN via Tavily, Paper dataclass for standardized types, query expansion with domain-specific synonyms, citation chaining via S2 `get_references()`, updated merge priority (OpenAlex first), `--expand` and `--chain` CLI flags
- **v1.7.0** (2026-04-12): Comprehensiveness fixes — CrossRef ISSN batching, S2 multi-journal venue filter removal, Tavily max raised 20→50, DOI supplement cap 3→10, metadata-rich merge priority
- **v1.6.0** (2026-04-10): Renamed `tavily` source to `google-scholar`; uses `include_domains` with academic publisher domains
- **v1.5.0** (2026-03-31): Unified SKILL.md with actual implementation
- **v1.4.0** (2026-03-31): Rewrote `--references` mode
- **v1.3.0** (2026-03-30): S2 fail-fast on rate limit + background enrichment script
- **v1.2.0** (2026-03-30): Added Step 3 relevance screening → paper-list.md output
- **v1.1.0** (2026-03-30): Merged lit-refs, added automatic metadata collection
- **v1.0.0** (2026-03-18): Initial skill creation from scripts module
