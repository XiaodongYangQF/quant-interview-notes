# README Update Draft — Version 1.8A

You can paste the following section near the top of your main `README.md`.

---

## Interactive Quant Interview Trainer

I built an interactive Streamlit app based on these quantitative finance interview notes.

The app turns static notes into an active interview-preparation tool with:

- searchable question bank
- topic, difficulty, status, and tag filters
- expandable intuition, solution, derivation, code, common mistake, and interview tip sections
- formula sheet / quick reference tab
- coding examples for Python and numerical finance
- quiz mode with hidden answers and self-assessment
- review mode for weak questions
- quiz result export to CSV and JSON

**Launch app:** `YOUR_STREAMLIT_APP_LINK_HERE`

### Current Coverage

- Probability and brainteasers
- Statistics and estimation
- Time series and forecasting
- Machine learning for quants
- Derivatives and Greeks
- Stochastic calculus
- Coding and numerical methods
- Risk measures and backtesting basics

### Screenshots

Replace the paths below with your actual screenshot file names.

```markdown
![Home](docs/screenshots/home.png)

![Question Bank](docs/screenshots/question-bank.png)

![Quiz Mode](docs/screenshots/quiz-mode.png)

![Formula Sheet](docs/screenshots/formula-sheet.png)

![Review Mode](docs/screenshots/review-mode.png)
```

### Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Data Structure

The app content is stored in JSON files:

```text
data/questions.json
data/formulas.json
```

Each question can include:

```json
{
  "id": "example_001",
  "topic": "Derivatives",
  "subtopic": "Black-Scholes-Merton",
  "difficulty": "Medium",
  "status": "Verified",
  "question": "Question text",
  "intuition": "Short intuition",
  "solution": "Interview-level solution",
  "derivation": "Optional LaTeX derivation",
  "formula": "Key formula",
  "code_language": "python",
  "code": "Optional code example",
  "complexity": "Optional complexity analysis",
  "common_mistake": "Common mistake",
  "interview_tip": "Interview tip",
  "tags": ["BSM", "Option Pricing"]
}
```
