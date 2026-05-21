# Version 1.7A Notes

This update adds Quiz Mode with session-based self-assessment and score summary.

## Changes

### App changes

- Added a new `Quiz Mode` tab.
- Added quiz filters:
  - topic
  - difficulty
  - status
  - derivation-only
  - coding-only
  - number of questions
  - optional random seed
- Added hidden-answer quiz workflow:
  1. Show question
  2. User thinks independently
  3. User clicks `Show answer`
  4. User self-assesses
- Added self-assessment buttons:
  - Correct
  - Partially correct
  - Wrong
  - Need review
- Added score summary:
  - raw score
  - percentage score
  - result breakdown
  - topic summary
  - review list
- Quiz progress is stored in Streamlit session state.

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
docs/version-notes/VERSION_1_7A_NOTES.md
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json docs/version-notes/VERSION_1_7A_NOTES.md
git commit -m "Add quiz mode v1.7A"
git push
```

## Run locally

```bash
streamlit run app.py
```

## Test checklist

- Open `Quiz Mode`.
- Select `Probability` and start a 5-question quiz.
- Click `Show answer`.
- Mark answers as Correct / Partially correct / Wrong / Need review.
- Finish the quiz and check the score summary.
- Test `Only derivation questions`.
- Test `Only coding questions`.
