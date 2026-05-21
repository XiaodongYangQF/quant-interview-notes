# Version 1.1B Notes

This update adds math derivation support to the Quant Interview Trainer.

## Changes

### App changes

- Added optional `derivation` field support.
- Added optional `common_mistake` field support.
- Added optional `interview_tip` field support.
- Added a sidebar checkbox: `Only show questions with derivations`.
- Added a metric for the number of questions with derivations.
- Search now includes derivations, common mistakes, and interview tips.
- Random practice now uses true random sampling.

### Data changes

Selected questions now include derivation-style content, including:

- Bayes' rule
- Expected maximum of Uniform(0,1) variables
- Poisson even probability
- Symmetric gambler's ruin
- Expected empty bins
- Exponential probability integral
- Black-Scholes-Merton PDE intuition
- Delta interpretation

## Files to replace

Replace these files in your repo:

```text
app.py
data/questions.json
```

Optional:

```text
docs/version-notes/VERSION_1_1B_NOTES.md
```

## Suggested commit message

```bash
git add app.py data/questions.json docs/version-notes/VERSION_1_1B_NOTES.md
git commit -m "Add math derivation support v1.1B"
git push
```

## Run locally

```bash
streamlit run app.py
```
