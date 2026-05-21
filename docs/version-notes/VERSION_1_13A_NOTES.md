# Version 1.13A Notes

This update adds more public-safe interview questions.

## Purpose

v1.13A expands the question bank without adding private, unpublished, or PhD-specific research content.

## New content areas

### Probability
- coupon collector
- Poisson thinning
- indicator variables
- zero covariance vs independence
- stopping times
- Bayes rule and base rates

### Statistics
- AIC and BIC
- likelihood ratio test
- omitted variable bias
- endogeneity
- adjusted R-squared
- Newey-West standard errors

### Time Series
- volatility clustering
- ARCH vs GARCH
- ARIMA differencing
- forecast horizon
- lookahead bias in feature engineering

### Machine Learning
- ROC-AUC
- cross-entropy loss
- imbalanced classification
- early stopping

### Derivatives
- forward contract value
- American call early exercise
- gamma intuition
- straddle strategy

### Stochastic Calculus
- Brownian scaling
- Ito lemma second derivative intuition

### Coding
- rolling z-score
- binary confusion matrix
- remove duplicates while preserving order
- C++ const correctness

### Brainteasers
- geometric waiting time with coin flips
- permutations and counting

## Current counts

- Questions: 274
- Formulas: 72
- New questions added: 33
- New formulas added: 8
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
docs/version-notes/VERSION_1_13A_NOTES.md
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json config/app_config.json docs/version-notes/VERSION_1_13A_NOTES.md
git commit -m "Add public-safe interview questions v1.13A"
git push
```

## Test checklist

```bash
streamlit run app.py
```

Search for:

```text
coupon collector
Poisson thinning
AIC
BIC
endogeneity
Newey-West
volatility clustering
cross-entropy
straddle
Brownian scaling
rolling z-score
const correctness
```

Also check:

- Question Bank
- Formula Sheet
- Quiz Mode
- Content Dashboard
- Curation Workspace
