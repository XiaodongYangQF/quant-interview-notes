# Version 1.16A Notes

This update adds Formula Revision Mode.

## Purpose

The app already has a Formula Sheet. v1.16A turns formulas into active-recall practice.

## New tab

Added:

```text
Formula Revision
```

## Revision modes

```text
Name → Formula
Formula → Meaning
```

## Features

- filter formulas by topic
- search formulas
- generate random formula
- manually load selected formula
- show prompt first
- reveal answer later
- self-assessment:
  - Remembered
  - Partially remembered
  - Need review
- download formula review result as JSON
- topic overview for formulas

## Current counts

- Questions: 274
- Formulas: 72
- Questions with derivations: 35
- Questions with code examples: 55

## Files to replace

Replace:

```text
app.py
data/questions.json
data/formulas.json
config/app_config.json
```

Add/update:

```text
README.md
docs/SCREENSHOT_CHECKLIST.md
docs/version-notes/VERSION_1_16A_NOTES.md
docs/presentation/FORMULA_REVISION_MODE.md
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json config/app_config.json README.md docs/
git commit -m "Add formula revision mode v1.16A"
git push
```

## Test checklist

```bash
streamlit run app.py
```

Check:

- Formula Revision tab
- Name → Formula mode
- Formula → Meaning mode
- Generate random formula
- Load selected formula
- Reveal answer
- Self-assessment buttons
- Download formula review result JSON
- Formula Sheet still works
- Coding Exercise still works
