# Version 1.15A Notes

This update adds a dedicated Coding Exercise Mode.

## Purpose

The app now has a large number of coding and implementation questions. v1.15A separates these into a focused coding-practice workflow.

## New tab

Added:

```text
Coding Exercise
```

## Features

- filter coding exercises by category / subtopic
- filter by code language
- filter by difficulty
- filter by status
- search coding exercises
- generate random exercise
- manually load selected exercise
- show prompt first
- reveal reference solution later
- show code solution
- show complexity
- show common mistakes and interview tips
- self-assessment:
  - Solved
  - Partially solved
  - Could not solve
  - Need review
- download single exercise result as JSON

## Current counts

- Questions: 274
- Formulas: 72
- Coding-suitable questions: 61
- Questions with code examples: 55
- Questions with derivations: 35

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
docs/version-notes/VERSION_1_15A_NOTES.md
docs/presentation/CODING_EXERCISE_MODE.md
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json config/app_config.json README.md docs/
git commit -m "Add coding exercise mode v1.15A"
git push
```

## Test checklist

```bash
streamlit run app.py
```

Check:

- Coding Exercise tab
- Category / subtopic filter
- Code language filter
- Generate random exercise
- Load selected exercise
- Reveal reference solution
- Self-assessment buttons
- Download exercise result JSON
- Question Bank still works
- Mock Interview still works
