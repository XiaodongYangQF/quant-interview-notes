# Version 1.6A Notes

This update adds Statistics, Time Series, and Machine Learning content to the Quant Interview Trainer.

## Changes

Added questions on:

### Statistics
- Method of Moments vs MLE
- Normal MLE derivation
- OLS matrix estimator
- p-values and confidence intervals
- Central Limit Theorem
- bias-variance tradeoff
- multicollinearity
- heteroskedasticity
- autocorrelation
- logistic regression
- sample variance
- correlation vs causation
- OLS implementation in Python

### Time Series
- stationarity
- AR(1)
- random walk and unit root
- autocorrelation
- ARMA
- cointegration
- GARCH
- Kalman filter
- forecast evaluation
- lagged feature construction

### Machine Learning
- supervised vs unsupervised learning
- time-series train-test split
- overfitting
- L1 vs L2 regularization
- random forest
- gradient boosting
- PCA
- precision and recall
- feature engineering
- time-series split implementation

## Current counts

- Total questions: 174
- Statistics questions: 15
- Time Series questions: 12
- Machine Learning questions: 10
- Questions with derivations: 31
- Questions with code examples: 25
- Formula sheet entries: 55

## Files to replace

Replace:

```text
data/questions.json
data/formulas.json
```

If your current app.py is not from v1.5A, also replace:

```text
app.py
```

## Suggested commit message

```bash
git add data/questions.json data/formulas.json docs/version-notes/VERSION_1_6A_NOTES.md
git commit -m "Add statistics time series and ML question bank v1.6A"
git push
```

## Run locally

```bash
streamlit run app.py
```

## Test checklist

- Filter Topic = `Statistics`.
- Filter Topic = `Time Series`.
- Filter Topic = `Machine Learning`.
- Search for `OLS`, `GARCH`, `cointegration`, `PCA`, `regularization`.
- Check Formula Sheet for Statistics, Time Series, and Machine Learning formulas.
