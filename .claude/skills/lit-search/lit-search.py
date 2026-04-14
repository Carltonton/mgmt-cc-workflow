#!/usr/bin/env python3
"""Entry point for lit-search. Handles PYTHONPATH so callers don't need boilerplate."""
import sys
import os

_SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SKILL_DIR)
os.environ["PYTHONPATH"] = _SKILL_DIR

from scripts.search_orchestrator import main

sys.argv = [sys.argv[0]] + sys.argv[1:]
main()
