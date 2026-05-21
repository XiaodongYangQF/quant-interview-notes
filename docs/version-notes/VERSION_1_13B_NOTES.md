# Version 1.13B Notes

This update improves search, sorting, and topic navigation.

## Purpose

The app now has a large question bank, so navigation matters more. v1.13B makes the app easier to browse, search, and use for focused study.

## App changes

### 1. Scoped search

Added sidebar search scopes:

```text
All fields
Question only
Answer / solution
Tags only
Code only
Formula only
Topic / subtopic
```

### 2. Sorting controls

Added sidebar sorting options:

```text
Topic
Subtopic
Difficulty
Status
Question ID
Has derivation
Has code
```

with ascending / descending direction.

### 3. Topic Navigator tab

Added a new tab:

```text
Topic Navigator
```

It includes:

- topic overview table
- topic-level metrics
- subtopic breakdown
- search within selected topic
- preview questions from selected topic/subtopics

### 4. About tab update

Updated feature list and future roadmap.

## Current counts

- Questions: 274
- Formulas: 72
- Questions with derivations: 35
- Questions with code examples: 55

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
docs/version-notes/VERSION_1_13B_NOTES.md
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json config/app_config.json docs/version-notes/VERSION_1_13B_NOTES.md
git commit -m "Improve search sorting and topic navigation v1.13B"
git push
```

## Test checklist

```bash
streamlit run app.py
```

Check:

- Topic Navigator
- Search scope = Question only
- Search scope = Code only
- Search scope = Formula only
- Sort by Difficulty
- Sort by Has derivation
- Question Bank pagination still works
- Quiz Mode still works
