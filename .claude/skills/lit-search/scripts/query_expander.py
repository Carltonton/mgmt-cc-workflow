"""
Query expansion for broader literature search coverage.

Generates multiple search variants from a base query using:
1. Domain-specific synonym substitution
2. Related-term generation via OpenAlex concepts
3. Query reformulation for different API styles

This helps surface papers that use different terminology for the same concepts.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# Domain-specific synonym maps for management / organizational psychology
DOMAIN_SYNONYMS: Dict[str, Dict[str, List[str]]] = {
    "management": {
        "coaching": [
            "executive coaching",
            "mentoring",
            "development intervention",
            "guidance",
            "supervision",
        ],
        "AI": [
            "artificial intelligence",
            "algorithm",
            "machine learning",
            "automated system",
            "digital assistant",
            "chatbot",
        ],
        "performance": [
            "outcomes",
            "effectiveness",
            "productivity",
            "job performance",
            "work performance",
        ],
        "leadership": [
            "leader",
            "leader-member exchange",
            "supervisory behavior",
            "management style",
        ],
        "organizational": [
            "organisation",
            "workplace",
            "firm",
            "company",
            "corporate",
        ],
        "feedback": [
            "performance feedback",
            "evaluation",
            "appraisal",
            "review",
        ],
        "employee": [
            "worker",
            "staff",
            "subordinate",
            "team member",
        ],
        "working alliance": [
            "therapeutic alliance",
            "helping relationship",
            "coaching relationship",
            "rapport",
        ],
        "trust": [
            "trustworthiness",
            "credibility",
            "reliability",
        ],
        "anthropomorphism": [
            "humanization",
            "personification",
            "social attribution",
            "human-like",
        ],
    },
    "psychology": {
        "scale": [
            "measurement",
            "instrument",
            "questionnaire",
            "psychometric",
        ],
        "validation": [
            "validity",
            "reliability",
            "confirmatory factor analysis",
            "CFA",
        ],
        "wellbeing": [
            "well-being",
            "wellness",
            "flourishing",
            "thriving",
        ],
        "self-efficacy": [
            "confidence",
            "agency",
            "belief in capability",
        ],
        "motivation": [
            "goal orientation",
            "drive",
            "intrinsic motivation",
        ],
    },
}


def expand_query(
    query: str,
    domain: str = "management",
    strategies: Optional[List[str]] = None,
) -> List[str]:
    """Generate expanded search queries from a base query.

    Args:
        query: Original search query
        domain: Research domain for term expansion
        strategies: Which expansion strategies to apply.
            Options: "synonyms" (default). Future: "concepts".

    Returns:
        List of expanded queries (always includes the original).
    """
    if strategies is None:
        strategies = ["synonyms"]

    expanded = [query]  # Always include original

    if "synonyms" in strategies:
        expanded.extend(_expand_with_synonyms(query, domain))

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for q in expanded:
        q_lower = q.lower().strip()
        if q_lower not in seen:
            seen.add(q_lower)
            unique.append(q)

    return unique


def _expand_with_synonyms(query: str, domain: str) -> List[str]:
    """Generate synonym-based query variants.

    For each key term in the query that has synonyms in the domain map,
    generate a new query with that synonym substituted.
    """
    synonyms = DOMAIN_SYNONYMS.get(domain, {})
    if not synonyms:
        return []

    variants = []
    query_lower = query.lower()

    for term, replacements in synonyms.items():
        if term.lower() in query_lower:
            # Generate one variant per synonym (limit to top 2 to avoid explosion)
            for replacement in replacements[:2]:
                variant = query.replace(term, replacement)
                if variant != query:  # Only add if actually changed
                    variants.append(variant)

    return variants[:5]  # Cap at 5 variants to keep search manageable
