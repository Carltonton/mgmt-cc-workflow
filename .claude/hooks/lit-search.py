#!/usr/bin/env python3
"""
Literature Search Hook for Claude Code

PreToolUse hook that intercepts WebSearch calls and redirects literature searches
to direct API calls (CrossRef, Semantic Scholar) instead of using MCP quota.

Hook Event: PreToolUse
Matcher: WebSearch (only)

Behavior:
  1. Parse the query from WebSearch parameters
  2. Detect if it's a literature search (using patterns)
  3. If yes: run Python API client, save results, block WebSearch
  4. If no: proceed with WebSearch (general web searches)

Usage in .claude/settings.json:
    "PreToolUse": [{
      "matcher": "WebSearch",
      "hooks": [{
        "type": "command",
        "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/literature-search.py",
        "timeout": 30
      }]
    }]
"""

from __future__ import annotations

import json
import sys
import os
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def get_hook_input() -> dict:
    """
    Read hook input from stdin.

    Returns:
        Parsed JSON input from the hook system
    """
    try:
        hook_input = json.load(sys.stdin)
        return hook_input
    except (json.JSONDecodeError, IOError):
        return {}


def get_project_dir() -> Path:
    """
    Get the project directory from environment.

    Returns:
        Path to the project directory
    """
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if project_dir:
        return Path(project_dir)
    # Fallback to current working directory
    return Path.cwd()


