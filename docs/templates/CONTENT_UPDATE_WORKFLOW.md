# Content Update Workflow

Use this workflow when adding or updating content.

## Step 1: Choose a template

Use one of:

```text
docs/templates/new_question_template.json
docs/templates/new_formula_template.json
docs/templates/new_coding_question_template.json
docs/templates/new_derivation_question_template.json
```

## Step 2: Add content

Add public-safe content to:

```text
data/questions.json
data/formulas.json
```

Keep private research-related drafts outside the public data files.

## Step 3: Run locally

```bash
streamlit run app.py
```

## Step 4: Validate

Open:

```text
Content Dashboard
```

Check:

- missing required fields
- duplicate IDs
- invalid status values
- invalid difficulty values
- Draft items
- questions without formula / derivation / code where relevant

## Step 5: Curate

Open:

```text
Curation Workspace
```

Inspect Draft or incomplete items.

## Step 6: Commit

```bash
git status
git add app.py data/questions.json data/formulas.json config/app_config.json docs/
git commit -m "Update quant interview trainer content"
git push
```
