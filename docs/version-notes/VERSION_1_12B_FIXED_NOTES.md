# Version 1.12B Fixed Notes

This is a bug-fix package for v1.12B.

## Fix

v1.12B loaded `app_config` through a Streamlit cached function before calling:

```python
st.set_page_config(...)
```

Streamlit requires `st.set_page_config()` to be the first Streamlit command in the script.

This fixed version calls `st.set_page_config()` first, then loads `app_config`.

## Current counts

- Questions: 241
- Formulas: 64
- Questions with derivations: 34
- Questions with code examples: 51

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
docs/version-notes/VERSION_1_12B_FIXED_NOTES.md
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json config/app_config.json docs/version-notes/VERSION_1_12B_FIXED_NOTES.md
git commit -m "Fix Streamlit page config order in v1.12B"
git push
```

## Test checklist

```bash
streamlit run app.py
```

Then check:

- Home
- Question Bank
- Display settings
- Content Workflow
- Content Dashboard
- Curation Workspace
- Quiz Mode
