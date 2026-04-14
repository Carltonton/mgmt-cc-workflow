"""
Jupyter Notebook Generator for Academic Research
学术研究笔记本生成器

Usage:
    python new_notebook.py --kind experiment --title "Data Exploration" --out scripts/python/
"""

import argparse
import json
from pathlib import Path
from typing import Dict

# Template mapping
TEMPLATE_FILES: Dict[str, str] = {
    "experiment": "assets/experiment-template.ipynb",
    "tutorial": "assets/tutorial-template.ipynb",
}


def main() -> None:
    """Main entry point for notebook generation."""
    parser = argparse.ArgumentParser(
        description="Generate Jupyter notebook from template"
    )
    parser.add_argument(
        "--kind",
        choices=list(TEMPLATE_FILES.keys()),
        required=True,
        help="Type of notebook template to use"
    )
    parser.add_argument(
        "--title",
        required=True,
        help="Title for the notebook (replaces TITLE placeholder)"
    )
    parser.add_argument(
        "--out",
        default="scripts/python/",
        help="Output directory for generated notebook (default: scripts/python/)"
    )
    args = parser.parse_args()

    # Load template (assets folder is in parent directory)
    template_path = Path(__file__).parent.parent / "assets" / Path(TEMPLATE_FILES[args.kind]).name
    with open(template_path) as f:
        notebook = json.load(f)

    # Replace TITLE placeholder in all cells
    for cell in notebook["cells"]:
        if cell["cell_type"] == "markdown":
            cell["source"] = [
                line.replace("TITLE", args.title) for line in cell["source"]
            ]
        elif cell["cell_type"] == "code":
            cell["source"] = [
                line.replace("TITLE", args.title) for line in cell["source"]
            ]

    # Save notebook
    title_slug = args.title.lower().replace(" ", "-").replace("/", "-")
    output_path = Path(args.out) / f"{title_slug}.ipynb"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(notebook, f, indent=2)

    print(f"✓ Notebook created: {output_path}")


if __name__ == "__main__":
    main()
