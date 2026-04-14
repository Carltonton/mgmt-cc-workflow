#!/usr/bin/env python3
"""
Batch convert PDF files to Markdown format using MinerU, and extract references from markdown.

MinerU is a high-accuracy document parsing tool that converts PDFs to Markdown with:
- Better table extraction (HTML format)
- Better formula/math extraction (LaTeX format)
- Automatic OCR for scanned PDFs
- Multi-column layout support

Usage:
    python convert_pdfs_to_md.py
    python convert_pdfs_to_md.py --input /path/to/pdfs --output /path/to/markdown
"""

from pathlib import Path
import re
import sys
import os
import subprocess
import shutil
import tempfile
from typing import Any, Dict, List, Optional, Tuple

# Add parent directory to path for imports
_SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
if _SKILL_DIR not in sys.path:
    sys.path.insert(0, _SKILL_DIR)

from config import DEFAULT_TOPIC, REFERENCES_DIR


# =============================================================================
# MinerU conversion functions
# =============================================================================

def mineru_to_markdown(pdf_path: Path, output_path: Path, backend: str = "pipeline") -> Path:
    """
    Convert PDF to Markdown format using MinerU.

    Args:
        pdf_path: Path to the input PDF file
        output_path: Path to the output Markdown file
        backend: MinerU backend to use ("pipeline" for CPU, "hybrid-auto-engine" for GPU)

    Returns:
        Path to the generated markdown file
    """
    # Estimate timeout based on file size (approx 30 seconds per MB, min 600 seconds)
    file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
    timeout = max(600, int(file_size_mb * 30))  # At least 10 minutes

    print(f"  Converting {pdf_path.name} ({file_size_mb:.1f} MB, timeout: {timeout}s)...", file=sys.stderr, flush=True)

    # Create a temporary directory for MinerU output
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_output = Path(temp_dir)

        # Build MinerU command using Python module (more reliable than shell script)
        cmd = [
            sys.executable, "-m", "mineru.cli.client",
            "-p", str(pdf_path),
            "-o", str(temp_output),
            "-b", backend,
            "-l", "en",  # Language: English
        ]

        # Run MinerU
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True
            )
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"MinerU conversion timed out for {pdf_path.name} after {timeout}s. Try using a smaller file or increase timeout.")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"MinerU failed: {e.stderr}") from e

        # Find the generated markdown file
        # MinerU creates: output_dir/pdf_name/auto/pdf_name.md
        pdf_stem = pdf_path.stem
        mineru_md_dir = temp_output / pdf_stem / "auto"
        mineru_md_path = mineru_md_dir / f"{pdf_stem}.md"

        if not mineru_md_path.exists():
            raise FileNotFoundError(f"MinerU did not create expected markdown file: {mineru_md_path}")

        # Create output directory and copy the markdown file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(mineru_md_path, output_path)

        return output_path


def pdf_to_markdown(pdf_path: Path, output_path: Path, backend: str = "pipeline") -> None:
    """
    Wrapper function for PDF to Markdown conversion using MinerU.

    Maintains compatibility with the old API while using MinerU internally.

    Args:
        pdf_path: Path to the input PDF file
        output_path: Path to the output Markdown file
        backend: MinerU backend to use (default: "pipeline" for CPU)
    """
    try:
        result_path = mineru_to_markdown(pdf_path, output_path, backend)
        print(f"Converted: {pdf_path.name} -> {result_path.name}")
    except Exception as e:
        print(f"Error converting {pdf_path.name}: {e}", file=sys.stderr)
        raise


# =============================================================================
# Reference extraction functions (retained from original)
# =============================================================================

def find_references_section(text: str) -> str:
    """
    Locate the REFERENCES section in markdown text.

    Args:
        text: Full markdown content

    Returns:
        Text of the REFERENCES section (from header to EOF)

    Raises:
        ValueError: If no references section found
    """
    patterns = [
        re.compile(r'^REFERENCES\s*$', re.MULTILINE),
        re.compile(r'^References\s*$', re.MULTILINE),
        re.compile(r'^REFERENCES\d', re.MULTILINE),
    ]

    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return text[match.start():]

    raise ValueError("No REFERENCES section found in markdown text")


