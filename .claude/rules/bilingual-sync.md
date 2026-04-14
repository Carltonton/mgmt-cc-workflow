# Bilingual Document Sync Rule

**Applies to:** All files matching `*_en.md` or `*_zh.md` in this repository.

## Naming Convention

- `*_en.md` = English version (source of truth for structure)
- `*_zh.md` = Chinese version
- Paired files share the same directory and prefix, e.g.:
  - `docs/PhD_Project_Brief_Lexuan_Huang_en.md` ↔ `docs/PhD_Project_Brief_Lexuan_Huang_zh.md`

## Auto-Detection

When editing any file ending in `_en.md` or `_zh.md`:
1. Derive the paired filename by replacing the suffix (`_en` ↔ `_zh`)
2. Check if the paired file exists in the same directory
3. If paired file exists → remind user to sync after editing
4. If paired file does NOT exist → warn that an orphan file was found and suggest creating the missing pair

## Sync Checklist

After editing one version, verify the paired file reflects:
- [ ] Section structure matches (same headings at same levels)
- [ ] Numbering systems aligned (RQ, H, equations, tables, figures)
- [ ] Added/deleted paragraphs reflected in the other version
- [ ] Key terminology translations are consistent
- [ ] `Last synced` date updated in both file headers

## Sync Header

Both files in a pair MUST include this header line:

```
> Last synced: YYYY-MM-DD
```

Update this date whenever changes are synchronized between versions.