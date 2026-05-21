# Question JSON Schema Guide

This file documents the recommended question structure for the Quant Interview Trainer.

## Required fields

```json
{
  "id": "unique_id",
  "topic": "Probability",
  "subtopic": "Conditional Probability",
  "difficulty": "Easy | Medium | Hard",
  "status": "Verified | Draft",
  "question": "Question text",
  "intuition": "Short intuitive explanation",
  "solution": "Interview-level answer",
  "tags": ["Tag 1", "Tag 2"]
}
```

## Optional fields

```json
{
  "derivation": "Optional LaTeX derivation using markdown",
  "formula": "Key formula",
  "code_language": "python | cpp | text",
  "code": "Optional code example",
  "complexity": "Time and space complexity",
  "common_mistake": "Common mistake",
  "interview_tip": "Practical interview tip"
}
```

## Recommended status workflow

```text
Draft → Reviewed → Verified
```

The current app supports `Draft` and `Verified`. If you want a `Reviewed` status later, update the valid status list in `build_question_quality_report`.

## ID naming convention

Suggested prefixes:

```text
prob_     Probability
stats_    Statistics
ts_       Time Series
ml_       Machine Learning
deriv_    Derivatives
greeks_   Greeks
stoch_    Stochastic Calculus
code_     Coding / Quant Developer
brain_    Brainteasers
```

## LaTeX in JSON

Use double backslashes:

```json
"derivation": "$$\\mathbb{E}[X]=\\int x f(x) dx$$"
```

## Code examples

For Python:

```json
"code_language": "python",
"code": "def example():\n    return 1"
```

For C++:

```json
"code_language": "cpp",
"code": "#include <iostream>\nint main(){ return 0; }"
```
