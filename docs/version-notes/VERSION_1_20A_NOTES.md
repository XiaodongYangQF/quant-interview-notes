# Version 1.20A Notes

This update adds navigation and UI polish.

## Purpose

v1.20A makes the app look cleaner and more professional now that the framework has many tabs and tools.

## Main changes

- added custom CSS styling
- shortened tab names
- allowed tabs to wrap into multiple rows
- improved metric-card styling
- improved sidebar visual style
- grouped sidebar filters into Core filters and Advanced filters
- changed filter behavior so blank means all
- updated app intro text
- updated roadmap
- added UI polish documentation

## Current counts

- Questions: 301
- Formulas: 72
- Questions with derivations: 35
- Questions with code examples: 82

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
docs/version-notes/VERSION_1_20A_NOTES.md
docs/presentation/NAVIGATION_UI_POLISH.md
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json config/app_config.json README.md docs/
git commit -m "Add navigation and UI polish v1.20A"
git push
```

## Test checklist

```bash
streamlit run app.py
```

Check:

- tabs wrap into two rows if needed
- shorter tab labels
- sidebar Core filters
- sidebar Advanced filters
- blank filters show all questions
- metric cards
- all tabs still open correctly
