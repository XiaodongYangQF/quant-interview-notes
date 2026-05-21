# Version 1.12B Notes

This update adds the App Settings & Content Management Foundation.

## Purpose

The app is now a stable framework. This version makes future content updates easier, safer, and more systematic.

## Main changes

### 1. App configuration file

Added:

```text
config/app_config.json
```

This controls:

- app title
- page icon
- intro text
- default status filter
- default display settings
- public/private content policy

### 2. Display settings

Added sidebar display controls:

- compact mode
- show/hide tags
- show/hide intuition
- show/hide solution section
- expand solutions by default
- show/hide derivations
- show/hide code examples
- show/hide complexity
- show/hide common mistakes
- show/hide interview tips
- questions per page

### 3. Question Bank pagination

The Question Bank now displays questions in pages based on the sidebar setting.

### 4. Content Workflow tab

Added a new tab:

```text
Content Workflow
```

It explains how to add questions, validate content, use the curation workspace, and commit updates.

### 5. JSON templates

Added:

```text
docs/templates/new_question_template.json
docs/templates/new_formula_template.json
docs/templates/new_coding_question_template.json
docs/templates/new_derivation_question_template.json
```

### 6. Content management guides

Added:

```text
docs/templates/CONTENT_UPDATE_WORKFLOW.md
docs/templates/PUBLIC_PRIVATE_CONTENT_GUIDE.md
```

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
```

Add:

```text
config/app_config.json
docs/version-notes/VERSION_1_12B_NOTES.md
docs/templates/new_question_template.json
docs/templates/new_formula_template.json
docs/templates/new_coding_question_template.json
docs/templates/new_derivation_question_template.json
docs/templates/CONTENT_UPDATE_WORKFLOW.md
docs/templates/PUBLIC_PRIVATE_CONTENT_GUIDE.md
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json config/app_config.json docs/
git commit -m "Add app settings and content workflow v1.12B"
git push
```

## Test checklist

- Run `streamlit run app.py`.
- Open the sidebar Display settings.
- Test Compact mode.
- Test Expand solutions by default.
- Change Questions per page.
- Open Content Workflow.
- Open Content Dashboard.
- Open Curation Workspace.
- Confirm Quiz Mode still works.
