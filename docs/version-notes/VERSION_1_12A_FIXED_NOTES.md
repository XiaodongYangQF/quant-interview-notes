# Version 1.12A Fixed Notes

This is the fixed version of v1.12A.

## Fix

The first v1.12A package accidentally removed helper functions for:

- Content Dashboard
- Curation Workspace

That caused this error:

```text
NameError: name 'render_content_dashboard' is not defined
```

This fixed package preserves those helper functions and only updates the Home tab.

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
docs/version-notes/VERSION_1_12A_FIXED_NOTES.md
docs/templates/
docs/screenshots/
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json docs/version-notes/VERSION_1_12A_FIXED_NOTES.md docs/templates/ docs/screenshots/
git commit -m "Fix v1.12A landing polish helper functions"
git push
```