def load_patterns(project_dir: Path) -> dict:
    """
    Load literature search detection patterns.

    Args:
        project_dir: Path to the project directory

    Returns:
        Dictionary with detection patterns
    """
    patterns_path = project_dir / ".claude" / "skills" / "lit-search" / "scripts" / "literature_patterns.json"

    try:
        with open(patterns_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Could not load patterns from {patterns_path}: {e}")
        # Return default patterns
        return {
            "academic_keywords": ["paper", "publication", "journal", "DOI", "cite"],
            "trigger_phrases": ["search for papers", "find literature"],
            "exclusion_patterns": ["wikipedia", "reddit", "news"],
            "override_phrases": ["do not use hook", "bypass hook"],
        }


def is_google_scholar_request(query: str, patterns: dict) -> bool:
    """
    Check if the query explicitly requests Google Scholar.

    When Google Scholar is requested, we redirect to Tavily API instead.

    Args:
        query: The search query
        patterns: Detection patterns dictionary (should contain google_scholar_trigger)

    Returns:
        True if Google Scholar is requested, False otherwise
    """
    query_lower = query.lower()
    google_triggers = patterns.get("google_scholar_trigger", ["google scholar", "scholar.google"])

    for trigger in google_triggers:
        if trigger.lower() in query_lower:
            logger.debug(f"Google Scholar trigger detected: {trigger}")
            return True

    return False


def is_literature_search(query: str, patterns: dict) -> bool:
    """
    Detect if a query is a literature search.

    Detection logic (in order of priority):
    1. Check if query contains any override_phrases → proceed (not literature)
    2. Check if query contains any exclusion_patterns → proceed (not literature)
    3. Check if query contains any trigger_phrases → block (is literature)
    4. Check if query contains academic_keywords → block (is literature)
    5. Default → proceed (not literature)

    Args:
        query: The search query
        patterns: Detection patterns dictionary

    Returns:
        True if this is a literature search, False otherwise
    """
    query_lower = query.lower()

    # 1. Check override phrases (user explicitly wants to bypass hook)
    for phrase in patterns.get("override_phrases", []):
        if phrase.lower() in query_lower:
            logger.debug(f"Override phrase detected: {phrase}")
            return False

    # 2. Check exclusion patterns (general web searches)
    for pattern in patterns.get("exclusion_patterns", []):
        if pattern.lower() in query_lower:
            logger.debug(f"Exclusion pattern detected: {pattern}")
            return False

    # 3. Check trigger phrases (explicit literature search)
    for phrase in patterns.get("trigger_phrases", []):
        if phrase.lower() in query_lower:
            logger.debug(f"Trigger phrase detected: {phrase}")
            return True

    # 4. Check academic keywords
    has_academic = any(keyword.lower() in query_lower for keyword in patterns.get("academic_keywords", []))

    if has_academic:
        logger.debug("Academic keyword detected")
        return True

    # 5. Default: not a literature search
    return False


def run_literature_search(query: str, project_dir: Path) -> dict:
    """
    Execute the literature search via Python API client.

    Args:
        query: The search query
        project_dir: Path to the project directory

    Returns:
        Dictionary with 'success' status and 'message'
    """
    try:
        orchestrator_path = project_dir / ".claude" / "skills" / "lit-search" / "scripts" / "search_orchestrator.py"

        if not orchestrator_path.exists():
            logger.error(f"Search orchestrator not found: {orchestrator_path}")
            logger.error("Ensure .claude/skills/lit-search/scripts/ directory exists")
            return {
                "success": False,
                "message": f"Search orchestrator not found at {orchestrator_path}"
            }

        # Run the orchestrator
        input_data = json.dumps({"query": query, "max_results": 10})
        result = subprocess.run(
            [sys.executable, str(orchestrator_path)],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(project_dir),
        )

        if result.returncode == 0:
            # Success - results were saved
            temp_file = project_dir / ".claude" / "skills" / "lit-search" / "scripts" / "temp" / "search_results.md"
            if temp_file.exists():
                logger.info(f"Search results saved to {temp_file}")
                return {
                    "success": True,
                    "results_file": str(temp_file),
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "message": "Search completed but no results file found"
                }
        else:
            logger.error(f"Orchestrator failed: {result.stderr}")
            return {
                "success": False,
                "message": f"Search failed: {result.stderr}"
            }

    except subprocess.TimeoutExpired:
        logger.error("Search timed out")
        return {
            "success": False,
            "message": "Search timed out after 30 seconds"
        }
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {
            "success": False,
            "message": f"Search error: {e}"
        }


def main():
    """Main hook entry point."""
    # Read hook input
    hook_input = get_hook_input()

    # Get the WebSearch query
    parameters = hook_input.get("parameters", {})
    query = parameters.get("query", "")

    if not query:
        # No query, proceed with WebSearch
        output = {"decision": "proceed"}
        json.dump(output, sys.stdout)
        return 0

    # Get project directory
    project_dir = get_project_dir()

    # Load detection patterns
    patterns = load_patterns(project_dir)

    # Priority 1: Check if Google Scholar is explicitly requested
    if is_google_scholar_request(query, patterns):
        logger.info(f"Google Scholar request detected: {query}")

        # Run Tavily search (Google Scholar replacement)
        result = run_literature_search(query, project_dir)

        if result["success"]:
            # Block WebSearch and tell Claude to read the results
            output = {
                "decision": "block",
                "reason": "Google Scholar search detected. Results saved to .claude/skills/lit-search/scripts/temp/search_results.md (via Tavily API). Please read that file for the search results."
            }
            json.dump(output, sys.stdout)
            return 0
        else:
            # Tavily search failed - fall back to WebSearch
            logger.warning(f"Tavily search failed: {result['message']}")
            logger.info("Proceeding with WebSearch")
            output = {"decision": "proceed"}
            json.dump(output, sys.stdout)
            return 0

    # Priority 2: Check if this is a general literature search
    if is_literature_search(query, patterns):
        logger.info(f"Literature search detected: {query}")

        # Run the literature search
        result = run_literature_search(query, project_dir)

        if result["success"]:
            # Block WebSearch and tell Claude to read the results
            temp_file = project_dir / ".claude" / "skills" / "lit-search" / "scripts" / "temp" / "search_results.md"
            output = {
                "decision": "block",
                "reason": f"Literature search detected. Results saved to .claude/skills/lit-search/scripts/temp/search_results.md. Please read that file for the search results."
            }
            json.dump(output, sys.stdout)
            return 0
        else:
            # Search failed - log and proceed with WebSearch
            logger.warning(f"Literature search failed: {result['message']}")
            logger.info("Proceeding with WebSearch")
            output = {"decision": "proceed"}
            json.dump(output, sys.stdout)
            return 0
    else:
        # Not a literature search - proceed with WebSearch
        logger.debug(f"Not a literature search: {query}")
        output = {"decision": "proceed"}
        json.dump(output, sys.stdout)
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Fail open — never block Claude due to a hook bug
        logger.exception("Hook error - failing open")
        output = {"decision": "proceed"}
        json.dump(output, sys.stdout)
        sys.exit(0)
