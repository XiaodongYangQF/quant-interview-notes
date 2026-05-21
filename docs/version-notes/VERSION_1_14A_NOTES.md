# Version 1.14A Notes

This update adds preset Mock Interview tracks.

## Purpose

The app already has a large question bank and quiz engine. v1.14A turns this into structured interview simulation.

## New tab

Added:

```text
Mock Interview
```

## Preset tracks

Added five public-safe mock interview tracks:

```text
Quant Researcher
Quant Developer
Derivatives Pricing
Probability & Brainteasers
Statistics & Machine Learning
```

## Track features

Each track has:

- description
- recommended number of questions
- target interview time
- weighted topic/bucket composition
- availability table
- optional random seed
- same hidden-answer workflow as Quiz Mode
- same self-assessment workflow
- same final score summary and review list

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
docs/version-notes/VERSION_1_14A_NOTES.md
docs/presentation/MOCK_INTERVIEW_TRACKS.md
README.md
docs/SCREENSHOT_CHECKLIST.md
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json config/app_config.json README.md docs/
git commit -m "Add mock interview tracks v1.14A"
git push
```

## Test checklist

```bash
streamlit run app.py
```

Check:

- Mock Interview tab
- Quant Researcher track
- Quant Developer track
- Derivatives Pricing track
- Track composition table
- Start / Restart Mock Interview
- Show answer
- Self-assessment buttons
- Final score summary
- Review Mode after mock interview
