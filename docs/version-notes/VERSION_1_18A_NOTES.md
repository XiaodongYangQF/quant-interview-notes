# Version 1.18A Notes

This update adds more public-safe coding exercises.

## Purpose

v1.18A expands the coding side of the app after adding Coding Exercise Mode in v1.15A.

## New exercise areas

### Python / pandas
- simple returns
- log returns
- rolling Sharpe ratio
- maximum drawdown
- time-series alignment
- daily OHLCV resampling
- trade-to-quote as-of matching
- bid-ask spread and mid price
- stale price detection
- portfolio turnover
- portfolio returns
- lagged-signal backtest

### NumPy
- vectorization
- covariance matrix

### Numerical methods
- bisection root finding
- Newton's method
- Monte Carlo option pricing

### Algorithms
- prefix sums
- sliding window
- Kadane's algorithm
- balanced parentheses

### C++
- stack vs heap memory
- destructor exception safety
- rule of zero
- reserve vs resize

### Quant developer
- streaming rolling mean
- market-data message deduplication

## Current counts

- Questions: 301
- Formulas: 72
- New coding questions added: 27
- Coding-suitable questions: 88
- Questions with code examples: 82
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
docs/version-notes/VERSION_1_18A_NOTES.md
docs/presentation/PUBLIC_SAFE_CODING_EXPANSION.md
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json config/app_config.json README.md docs/
git commit -m "Add public-safe coding exercises v1.18A"
git push
```

## Test checklist

```bash
streamlit run app.py
```

Search for:

```text
log returns
maximum drawdown
merge_asof
OHLCV
bisection
Newton
Monte Carlo
prefix sums
Kadane
const
portfolio turnover
lagged-signal backtest
```

Check:

- Coding Exercise tab
- Code language filter
- Topic Navigator
- Content Dashboard
- Curation Workspace
