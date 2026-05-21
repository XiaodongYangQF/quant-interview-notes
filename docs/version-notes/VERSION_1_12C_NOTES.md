# Version 1.12C Notes

This update finalizes the public-facing project presentation.

## Purpose

v1.12C focuses on:

- final README
- screenshot workflow
- LinkedIn / personal website presentation
- GitHub presentation
- deployment checklist

It does not add new question content.

## Main additions

### Root files

```text
README.md
requirements.txt
.gitignore
```

### Documentation

```text
docs/SCREENSHOT_CHECKLIST.md
docs/DEPLOYMENT_CHECKLIST.md
docs/presentation/LINKEDIN_AND_WEBSITE_TEXT.md
docs/presentation/GITHUB_PRESENTATION_GUIDE.md
docs/version-notes/VERSION_1_12C_NOTES.md
```

### App change

The About tab roadmap is updated to remove v1.12C as a future item.

## Current counts

- Questions: 241
- Formulas: 64
- Questions with derivations: 34
- Questions with code examples: 51

## Files to replace/add

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
requirements.txt
.gitignore
docs/SCREENSHOT_CHECKLIST.md
docs/DEPLOYMENT_CHECKLIST.md
docs/presentation/
docs/version-notes/VERSION_1_12C_NOTES.md
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json config/app_config.json README.md requirements.txt .gitignore docs/
git commit -m "Finalize README screenshots and public presentation v1.12C"
git push
```

## Test checklist

```bash
streamlit run app.py
```

Then check:

- Home
- Question Bank
- Quiz Mode
- Review Mode
- Formula Sheet
- Content Dashboard
- Curation Workspace
- Content Workflow
- About
