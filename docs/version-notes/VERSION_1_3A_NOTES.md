# Version 1.3A Notes

This update adds a Stochastic Calculus and Brownian Motion question bank to the Quant Interview Trainer.

## Changes

Added questions on:

- Brownian motion
- Quadratic variation
- Ito rules
- Ito's lemma
- Geometric Brownian motion
- Martingales
- Risk-neutral measure
- Girsanov theorem intuition
- Market price of risk
- Ito integral and Ito isometry
- Feynman-Kac theorem
- Stopping times and optional stopping
- Filtration and adapted processes
- OU process
- Hitting times and barrier options
- Stochastic volatility and jump processes
- Self-financing strategies
- Ito-to-BSM PDE connection
- Brownian and volatility scaling

## Current counts

- Total questions: 118
- Stochastic Calculus questions: 30
- Questions with derivations: 28

## Files to replace

Replace:

```text
data/questions.json
```

No app.py change is required.

## Suggested commit message

```bash
git add data/questions.json docs/version-notes/VERSION_1_3A_NOTES.md
git commit -m "Add stochastic calculus question bank v1.3A"
git push
```

## Run locally

```bash
streamlit run app.py
```
