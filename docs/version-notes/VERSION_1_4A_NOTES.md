# Version 1.4A Notes

This update adds a Formula Sheet / Quick Reference tab to the Quant Interview Trainer.

## Changes

### App changes

- Added a new `Formula Sheet` tab.
- Added support for `data/formulas.json`.
- Added formula search.
- Added formula topic filter.
- Formula cards render LaTeX formulas using `st.latex`.
- Formula data cache refreshes when `formulas.json` changes.

### Data changes

- Added `data/formulas.json`.
- Included 43 formulas across:
  - Probability
  - Derivatives
  - Greeks
  - Stochastic Calculus

## Files to replace or add

Replace:

```text
app.py
data/questions.json
```

Add:

```text
data/formulas.json
docs/version-notes/VERSION_1_4A_NOTES.md
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json docs/version-notes/VERSION_1_4A_NOTES.md
git commit -m "Add formula sheet tab v1.4A"
git push
```

## Run locally

```bash
streamlit run app.py
```

## Test checklist

- Check `Question Bank`.
- Check `Practice Mode`.
- Open `Formula Sheet`.
- Search for `Bayes`, `BSM`, `delta`, `Ito`.
- Filter formula topics.
