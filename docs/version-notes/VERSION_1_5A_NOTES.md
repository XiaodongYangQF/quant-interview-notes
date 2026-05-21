# Version 1.5A Notes

This update adds coding interview support to the Quant Interview Trainer.

## Changes

### App changes

- Added optional `code` field support.
- Added optional `code_language` field support.
- Added optional `complexity` field support.
- Added a new `Code example` expander in question cards.
- Added a new `Complexity` expander in question cards.
- Added sidebar checkbox: `Only show questions with code examples`.
- Search now includes code and complexity text.
- Added metric: `With code`.

### Data changes

Added coding questions covering:

- Python financial returns
- Rolling volatility
- Vectorized Black-Scholes pricing
- Implied volatility by bisection
- Monte Carlo option pricing
- Antithetic variates
- Binomial tree pricing
- American option early exercise
- Historical VaR and Expected Shortfall
- Maximum drawdown
- Sharpe ratio
- Simple signal backtesting
- Hash-map and array algorithm questions
- Moving average
- Missing-date checks
- Numerical root finding
- Introductory C++ questions

## Current counts

- Total questions: 139
- Coding questions: 22
- Questions with code examples: 22

## Files to replace or add

Replace:

```text
app.py
data/questions.json
data/formulas.json
```

Add:

```text
docs/version-notes/VERSION_1_5A_NOTES.md
docs/templates/coding_question_template.json
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json docs/version-notes/VERSION_1_5A_NOTES.md docs/templates/coding_question_template.json
git commit -m "Add coding interview support v1.5A"
git push
```

## Run locally

```bash
streamlit run app.py
```

## Test checklist

- Check `Question Bank`.
- Filter Topic = `Coding`.
- Tick `Only show questions with code examples`.
- Search for `Black-Scholes`, `VaR`, `Monte Carlo`, `bisection`, `C++`.
- Open `Code example` and `Complexity` expanders.
