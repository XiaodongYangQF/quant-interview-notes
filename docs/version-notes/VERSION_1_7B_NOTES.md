# Version 1.7B Notes

This update improves Quiz Mode by adding export and review workflow features.

## Changes

### Quiz export

- Added CSV export for quiz results.
- Added JSON export for quiz results.
- Added JSON export for review-list questions.

### Review Mode

- Added a new `Review Mode` tab.
- Review Mode shows questions marked:
  - Wrong
  - Partially correct
  - Need review
- Added weak-topic count table.

### App internals

- Added helper functions:
  - `build_quiz_export_payload`
  - `quiz_payload_to_csv`
  - `get_review_questions_from_quiz`
- Added `csv`, `io`, and `datetime` imports.

## Current counts

- Total questions: 174
- Formula sheet entries: 55
- Questions with derivations: 31
- Questions with code examples: 25

## Files to replace

Replace:

```text
app.py
data/questions.json
data/formulas.json
```

Add:

```text
docs/version-notes/VERSION_1_7B_NOTES.md
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json docs/version-notes/VERSION_1_7B_NOTES.md
git commit -m "Add quiz export and review mode v1.7B"
git push
```

## Run locally

```bash
streamlit run app.py
```

## Test checklist

- Start a quiz.
- Mark some questions as Wrong / Partially correct / Need review.
- Finish the quiz.
- Download CSV quiz results.
- Download JSON quiz results.
- Download review-list JSON.
- Open Review Mode and check weak-topic count.