def clean_reference_text(section_text: str) -> str:
    """
    Remove PDF artifacts from reference section text.

    Args:
        section_text: Raw references section text

    Returns:
        Cleaned reference text
    """
    lines = section_text.split('\n')
    cleaned = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if cleaned and cleaned[-1] != '':
                cleaned.append('')
            continue

        if stripped in ('---', '***', '___'):
            continue

        if re.match(r'^\d{4}\s+\d+\s+[A-Z]', stripped):
            continue

        if re.match(r'^\d{4}$', stripped):
            continue

        if re.match(r'^\d{1,4}$', stripped):
            continue

        if re.match(r'^[A-Z][a-z]+,\s+[A-Z][a-z]+', stripped) \
           and not re.search(r'\d{4}', stripped):
            continue

        cleaned.append(stripped)

    text = '\n'.join(cleaned)
    text = re.sub(r'-\n(\S)', r'\1', text)
    text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text


def split_into_references(cleaned_text: str) -> list:
    """
    Split cleaned reference text into individual reference blocks.

    Args:
        cleaned_text: Cleaned reference section text

    Returns:
        List of individual reference text strings
    """
    lines = cleaned_text.split('\n')
    references = []
    current_ref = []

    REF_START = re.compile(
        r'^([A-Z][a-z]+(?:[-\'][A-Z][a-z]+)*)'
        r'\s*[,.]\s*'
        r'.*?'
        r'\b((?:19|20)\d{2})\b'
    )

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_ref:
                current_ref.append('')
            continue

        if current_ref and REF_START.match(stripped):
            ref_text = ' '.join(current_ref).strip()
            if ref_text:
                references.append(ref_text)
            current_ref = [stripped]
        else:
            current_ref.append(stripped)

    if current_ref:
        ref_text = ' '.join(current_ref).strip()
        if ref_text:
            references.append(ref_text)

    return references


def parse_single_reference(raw: str) -> Dict[str, Any]:
    """
    Parse a single reference text block into structured data.

    Args:
        raw: Single reference text (potentially multi-line)

    Returns:
        Parsed reference dict
    """
    ref = {
        'raw_text': raw,
        'authors': [],
        'year': None,
        'title': '',
        'journal': None,
        'volume': None,
        'pages': None,
        'publisher': None,
        'doi_in_text': None,
        'source': 'markdown_reference',
        'ref_type': 'unknown',
        'parse_quality': 'low',
    }

    doi_match = re.search(r'(10\.\d{4,9}/[^\s\]>\"\'`,;]+)', raw)
    if doi_match:
        ref['doi_in_text'] = doi_match.group(1)

    year_match = re.search(r'\b((?:19|20)\d{2})\b', raw)
    if year_match:
        ref['year'] = int(year_match.group(1))
        year_pos = year_match.start()
    else:
        return ref

    authors_text = raw[:year_pos].rstrip('. ,')
    metadata_text = raw[year_pos + len(year_match.group(0)):].strip().lstrip('. ')

    ref['authors'] = parse_authors(authors_text)

    if re.search(r'\bIn\b', metadata_text) or re.search(r'\(Eds?\.\)', metadata_text):
        ref['ref_type'] = 'book_chapter'
        parse_book_chapter_metadata(ref, metadata_text)
    elif re.search(r'\d+\s*:\s*\d+', metadata_text) and not re.search(r'Available at', metadata_text):
        ref['ref_type'] = 'journal_article'
        parse_journal_metadata(ref, metadata_text)
    elif re.search(r'Available at|http', metadata_text):
        ref['ref_type'] = 'web'
        parse_web_metadata(ref, metadata_text)
    elif re.search(r'[A-Z][a-z]+(?:\s[A-Z])?:\s*[A-Z][a-z]+', metadata_text):
        ref['ref_type'] = 'book'
        parse_book_metadata(ref, metadata_text)

    if ref['title'] and ref['journal'] and ref['authors']:
        ref['parse_quality'] = 'high'
    elif ref['title'] and ref['authors']:
        ref['parse_quality'] = 'medium'

    return ref


