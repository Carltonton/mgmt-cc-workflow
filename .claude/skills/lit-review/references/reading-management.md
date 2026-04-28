# Reading & Citation Management

## Citation Management Software

| Software | Strengths | Free? |
|----------|-----------|-------|
| **Zotero** | Free, user-friendly, browser integration | Yes |
| **Mendeley** | PDF organization, collaboration | Yes |
| **EndNote** | Comprehensive, industry standard | No |
| **RefWorks** | Web-based, collaborative | No |

## Reading Strategy

### First Pass (Skimming)
- Read title, abstract, introduction, conclusion
- Identify relevance to your research
- Note key findings and contribution

### Second Pass (Selective)
- Read key sections in detail
- Note methodology, variables, results
- Identify connections to other works

### Third Pass (Deep Reading)
- Full reading of most relevant papers
- Take detailed notes
- Identify theoretical contributions

---

## Project Integration

**When working in a project with local bibliography:**
- Check for `Bibliography_base.bib` or similar in project root
- Use `Grep` to search for relevant entries before external search
- Add new citations to the project bibliography
- Run `/validate-bib` to ensure citation completeness

**Typical project structure:**

```
project_root/
├── Bibliography_base.bib          # Central bibliography
├── quality_reports/
│   └── lit_review_*.md            # Literature review outputs
├── master_supporting_docs/        # Uploaded papers
└── paper/sections/
    └── 02_literature.tex          # Current literature section
```
