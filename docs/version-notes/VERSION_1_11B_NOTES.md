# Version 1.11B Notes

This update is a public-safe advanced interview expansion.

Important: this version is built from public v1.10B, not from the research-focused v1.11A draft.

## Purpose

Add more advanced but non-research-specific interview questions across:

- probability
- statistics
- time series
- machine learning
- derivatives
- stochastic calculus
- coding
- brainteasers

## New content examples

### Probability
- inclusion-exclusion
- law of total variance
- Jensen's inequality
- exponential race
- moment generating functions
- change of variables
- bivariate normal conditioning
- stationary distribution of Markov chains
- martingale example

### Statistics
- score function
- Fisher information
- delta method
- bootstrap
- Bayesian prior / likelihood / posterior
- ridge regression
- multiple testing

### Time Series and Machine Learning
- ACF/PACF
- seasonality
- structural breaks
- walk-forward validation
- probability calibration
- feature importance limitations
- data leakage

### Derivatives and Stochastic Calculus
- put-call parity with dividends
- static replication
- vega hedging
- volatility smile limitations of BSM
- local volatility intuition
- barrier option path dependency
- Ito product rule
- Ito integral expectation
- diffusion generator

### Coding and Brainteasers
- walk-forward validation code
- winsorization code
- extra classic expected-value and assumption questions

## Current counts

- Questions: 241
- Formulas: 64
- New questions added: 37
- New formulas added: 9
- Questions with derivations: 34
- Questions with code examples: 51

## Files to replace

Replace:

```text
app.py
data/questions.json
data/formulas.json
```

Add:

```text
docs/version-notes/VERSION_1_11B_NOTES.md
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json docs/version-notes/VERSION_1_11B_NOTES.md
git commit -m "Add public-safe advanced interview expansion v1.11B"
git push
```

## Test checklist

- Search for `Jensen`, `Fisher`, `delta method`, `bootstrap`.
- Search for `walk-forward`, `data leakage`, `volatility smile`, `Ito product`.
- Check Formula Sheet for new formulas.
- Check Content Dashboard and Curation Workspace.
- Test Quiz Mode with Probability, Statistics, Derivatives, and Coding.