def parse_authors(authors_text: str) -> list:
    """
    Parse authors from author portion of reference.

    Handles:
    - "Last, F. M."
    - "Last, F. M., & Last, F. M."
    - "Last, F. M., Last, F. M., & Last, F. M."
    - "Last et al."
    """
    authors = []

    parts = re.split(r'\s*&\s*', authors_text)

    for part in parts:
        subparts = re.split(r',\s*', part)

        i = 0
        while i < len(subparts):
            if i + 2 < len(subparts):
                last_name = subparts[i].strip()
                if last_name and re.match(r'^[A-Z][a-z]+', last_name):
                    initials = subparts[i + 1].strip()
                    if initials and re.match(r'^[A-Z]\.$', initials):
                        middle = subparts[i + 2].strip()
                        if middle and re.match(r'^[A-Z]\.$', middle):
                            authors.append(f"{last_name}, {initials} {middle}")
                            i += 3
                            continue

            if i + 1 < len(subparts):
                last_name = subparts[i].strip()
                if last_name and re.match(r'^[A-Z][a-z]+', last_name):
                    initials = subparts[i + 1].strip()
                    if initials and re.match(r'^[A-Z]\.$', initials):
                        authors.append(f"{last_name}, {initials}")
                        i += 2
                        continue

            if subparts[i].strip():
                authors.append(subparts[i].strip())
            break

    return authors


def parse_journal_metadata(ref: Dict, metadata: str) -> None:
    """Parse journal article metadata: "Title. Journal, Vol: Pages." """
    title_match = re.match(r'(.*?)\.\s+([A-Z][^.]+?)\s*,\s*(\d+)?:?\s*(\d+)?-?(\d+)?\.?', metadata)
    if title_match:
        ref['title'] = title_match.group(1).strip()
        ref['journal'] = title_match.group(2).strip()
        ref['volume'] = title_match.group(3)
        if title_match.group(5):
            ref['pages'] = f"{title_match.group(4)}-{title_match.group(5)}"
        elif title_match.group(4):
            ref['pages'] = title_match.group(4)
    else:
        title_end = metadata.find('.')
        if title_end > 0:
            ref['title'] = metadata[:title_end].strip()


def parse_book_chapter_metadata(ref: Dict, metadata: str) -> None:
    """Parse book chapter metadata: "Title. In Editor (Ed.), Book: Pages. Publisher"."""
    in_match = re.match(r'(.*?)\.\s+In\s+', metadata)
    if in_match:
        ref['title'] = in_match.group(1).strip()
        pages_match = re.search(r':\s*(\d+)-?(\d+)?', metadata[in_match.end():])
        if pages_match:
            ref['pages'] = f"{pages_match.group(1)}-{pages_match.group(2)}" if pages_match.group(2) else pages_match.group(1)
    else:
        ref['title'] = metadata.split('.')[0].strip()


def parse_book_metadata(ref: Dict, metadata: str) -> None:
    """Parse book metadata: "Title. City, ST: Publisher"."""
    ref['title'] = metadata.split('.')[0].strip()
    colon_pos = metadata.rfind(':')
    if colon_pos > 0:
        ref['publisher'] = metadata[colon_pos + 1:].strip()


def parse_web_metadata(ref: Dict, metadata: str) -> None:
    """Parse web source metadata."""
    ref['title'] = metadata.split('.')[0].strip()


