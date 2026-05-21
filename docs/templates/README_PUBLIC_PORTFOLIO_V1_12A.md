# Quant Interview Trainer

An interactive Streamlit app for quantitative finance interview preparation.

This project turns static notes into a structured and practical learning tool with:

- searchable question bank
- formula sheet
- derivations and interview tips
- coding examples
- quiz mode with self-assessment
- review mode for weak questions
- content dashboard and curation workspace

## Why I built this

I wanted a more practical way to prepare for quantitative finance interviews than storing notes only in a PDF or GitHub repository.  
This app turns interview material into an interactive revision and practice platform.

## Features

### Learning and revision
- Question Bank with topic, difficulty, status, and tag filters
- Formula Sheet for fast review
- Derivations, common mistakes, and interview tips

### Practice
- Random Practice mode
- Quiz Mode
- Review Mode for weak topics
- Export quiz results

### Project-quality tools
- Content Dashboard for validation
- Curation Workspace for maintaining question quality
- JSON-based structure for easy extension

## Topic coverage

Current topics include:

- Probability
- Statistics
- Time Series
- Machine Learning
- Derivatives
- Greeks
- Stochastic Calculus
- Coding
- Quant Developer topics
- Brainteasers

## App screenshots

```markdown
![Home](docs/screenshots/home.png)
![Question Bank](docs/screenshots/question_bank.png)
![Quiz Mode](docs/screenshots/quiz_mode.png)
![Formula Sheet](docs/screenshots/formula_sheet.png)
![Content Dashboard](docs/screenshots/content_dashboard.png)
![Curation Workspace](docs/screenshots/curation_workspace.png)
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data files

```text
data/questions.json
data/formulas.json
```
