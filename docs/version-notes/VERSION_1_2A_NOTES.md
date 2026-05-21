# Version 1.2A Notes

This update adds core Derivatives and Greeks interview questions to the Quant Interview Trainer.

## Changes

- Added/updated core derivatives questions.
- Added/updated core Greeks questions.
- Added derivation fields for key topics such as:
  - Black-Scholes-Merton PDE intuition
  - Forward price
  - Put-call parity
  - Risk-neutral pricing
  - BSM delta relationships
  - Greek relationships from put-call parity
  - Digital option pricing
  - Delta-hedged P&L
  - One-step binomial risk-neutral probability
  - Breeden-Litzenberger risk-neutral density result

## Current counts

- Total questions: 88
- Derivatives questions: 30
- Greeks questions: 9
- Questions with derivations: 19

## Files to replace

Replace:

```text
data/questions.json
```

No app.py change is required.

## Suggested commit message

```bash
git add data/questions.json docs/version-notes/VERSION_1_2A_NOTES.md
git commit -m "Add derivatives and Greeks question bank v1.2A"
git push
```

## Run locally

```bash
streamlit run app.py
```
