import csv
import io
import json
import random
from datetime import datetime
from pathlib import Path
from collections import Counter, defaultdict

import streamlit as st


APP_TITLE = "Quant Interview Trainer"
DATA_PATH = Path(__file__).parent / "data" / "questions.json"
FORMULA_PATH = Path(__file__).parent / "data" / "formulas.json"


@st.cache_data
def load_questions(file_mtime):
    """Load question data from JSON. Cache refreshes when the JSON file changes."""
    if not DATA_PATH.exists():
        return []
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_formulas(file_mtime):
    """Load formula sheet data from JSON. Cache refreshes when the JSON file changes."""
    if not FORMULA_PATH.exists():
        return []
    with FORMULA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def unique_values(items, key):
    return sorted({item.get(key, "") for item in items if item.get(key, "")})


def unique_tags(items):
    tags = set()
    for item in items:
        tags.update(item.get("tags", []))
    return sorted(tags)


def match_search(item, search_text):
    if not search_text:
        return True

    searchable_fields = [
        item.get("question", ""),
        item.get("solution", ""),
        item.get("intuition", ""),
        item.get("derivation", ""),
        item.get("common_mistake", ""),
        item.get("interview_tip", ""),
        item.get("code", ""),
        item.get("complexity", ""),
        item.get("topic", ""),
        item.get("subtopic", ""),
        " ".join(item.get("tags", [])),
    ]

    text = " ".join(searchable_fields).lower()
    return search_text.lower() in text


def match_formula_search(item, search_text):
    if not search_text:
        return True

    searchable_fields = [
        item.get("name", ""),
        item.get("topic", ""),
        item.get("subtopic", ""),
        item.get("formula", ""),
        item.get("explanation", ""),
        " ".join(item.get("tags", [])),
    ]

    text = " ".join(searchable_fields).lower()
    return search_text.lower() in text


def render_optional_expander(title, content, kind="markdown"):
    """Render an optional expandable section if content exists."""
    if not content:
        return

    with st.expander(title):
        if kind == "warning":
            st.warning(content)
        elif kind == "info":
            st.info(content)
        else:
            st.markdown(content)


def question_card(item, index):
    status = item.get("status", "Draft")
    difficulty = item.get("difficulty", "Unknown")
    topic = item.get("topic", "Unknown")
    subtopic = item.get("subtopic", "")

    with st.container(border=True):
        st.markdown(f"### {index}. {item.get('question', 'Untitled question')}")
        st.caption(f"{topic} · {subtopic} · {difficulty} · {status}")

        tags = item.get("tags", [])
        if tags:
            st.markdown(" ".join([f"`{tag}`" for tag in tags]))

        render_optional_expander(
            "Interview intuition",
            item.get("intuition", "No intuition added yet."),
        )

        with st.expander("Full solution"):
            st.write(item.get("solution", "No solution added yet."))

            formula = item.get("formula", "")
            if formula:
                st.markdown("**Key formula**")
                st.code(formula, language="text")

        render_optional_expander("Math derivation", item.get("derivation", ""))

        code = item.get("code", "")
        if code:
            language = item.get("code_language", "python")
            with st.expander("Code example"):
                st.code(code, language=language)

        render_optional_expander("Complexity", item.get("complexity", ""), kind="info")
        render_optional_expander("Common mistake", item.get("common_mistake", ""), kind="warning")
        render_optional_expander("Interview tip", item.get("interview_tip", ""), kind="info")


def question_prompt_card(item, index, total):
    """Render a quiz prompt without immediately revealing the answer."""
    with st.container(border=True):
        st.markdown(f"### Question {index} of {total}")
        st.markdown(f"**{item.get('question', 'Untitled question')}**")
        st.caption(
            f"{item.get('topic', 'Unknown')} · "
            f"{item.get('subtopic', '')} · "
            f"{item.get('difficulty', 'Unknown')} · "
            f"{item.get('status', 'Draft')}"
        )

        tags = item.get("tags", [])
        if tags:
            st.markdown(" ".join([f"`{tag}`" for tag in tags]))


def quiz_answer_card(item):
    """Render answer content for quiz mode."""
    render_optional_expander("Interview intuition", item.get("intuition", "No intuition added yet."))

    with st.expander("Full solution", expanded=True):
        st.write(item.get("solution", "No solution added yet."))

        formula = item.get("formula", "")
        if formula:
            st.markdown("**Key formula**")
            st.code(formula, language="text")

    render_optional_expander("Math derivation", item.get("derivation", ""))

    code = item.get("code", "")
    if code:
        language = item.get("code_language", "python")
        with st.expander("Code example"):
            st.code(code, language=language)

    render_optional_expander("Complexity", item.get("complexity", ""), kind="info")
    render_optional_expander("Common mistake", item.get("common_mistake", ""), kind="warning")
    render_optional_expander("Interview tip", item.get("interview_tip", ""), kind="info")


def formula_card(item, index):
    with st.container(border=True):
        st.markdown(f"### {index}. {item.get('name', 'Untitled formula')}")
        st.caption(f"{item.get('topic', 'Unknown')} · {item.get('subtopic', '')}")

        formula = item.get("formula", "")
        if formula:
            st.latex(formula)

        explanation = item.get("explanation", "")
        if explanation:
            st.write(explanation)

        tags = item.get("tags", [])
        if tags:
            st.markdown(" ".join([f"`{tag}`" for tag in tags]))


