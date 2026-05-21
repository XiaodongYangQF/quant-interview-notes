# Version 1.9A Notes

This update expands the Quant Developer / C++ / Algorithms side of the Quant Interview Trainer.

## Changes

Added questions on:

### C++
- passing by value, pointer, and reference
- RAII
- unique_ptr vs shared_ptr
- std::vector and cache locality
- std::map vs std::unordered_map
- move semantics

### Algorithms
- binary search
- streaming median with two heaps
- LRU cache
- rolling window maximum
- stable sorting
- merging sorted arrays
- sorted-array intersection

### Quant Developer / Trading Systems
- cache locality
- dynamic memory allocation
- latency vs throughput
- false sharing
- limit order book
- top-of-book tracker
- simple order book design
- lookahead bias
- market data validation
- crossed-market detection
- VWAP
- implementation shortfall
- idempotency
- sequence numbers

### Numerical Methods
- numerical stability
- avoiding explicit matrix inverse
- finite difference pricing intuition

## Current counts

- Total questions: 204
- Coding questions: 52
- Questions with code examples: 49
- C++-related questions: 11
- Formula sheet entries: 55

## Files to replace

Replace:

```text
app.py
data/questions.json
data/formulas.json
```

Add:

```text
docs/version-notes/VERSION_1_9A_NOTES.md
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json docs/version-notes/VERSION_1_9A_NOTES.md
git commit -m "Add C++ quant developer and algorithms questions v1.9A"
git push
```

## Run locally

```bash
streamlit run app.py
```

## Test checklist

- Filter Topic = `Coding`.
- Search for `C++`, `order book`, `latency`, `VWAP`, `LRU`, `binary search`.
- Tick `Only show questions with code examples`.
- Test Quiz Mode with Topic = `Coding`.
