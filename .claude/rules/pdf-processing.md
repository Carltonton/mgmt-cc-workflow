---
paths:
  - "references/**"
  - "master_supporting_docs/**"
---

# PDF Processing with MinerU

**Updated:** 2026-04-13
**Tool:** MinerU v3.0+ (replaces PyMuPDF/Tesseract)

---

## Quick Start

```bash
# Convert a single PDF
mineru -p input.pdf -o output_dir -b pipeline

# Convert all PDFs in a directory
python .claude/skills/lit-search/scripts/convert_pdfs_to_md.py --input /path/to/pdfs --output /path/to/markdown

# Using GPU backend (faster, requires GPU)
python .claude/skills/lit-search/scripts/convert_pdfs_to_md.py --input /path/to/pdfs --backend hybrid-auto-engine
```

---

## MinerU Capabilities

| Feature | Description |
|---------|-------------|
| **Table extraction** | HTML format with structure preservation |
| **Formula extraction** | LaTeX format for math equations |
| **Layout analysis** | Multi-column, cross-page table merging |
| **OCR accuracy** | 86+ score on OmniDocBench (vs 75 for Tesseract) |
| **Language support** | 109 languages |
| **Output format** | Markdown + JSON with images |

---

## The Processing Workflow

### Step 1: Receive PDF Upload
- User uploads PDF to `references/articles_pdf/` or `master_supporting_docs/`
- Claude DOES NOT attempt to read PDFs directly with Read tool

### Step 2: Convert with MinerU

**Option A: CLI (Recommended for single files)**
```bash
mineru -p paper_name.pdf -o output_dir -b pipeline
```

**Option B: Python script (Recommended for batch)**
```bash
python .claude/skills/lit-search/scripts/convert_pdfs_to_md.py --input pdf_dir --output md_dir
```

### Step 3: Access Markdown Output

MinerU creates structured output:
```
output_dir/
└── paper_name/
    └── auto/
        ├── paper_name.md           # Main markdown file
        ├── images/                  # Extracted images
        ├── paper_name_model.json    # Structured data
        └── paper_name_layout.pdf    # Layout visualization
```

### Step 4: Read Markdown Content

Use the Read tool to access the markdown:
```python
# Read the converted markdown
md_content = Path("output_dir/paper_name/auto/paper_name.md").read_text()
```

---

## Backend Selection

| Backend | Best For | GPU Required | Speed | Accuracy |
|---------|----------|--------------|-------|----------|
| **pipeline** | General use, CPU-only | No | Medium | 86+ |
| **hybrid-auto-engine** | High accuracy | Yes (Apple Silicon/NVIDIA) | Fast | 90+ |

**Default:** `pipeline` (works on any machine)

---

## Error Handling

### If conversion fails:

1. **Check MinerU installation:**
   ```bash
   mineru --version
   ```

2. **Try alternative backend:**
   ```bash
   mineru -p paper.pdf -o output -b hybrid-auto-engine
   ```

3. **Check PDF integrity:**
   ```bash
   pdfinfo paper_name.pdf | grep "Pages:"
   ```

### If specific pages fail:

Use page range to skip problematic sections:
```bash
mineru -p paper.pdf -o output -s 0 -e 10  # Pages 0-10 only
```

---

## Integration with Existing Scripts

The conversion script maintains backward compatibility:

```python
from scripts.convert_pdfs_to_md import pdf_to_markdown
from pathlib import Path

# Same API as before, now using MinerU
pdf_to_markdown(
    pdf_path=Path("paper.pdf"),
    output_path=Path("paper.md"),
    backend="pipeline"  # New: backend selection
)
```

---

## Migration from PyMuPDF

| Old Method | New Method |
|------------|------------|
| `fitz.open(pdf)` | `mineru -p pdf -o output` |
| `page.get_text()` | Auto-generated markdown |
| Tesseract OCR | Built-in VLM+OCR |
| Manual table parsing | HTML table output |
| Raw formula text | LaTeX format |

---

## References

- [MinerU GitHub](https://github.com/opendatalab/MinerU)
- [MinerU Documentation](https://mineru.readthedocs.io/)
- [OmniDocBench](https://github.com/opendatalab/OmniDocBench)
