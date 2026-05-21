# Deployment Checklist

## Before deployment

Run locally:

```bash
streamlit run app.py
```

Check:

- Home
- Question Bank
- Practice Mode
- Quiz Mode
- Review Mode
- Formula Sheet
- Content Dashboard
- Curation Workspace
- Content Workflow
- About

## Files that should be committed

```text
app.py
requirements.txt
README.md
config/app_config.json
data/questions.json
data/formulas.json
docs/
.gitignore
```

## Files/folders that should NOT be committed

```text
__pycache__/
*.pyc
private/
research_private/
*.local.json
.streamlit/secrets.toml
```

## Streamlit deployment settings

Use:

```text
Repository: your quant-interview-notes repository
Branch: main
Main file path: app.py
```

## After deployment

1. Open the app link.
2. Test all tabs.
3. Take screenshots.
4. Save screenshots in `docs/screenshots/`.
5. Update README screenshot section if needed.
6. Commit screenshots.
