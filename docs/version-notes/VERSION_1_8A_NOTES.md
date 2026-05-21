# Version 1.8A Notes

This update focuses on portfolio polish and presentation.

## Changes

### App changes

- Added a new `Home` tab.
- Added a portfolio-friendly project introduction.
- Added project snapshot metrics.
- Added topic coverage table.
- Added suggested study workflow.
- Updated About tab to mention the portfolio home page.

### Documentation templates

Added:

- README update draft
- LinkedIn / personal website description draft
- GitHub repo presentation suggestions

## Current counts

- Questions: 174
- Formula sheet entries: 55
- Questions with derivations: 31
- Questions with code examples: 25

## Files to replace

Replace:

```text
app.py
data/questions.json
data/formulas.json
```

Add:

```text
docs/version-notes/VERSION_1_8A_NOTES.md
docs/templates/README_UPDATE_V1_8A.md
docs/templates/LINKEDIN_PERSONAL_WEBSITE_DRAFT.md
docs/templates/GITHUB_REPO_PRESENTATION.md
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json docs/version-notes/VERSION_1_8A_NOTES.md docs/templates/
git commit -m "Add portfolio polish and home tab v1.8A"
git push
```

## Test checklist

- Open the new `Home` tab.
- Check project snapshot metrics.
- Check topic coverage table.
- Check all old tabs still work:
  - Question Bank
  - Practice Mode
  - Quiz Mode
  - Review Mode
  - Formula Sheet
