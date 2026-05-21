# Version 1.12A Roadmap Fixed Notes

This is a small UI text fix on top of the fixed v1.12A package.

## Fix

The About tab had duplicated `Suggested next versions` items:

```text
Version 1.9
Version 1.11A
Version 2.0
Version 1.9
Version 1.11A
Version 2.0
```

This version replaces that duplicated and outdated list with a clean public-safe roadmap:

```text
Version 1.12B: Final README and screenshot refresh
Version 1.13A: More public-safe interview questions
Version 2.0: Optional persistent progress tracking
```

## Current counts

- Questions: 241
- Formulas: 64
- Questions with derivations: 34
- Questions with code examples: 51

## Files to replace

Replace:

```text
app.py
data/questions.json
data/formulas.json
```

Add/update:

```text
docs/version-notes/VERSION_1_12A_ROADMAP_FIXED_NOTES.md
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json docs/version-notes/VERSION_1_12A_ROADMAP_FIXED_NOTES.md
git commit -m "Fix duplicated roadmap text in About tab"
git push
```
