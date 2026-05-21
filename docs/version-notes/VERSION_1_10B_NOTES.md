# Version 1.10B Notes

This update adds a Content Curation Workspace to make the Content Dashboard actionable.

## New tab

Added:

```text
Curation Workspace
```

## What it does

The Curation Workspace helps you:

- filter questions by topic
- filter questions by status
- filter questions by curation bucket
- search curation rows
- identify Draft questions
- identify questions missing formula, derivation, common mistake, or interview tip
- identify coding questions without code
- inspect one question at a time
- preview the full question card
- view raw JSON
- download selected question JSON
- download a curation patch template
- download the filtered curation table as JSON

## Curation buckets

Questions are assigned to buckets such as:

- Draft
- Missing required field
- Missing formula
- Missing derivation
- Missing common mistake
- Missing interview tip
- Code missing language
- Technical topic without derivation
- Coding topic without code

## Documentation

Added:

```text
docs/templates/QUESTION_JSON_SCHEMA_GUIDE.md
```

## Current counts

- Questions: 204
- Formulas: 55
- Questions with derivations: 31
- Questions with code examples: 49

## Files to replace

Replace:

```text
app.py
data/questions.json
data/formulas.json
```

Add:

```text
docs/version-notes/VERSION_1_10B_NOTES.md
docs/templates/QUESTION_JSON_SCHEMA_GUIDE.md
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json docs/version-notes/VERSION_1_10B_NOTES.md docs/templates/QUESTION_JSON_SCHEMA_GUIDE.md
git commit -m "Add content curation workspace v1.10B"
git push
```

## Test checklist

- Open `Curation Workspace`.
- Filter by `Draft`.
- Filter by `Missing derivation`.
- Select one question ID.
- Download selected question JSON.
- Download curation patch template.
- Download filtered curation table.
- Check that `Content Dashboard` still works.
