# Portable Bibliography Search Module

Self-contained literature search system for Claude Code hooks.

## Overview

This module provides automatic literature search by intercepting WebSearch calls and redirecting them to direct API calls (CrossRef, Semantic Scholar, Tavily). It's designed to be portable - just copy the `.claude/` directory to any project and it works.

## Installation

### For New Projects

1. Copy the `.claude/` directory to your project root
2. Customize `.claude/hooks/literature_patterns.json` for your research domain
3. Set environment variables for API keys (optional but recommended)
4. Works immediately!

## Configuration

### Environment Variables (Optional)

Set these for better rate limits and Google Scholar replacement:

```bash
# CrossRef API (better rate limits with email)
export CROSSREF_EMAIL="your-email@example.com"

# Semantic Scholar API (optional but recommended)
export SEMANTIC_SCHOLAR_API_KEY="your-api-key"

# Tavily API (required for Google Scholar replacement)
export TAVILY_API_KEY="your-tavily-api-key"
```

### Get API Keys

| Service          | Link                                                | Free Tier           |
| ---------------- | --------------------------------------------------- | ------------------- |
| CrossRef         | https://api.crossref.org/                           | Yes, no key needed  |
| Semantic Scholar | https://www.semanticscholar.org/product/api#api-key | Yes, 100 req/5min   |
| Tavily           | https://tavily.com                                  | Yes, 1000 req/month |

### Custom Detection Patterns

Edit `.claude/hooks/literature_patterns.json` to customize what triggers literature search:

```json
{
  "academic_keywords": ["paper", "publication", "journal", "DOI"],
  "trigger_phrases": ["search for papers", "find literature"],
  "exclusion_patterns": ["wikipedia", "reddit"],
  "google_scholar_trigger": ["google scholar", "Google Scholar"]
}
```

## Usage

The hook automatically intercepts literature searches:

```
User: "search for papers on your research topic"
→ Hook detects "papers" = literature search
→ Uses CrossRef/Semantic Scholar APIs
→ Saves results to .claude/temp/search_results.md
→ Blocks WebSearch (saves MCP quota!)
→ Claude reads and summarizes results
```

### Google Scholar Replacement

When you mention "Google Scholar", it uses Tavily API instead:

```
User: "Search via Google Scholar for board fault lines papers"
→ Hook detects "Google Scholar"
→ Uses Tavily API (academic web search)
→ Returns comprehensive results
```

## Direct CLI Usage

You can also use the module directly from command line:

```bash
# Search CrossRef
python3 .claude/skills/lit-search/scripts/search_orchestrator.py \
    --query "research methodology" \
    --source crossref \
    --max-results 5

# Search all APIs
python3 .claude/skills/lit-search/scripts/search_orchestrator.py \
    --query "machine learning" \
    --source all
```

## Directory Structure

```
.claude/
├── scripts/                           # Scripts module
│   ├── __init__.py                   # Public API
│   ├── config.py                     # Configuration
│   ├── exceptions.py                 # Custom exceptions
│   ├── api_base.py                   # Base client class
│   ├── crossref_client.py            # CrossRef API
│   ├── semantic_scholar_client.py    # Semantic Scholar API
│   ├── tavily_client.py              # Tavily API (Google Scholar)
│   ├── search_orchestrator.py        # Main search logic
│   └── README.md                     # This file
├── hooks/
│   ├── literature-search.py          # Hook interceptor
│   └── literature_patterns.json      # Detection patterns
├── temp/                              # Auto-created
│   └── search_results.md              # Search results
└── settings.json                      # Hook configuration
```

## Dependencies

Required Python packages (already in requirements.txt):

```
requests>=2.31.0
tenacity>=8.2.0
ratelimit>=2.2.0
tavily-python>=0.3.0  # Optional, for Google Scholar
```

Install with:

```bash
pip install requests tenacity ratelimit tavily-python
```

## How It Works

### Detection Logic

The hook uses pattern matching to detect literature searches:

1. **Override phrases** → Proceed (not literature)
2. **Exclusion patterns** → Proceed (not literature)
3. **Google Scholar trigger** → Use Tavily API
4. **Trigger phrases** → Literature search
5. **Academic keywords** → Literature search
6. **Default** → Proceed with WebSearch

### API Priority

When a literature search is detected:

1. **CrossRef** - Academic metadata, no key required
2. **Semantic Scholar** - Citation counts, abstracts
3. **Tavily** - Web search (when Google Scholar mentioned)

Results are deduplicated and saved as Markdown.

## Troubleshooting

### Hook Not Working

```bash
# Test the hook directly
echo '{"tool_name": "WebSearch", "parameters": {"query": "test papers"}}' | \
python3 .claude/hooks/literature-search.py

# Should return: {"decision": "block", "reason": "..."}
```

### Module Not Found

Ensure PYTHONPATH is set in `.claude/settings.json`:

```json
"command": "cd \"$CLAUDE_PROJECT_DIR\" && PYTHONPATH=\"$CLAUDE_PROJECT_DIR/.claude\" python3 .claude/hooks/literature-search.py"
```

### API Rate Limits

- CrossRef: 1 request/second (polite usage)
- Semantic Scholar: 20 req/5min free, 100 req/5min with key
- Tavily: 1000 requests/month free tier

Set API keys for higher limits.

## Version

**Portable Module**: v0.2.0-portable

## License

This module is part of the Claude Code academic workflow template.
