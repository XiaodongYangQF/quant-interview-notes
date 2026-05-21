# Version 1.17A Notes

This update adds a Performance Analytics dashboard.

## Purpose

v1.17A helps users understand their current practice-session performance and identify weak topics.

## New tab

Added:

```text
Performance Analytics
```

## Features

### Quiz / Mock Interview analytics

- total questions
- answered questions
- raw score
- score percentage
- number of review items
- topic performance table
- difficulty performance table
- review-priority questions
- export analytics as JSON
- export analytics as CSV

### Coding Exercise analytics

- current coding result
- coding category
- difficulty
- export current coding analytics as JSON

### Formula Revision analytics

- current formula result
- formula topic
- revision mode
- export current formula analytics as JSON

### Study suggestion

The tab suggests weak topics based on current quiz/mock interview results.

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
docs/version-notes/VERSION_1_17A_NOTES.md
docs/presentation/PERFORMANCE_ANALYTICS.md
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json config/app_config.json README.md docs/
git commit -m "Add performance analytics dashboard v1.17A"
git push
```

## Test checklist

```bash
streamlit run app.py
```

Check:

- Finish or partially complete a Quiz Mode session
- Open Performance Analytics
- Check topic performance
- Check difficulty performance
- Download JSON
- Download CSV
- Try Coding Exercise and check analytics
- Try Formula Revision and check analytics