def initialize_quiz_state():
    defaults = {
        "quiz_questions": [],
        "quiz_index": 0,
        "quiz_results": {},
        "quiz_started": False,
        "quiz_finished": False,
        "quiz_show_answer": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_quiz():
    st.session_state.quiz_questions = []
    st.session_state.quiz_index = 0
    st.session_state.quiz_results = {}
    st.session_state.quiz_started = False
    st.session_state.quiz_finished = False
    st.session_state.quiz_show_answer = False


def start_quiz(candidate_questions, n_questions, seed=None):
    if not candidate_questions:
        st.warning("No questions available for the selected quiz filters.")
        return

    rng = random.Random(seed)
    n = min(n_questions, len(candidate_questions))
    selected = rng.sample(candidate_questions, n)

    st.session_state.quiz_questions = selected
    st.session_state.quiz_index = 0
    st.session_state.quiz_results = {}
    st.session_state.quiz_started = True
    st.session_state.quiz_finished = False
    st.session_state.quiz_show_answer = False


def record_quiz_result(result_label):
    questions = st.session_state.quiz_questions
    idx = st.session_state.quiz_index

    if idx >= len(questions):
        st.session_state.quiz_finished = True
        return

    qid = questions[idx].get("id", f"question_{idx}")
    st.session_state.quiz_results[qid] = {
        "result": result_label,
        "question": questions[idx],
    }

    if idx + 1 >= len(questions):
        st.session_state.quiz_finished = True
    else:
        st.session_state.quiz_index += 1
        st.session_state.quiz_show_answer = False


def quiz_score_value(result_label):
    if result_label == "Correct":
        return 1.0
    if result_label == "Partially correct":
        return 0.5
    return 0.0



def build_quiz_export_payload():
    """Build a JSON-serializable quiz result payload."""
    quiz_questions = st.session_state.quiz_questions
    results = st.session_state.quiz_results

    total = len(quiz_questions)
    raw_score = sum(quiz_score_value(v["result"]) for v in results.values())
    percentage = 100 * raw_score / total if total else 0

    items = []
    for idx, q in enumerate(quiz_questions, start=1):
        qid = q.get("id", f"question_{idx}")
        result = results.get(qid, {}).get("result", "Unanswered")
        items.append(
            {
                "index": idx,
                "id": qid,
                "topic": q.get("topic", ""),
                "subtopic": q.get("subtopic", ""),
                "difficulty": q.get("difficulty", ""),
                "status": q.get("status", ""),
                "result": result,
                "question": q.get("question", ""),
                "formula": q.get("formula", ""),
                "tags": ", ".join(q.get("tags", [])),
            }
        )

    topic_summary = defaultdict(lambda: {"total": 0, "score": 0.0})
    for q in quiz_questions:
        qid = q.get("id")
        topic = q.get("topic", "Unknown")
        topic_summary[topic]["total"] += 1
        if qid in results:
            topic_summary[topic]["score"] += quiz_score_value(results[qid]["result"])

    topic_rows = []
    for topic, values in sorted(topic_summary.items()):
        total_topic = values["total"]
        score_topic = values["score"]
        topic_rows.append(
            {
                "topic": topic,
                "score": score_topic,
                "total": total_topic,
                "score_percent": 100 * score_topic / total_topic if total_topic else 0,
            }
        )

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_questions": total,
        "raw_score": raw_score,
        "score_percent": percentage,
        "items": items,
        "topic_summary": topic_rows,
    }


