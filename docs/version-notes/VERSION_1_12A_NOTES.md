# Version 1.12A Notes

This update focuses on public portfolio polish.

Important: this version is built from the public-safe v1.11B version.

## Main goals

- improve Home / landing-page quality
- improve README presentation
- define a screenshot workflow
- improve GitHub / LinkedIn / personal website presentation materials

## App changes

### Home tab improvements
- clearer project introduction
- stronger feature explanation
- better positioning as both a learning tool and portfolio project
- improved project snapshot metrics
- explicit recommended study route
- explicit project positioning statement

## Documentation templates added

```text
docs/templates/README_PUBLIC_PORTFOLIO_V1_12A.md
docs/templates/SCREENSHOT_CHECKLIST_V1_12A.md
docs/templates/LINKEDIN_PERSONAL_WEBSITE_V1_12A.md
docs/templates/GITHUB_PRESENTATION_V1_12A.md
docs/templates/APP_LANDING_QUALITY_NOTES_V1_12A.md
```

## Screenshot folder added

```text
docs/screenshots/
```

This folder includes a small helper note for storing screenshots.

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
docs/version-notes/VERSION_1_12A_NOTES.md
docs/templates/README_PUBLIC_PORTFOLIO_V1_12A.md
docs/templates/SCREENSHOT_CHECKLIST_V1_12A.md
docs/templates/LINKEDIN_PERSONAL_WEBSITE_V1_12A.md
docs/templates/GITHUB_PRESENTATION_V1_12A.md
docs/templates/APP_LANDING_QUALITY_NOTES_V1_12A.md
docs/screenshots/
```

## Suggested commit message

```bash
git add app.py data/questions.json data/formulas.json docs/version-notes/VERSION_1_12A_NOTES.md docs/templates/ docs/screenshots/
git commit -m "Add public portfolio polish and landing quality v1.12A"
git push
```

## Test checklist

- open `Home`
- check hero / landing section
- check project snapshot metrics
- check topic coverage table
- confirm all other tabs still work
- update screenshots using the new screenshot checklist
- use the README template to refresh your repository front page
