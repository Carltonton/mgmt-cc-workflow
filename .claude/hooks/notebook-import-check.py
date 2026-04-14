#!/usr/bin/env python3
"""
Notebook Import Check Hook

检查 .ipynb 文件中是否存在外部项目模块导入（违反自包含原则）。

检测模式：
- from scripts.python...
- from scripts....
- from . import...
- from .. import...

Hook Event: PostToolUse (matcher: "Write|Edit")
Returns: Exit code 0 (non-blocking warning visible but doesn't stop work)

规范来源：.claude/skills/jupyter-notebook/SKILL.md - Notebook 自包含原则
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

# Colors for terminal output
CYAN = "\033[0;36m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
NC = "\033[0m"  # No color

# 禁止的导入模式（正则表达式）
FORBIDDEN_PATTERNS = [
    r'from\s+scripts\.python\.\w+',
    r'from\s+scripts\.\.\w+',
    r'from\s+\.\s+\w+',
    r'from\s+\.\.\s+\w+',
    r'from\s+\.\.?scripts',
    r'import\s+scripts\.',
]

# 允许的导入（误报排除）
ALLOWED_PATTERNS = [
    r'from\s+\.?\w+_template',  # 模板文件
    r'import\s+\w+\s+as\s+\w+',  # 标准包别名
]

# 跳过的目录
SKIP_DIRS = [
    "/docs/",
    "/templates/",
    "/.claude/",
    "/node_modules/",
    "/build/",
    "/dist/"
]


def check_forbidden_imports(code: str) -> list[str]:
    """检查代码中是否包含禁止的导入模式。

    Args:
        code: Python 代码字符串

    Returns:
        匹配到的禁止导入模式列表
    """
    violations = []

    for pattern in FORBIDDEN_PATTERNS:
        matches = re.findall(pattern, code)
        if matches:
            # 排除允许的误报
            for match in matches:
                is_allowed = False
                for allowed in ALLOWED_PATTERNS:
                    if re.search(allowed, match):
                        is_allowed = True
                        break
                if not is_allowed:
                    violations.append(match)

    return violations


def extract_python_from_ipynb(file_path: str) -> str:
    """从 notebook 中提取所有 Python 代码。

    Args:
        file_path: notebook 文件路径

    Returns:
        提取的 Python 代码字符串
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            import json
            notebook = json.load(f)
    except (json.JSONDecodeError, IOError, UnicodeDecodeError):
        return ""

    code_cells = []

    for cell in notebook.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = cell.get('source', [])
            if isinstance(source, list):
                source = '\n'.join(source)
            if source and isinstance(source, str):
                code_cells.append(source)

    return '\n'.join(code_cells)


def format_warning(file_path: str, violations: list[str]) -> str:
    """格式化警告消息。"""
    filename = Path(file_path).name
    violations_str = ', '.join(set(violations))

    return f"""
{YELLOW}⚠️ Notebook 自包含检查:{NC} {filename}
   → {RED}检测到外部项目导入: {violations_str}{NC}
   → {CYAN}规范: 所有代码必须内联在 notebook 中{NC}
   → 参见: .claude/skills/jupyter-notebook/SKILL.md
"""


def should_skip(file_path: str) -> bool:
    """检查是否跳过此文件。"""
    path = Path(file_path)

    # 只检查 .ipynb 文件
    if path.suffix != '.ipynb':
        return True

    # 跳过指定目录
    for skip_dir in SKIP_DIRS:
        if skip_dir in file_path:
            return True

    return False


def main() -> int:
    """Main hook entry point."""
    # Read hook input
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, IOError):
        return 0

    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        return 0

    # Skip if not a notebook file
    if not file_path.endswith('.ipynb'):
        return 0

    # Skip if in skipped directory
    if should_skip(file_path):
        return 0

    # Extract Python code from notebook
    code = extract_python_from_ipynb(file_path)

    if not code:
        return 0

    # Check for forbidden imports
    violations = check_forbidden_imports(code)

    if violations:
        # Show warning
        print(format_warning(file_path, violations))
        return 1  # Return non-zero to indicate violation found

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Fail open — never block Claude due to a hook bug
        sys.exit(0)