def quiz_payload_to_csv(payload):
    """Convert quiz export payload to CSV text."""
    output = io.StringIO()
    fieldnames = [
        "index",
        "id",
        "topic",
        "subtopic",
        "difficulty",
        "status",
        "result",
        "question",
        "formula",
        "tags",
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for row in payload["items"]:
        writer.writerow(row)

    return output.getvalue()


def get_review_questions_from_quiz():
    """Return questions marked as weak during the current quiz session."""
    results = st.session_state.quiz_results
    return [
        v["question"]
        for v in results.values()
        if v["result"] in {"Wrong", "Need review", "Partially correct"}
    ]

def render_quiz_summary():
    quiz_questions = st.session_state.quiz_questions
    results = st.session_state.quiz_results

    total = len(quiz_questions)
    answered = len(results)
    raw_score = sum(quiz_score_value(v["result"]) for v in results.values())
    percentage = 100 * raw_score / total if total else 0

    st.success("Quiz completed!")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Questions", total)
    col2.metric("Answered", answered)
    col3.metric("Score", f"{raw_score:.1f}/{total}")
    col4.metric("Score %", f"{percentage:.1f}%")

    result_counts = Counter(v["result"] for v in results.values())

    st.markdown("### Result breakdown")
    st.write(
        {
            "Correct": result_counts.get("Correct", 0),
            "Partially correct": result_counts.get("Partially correct", 0),
            "Wrong": result_counts.get("Wrong", 0),
            "Need review": result_counts.get("Need review", 0),
        }
    )

    topic_summary = defaultdict(lambda: {"total": 0, "score": 0.0})
    for q in quiz_questions:
        qid = q.get("id")
        topic = q.get("topic", "Unknown")
        topic_summary[topic]["total"] += 1
        if qid in results:
            topic_summary[topic]["score"] += quiz_score_value(results[qid]["result"])

    st.markdown("### Topic summary")
    summary_rows = []
    for topic, values in sorted(topic_summary.items()):
        topic_total = values["total"]
        topic_score = values["score"]
        summary_rows.append(
            {
                "Topic": topic,
                "Score": f"{topic_score:.1f}/{topic_total}",
                "Score %": f"{100 * topic_score / topic_total:.1f}%",
            }
        )
    st.dataframe(summary_rows, use_container_width=True, hide_index=True)

    payload = build_quiz_export_payload()
    csv_text = quiz_payload_to_csv(payload)
    json_text = json.dumps(payload, indent=2, ensure_ascii=False)

    st.markdown("### Export quiz results")
    export_col1, export_col2 = st.columns(2)
    with export_col1:
        st.download_button(
            label="Download quiz results CSV",
            data=csv_text,
            file_name="quant_interview_quiz_results.csv",
            mime="text/csv",
        )
    with export_col2:
        st.download_button(
            label="Download quiz results JSON",
            data=json_text,
            file_name="quant_interview_quiz_results.json",
            mime="application/json",
        )

    review_items = get_review_questions_from_quiz()

    st.markdown("### Review list")
    if not review_items:
        st.info("No review items. Excellent work.")
    else:
        st.caption("Questions marked Wrong, Partially correct, or Need review.")

        review_payload = {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "review_count": len(review_items),
            "review_items": [
                {
                    "id": q.get("id", ""),
                    "topic": q.get("topic", ""),
                    "subtopic": q.get("subtopic", ""),
                    "difficulty": q.get("difficulty", ""),
                    "question": q.get("question", ""),
                    "solution": q.get("solution", ""),
                    "formula": q.get("formula", ""),
                    "tags": q.get("tags", []),
                }
                for q in review_items
            ],
        }

        st.download_button(
            label="Download review list JSON",
            data=json.dumps(review_payload, indent=2, ensure_ascii=False),
            file_name="quant_interview_review_list.json",
            mime="application/json",
        )

        for i, item in enumerate(review_items, start=1):
            question_card(item, i)

    if st.button("Start a new quiz"):
        reset_quiz()


def build_topic_summary(questions):
    """Build topic-level summary for the home page."""
    rows = []
    for topic in sorted({q.get("topic", "Unknown") for q in questions}):
        topic_questions = [q for q in questions if q.get("topic", "Unknown") == topic]
        rows.append(
            {
                "Topic": topic,
                "Questions": len(topic_questions),
                "Verified": sum(q.get("status") == "Verified" for q in topic_questions),
                "With derivations": sum(bool(q.get("derivation")) for q in topic_questions),
                "With code": sum(bool(q.get("code")) for q in topic_questions),
            }
        )
    return rows


def render_home_tab(questions, formulas):
    """Render a portfolio-friendly home tab."""
    st.subheader("Quant Interview Trainer")

    st.markdown(
        """
        This app is an interactive preparation tool for quantitative finance interviews.
        It turns structured quant interview notes into a searchable question bank,
        formula sheet, coding-practice library, and quiz-based review system.
        """
    )

    home_col1, home_col2, home_col3 = st.columns(3)
    with home_col1:
        st.markdown(
            """
            **For interview practice**
            - Hidden-answer quiz mode
            - Self-assessment workflow
            - Review list for weak questions
            """
        )
    with home_col2:
        st.markdown(
            """
            **For technical revision**
            - Probability and statistics
            - Derivatives and Greeks
            - Stochastic calculus and time series
            """
        )
    with home_col3:
        st.markdown(
            """
            **For coding preparation**
            - Python examples
            - Numerical methods
            - Risk and option-pricing functions
            """
        )

    st.markdown("### Project snapshot")

    metric_cols = st.columns(5)
    metric_cols[0].metric("Questions", len(questions))
    metric_cols[1].metric("Formulas", len(formulas))
    metric_cols[2].metric("Topics", len({q.get("topic", "Unknown") for q in questions}))
    metric_cols[3].metric("Derivations", sum(bool(q.get("derivation")) for q in questions))
    metric_cols[4].metric("Code examples", sum(bool(q.get("code")) for q in questions))

    st.markdown("### Topic coverage")
    st.dataframe(build_topic_summary(questions), use_container_width=True, hide_index=True)

    st.markdown("### Suggested workflow")

    st.markdown(
        """
        1. Use **Question Bank** to search and review topics.
        2. Use **Formula Sheet** for quick revision before interviews.
        3. Use **Quiz Mode** to simulate active recall.
        4. Use **Review Mode** to revisit weak questions.
        5. Export quiz results for your own study record.
        """
    )

    st.info(
        "Tip: For serious interview preparation, start with Probability, "
        "then Derivatives/Greeks, then Stochastic Calculus, then Coding."
    )


def find_duplicate_values(items, key, normalizer=None):
    """Find duplicate values for a selected key."""
    normalizer = normalizer or (lambda x: x)
    values = []

    for item in items:
        value = item.get(key, "")
        if isinstance(value, str):
            value = value.strip()
        if value:
            values.append(normalizer(value))

    counts = Counter(values)
    return [
        {"Value": value, "Count": count}
        for value, count in counts.items()
        if count > 1
    ]


def build_question_quality_report(questions):
    """Build quality-control checks for question data."""
    required_fields = [
        "id",
        "topic",
        "subtopic",
        "difficulty",
        "status",
        "question",
        "intuition",
        "solution",
        "tags",
    ]
    valid_difficulties = {"Easy", "Medium", "Hard"}
    valid_statuses = {"Verified", "Draft"}

    missing_rows = []
    invalid_rows = []

    for q in questions:
        qid = q.get("id", "<missing id>")

        for field in required_fields:
            value = q.get(field)
            missing = value is None or value == "" or value == []
            if missing:
                missing_rows.append(
                    {
                        "id": qid,
                        "topic": q.get("topic", ""),
                        "field": field,
                        "question": q.get("question", "")[:120],
                    }
                )

        difficulty = q.get("difficulty")
        if difficulty not in valid_difficulties:
            invalid_rows.append(
                {
                    "id": qid,
                    "issue": "Invalid difficulty",
                    "value": difficulty,
                    "expected": "Easy / Medium / Hard",
                }
            )

        status = q.get("status")
        if status not in valid_statuses:
            invalid_rows.append(
                {
                    "id": qid,
                    "issue": "Invalid status",
                    "value": status,
                    "expected": "Verified / Draft",
                }
            )

        tags = q.get("tags", [])
        if tags and not isinstance(tags, list):
            invalid_rows.append(
                {
                    "id": qid,
                    "issue": "Tags should be a list",
                    "value": str(tags),
                    "expected": "list[str]",
                }
            )

        if q.get("code") and not q.get("code_language"):
            invalid_rows.append(
                {
                    "id": qid,
                    "issue": "Code exists but code_language is missing",
                    "value": "",
                    "expected": "python / cpp / text / etc.",
                }
            )

    duplicate_ids = find_duplicate_values(questions, "id")
    duplicate_questions = find_duplicate_values(
        questions,
        "question",
        normalizer=lambda x: " ".join(x.lower().split()),
    )

    topic_rows = []
    for topic in sorted({q.get("topic", "Unknown") for q in questions}):
        topic_questions = [q for q in questions if q.get("topic", "Unknown") == topic]
        topic_rows.append(
            {
                "Topic": topic,
                "Questions": len(topic_questions),
                "Verified": sum(q.get("status") == "Verified" for q in topic_questions),
                "Draft": sum(q.get("status") == "Draft" for q in topic_questions),
                "With formula": sum(bool(q.get("formula")) for q in topic_questions),
                "With derivation": sum(bool(q.get("derivation")) for q in topic_questions),
                "With code": sum(bool(q.get("code")) for q in topic_questions),
            }
        )

    optional_coverage_rows = [
        {"Field": "formula", "Count": sum(bool(q.get("formula")) for q in questions)},
        {"Field": "derivation", "Count": sum(bool(q.get("derivation")) for q in questions)},
        {"Field": "code", "Count": sum(bool(q.get("code")) for q in questions)},
        {"Field": "complexity", "Count": sum(bool(q.get("complexity")) for q in questions)},
        {"Field": "common_mistake", "Count": sum(bool(q.get("common_mistake")) for q in questions)},
        {"Field": "interview_tip", "Count": sum(bool(q.get("interview_tip")) for q in questions)},
    ]

    formula_missing_rows = [
        {
            "id": q.get("id", ""),
            "topic": q.get("topic", ""),
            "difficulty": q.get("difficulty", ""),
            "question": q.get("question", "")[:120],
        }
        for q in questions
        if not q.get("formula")
    ]

    draft_rows = [
        {
            "id": q.get("id", ""),
            "topic": q.get("topic", ""),
            "subtopic": q.get("subtopic", ""),
            "difficulty": q.get("difficulty", ""),
            "question": q.get("question", "")[:120],
        }
        for q in questions
        if q.get("status") == "Draft"
    ]

    return {
        "missing_rows": missing_rows,
        "invalid_rows": invalid_rows,
        "duplicate_ids": duplicate_ids,
        "duplicate_questions": duplicate_questions,
        "topic_rows": topic_rows,
        "optional_coverage_rows": optional_coverage_rows,
        "formula_missing_rows": formula_missing_rows,
        "draft_rows": draft_rows,
    }


def build_formula_quality_report(formulas):
    """Build quality-control checks for formula sheet data."""
    required_fields = ["id", "topic", "subtopic", "name", "formula", "explanation", "tags"]

    missing_rows = []
    invalid_rows = []

    for f in formulas:
        fid = f.get("id", "<missing id>")

        for field in required_fields:
            value = f.get(field)
            missing = value is None or value == "" or value == []
            if missing:
                missing_rows.append(
                    {
                        "id": fid,
                        "topic": f.get("topic", ""),
                        "field": field,
                        "name": f.get("name", "")[:120],
                    }
                )

        tags = f.get("tags", [])
        if tags and not isinstance(tags, list):
            invalid_rows.append(
                {
                    "id": fid,
                    "issue": "Tags should be a list",
                    "value": str(tags),
                    "expected": "list[str]",
                }
            )

    duplicate_ids = find_duplicate_values(formulas, "id")
    duplicate_names = find_duplicate_values(
        formulas,
        "name",
        normalizer=lambda x: " ".join(x.lower().split()),
    )

    topic_rows = []
    for topic in sorted({f.get("topic", "Unknown") for f in formulas}):
        topic_formulas = [f for f in formulas if f.get("topic", "Unknown") == topic]
        topic_rows.append(
            {
                "Topic": topic,
                "Formulas": len(topic_formulas),
            }
        )

    return {
        "missing_rows": missing_rows,
        "invalid_rows": invalid_rows,
        "duplicate_ids": duplicate_ids,
        "duplicate_names": duplicate_names,
        "topic_rows": topic_rows,
    }


def render_content_dashboard(questions, formulas):
    """Render data-quality dashboard for the app content."""
    st.subheader("Content Quality Dashboard")

    st.markdown(
        """
        This dashboard helps maintain the quality of the JSON content behind the app.
        It checks missing fields, duplicate IDs, duplicate questions, status coverage,
        formula coverage, derivation coverage, and code-example coverage.
        """
    )

    q_report = build_question_quality_report(questions)
    f_report = build_formula_quality_report(formulas)

    total_questions = len(questions)
    total_formulas = len(formulas)
    total_issues = (
        len(q_report["missing_rows"])
        + len(q_report["invalid_rows"])
        + len(q_report["duplicate_ids"])
        + len(q_report["duplicate_questions"])
        + len(f_report["missing_rows"])
        + len(f_report["invalid_rows"])
        + len(f_report["duplicate_ids"])
        + len(f_report["duplicate_names"])
    )

    metric_cols = st.columns(6)
    metric_cols[0].metric("Questions", total_questions)
    metric_cols[1].metric("Formulas", total_formulas)
    metric_cols[2].metric("Draft questions", sum(q.get("status") == "Draft" for q in questions))
    metric_cols[3].metric("Missing required fields", len(q_report["missing_rows"]) + len(f_report["missing_rows"]))
    metric_cols[4].metric("Duplicate ID issues", len(q_report["duplicate_ids"]) + len(f_report["duplicate_ids"]))
    metric_cols[5].metric("Total flagged issues", total_issues)

    if total_issues == 0:
        st.success("No major content-quality issues found.")
    else:
        st.warning("Some content-quality issues were flagged. Review the tables below.")

    st.markdown("### Question topic coverage")
    st.dataframe(q_report["topic_rows"], use_container_width=True, hide_index=True)

    st.markdown("### Optional field coverage")
    coverage_rows = []
    for row in q_report["optional_coverage_rows"]:
        count = row["Count"]
        coverage_rows.append(
            {
                "Field": row["Field"],
                "Count": count,
                "Coverage %": f"{100 * count / total_questions:.1f}%" if total_questions else "0.0%",
            }
        )
    st.dataframe(coverage_rows, use_container_width=True, hide_index=True)

    st.markdown("### Formula topic coverage")
    st.dataframe(f_report["topic_rows"], use_container_width=True, hide_index=True)

    st.markdown("### Required-field checks")

    with st.expander("Questions with missing required fields", expanded=False):
        if q_report["missing_rows"]:
            st.dataframe(q_report["missing_rows"], use_container_width=True, hide_index=True)
        else:
            st.success("No question required-field issues found.")

    with st.expander("Formulas with missing required fields", expanded=False):
        if f_report["missing_rows"]:
            st.dataframe(f_report["missing_rows"], use_container_width=True, hide_index=True)
        else:
            st.success("No formula required-field issues found.")

    st.markdown("### Duplicate checks")

    dup_col1, dup_col2 = st.columns(2)
    with dup_col1:
        st.markdown("**Duplicate question IDs**")
        if q_report["duplicate_ids"]:
            st.dataframe(q_report["duplicate_ids"], use_container_width=True, hide_index=True)
        else:
            st.success("No duplicate question IDs.")

        st.markdown("**Duplicate formula IDs**")
        if f_report["duplicate_ids"]:
            st.dataframe(f_report["duplicate_ids"], use_container_width=True, hide_index=True)
        else:
            st.success("No duplicate formula IDs.")

    with dup_col2:
        st.markdown("**Possible duplicate question text**")
        if q_report["duplicate_questions"]:
            st.dataframe(q_report["duplicate_questions"], use_container_width=True, hide_index=True)
        else:
            st.success("No duplicate question text detected.")

        st.markdown("**Possible duplicate formula names**")
        if f_report["duplicate_names"]:
            st.dataframe(f_report["duplicate_names"], use_container_width=True, hide_index=True)
        else:
            st.success("No duplicate formula names detected.")

    st.markdown("### Invalid value checks")

    with st.expander("Invalid question values", expanded=False):
        if q_report["invalid_rows"]:
            st.dataframe(q_report["invalid_rows"], use_container_width=True, hide_index=True)
        else:
            st.success("No invalid question values found.")

    with st.expander("Invalid formula values", expanded=False):
        if f_report["invalid_rows"]:
            st.dataframe(f_report["invalid_rows"], use_container_width=True, hide_index=True)
        else:
            st.success("No invalid formula values found.")

    st.markdown("### Draft and formula-review lists")

    review_col1, review_col2 = st.columns(2)

    with review_col1:
        st.markdown("**Draft questions**")
        if q_report["draft_rows"]:
            st.dataframe(q_report["draft_rows"], use_container_width=True, hide_index=True)
        else:
            st.success("No draft questions.")

    with review_col2:
        st.markdown("**Questions without a formula field**")
        st.caption("This is not always an error. Some conceptual or coding questions do not need formulas.")
        if q_report["formula_missing_rows"]:
            st.dataframe(q_report["formula_missing_rows"], use_container_width=True, hide_index=True)
        else:
            st.success("All questions have formula fields.")

    export_payload = {
        "question_report": q_report,
        "formula_report": f_report,
        "summary": {
            "total_questions": total_questions,
            "total_formulas": total_formulas,
            "total_flagged_issues": total_issues,
        },
    }

    st.markdown("### Export content-quality report")
    st.download_button(
        label="Download content quality report JSON",
        data=json.dumps(export_payload, indent=2, ensure_ascii=False),
        file_name="quant_interview_content_quality_report.json",
        mime="application/json",
    )


def get_curation_bucket(q):
    """Assign a question to one or more curation buckets."""
    buckets = []

    if q.get("status") == "Draft":
        buckets.append("Draft")

    required_fields = ["id", "topic", "subtopic", "difficulty", "status", "question", "intuition", "solution", "tags"]
    if any(q.get(field) in [None, "", []] for field in required_fields):
        buckets.append("Missing required field")

    if not q.get("formula"):
        buckets.append("Missing formula")

    if not q.get("derivation"):
        buckets.append("Missing derivation")

    if not q.get("common_mistake"):
        buckets.append("Missing common mistake")

    if not q.get("interview_tip"):
        buckets.append("Missing interview tip")

    if q.get("code") and not q.get("code_language"):
        buckets.append("Code missing language")

    if q.get("topic") in {"Derivatives", "Greeks", "Stochastic Calculus"} and not q.get("derivation"):
        buckets.append("Technical topic without derivation")

    if q.get("topic") == "Coding" and not q.get("code"):
        buckets.append("Coding topic without code")

    return buckets


def build_curation_rows(questions):
    """Build rows for the content curation workspace."""
    rows = []
    for q in questions:
        buckets = get_curation_bucket(q)
        rows.append(
            {
                "id": q.get("id", ""),
                "topic": q.get("topic", ""),
                "subtopic": q.get("subtopic", ""),
                "difficulty": q.get("difficulty", ""),
                "status": q.get("status", ""),
                "buckets": ", ".join(buckets) if buckets else "No major issue",
                "has_formula": bool(q.get("formula")),
                "has_derivation": bool(q.get("derivation")),
                "has_code": bool(q.get("code")),
                "has_common_mistake": bool(q.get("common_mistake")),
                "has_interview_tip": bool(q.get("interview_tip")),
                "question": q.get("question", ""),
            }
        )
    return rows


def make_question_patch_template(q):
    """Create a JSON patch-style template for manually improving one question."""
    return {
        "id": q.get("id", ""),
        "current_status": q.get("status", ""),
        "suggested_updates": {
            "status": "Verified",
            "intuition": q.get("intuition", ""),
            "solution": q.get("solution", ""),
            "derivation": q.get("derivation", "ADD_DERIVATION_IF_NEEDED"),
            "formula": q.get("formula", "ADD_FORMULA_IF_NEEDED"),
            "common_mistake": q.get("common_mistake", "ADD_COMMON_MISTAKE"),
            "interview_tip": q.get("interview_tip", "ADD_INTERVIEW_TIP"),
            "tags": q.get("tags", []),
        },
        "original_question": q,
    }


def render_curation_workspace(questions):
    """Render a workspace for manually curating question content."""
    st.subheader("Content Curation Workspace")

    st.markdown(
        """
        This workspace helps you review and improve the question bank.
        It does **not** edit `questions.json` automatically. Instead, it helps you
        find weak items, inspect their JSON, and export curation files for manual editing.
        """
    )

    rows = build_curation_rows(questions)

    all_buckets = sorted(
        {
            bucket.strip()
            for row in rows
            for bucket in row["buckets"].split(",")
            if bucket.strip()
        }
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        selected_topics = st.multiselect(
            "Curation topics",
            sorted({row["topic"] for row in rows}),
            default=sorted({row["topic"] for row in rows}),
            key="curation_topics",
        )
    with c2:
        selected_statuses = st.multiselect(
            "Curation status",
            sorted({row["status"] for row in rows}),
            default=sorted({row["status"] for row in rows}),
            key="curation_statuses",
        )
    with c3:
        selected_buckets = st.multiselect(
            "Curation bucket",
            all_buckets,
            default=[],
            help="Leave empty to show all buckets.",
            key="curation_buckets",
        )

    search = st.text_input("Search curation rows", key="curation_search")

    filtered_rows = []
    for row in rows:
        topic_ok = row["topic"] in selected_topics
        status_ok = row["status"] in selected_statuses
        bucket_ok = True if not selected_buckets else any(b in row["buckets"] for b in selected_buckets)

        search_text = " ".join(
            [
                row["id"],
                row["topic"],
                row["subtopic"],
                row["difficulty"],
                row["status"],
                row["buckets"],
                row["question"],
            ]
        ).lower()
        search_ok = True if not search else search.lower() in search_text

        if topic_ok and status_ok and bucket_ok and search_ok:
            filtered_rows.append(row)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total questions", len(rows))
    m2.metric("Filtered rows", len(filtered_rows))
    m3.metric("Draft rows", sum(row["status"] == "Draft" for row in filtered_rows))
    m4.metric("Rows with issues", sum(row["buckets"] != "No major issue" for row in filtered_rows))

    st.markdown("### Curation table")
    st.dataframe(filtered_rows, use_container_width=True, hide_index=True)

    st.download_button(
        label="Download filtered curation table JSON",
        data=json.dumps(filtered_rows, indent=2, ensure_ascii=False),
        file_name="quant_interview_curation_table.json",
        mime="application/json",
    )

    st.markdown("### Inspect one question")

    id_to_question = {q.get("id", ""): q for q in questions}
    filtered_ids = [row["id"] for row in filtered_rows if row["id"] in id_to_question]

    if not filtered_ids:
        st.info("No question is available for inspection under the current filters.")
        return

    selected_id = st.selectbox("Select question ID", filtered_ids, key="curation_selected_id")
    selected_question = id_to_question[selected_id]

    st.markdown("#### Question preview")
    question_card(selected_question, 1)

    st.markdown("#### Raw JSON")
    raw_json = json.dumps(selected_question, indent=2, ensure_ascii=False)
    st.code(raw_json, language="json")

    st.download_button(
        label="Download selected question JSON",
        data=raw_json,
        file_name=f"{selected_id}.json",
        mime="application/json",
    )

    patch_template = make_question_patch_template(selected_question)
    patch_json = json.dumps(patch_template, indent=2, ensure_ascii=False)

    st.markdown("#### Curation patch template")
    st.caption(
        "Use this as a manual editing guide. After editing, copy the improved fields back into data/questions.json."
    )
    st.code(patch_json, language="json")

    st.download_button(
        label="Download curation patch template",
        data=patch_json,
        file_name=f"{selected_id}_curation_patch.json",
        mime="application/json",
    )

    st.markdown("### Manual update workflow")
    st.info(
        "Recommended workflow: inspect a draft or incomplete question → download/copy the patch template → "
        "edit the content → paste the improved fields into data/questions.json → run the app locally → "
        "check Content Dashboard → commit and push."
    )

def main():
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="📈",
        layout="wide",
    )

    initialize_quiz_state()

    question_mtime = DATA_PATH.stat().st_mtime if DATA_PATH.exists() else 0
    formula_mtime = FORMULA_PATH.stat().st_mtime if FORMULA_PATH.exists() else 0

    questions = load_questions(question_mtime)
    formulas = load_formulas(formula_mtime)

    st.title("📈 Quant Interview Trainer")
    st.markdown(
        """
        An interactive question bank for quantitative finance interviews.

        Use this app to review probability, statistics, derivatives, coding,
        stochastic calculus, brainteasers, and quant finance fundamentals.
        """
    )

    if not questions:
        st.warning("No questions found. Please check data/questions.json.")
        return

    topics = unique_values(questions, "topic")
    difficulties = unique_values(questions, "difficulty")
    statuses = unique_values(questions, "status")
    tags = unique_tags(questions)
    n_derivations = sum(bool(q.get("derivation")) for q in questions)
    n_code = sum(bool(q.get("code")) for q in questions)

    st.sidebar.header("Question Filters")

    search_text = st.sidebar.text_input("Search questions, answers, derivations, code, or tags")

    selected_topics = st.sidebar.multiselect(
        "Topic",
        topics,
        default=topics,
    )

    selected_difficulties = st.sidebar.multiselect(
        "Difficulty",
        difficulties,
        default=difficulties,
    )

    selected_statuses = st.sidebar.multiselect(
        "Status",
        statuses,
        default=statuses,
    )

    selected_tags = st.sidebar.multiselect(
        "Tags",
        tags,
    )

    only_derivations = st.sidebar.checkbox("Only show questions with derivations")
    only_code = st.sidebar.checkbox("Only show questions with code examples")

    filtered = []
    for item in questions:
        item_tags = set(item.get("tags", []))

        topic_ok = item.get("topic") in selected_topics
        difficulty_ok = item.get("difficulty") in selected_difficulties
        status_ok = item.get("status") in selected_statuses
        search_ok = match_search(item, search_text)
        tags_ok = True if not selected_tags else bool(item_tags.intersection(selected_tags))
        derivation_ok = True if not only_derivations else bool(item.get("derivation"))
        code_ok = True if not only_code else bool(item.get("code"))

        if topic_ok and difficulty_ok and status_ok and search_ok and tags_ok and derivation_ok and code_ok:
            filtered.append(item)

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total questions", len(questions))
    col2.metric("Filtered questions", len(filtered))
    col3.metric("Topics", len(topics))
    col4.metric("Verified", sum(q.get("status") == "Verified" for q in questions))
    col5.metric("With derivations", n_derivations)
    col6.metric("With code", n_code)

    tab_home, tab_bank, tab_practice, tab_quiz, tab_review, tab_formula, tab_quality, tab_curation, tab_about = st.tabs(
        ["Home", "Question Bank", "Practice Mode", "Quiz Mode", "Review Mode", "Formula Sheet", "Content Dashboard", "Curation Workspace", "About"]
    )


    with tab_home:
        render_home_tab(questions, formulas)


    with tab_bank:
        st.subheader("Question Bank")

        if not filtered:
            st.info("No questions match the current filters.")
        else:
            for i, item in enumerate(filtered, start=1):
                question_card(item, i)

    with tab_practice:
        st.subheader("Random Practice")

        st.write(
            "Click the button below to sample one question from the current filtered set."
        )

        if "practice_question" not in st.session_state:
            st.session_state.practice_question = None

        if st.button("Generate random question"):
            if filtered:
                st.session_state.practice_question = random.choice(filtered)

        if st.session_state.practice_question:
            question_card(st.session_state.practice_question, 1)
        else:
            st.info("Generate a question to start practice mode.")

    with tab_quiz:
        st.subheader("Quiz Mode")

        st.write(
            "Create a short interview-style quiz, answer each question yourself, "
            "then mark your performance."
        )

        quiz_col1, quiz_col2 = st.columns([1, 2])

        with quiz_col1:
            st.markdown("### Quiz settings")

            quiz_topics = st.multiselect(
                "Quiz topics",
                topics,
                default=["Probability"] if "Probability" in topics else topics[:1],
                key="quiz_topics",
            )

            quiz_difficulties = st.multiselect(
                "Quiz difficulties",
                difficulties,
                default=difficulties,
                key="quiz_difficulties",
            )

            quiz_statuses = st.multiselect(
                "Quiz status",
                statuses,
                default=["Verified"] if "Verified" in statuses else statuses,
                key="quiz_statuses",
            )

            quiz_only_derivations = st.checkbox(
                "Only derivation questions",
                key="quiz_only_derivations",
            )

            quiz_only_code = st.checkbox(
                "Only coding questions",
                key="quiz_only_code",
            )

            candidate_quiz_questions = [
                q for q in questions
                if q.get("topic") in quiz_topics
                and q.get("difficulty") in quiz_difficulties
                and q.get("status") in quiz_statuses
                and (not quiz_only_derivations or bool(q.get("derivation")))
                and (not quiz_only_code or bool(q.get("code")))
            ]

            max_quiz_n = max(1, min(30, len(candidate_quiz_questions))) if candidate_quiz_questions else 1
            quiz_n = st.slider(
                "Number of questions",
                min_value=1,
                max_value=max_quiz_n,
                value=min(10, max_quiz_n),
                key="quiz_n",
            )

            quiz_seed_text = st.text_input(
                "Optional random seed",
                value="",
                help="Leave blank for a different quiz each time.",
            )

            seed = None
            if quiz_seed_text.strip():
                try:
                    seed = int(quiz_seed_text.strip())
                except ValueError:
                    st.warning("Seed must be an integer. The app will ignore this seed.")
                    seed = None

            st.caption(f"Available questions for this quiz: {len(candidate_quiz_questions)}")

            if st.button("Start / Restart Quiz"):
                start_quiz(candidate_quiz_questions, quiz_n, seed=seed)

            if st.button("Reset Quiz"):
                reset_quiz()

        with quiz_col2:
            if not st.session_state.quiz_started:
                st.info("Choose quiz settings and click **Start / Restart Quiz**.")
            elif st.session_state.quiz_finished:
                render_quiz_summary()
            else:
                quiz_questions = st.session_state.quiz_questions
                idx = st.session_state.quiz_index
                current = quiz_questions[idx]

                progress_value = (idx + 1) / len(quiz_questions)
                st.progress(progress_value)
                st.caption(f"Progress: {idx + 1}/{len(quiz_questions)}")

                question_prompt_card(current, idx + 1, len(quiz_questions))

                if not st.session_state.quiz_show_answer:
                    if st.button("Show answer"):
                        st.session_state.quiz_show_answer = True
                        st.rerun()
                else:
                    quiz_answer_card(current)

                    st.markdown("### Self-assessment")
                    c1, c2, c3, c4 = st.columns(4)

                    with c1:
                        if st.button("Correct"):
                            record_quiz_result("Correct")
                            st.rerun()
                    with c2:
                        if st.button("Partially correct"):
                            record_quiz_result("Partially correct")
                            st.rerun()
                    with c3:
                        if st.button("Wrong"):
                            record_quiz_result("Wrong")
                            st.rerun()
                    with c4:
                        if st.button("Need review"):
                            record_quiz_result("Need review")
                            st.rerun()


    with tab_review:
        st.subheader("Review Mode")

        if not st.session_state.quiz_started:
            st.info("Complete a quiz first to generate a session review list.")
        else:
            review_items = get_review_questions_from_quiz()

            if not review_items:
                if st.session_state.quiz_finished:
                    st.success("No weak questions in the latest quiz session.")
                else:
                    st.info("No review items yet. Finish or self-assess more quiz questions.")
            else:
                st.write(
                    "This tab shows questions marked as **Wrong**, "
                    "**Partially correct**, or **Need review** in the current quiz session."
                )

                topic_counts = Counter(q.get("topic", "Unknown") for q in review_items)
                st.markdown("### Weak-topic count")
                st.dataframe(
                    [{"Topic": topic, "Review count": count} for topic, count in topic_counts.items()],
                    use_container_width=True,
                    hide_index=True,
                )

                for i, item in enumerate(review_items, start=1):
                    question_card(item, i)


    with tab_formula:
        st.subheader("Formula Sheet")

        if not formulas:
            st.info("No formulas found. Please check data/formulas.json.")
        else:
            formula_topics = unique_values(formulas, "topic")
            formula_search = st.text_input("Search formulas", key="formula_search")

            selected_formula_topics = st.multiselect(
                "Formula topics",
                formula_topics,
                default=formula_topics,
                key="formula_topics",
            )

            filtered_formulas = [
                item
                for item in formulas
                if item.get("topic") in selected_formula_topics
                and match_formula_search(item, formula_search)
            ]

            st.caption(f"Showing {len(filtered_formulas)} of {len(formulas)} formulas")

            if not filtered_formulas:
                st.info("No formulas match the current filters.")
            else:
                for i, item in enumerate(filtered_formulas, start=1):
                    formula_card(item, i)


    with tab_quality:
        render_content_dashboard(questions, formulas)



    with tab_curation:
        render_curation_workspace(questions)


    with tab_about:
        st.subheader("About this app")

        st.markdown(
            """
            This is the Quant Interview Trainer.

            **Current features**
            - Portfolio-friendly home page
            - Searchable question bank
            - Topic, difficulty, status, and tag filters
            - Expandable intuition and solution sections
            - Optional math derivation sections
            - Optional code example sections
            - Optional complexity analysis sections
            - Optional common mistake and interview tip sections
            - Random practice mode
            - Session-based quiz mode with self-assessment
            - Quiz result export to CSV and JSON
            - Review Mode for weak questions
            - Formula sheet / quick reference tab
            - Content Quality Dashboard for JSON validation
            - Content Curation Workspace for manual review
            - JSON-based data structure

            **Suggested next versions**
            - Version 1.9: More C++ and quant developer questions
            - Version 1.11A: Advanced derivatives and research-focused questions
            - Version 2.0: Persistent progress tracking
            - Version 1.9: More C++ and quant developer questions
            - Version 1.11A: Advanced derivatives and research-focused questions
            - Version 2.0: Persistent progress tracking
            """
        )


if __name__ == "__main__":
    main()