def extract_and_save_references(md_path: Path, topic: str = None) -> list:
    """
    Main entry point: extract references from markdown file and save to metadata.json.

    Args:
        md_path: Path to the markdown file
        topic: Topic directory name (default: coaching-papers)

    Returns:
        List of parsed reference dicts
    """
    from .metadata_manager import MetadataManager

    if topic is None:
        topic = DEFAULT_TOPIC

    text = md_path.read_text(encoding="utf-8")

    try:
        section = find_references_section(text)
    except ValueError as e:
        print(f"Warning: {e}", file=sys.stderr)
        return []

    cleaned = clean_reference_text(section)
    raw_refs = split_into_references(cleaned)
    parsed_refs = [parse_single_reference(ref) for ref in raw_refs]

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()

    normalized = []
    for ref in parsed_refs:
        normalized.append({
            "title": ref.get("title", ""),
            "authors": ref.get("authors", []),
            "year": ref.get("year"),
            "journal": ref.get("journal"),
            "doi": ref.get("doi_in_text"),
            "abstract": None,
            "keywords": [],
            "source": "markdown_reference",
            "added_date": now,
        })

    manager = MetadataManager(topic=topic)
    stats = manager.add_papers(normalized, search_query=f"references:{md_path.stem}")

    print(f"Extracted {len(parsed_refs)} references from {md_path.name}", file=sys.stderr)
    print(f"  Added: {stats['added']}, Updated: {stats['updated']}", file=sys.stderr)

    return normalized


# =============================================================================
# Main entry point
# =============================================================================

def main():
    """Main entry point for batch PDF to Markdown conversion using MinerU.

    Two modes:
      - Directory mode (--input): Scan a directory for all PDFs and convert them.
      - Legacy mode (no args): Convert the predefined list of coaching papers.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert PDFs to Markdown using MinerU",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all PDFs in a directory
  python convert_pdfs_to_md.py --input /path/to/pdfs --output /path/to/markdown

  # Convert with GPU backend (faster, requires GPU)
  python convert_pdfs_to_md.py --input /path/to/pdfs --output /path/to/markdown --backend hybrid-auto-engine

  # Convert predefined coaching papers (legacy mode)
  python convert_pdfs_to_md.py
        """
    )

    parser.add_argument("--input", help="Directory of PDFs to convert (scans all .pdf files)")
    parser.add_argument("--output", help="Output directory for markdown files (default: <input_dir>_md)")
    parser.add_argument("--backend", choices=["pipeline", "hybrid-auto-engine"], default="pipeline",
                        help="MinerU backend: pipeline (CPU-only) or hybrid-auto-engine (GPU加速)")
    args = parser.parse_args()

    if args.input:
        pdf_dir = Path(args.input)
        if not pdf_dir.exists():
            print(f"ERROR: Input directory does not exist: {pdf_dir}", file=sys.stderr)
            sys.exit(1)

        md_dir = Path(args.output) if args.output else pdf_dir.parent / f"{pdf_dir.name}_md"
        md_dir.mkdir(parents=True, exist_ok=True)

        pdf_files = sorted(pdf_dir.glob("*.pdf"))
        if not pdf_files:
            print(f"ERROR: No PDF files found in {pdf_dir}", file=sys.stderr)
            sys.exit(1)

        print(f"Found {len(pdf_files)} PDF files in {pdf_dir}")
        print(f"Using MinerU backend: {args.backend}")

        for pdf_path in pdf_files:
            md_name = pdf_path.stem + ".md"
            output_path = md_dir / md_name

            if output_path.exists():
                print(f"  Skip (exists): {pdf_path.name}")
                continue

            try:
                pdf_to_markdown(pdf_path, output_path, backend=args.backend)
            except Exception as e:
                print(f"Error converting {pdf_path.name}: {e}")

    else:
        # Legacy mode: predefined papers list
        pdf_dir = Path("references/articles_pdf")
        md_dir = Path("references/articles_md")

        md_dir.mkdir(parents=True, exist_ok=True)

        # Get all PDFs in the directory if predefined list is empty
        pdf_files = sorted(pdf_dir.glob("*.pdf"))

        print(f"Found {len(pdf_files)} PDF files in {pdf_dir}")
        print(f"Using MinerU backend: {args.backend}")

        for pdf_path in pdf_files:
            md_name = pdf_path.stem + ".md"
            output_path = md_dir / md_name

            if pdf_path.exists():
                try:
                    pdf_to_markdown(pdf_path, output_path, backend=args.backend)
                except Exception as e:
                    print(f"Error converting {pdf_path.name}: {e}")
            else:
                print(f"File not found: {pdf_path.name}")

    print(f"\nConversion complete! Output directory: {md_dir}")


if __name__ == "__main__":
    main()
