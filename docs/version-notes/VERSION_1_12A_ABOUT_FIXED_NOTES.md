# Version 1.12A About Tab Fixed Notes

This is a small UI formatting fix on top of the v1.12A roadmap-fixed package.

## Fix

The About tab displayed:

```text
JSON-based data structure Suggested next versions
```

on the same bullet-line area.

This package rewrites the About tab markdown with a clear blank line between:

```text
Current features
```

and:

```text
Suggested next versions
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
docs/version-notes/VERSION_1_12A_ABOUT_FIXED_NOTES.md
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json docs/version-notes/VERSION_1_12A_ABOUT_FIXED_NOTES.md
git commit -m "Fix About tab roadmap formatting"
git push
```
