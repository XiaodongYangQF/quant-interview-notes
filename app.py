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
CONFIG_PATH = Path(__file__).parent / "config" / "app_config.json"

DEFAULT_CONFIG = {
    "app_title": "Quant Interview Trainer",
    "page_icon": "📈",
    "layout": "wide",
    "app_intro_markdown": (
        "An interactive question bank for quantitative finance interviews.\n\n"
        "Use this app to review probability, statistics, derivatives, coding, "
        "stochastic calculus, brainteasers, and quant finance fundamentals."
    ),
    "default_status_filter": ["Verified", "Draft"],
    "display_defaults": {
        "compact_mode": False,
        "show_tags": True,
        "show_intuition": True,
        "show_solution": True,
        "expand_solutions_by_default": False,
        "show_derivations": True,
        "show_code_examples": True,
        "show_complexity": True,
        "show_common_mistakes": True,
        "show_interview_tips": True,
        "questions_per_page": 25
    },
    "public_private_policy": {
        "public_question_file": "data/questions.json",
        "public_formula_file": "data/formulas.json",
        "private_folder": "private/",
        "private_folder_should_be_gitignored": True
    }
}


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


@st.cache_data
def load_app_config(file_mtime):
    """Load app configuration. Cache refreshes when the config file changes."""
    config = json.loads(json.dumps(DEFAULT_CONFIG))

    if not CONFIG_PATH.exists():
        return config

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        user_config = json.load(f)

    def deep_update(base, updates):
        for key, value in updates.items():
            if isinstance(value, dict) and isinstance(base.get(key), dict):
                deep_update(base[key], value)
            else:
                base[key] = value
        return base

    return deep_update(config, user_config)


def unique_values(items, key):
    return sorted({item.get(key, "") for item in items if item.get(key, "")})


def unique_tags(items):
    tags = set()
    for item in items:
        tags.update(item.get("tags", []))
    return sorted(tags)


def match_search(item, search_text):
    return match_search_scoped(item, search_text, scope="All fields")


def match_search_scoped(item, search_text, scope="All fields"):
    """Search questions using a selected search scope."""
    if not search_text:
        return True

    scope_fields = {
        "All fields": [
            "question",
            "solution",
            "intuition",
            "derivation",
            "common_mistake",
            "interview_tip",
            "code",
            "complexity",
            "topic",
            "subtopic",
            "tags",
            "formula",
        ],
        "Question only": ["question"],
        "Answer / solution": ["solution", "intuition", "derivation", "common_mistake", "interview_tip"],
        "Tags only": ["tags"],
        "Code only": ["code", "complexity", "code_language"],
        "Formula only": ["formula"],
        "Topic / subtopic": ["topic", "subtopic"],
    }

    fields = scope_fields.get(scope, scope_fields["All fields"])
    searchable_fields = []

    for field in fields:
        value = item.get(field, "")
        if isinstance(value, list):
            searchable_fields.append(" ".join(str(v) for v in value))
        else:
            searchable_fields.append(str(value))

    text = " ".join(searchable_fields).lower()
    return search_text.lower() in text


def sort_questions(items, sort_by="Topic", ascending=True):
    """Sort questions for display."""
    difficulty_rank = {"Easy": 1, "Medium": 2, "Hard": 3}

    def key_func(item):
        if sort_by == "Topic":
            return (item.get("topic", ""), item.get("subtopic", ""), item.get("id", ""))
        if sort_by == "Difficulty":
            return (difficulty_rank.get(item.get("difficulty", ""), 99), item.get("topic", ""), item.get("id", ""))
        if sort_by == "Status":
            return (item.get("status", ""), item.get("topic", ""), item.get("id", ""))
        if sort_by == "Question ID":
            return item.get("id", "")
        if sort_by == "Subtopic":
            return (item.get("subtopic", ""), item.get("topic", ""), item.get("id", ""))
        if sort_by == "Has derivation":
            return (not bool(item.get("derivation")), item.get("topic", ""), item.get("id", ""))
        if sort_by == "Has code":
            return (not bool(item.get("code")), item.get("topic", ""), item.get("id", ""))
        return (item.get("topic", ""), item.get("id", ""))

    return sorted(items, key=key_func, reverse=not ascending)


def build_topic_navigator_rows(questions):
    """Build topic-level navigation summary."""
    rows = []
    for topic in sorted({q.get("topic", "Unknown") for q in questions}):
        topic_questions = [q for q in questions if q.get("topic", "Unknown") == topic]
        subtopics = sorted({q.get("subtopic", "") for q in topic_questions if q.get("subtopic", "")})
        rows.append(
            {
                "Topic": topic,
                "Questions": len(topic_questions),
                "Verified": sum(q.get("status") == "Verified" for q in topic_questions),
                "Draft": sum(q.get("status") == "Draft" for q in topic_questions),
                "Subtopics": len(subtopics),
                "With derivations": sum(bool(q.get("derivation")) for q in topic_questions),
                "With code": sum(bool(q.get("code")) for q in topic_questions),
            }
        )
    return rows


def render_topic_navigator(questions):
    """Render a topic navigation tab."""
    st.subheader("Topic Navigator")

    st.markdown(
        """
        Use this tab to understand the structure of the question bank and quickly explore
        topics, subtopics, and representative questions.
        """
    )

    topic_rows = build_topic_navigator_rows(questions)

    st.markdown("### Topic overview")
    st.dataframe(topic_rows, use_container_width=True, hide_index=True)

    topics = sorted({q.get("topic", "Unknown") for q in questions})
    selected_topic = st.selectbox("Select a topic to inspect", topics, key="navigator_topic")

    topic_questions = [q for q in questions if q.get("topic", "Unknown") == selected_topic]
    subtopics = sorted({q.get("subtopic", "") for q in topic_questions if q.get("subtopic", "")})

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Questions", len(topic_questions))
    c2.metric("Subtopics", len(subtopics))
    c3.metric("Verified", sum(q.get("status") == "Verified" for q in topic_questions))
    c4.metric("Draft", sum(q.get("status") == "Draft" for q in topic_questions))

    st.markdown("### Subtopic breakdown")
    subtopic_rows = []
    for subtopic in subtopics:
        subset = [q for q in topic_questions if q.get("subtopic", "") == subtopic]
        subtopic_rows.append(
            {
                "Subtopic": subtopic,
                "Questions": len(subset),
                "Verified": sum(q.get("status") == "Verified" for q in subset),
                "Draft": sum(q.get("status") == "Draft" for q in subset),
                "With derivations": sum(bool(q.get("derivation")) for q in subset),
                "With code": sum(bool(q.get("code")) for q in subset),
            }
        )

    if subtopic_rows:
        st.dataframe(subtopic_rows, use_container_width=True, hide_index=True)
    else:
        st.info("No subtopics found for this topic.")

    st.markdown("### Questions in this topic")
    selected_subtopics = st.multiselect(
        "Filter subtopics",
        subtopics,
        default=subtopics,
        key="navigator_subtopics",
    )

    topic_search = st.text_input("Search within selected topic", key="navigator_search")

    filtered_topic_questions = []
    for q in topic_questions:
        subtopic_ok = True if not selected_subtopics else q.get("subtopic", "") in selected_subtopics
        search_ok = match_search_scoped(q, topic_search, scope="All fields")
        if subtopic_ok and search_ok:
            filtered_topic_questions.append(q)

    filtered_topic_questions = sort_questions(filtered_topic_questions, sort_by="Subtopic", ascending=True)

    st.caption(f"Showing {len(filtered_topic_questions)} questions from {selected_topic}.")

    max_preview = st.slider(
        "Number of preview questions",
        min_value=3,
        max_value=min(30, max(3, len(filtered_topic_questions))) if filtered_topic_questions else 3,
        value=min(10, max(3, len(filtered_topic_questions))) if filtered_topic_questions else 3,
        step=1,
        key="navigator_preview_count",
    )

    for i, item in enumerate(filtered_topic_questions[:max_preview], start=1):
        question_card(item, i)


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


def get_display_setting(name, default=None):
    """Read display settings from Streamlit session state."""
    return st.session_state.get(name, default)


def render_optional_expander(title, content, kind="markdown", expanded=False):
    """Render an optional expandable section if content exists."""
    if not content:
        return

    with st.expander(title, expanded=expanded):
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

    compact_mode = get_display_setting("compact_mode", False)
    show_tags = get_display_setting("show_tags", True)
    show_intuition = get_display_setting("show_intuition", True)
    show_solution = get_display_setting("show_solution", True)
    expand_solutions = get_display_setting("expand_solutions_by_default", False)
    show_derivations = get_display_setting("show_derivations", True)
    show_code_examples = get_display_setting("show_code_examples", True)
    show_complexity = get_display_setting("show_complexity", True)
    show_common_mistakes = get_display_setting("show_common_mistakes", True)
    show_interview_tips = get_display_setting("show_interview_tips", True)

    with st.container(border=True):
        st.markdown(f"### {index}. {item.get('question', 'Untitled question')}")
        st.caption(f"{topic} · {subtopic} · {difficulty} · {status}")

        tags = item.get("tags", [])
        if tags and show_tags:
            st.markdown(" ".join([f"`{tag}`" for tag in tags]))

        if show_intuition and not compact_mode:
            render_optional_expander(
                "Interview intuition",
                item.get("intuition", "No intuition added yet."),
            )

        if show_solution:
            with st.expander("Full solution", expanded=expand_solutions):
                st.write(item.get("solution", "No solution added yet."))

                formula = item.get("formula", "")
                if formula:
                    st.markdown("**Key formula**")
                    st.code(formula, language="text")

        if show_derivations and not compact_mode:
            render_optional_expander("Math derivation", item.get("derivation", ""))

        code = item.get("code", "")
        if code and show_code_examples and not compact_mode:
            language = item.get("code_language", "python")
            with st.expander("Code example"):
                st.code(code, language=language)

        if show_complexity and not compact_mode:
            render_optional_expander("Complexity", item.get("complexity", ""), kind="info")

        if show_common_mistakes and not compact_mode:
            render_optional_expander("Common mistake", item.get("common_mistake", ""), kind="warning")

        if show_interview_tips and not compact_mode:
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
    compact_mode = get_display_setting("compact_mode", False)
    show_intuition = get_display_setting("show_intuition", True)
    show_derivations = get_display_setting("show_derivations", True)
    show_code_examples = get_display_setting("show_code_examples", True)
    show_complexity = get_display_setting("show_complexity", True)
    show_common_mistakes = get_display_setting("show_common_mistakes", True)
    show_interview_tips = get_display_setting("show_interview_tips", True)

    if show_intuition and not compact_mode:
        render_optional_expander("Interview intuition", item.get("intuition", "No intuition added yet."))

    with st.expander("Full solution", expanded=True):
        st.write(item.get("solution", "No solution added yet."))

        formula = item.get("formula", "")
        if formula:
            st.markdown("**Key formula**")
            st.code(formula, language="text")

    if show_derivations and not compact_mode:
        render_optional_expander("Math derivation", item.get("derivation", ""))

    code = item.get("code", "")
    if code and show_code_examples and not compact_mode:
        language = item.get("code_language", "python")
        with st.expander("Code example"):
            st.code(code, language=language)

    if show_complexity and not compact_mode:
        render_optional_expander("Complexity", item.get("complexity", ""), kind="info")

    if show_common_mistakes and not compact_mode:
        render_optional_expander("Common mistake", item.get("common_mistake", ""), kind="warning")

    if show_interview_tips and not compact_mode:
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
        "coding_current": None,
        "coding_show_solution": False,
        "coding_result": None,
        "formula_current": None,
        "formula_show_answer": False,
        "formula_result": None,
        "formula_mode": "Name → Formula",
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
    """Render a portfolio-friendly landing page."""
    st.subheader("Quant Interview Trainer")

    st.markdown(
        """
        Turn static interview notes into an interactive active-recall platform for
        quantitative finance interviews.

        This app combines a searchable question bank, topic navigation, quiz mode,
        mock interview tracks, coding exercises, formula revision, review workflow,
        analytics, and content-quality tools in one place.
        """
    )

    hero_col1, hero_col2 = st.columns([2, 1])

    with hero_col1:
        st.markdown(
            """
            ### What this app does

            - helps you review quant interview topics in a structured way
            - supports active recall through quiz mode
            - stores formulas, derivations, and coding examples together
            - highlights weak topics using review mode
            - helps maintain content quality as the question bank grows
            """
        )

        st.markdown(
            """
            ### Best use cases

            - quant researcher interview prep
            - quant trader / systematic trading prep
            - quant developer and coding interview prep
            - probability, statistics, derivatives, and stochastic calculus revision
            """
        )

    with hero_col2:
        st.info(
            "Suggested workflow:\n\n"
            "1. Explore **Topic Navigator**\n"
            "2. Study with **Question Bank**\n"
            "3. Practise with **Quiz Mode** or **Mock Interview**\n"
            "4. Use **Coding Exercise** and **Formula Revision**\n"
            "5. Check **Performance Analytics** and **Review Mode**"
        )

    st.markdown("### Project snapshot")

    metric_cols = st.columns(6)
    metric_cols[0].metric("Questions", len(questions))
    metric_cols[1].metric("Formulas", len(formulas))
    metric_cols[2].metric("Topics", len({q.get("topic", "Unknown") for q in questions}))
    metric_cols[3].metric("Derivations", sum(bool(q.get("derivation")) for q in questions))
    metric_cols[4].metric("Code examples", sum(bool(q.get("code")) for q in questions))
    metric_cols[5].metric("Verified", sum(q.get("status") == "Verified" for q in questions))

    st.markdown("### Main features")

    feat1, feat2, feat3 = st.columns(3)
    with feat1:
        st.markdown(
            """
            **Learning & revision**
            - searchable question bank
            - topic and difficulty filters
            - formula sheet
            - derivations and interview tips
            """
        )
    with feat2:
        st.markdown(
            """
            **Practice**
            - random practice mode
            - quiz mode
            - self-assessment
            - weak-question review list
            """
        )
    with feat3:
        st.markdown(
            """
            **Project quality**
            - content dashboard
            - curation workspace
            - JSON-based structure
            - exportable quiz and curation files
            """
        )

    st.markdown("### Topic coverage")
    st.dataframe(build_topic_summary(questions), use_container_width=True, hide_index=True)

    st.markdown("### Recommended study route")
    st.markdown(
        """
        1. **Probability & Statistics** – start with foundations.
        2. **Derivatives & Greeks** – core interview topics.
        3. **Stochastic Calculus & Time Series** – more advanced quantitative material.
        4. **Coding & Quant Developer topics** – practical implementation ability.
        5. **Quiz Mode** – test retention under interview-style conditions.
        """
    )

    st.markdown("### Project positioning")
    st.success(
        "The core app framework is now close to complete. Future work can mainly focus on "
        "adding more public-safe content, screenshots, deployment polish, and optional persistent progress tracking."
    )

    st.caption(
        "Tip: After each major update, refresh screenshots for the Home tab, Question Bank, "
        "Quiz Mode, Formula Sheet, Content Dashboard, and Curation Workspace."
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


def render_content_workflow(app_config):
    """Render a long-term content-management workflow tab."""
    st.subheader("Content Workflow")

    st.markdown(
        """
        This tab explains how to maintain and extend the app safely.
        The goal is to make future updates simple: add content, validate it,
        curate it, then commit it.
        """
    )

    st.markdown("### Recommended update workflow")

    st.markdown(
        """
        1. Add a new question or formula using the JSON templates.
        2. Save the update in `data/questions.json` or `data/formulas.json`.
        3. Run the app locally with `streamlit run app.py`.
        4. Open **Content Dashboard** to check missing fields, duplicates, and status.
        5. Open **Curation Workspace** to inspect Draft or incomplete items.
        6. Mark stable items as `Verified`.
        7. Commit and push the update to GitHub.
        """
    )

    st.markdown("### Public/private content rule")

    policy = app_config.get("public_private_policy", {})
    public_q = policy.get("public_question_file", "data/questions.json")
    public_f = policy.get("public_formula_file", "data/formulas.json")
    private_folder = policy.get("private_folder", "private/")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Public-safe files**")
        st.code(f"{public_q}\n{public_f}", language="text")
        st.caption("Only put public-safe interview content here.")

    with col2:
        st.markdown("**Private draft area**")
        st.code(private_folder, language="text")
        st.caption("Use this for private or research-sensitive drafts. Keep it out of GitHub.")

    st.warning(
        "Do not commit private PhD research notes, unpublished research ideas, "
        "or sensitive materials into the public question bank."
    )

    st.markdown("### Recommended content statuses")

    st.markdown(
        """
        - `Draft`: new or incomplete content.
        - `Verified`: checked, public-safe, and ready to show.
        """
    )

    st.markdown("### Suggested folder structure")

    st.code(
        """
data/
  questions.json
  formulas.json

config/
  app_config.json

docs/
  templates/
  version-notes/
  screenshots/

private/          # optional, should be gitignored
  research_questions_draft.json
  private_notes.md
        """.strip(),
        language="text",
    )

    st.markdown("### Useful templates")

    st.markdown(
        """
        Use the templates in `docs/templates/` when adding new content:

        - `new_question_template.json`
        - `new_formula_template.json`
        - `new_coding_question_template.json`
        - `new_derivation_question_template.json`
        - `CONTENT_UPDATE_WORKFLOW.md`
        - `PUBLIC_PRIVATE_CONTENT_GUIDE.md`
        """
    )

    st.markdown("### Suggested Git commands")

    st.code(
        """
git status
git add app.py data/questions.json data/formulas.json config/app_config.json docs/
git commit -m "Update quant interview trainer content"
git push
        """.strip(),
        language="bash",
    )


def get_mock_interview_tracks():
    """Return public-safe preset mock interview tracks."""
    return {
        "Quant Researcher": {
            "description": "Balanced research-style interview with probability, statistics, derivatives, stochastic calculus, and coding.",
            "recommended_questions": 12,
            "recommended_minutes": 45,
            "buckets": [
                {"label": "Probability", "topic": "Probability", "weight": 0.22},
                {"label": "Statistics", "topic": "Statistics", "weight": 0.20},
                {"label": "Derivatives", "topic": "Derivatives", "weight": 0.18},
                {"label": "Stochastic Calculus", "topic": "Stochastic Calculus", "weight": 0.15},
                {"label": "Time Series / ML", "topics": ["Time Series", "Machine Learning"], "weight": 0.15},
                {"label": "Coding", "topic": "Coding", "weight": 0.10},
            ],
        },
        "Quant Developer": {
            "description": "Coding-heavy track for quant developer, systematic trading, and market-data roles.",
            "recommended_questions": 12,
            "recommended_minutes": 45,
            "buckets": [
                {"label": "C++", "topic": "Coding", "subtopics": ["C++"], "weight": 0.22},
                {"label": "Algorithms", "topic": "Coding", "subtopics": ["Algorithms"], "weight": 0.20},
                {"label": "Python", "topic": "Coding", "subtopics": ["Python"], "weight": 0.18},
                {"label": "Quant Developer", "topic": "Coding", "subtopics": ["Quant Developer"], "weight": 0.18},
                {"label": "Numerical Methods", "topic": "Coding", "subtopics": ["Numerical Methods"], "weight": 0.12},
                {"label": "Probability / Statistics", "topics": ["Probability", "Statistics"], "weight": 0.10},
            ],
        },
        "Derivatives Pricing": {
            "description": "Derivative pricing, Greeks, stochastic calculus, and numerical methods.",
            "recommended_questions": 12,
            "recommended_minutes": 45,
            "buckets": [
                {"label": "Derivatives", "topic": "Derivatives", "weight": 0.35},
                {"label": "Greeks", "topic": "Greeks", "weight": 0.18},
                {"label": "Stochastic Calculus", "topic": "Stochastic Calculus", "weight": 0.22},
                {"label": "Numerical / Coding", "topic": "Coding", "subtopics": ["Numerical Methods", "Python"], "weight": 0.15},
                {"label": "Probability", "topic": "Probability", "weight": 0.10},
            ],
        },
        "Probability & Brainteasers": {
            "description": "Classic quant interview foundations: probability, expected value, and brainteasers.",
            "recommended_questions": 10,
            "recommended_minutes": 35,
            "buckets": [
                {"label": "Probability", "topic": "Probability", "weight": 0.70},
                {"label": "Brainteasers", "topic": "Brainteasers", "weight": 0.20},
                {"label": "Statistics", "topic": "Statistics", "weight": 0.10},
            ],
        },
        "Statistics & Machine Learning": {
            "description": "Statistics, time series, machine learning, and validation-focused questions.",
            "recommended_questions": 12,
            "recommended_minutes": 45,
            "buckets": [
                {"label": "Statistics", "topic": "Statistics", "weight": 0.35},
                {"label": "Machine Learning", "topic": "Machine Learning", "weight": 0.25},
                {"label": "Time Series", "topic": "Time Series", "weight": 0.25},
                {"label": "Python / Coding", "topic": "Coding", "subtopics": ["Python"], "weight": 0.15},
            ],
        },
    }


def question_matches_bucket(question, bucket):
    """Check whether a question belongs to a mock-interview bucket."""
    topic = question.get("topic", "")
    subtopic = question.get("subtopic", "")

    if "topics" in bucket and topic not in bucket["topics"]:
        return False

    if "topic" in bucket and topic != bucket["topic"]:
        return False

    if "subtopics" in bucket and subtopic not in bucket["subtopics"]:
        return False

    return True


def allocate_mock_counts(buckets, total_questions):
    """Allocate question counts across weighted buckets using largest remainder."""
    if total_questions <= 0:
        return [0 for _ in buckets]

    raw = [bucket.get("weight", 0) * total_questions for bucket in buckets]
    base = [int(x) for x in raw]
    remaining = total_questions - sum(base)

    remainders = sorted(
        enumerate([raw_i - base_i for raw_i, base_i in zip(raw, base)]),
        key=lambda x: x[1],
        reverse=True,
    )

    for i, _ in remainders[:remaining]:
        base[i] += 1

    return base


def select_mock_questions(questions, track_config, n_questions, difficulties, statuses, seed=None):
    """Select questions for a weighted mock interview."""
    rng = random.Random(seed)
    buckets = track_config["buckets"]

    base_pool = [
        q for q in questions
        if q.get("difficulty") in difficulties
        and q.get("status") in statuses
    ]

    selected = []
    selected_ids = set()
    counts = allocate_mock_counts(buckets, n_questions)

    for bucket, count in zip(buckets, counts):
        if count <= 0:
            continue

        candidates = [
            q for q in base_pool
            if q.get("id") not in selected_ids
            and question_matches_bucket(q, bucket)
        ]

        rng.shuffle(candidates)
        chosen = candidates[:count]

        selected.extend(chosen)
        selected_ids.update(q.get("id") for q in chosen)

    if len(selected) < n_questions:
        remaining_pool = [q for q in base_pool if q.get("id") not in selected_ids]
        rng.shuffle(remaining_pool)
        needed = n_questions - len(selected)
        selected.extend(remaining_pool[:needed])

    rng.shuffle(selected)
    return selected[:n_questions]


def build_mock_track_preview(questions, track_config, difficulties, statuses):
    """Build availability table for a mock track."""
    rows = []
    for bucket in track_config["buckets"]:
        available = [
            q for q in questions
            if q.get("difficulty") in difficulties
            and q.get("status") in statuses
            and question_matches_bucket(q, bucket)
        ]
        rows.append(
            {
                "Bucket": bucket["label"],
                "Weight": f"{100 * bucket.get('weight', 0):.0f}%",
                "Available questions": len(available),
            }
        )
    return rows


def render_mock_interview(questions, topics, difficulties, statuses):
    """Render mock interview tracks using the existing quiz engine."""
    st.subheader("Mock Interview Tracks")

    st.markdown(
        """
        Choose a preset track to simulate a structured quant interview.
        The mock interview uses the same hidden-answer and self-assessment workflow
        as Quiz Mode, but questions are sampled using track-specific topic weights.
        """
    )

    tracks = get_mock_interview_tracks()

    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.markdown("### Track settings")

        track_name = st.selectbox(
            "Interview track",
            list(tracks.keys()),
            key="mock_track_name",
        )
        track_config = tracks[track_name]

        st.info(track_config["description"])

        mock_difficulties = st.multiselect(
            "Difficulties",
            difficulties,
            default=difficulties,
            key="mock_difficulties",
        )

        mock_statuses = st.multiselect(
            "Status",
            statuses,
            default=["Verified"] if "Verified" in statuses else statuses,
            key="mock_statuses",
        )

        recommended_n = track_config.get("recommended_questions", 12)
        mock_n = st.slider(
            "Number of questions",
            min_value=5,
            max_value=30,
            value=min(recommended_n, 30),
            step=1,
            key="mock_n",
        )

        recommended_minutes = track_config.get("recommended_minutes", 45)
        mock_minutes = st.slider(
            "Target interview time (minutes)",
            min_value=10,
            max_value=90,
            value=recommended_minutes,
            step=5,
            key="mock_minutes",
        )

        seed_text = st.text_input(
            "Optional random seed",
            value="",
            key="mock_seed",
            help="Use a fixed integer seed to reproduce the same mock interview.",
        )

        seed = None
        if seed_text.strip():
            try:
                seed = int(seed_text.strip())
            except ValueError:
                st.warning("Seed must be an integer. The app will ignore this seed.")
                seed = None

        preview_rows = build_mock_track_preview(
            questions,
            track_config,
            mock_difficulties,
            mock_statuses,
        )

        st.markdown("### Track composition")
        st.dataframe(preview_rows, use_container_width=True, hide_index=True)

        total_available = sum(row["Available questions"] for row in preview_rows)
        st.caption(f"Total bucket availability before de-duplication: {total_available}")

        if st.button("Start / Restart Mock Interview"):
            selected = select_mock_questions(
                questions,
                track_config,
                mock_n,
                mock_difficulties,
                mock_statuses,
                seed=seed,
            )

            if not selected:
                st.warning("No questions available for this mock interview setting.")
            else:
                reset_quiz()
                st.session_state.quiz_questions = selected
                st.session_state.quiz_index = 0
                st.session_state.quiz_results = {}
                st.session_state.quiz_started = True
                st.session_state.quiz_finished = False
                st.session_state.quiz_show_answer = False
                st.session_state.mock_track_name = track_name
                st.session_state.mock_target_minutes = mock_minutes
                st.rerun()

        if st.button("Reset Mock Interview"):
            reset_quiz()
            st.rerun()

    with right_col:
        if not st.session_state.quiz_started:
            st.info("Choose a track and click **Start / Restart Mock Interview**.")
        elif st.session_state.quiz_finished:
            active_track = st.session_state.get("mock_track_name", "Mock Interview")
            target_minutes = st.session_state.get("mock_target_minutes", None)

            st.markdown(f"### {active_track} summary")
            if target_minutes:
                st.caption(f"Target interview time: {target_minutes} minutes")

            render_quiz_summary()
        else:
            active_track = st.session_state.get("mock_track_name", track_name)
            target_minutes = st.session_state.get("mock_target_minutes", mock_minutes)

            st.markdown(f"### Active mock interview: {active_track}")
            st.caption(f"Target interview time: {target_minutes} minutes")

            quiz_questions = st.session_state.quiz_questions
            idx = st.session_state.quiz_index
            current = quiz_questions[idx]

            progress_value = (idx + 1) / len(quiz_questions)
            st.progress(progress_value)
            st.caption(f"Progress: {idx + 1}/{len(quiz_questions)}")

            question_prompt_card(current, idx + 1, len(quiz_questions))

            if not st.session_state.quiz_show_answer:
                if st.button("Show answer", key="mock_show_answer"):
                    st.session_state.quiz_show_answer = True
                    st.rerun()
            else:
                quiz_answer_card(current)

                st.markdown("### Self-assessment")
                c1, c2, c3, c4 = st.columns(4)

                with c1:
                    if st.button("Correct", key="mock_correct"):
                        record_quiz_result("Correct")
                        st.rerun()
                with c2:
                    if st.button("Partially correct", key="mock_partial"):
                        record_quiz_result("Partially correct")
                        st.rerun()
                with c3:
                    if st.button("Wrong", key="mock_wrong"):
                        record_quiz_result("Wrong")
                        st.rerun()
                with c4:
                    if st.button("Need review", key="mock_review"):
                        record_quiz_result("Need review")
                        st.rerun()


def get_coding_exercise_questions(questions):
    """Return questions suitable for Coding Exercise Mode."""
    return [
        q for q in questions
        if q.get("topic") == "Coding" or bool(q.get("code"))
    ]


def unique_code_languages(coding_questions):
    """Return available code languages."""
    languages = sorted(
        {
            q.get("code_language", "text")
            for q in coding_questions
            if q.get("code") or q.get("code_language")
        }
    )
    return languages if languages else ["text"]


def get_coding_categories(coding_questions):
    """Return coding exercise categories based on subtopics."""
    categories = sorted({q.get("subtopic", "General") for q in coding_questions})
    return categories


def render_coding_prompt(item):
    """Render a coding exercise prompt without immediately showing the solution."""
    with st.container(border=True):
        st.markdown(f"### {item.get('question', 'Untitled coding question')}")
        st.caption(
            f"{item.get('topic', 'Unknown')} · "
            f"{item.get('subtopic', '')} · "
            f"{item.get('difficulty', 'Unknown')} · "
            f"{item.get('status', 'Draft')}"
        )

        tags = item.get("tags", [])
        if tags:
            st.markdown(" ".join([f"`{tag}`" for tag in tags]))

        intuition = item.get("intuition", "")
        if intuition:
            with st.expander("Hint / intuition", expanded=False):
                st.markdown(intuition)

        formula = item.get("formula", "")
        if formula:
            with st.expander("Key formula / idea", expanded=False):
                st.code(formula, language="text")

        starter_code = item.get("starter_code", "")
        if starter_code:
            st.markdown("#### Starter code")
            st.code(starter_code, language=item.get("code_language", "text"))
        else:
            st.info(
                "No starter code is stored for this question yet. "
                "Try writing your own solution first, then reveal the reference solution."
            )


def render_coding_solution(item):
    """Render the coding exercise solution."""
    st.markdown("### Reference solution")

    solution = item.get("solution", "")
    if solution:
        st.markdown(solution)

    code = item.get("code", "")
    if code:
        st.code(code, language=item.get("code_language", "text"))
    else:
        st.warning("No code solution has been added for this question yet.")

    complexity = item.get("complexity", "")
    if complexity:
        with st.expander("Complexity", expanded=True):
            st.info(complexity)

    common_mistake = item.get("common_mistake", "")
    if common_mistake:
        with st.expander("Common mistake", expanded=False):
            st.warning(common_mistake)

    interview_tip = item.get("interview_tip", "")
    if interview_tip:
        with st.expander("Interview tip", expanded=False):
            st.info(interview_tip)


def render_coding_exercise_mode(questions, difficulties, statuses):
    """Render dedicated coding exercise mode."""
    st.subheader("Coding Exercise Mode")

    st.markdown(
        """
        Practise coding questions separately from the main question bank.
        This mode is designed for Python, C++, algorithms, numerical methods,
        market-data, and quant developer interview preparation.
        """
    )

    coding_questions = get_coding_exercise_questions(questions)

    if not coding_questions:
        st.info("No coding questions are available yet.")
        return

    categories = get_coding_categories(coding_questions)
    languages = unique_code_languages(coding_questions)

    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.markdown("### Exercise filters")

        selected_categories = st.multiselect(
            "Category / subtopic",
            categories,
            default=categories,
            key="coding_categories",
        )

        selected_languages = st.multiselect(
            "Code language",
            languages,
            default=languages,
            key="coding_languages",
        )

        selected_difficulties = st.multiselect(
            "Difficulty",
            difficulties,
            default=difficulties,
            key="coding_difficulties",
        )

        selected_statuses = st.multiselect(
            "Status",
            statuses,
            default=["Verified"] if "Verified" in statuses else statuses,
            key="coding_statuses",
        )

        search_text = st.text_input(
            "Search coding exercises",
            key="coding_search_text",
        )

        filtered_coding = []
        for q in coding_questions:
            category_ok = q.get("subtopic", "General") in selected_categories
            language_ok = q.get("code_language", "text") in selected_languages or not q.get("code")
            difficulty_ok = q.get("difficulty") in selected_difficulties
            status_ok = q.get("status") in selected_statuses
            search_ok = match_search_scoped(q, search_text, scope="All fields")

            if category_ok and language_ok and difficulty_ok and status_ok and search_ok:
                filtered_coding.append(q)

        filtered_coding = sort_questions(filtered_coding, sort_by="Subtopic", ascending=True)

        c1, c2 = st.columns(2)
        c1.metric("Available", len(filtered_coding))
        c2.metric("With code", sum(bool(q.get("code")) for q in filtered_coding))

        st.markdown("### Exercise actions")

        if st.button("Generate random exercise"):
            if not filtered_coding:
                st.warning("No coding exercises match the current filters.")
            else:
                st.session_state.coding_current = random.choice(filtered_coding)
                st.session_state.coding_show_solution = False
                st.session_state.coding_result = None
                st.rerun()

        if filtered_coding:
            id_to_question = {
                f"{q.get('id', '')} — {q.get('question', '')[:70]}": q
                for q in filtered_coding
            }

            selected_label = st.selectbox(
                "Or choose an exercise",
                list(id_to_question.keys()),
                key="coding_selected_question",
            )

            if st.button("Load selected exercise"):
                st.session_state.coding_current = id_to_question[selected_label]
                st.session_state.coding_show_solution = False
                st.session_state.coding_result = None
                st.rerun()

        if st.button("Reset coding exercise"):
            st.session_state.coding_current = None
            st.session_state.coding_show_solution = False
            st.session_state.coding_result = None
            st.rerun()

        st.markdown("### Category overview")
        category_rows = []
        for category in categories:
            subset = [q for q in coding_questions if q.get("subtopic", "General") == category]
            category_rows.append(
                {
                    "Category": category,
                    "Questions": len(subset),
                    "With code": sum(bool(q.get("code")) for q in subset),
                    "Verified": sum(q.get("status") == "Verified" for q in subset),
                }
            )
        st.dataframe(category_rows, use_container_width=True, hide_index=True)

    with right_col:
        current = st.session_state.get("coding_current", None)

        if current is None:
            st.info("Generate or load a coding exercise to start.")
            return

        render_coding_prompt(current)

        if not st.session_state.get("coding_show_solution", False):
            if st.button("Reveal reference solution"):
                st.session_state.coding_show_solution = True
                st.rerun()
        else:
            render_coding_solution(current)

            st.markdown("### Self-assessment")
            c1, c2, c3, c4 = st.columns(4)

            with c1:
                if st.button("Solved"):
                    st.session_state.coding_result = "Solved"
            with c2:
                if st.button("Partially solved"):
                    st.session_state.coding_result = "Partially solved"
            with c3:
                if st.button("Could not solve"):
                    st.session_state.coding_result = "Could not solve"
            with c4:
                if st.button("Need review"):
                    st.session_state.coding_result = "Need review"

            if st.session_state.get("coding_result"):
                st.success(f"Marked as: {st.session_state.coding_result}")

                current_id = current.get("id", "")
                current_record = {
                    "id": current_id,
                    "question": current.get("question", ""),
                    "topic": current.get("topic", ""),
                    "subtopic": current.get("subtopic", ""),
                    "difficulty": current.get("difficulty", ""),
                    "result": st.session_state.coding_result,
                }

                st.download_button(
                    label="Download this exercise result JSON",
                    data=json.dumps(current_record, indent=2, ensure_ascii=False),
                    file_name=f"{current_id}_coding_result.json",
                    mime="application/json",
                )



def render_formula_prompt(item, mode):
    """Render formula revision prompt."""
    with st.container(border=True):
        topic = item.get("topic", "Unknown")
        subtopic = item.get("subtopic", "")
        name = item.get("name", "Untitled formula")
        formula = item.get("formula", "")

        st.caption(f"{topic} · {subtopic}")

        if mode == "Name → Formula":
            st.markdown(f"### {name}")
            st.info("Try to recall the formula before revealing the answer.")
        elif mode == "Formula → Meaning":
            st.markdown("### What does this formula mean?")
            if formula:
                st.latex(formula)
            st.info("Try to explain the formula, its use, and the topic it belongs to.")
        else:
            st.markdown(f"### {name}")
            if formula:
                st.latex(formula)


def render_formula_answer(item, mode):
    """Render formula revision answer."""
    topic = item.get("topic", "Unknown")
    subtopic = item.get("subtopic", "")
    name = item.get("name", "Untitled formula")
    formula = item.get("formula", "")
    explanation = item.get("explanation", "")
    tags = item.get("tags", [])

    st.markdown("### Answer")

    if mode == "Formula → Meaning":
        st.markdown(f"**Name:** {name}")
        st.caption(f"{topic} · {subtopic}")
    else:
        if formula:
            st.latex(formula)

    if explanation:
        st.markdown("**Explanation**")
        st.write(explanation)

    if tags:
        st.markdown(" ".join([f"`{tag}`" for tag in tags]))


def render_formula_revision_mode(formulas):
    """Render formula revision / flashcard mode."""
    st.subheader("Formula Revision Mode")

    st.markdown(
        """
        Use this mode to revise formulas actively instead of only reading the formula sheet.
        You can practise from formula name to formula, or from formula to meaning.
        """
    )

    if not formulas:
        st.info("No formulas are available yet.")
        return

    topics = unique_values(formulas, "topic")

    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.markdown("### Revision settings")

        mode = st.radio(
            "Revision mode",
            ["Name → Formula", "Formula → Meaning"],
            index=0,
            key="formula_revision_mode",
        )

        selected_topics = st.multiselect(
            "Formula topics",
            topics,
            default=topics,
            key="formula_revision_topics",
        )

        search_text = st.text_input(
            "Search formulas",
            key="formula_revision_search",
        )

        filtered_formulas = [
            f for f in formulas
            if f.get("topic") in selected_topics
            and match_formula_search(f, search_text)
        ]

        st.metric("Available formulas", len(filtered_formulas))

        st.markdown("### Actions")

        if st.button("Generate random formula"):
            if not filtered_formulas:
                st.warning("No formulas match the current filters.")
            else:
                st.session_state.formula_current = random.choice(filtered_formulas)
                st.session_state.formula_show_answer = False
                st.session_state.formula_result = None
                st.session_state.formula_mode = mode
                st.rerun()

        if filtered_formulas:
            id_to_formula = {
                f"{f.get('id', '')} — {f.get('name', '')[:70]}": f
                for f in filtered_formulas
            }

            selected_label = st.selectbox(
                "Or choose a formula",
                list(id_to_formula.keys()),
                key="formula_selected_item",
            )

            if st.button("Load selected formula"):
                st.session_state.formula_current = id_to_formula[selected_label]
                st.session_state.formula_show_answer = False
                st.session_state.formula_result = None
                st.session_state.formula_mode = mode
                st.rerun()

        if st.button("Reset formula revision"):
            st.session_state.formula_current = None
            st.session_state.formula_show_answer = False
            st.session_state.formula_result = None
            st.session_state.formula_mode = mode
            st.rerun()

        st.markdown("### Topic overview")
        topic_rows = []
        for topic in topics:
            subset = [f for f in formulas if f.get("topic") == topic]
            topic_rows.append(
                {
                    "Topic": topic,
                    "Formulas": len(subset),
                    "Subtopics": len({f.get("subtopic", "") for f in subset if f.get("subtopic", "")}),
                }
            )
        st.dataframe(topic_rows, use_container_width=True, hide_index=True)

    with right_col:
        current = st.session_state.get("formula_current", None)

        if current is None:
            st.info("Generate or load a formula to start revision.")
            return

        active_mode = st.session_state.get("formula_mode", mode)

        render_formula_prompt(current, active_mode)

        if not st.session_state.get("formula_show_answer", False):
            if st.button("Reveal answer"):
                st.session_state.formula_show_answer = True
                st.rerun()
        else:
            render_formula_answer(current, active_mode)

            st.markdown("### Self-assessment")
            c1, c2, c3 = st.columns(3)

            with c1:
                if st.button("Remembered"):
                    st.session_state.formula_result = "Remembered"
            with c2:
                if st.button("Partially remembered"):
                    st.session_state.formula_result = "Partially remembered"
            with c3:
                if st.button("Need review"):
                    st.session_state.formula_result = "Need review"

            if st.session_state.get("formula_result"):
                st.success(f"Marked as: {st.session_state.formula_result}")

                current_id = current.get("id", "")
                current_record = {
                    "id": current_id,
                    "name": current.get("name", ""),
                    "topic": current.get("topic", ""),
                    "subtopic": current.get("subtopic", ""),
                    "mode": active_mode,
                    "result": st.session_state.formula_result,
                }

                st.download_button(
                    label="Download this formula review result JSON",
                    data=json.dumps(current_record, indent=2, ensure_ascii=False),
                    file_name=f"{current_id}_formula_review_result.json",
                    mime="application/json",
                )



def build_practice_analytics(questions):
    """Build analytics from current quiz/mock session state."""
    quiz_questions = st.session_state.get("quiz_questions", [])
    results = st.session_state.get("quiz_results", {})

    if not quiz_questions:
        return None

    rows = []
    for q in quiz_questions:
        qid = q.get("id", "")
        result = results.get(qid, {}).get("result", "Unanswered")
        rows.append(
            {
                "id": qid,
                "topic": q.get("topic", "Unknown"),
                "subtopic": q.get("subtopic", ""),
                "difficulty": q.get("difficulty", ""),
                "status": q.get("status", ""),
                "result": result,
                "score": quiz_score_value(result) if result != "Unanswered" else 0.0,
                "question": q.get("question", ""),
            }
        )

    total = len(rows)
    answered = sum(row["result"] != "Unanswered" for row in rows)
    raw_score = sum(row["score"] for row in rows)
    score_percent = 100 * raw_score / total if total else 0

    topic_summary = []
    for topic in sorted({row["topic"] for row in rows}):
        subset = [row for row in rows if row["topic"] == topic]
        topic_total = len(subset)
        topic_answered = sum(row["result"] != "Unanswered" for row in subset)
        topic_score = sum(row["score"] for row in subset)
        topic_summary.append(
            {
                "Topic": topic,
                "Questions": topic_total,
                "Answered": topic_answered,
                "Score": f"{topic_score:.1f}/{topic_total}",
                "Score %": f"{100 * topic_score / topic_total:.1f}%" if topic_total else "0.0%",
                "Need review": sum(row["result"] in {"Wrong", "Partially correct", "Need review"} for row in subset),
            }
        )

    difficulty_summary = []
    for difficulty in sorted({row["difficulty"] for row in rows}):
        subset = [row for row in rows if row["difficulty"] == difficulty]
        diff_total = len(subset)
        diff_score = sum(row["score"] for row in subset)
        difficulty_summary.append(
            {
                "Difficulty": difficulty,
                "Questions": diff_total,
                "Score": f"{diff_score:.1f}/{diff_total}",
                "Score %": f"{100 * diff_score / diff_total:.1f}%" if diff_total else "0.0%",
                "Need review": sum(row["result"] in {"Wrong", "Partially correct", "Need review"} for row in subset),
            }
        )

    review_rows = [
        row for row in rows
        if row["result"] in {"Wrong", "Partially correct", "Need review", "Unanswered"}
    ]

    return {
        "rows": rows,
        "summary": {
            "total": total,
            "answered": answered,
            "raw_score": raw_score,
            "score_percent": score_percent,
            "need_review": len([r for r in rows if r["result"] in {"Wrong", "Partially correct", "Need review"}]),
            "unanswered": len([r for r in rows if r["result"] == "Unanswered"]),
        },
        "topic_summary": topic_summary,
        "difficulty_summary": difficulty_summary,
        "review_rows": review_rows,
    }


def build_coding_analytics():
    """Build analytics from the current coding exercise state."""
    current = st.session_state.get("coding_current", None)
    result = st.session_state.get("coding_result", None)

    if current is None:
        return None

    return {
        "id": current.get("id", ""),
        "topic": current.get("topic", ""),
        "subtopic": current.get("subtopic", ""),
        "difficulty": current.get("difficulty", ""),
        "question": current.get("question", ""),
        "result": result or "Not assessed",
    }


def build_formula_analytics():
    """Build analytics from the current formula revision state."""
    current = st.session_state.get("formula_current", None)
    result = st.session_state.get("formula_result", None)

    if current is None:
        return None

    return {
        "id": current.get("id", ""),
        "name": current.get("name", ""),
        "topic": current.get("topic", ""),
        "subtopic": current.get("subtopic", ""),
        "mode": st.session_state.get("formula_mode", ""),
        "result": result or "Not assessed",
    }


def render_performance_analytics(questions, formulas):
    """Render lightweight analytics for current practice sessions."""
    st.subheader("Performance Analytics")

    st.markdown(
        """
        This dashboard summarizes the current practice session. It does not permanently store user data.
        Use the export buttons if you want to save your results externally.
        """
    )

    quiz_analytics = build_practice_analytics(questions)
    coding_analytics = build_coding_analytics()
    formula_analytics = build_formula_analytics()

    st.markdown("### Quiz / Mock Interview Analytics")

    if quiz_analytics is None:
        st.info("No quiz or mock interview session is active yet.")
    else:
        summary = quiz_analytics["summary"]

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Questions", summary["total"])
        c2.metric("Answered", summary["answered"])
        c3.metric("Score", f"{summary['raw_score']:.1f}/{summary['total']}")
        c4.metric("Score %", f"{summary['score_percent']:.1f}%")
        c5.metric("Need review", summary["need_review"])

        st.markdown("#### Topic performance")
        st.dataframe(quiz_analytics["topic_summary"], use_container_width=True, hide_index=True)

        st.markdown("#### Difficulty performance")
        st.dataframe(quiz_analytics["difficulty_summary"], use_container_width=True, hide_index=True)

        with st.expander("Review-priority questions", expanded=False):
            if quiz_analytics["review_rows"]:
                st.dataframe(
                    [
                        {
                            "id": row["id"],
                            "topic": row["topic"],
                            "subtopic": row["subtopic"],
                            "difficulty": row["difficulty"],
                            "result": row["result"],
                            "question": row["question"][:140],
                        }
                        for row in quiz_analytics["review_rows"]
                    ],
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.success("No weak questions in the current session.")

        st.download_button(
            label="Download quiz/mock analytics JSON",
            data=json.dumps(quiz_analytics, indent=2, ensure_ascii=False),
            file_name="quant_interview_practice_analytics.json",
            mime="application/json",
        )

        csv_rows = quiz_analytics["rows"]
        csv_text = "id,topic,subtopic,difficulty,status,result,score,question\n"
        for row in csv_rows:
            safe_question = str(row["question"]).replace('"', '""').replace("\n", " ")
            csv_text += (
                f'"{row["id"]}","{row["topic"]}","{row["subtopic"]}",'
                f'"{row["difficulty"]}","{row["status"]}","{row["result"]}",'
                f'{row["score"]},"{safe_question}"\n'
            )

        st.download_button(
            label="Download quiz/mock analytics CSV",
            data=csv_text,
            file_name="quant_interview_practice_analytics.csv",
            mime="text/csv",
        )

    st.markdown("---")
    st.markdown("### Coding Exercise Analytics")

    if coding_analytics is None:
        st.info("No coding exercise is active yet.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Current result", coding_analytics["result"])
        c2.metric("Category", coding_analytics["subtopic"])
        c3.metric("Difficulty", coding_analytics["difficulty"])

        st.dataframe([coding_analytics], use_container_width=True, hide_index=True)

        st.download_button(
            label="Download coding analytics JSON",
            data=json.dumps(coding_analytics, indent=2, ensure_ascii=False),
            file_name="quant_interview_coding_analytics.json",
            mime="application/json",
        )

    st.markdown("---")
    st.markdown("### Formula Revision Analytics")

    if formula_analytics is None:
        st.info("No formula revision item is active yet.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Current result", formula_analytics["result"])
        c2.metric("Topic", formula_analytics["topic"])
        c3.metric("Mode", formula_analytics["mode"])

        st.dataframe([formula_analytics], use_container_width=True, hide_index=True)

        st.download_button(
            label="Download formula analytics JSON",
            data=json.dumps(formula_analytics, indent=2, ensure_ascii=False),
            file_name="quant_interview_formula_analytics.json",
            mime="application/json",
        )

    st.markdown("---")
    st.markdown("### Suggested next study action")

    if quiz_analytics is not None:
        weak_topics = [
            row["Topic"] for row in quiz_analytics["topic_summary"]
            if row["Need review"] > 0
        ]

        if weak_topics:
            st.warning(
                "Suggested review topics: "
                + ", ".join(weak_topics[:5])
            )
        else:
            st.success("No weak topics detected in the current quiz/mock session.")
    else:
        st.info("Start a quiz or mock interview to generate study suggestions.")



def render_app_status(questions, formulas):
    """Render a near-final app status / roadmap tab."""
    st.subheader("App Status & Roadmap")

    st.markdown(
        """
        This page summarizes the current app framework and what remains before the project
        can be treated as a stable public portfolio project.
        """
    )

    st.markdown("### Current framework status")

    status_rows = [
        {"Area": "Question Bank", "Status": "Complete", "Notes": "Searchable and filterable"},
        {"Area": "Topic Navigator", "Status": "Complete", "Notes": "Topic/subtopic exploration"},
        {"Area": "Practice Mode", "Status": "Complete", "Notes": "Random practice questions"},
        {"Area": "Quiz Mode", "Status": "Complete", "Notes": "Hidden answers and self-assessment"},
        {"Area": "Mock Interview", "Status": "Complete", "Notes": "Preset interview tracks"},
        {"Area": "Coding Exercise", "Status": "Complete", "Notes": "Dedicated coding practice"},
        {"Area": "Formula Revision", "Status": "Complete", "Notes": "Active formula recall"},
        {"Area": "Performance Analytics", "Status": "Complete", "Notes": "Session-level analytics"},
        {"Area": "Review Mode", "Status": "Complete", "Notes": "Weak-question review"},
        {"Area": "Formula Sheet", "Status": "Complete", "Notes": "Quick reference"},
        {"Area": "Content Dashboard", "Status": "Complete", "Notes": "JSON validation"},
        {"Area": "Curation Workspace", "Status": "Complete", "Notes": "Manual review workflow"},
        {"Area": "Content Workflow", "Status": "Complete", "Notes": "Long-term update process"},
        {"Area": "Persistent progress", "Status": "Later", "Notes": "Optional v2.0 feature"},
    ]

    st.dataframe(status_rows, use_container_width=True, hide_index=True)

    st.markdown("### Current content snapshot")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Questions", len(questions))
    c2.metric("Formulas", len(formulas))
    c3.metric("Code examples", sum(bool(q.get("code")) for q in questions))
    c4.metric("Derivations", sum(bool(q.get("derivation")) for q in questions))
    c5.metric("Verified", sum(q.get("status") == "Verified" for q in questions))

    st.markdown("### Recommended next actions")

    next_rows = [
        {
            "Priority": 1,
            "Action": "Take final screenshots",
            "Why": "Needed for README, GitHub, website, and LinkedIn presentation",
        },
        {
            "Priority": 2,
            "Action": "Deploy / redeploy Streamlit app",
            "Why": "Make the app accessible from GitHub and personal website",
        },
        {
            "Priority": 3,
            "Action": "Check Content Dashboard",
            "Why": "Confirm no duplicate IDs or missing required fields",
        },
        {
            "Priority": 4,
            "Action": "Add more public-safe content gradually",
            "Why": "The framework is ready; content can now grow safely",
        },
        {
            "Priority": 5,
            "Action": "Consider v2.0 persistent progress later",
            "Why": "Useful but not required for portfolio readiness",
        },
    ]

    st.dataframe(next_rows, use_container_width=True, hide_index=True)

    st.markdown("### Final public roadmap")

    st.code(
        """
v1.19A  UI cleanup and final portfolio polish
v1.20A  Screenshot refresh and deployment check
v1.21A  Optional small bug-fix / stabilization release
v2.0    Optional persistent progress tracking
        """.strip(),
        language="text",
    )

    st.info(
        "Recommendation: after this version, stop adding major app features for a while. "
        "Focus on testing, screenshots, deployment, and gradually adding public-safe content."
    )


def main():
    # IMPORTANT:
    # st.set_page_config must be the first Streamlit command in the app.
    # Therefore, we call it before loading config through st.cache_data.
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=DEFAULT_CONFIG.get("page_icon", "📈"),
        layout=DEFAULT_CONFIG.get("layout", "wide"),
    )

    config_mtime = CONFIG_PATH.stat().st_mtime if CONFIG_PATH.exists() else 0
    app_config = load_app_config(config_mtime)

    initialize_quiz_state()

    question_mtime = DATA_PATH.stat().st_mtime if DATA_PATH.exists() else 0
    formula_mtime = FORMULA_PATH.stat().st_mtime if FORMULA_PATH.exists() else 0

    questions = load_questions(question_mtime)
    formulas = load_formulas(formula_mtime)

    st.title(f"{app_config.get('page_icon', '📈')} {app_config.get('app_title', APP_TITLE)}")
    st.markdown(app_config.get("app_intro_markdown", DEFAULT_CONFIG["app_intro_markdown"]))

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

    with st.sidebar.expander("Search settings", expanded=True):
        search_text = st.text_input("Search text")
        search_scope = st.selectbox(
            "Search scope",
            [
                "All fields",
                "Question only",
                "Answer / solution",
                "Tags only",
                "Code only",
                "Formula only",
                "Topic / subtopic",
            ],
            index=0,
        )

    with st.sidebar.expander("Sorting settings", expanded=False):
        sort_by = st.selectbox(
            "Sort questions by",
            [
                "Topic",
                "Subtopic",
                "Difficulty",
                "Status",
                "Question ID",
                "Has derivation",
                "Has code",
            ],
            index=0,
        )
        sort_direction = st.radio(
            "Sort direction",
            ["Ascending", "Descending"],
            index=0,
            horizontal=True,
        )

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

    default_statuses = [
        status for status in app_config.get("default_status_filter", statuses)
        if status in statuses
    ] or statuses

    selected_statuses = st.sidebar.multiselect(
        "Status",
        statuses,
        default=default_statuses,
    )

    selected_tags = st.sidebar.multiselect(
        "Tags",
        tags,
    )

    only_derivations = st.sidebar.checkbox("Only show questions with derivations")
    only_code = st.sidebar.checkbox("Only show questions with code examples")

    display_defaults = app_config.get("display_defaults", DEFAULT_CONFIG["display_defaults"])

    with st.sidebar.expander("Display settings", expanded=False):
        st.checkbox("Compact mode", value=display_defaults.get("compact_mode", False), key="compact_mode")
        st.checkbox("Show tags", value=display_defaults.get("show_tags", True), key="show_tags")
        st.checkbox("Show intuition", value=display_defaults.get("show_intuition", True), key="show_intuition")
        st.checkbox("Show solution section", value=display_defaults.get("show_solution", True), key="show_solution")
        st.checkbox(
            "Expand solutions by default",
            value=display_defaults.get("expand_solutions_by_default", False),
            key="expand_solutions_by_default",
        )
        st.checkbox("Show derivations", value=display_defaults.get("show_derivations", True), key="show_derivations")
        st.checkbox("Show code examples", value=display_defaults.get("show_code_examples", True), key="show_code_examples")
        st.checkbox("Show complexity", value=display_defaults.get("show_complexity", True), key="show_complexity")
        st.checkbox("Show common mistakes", value=display_defaults.get("show_common_mistakes", True), key="show_common_mistakes")
        st.checkbox("Show interview tips", value=display_defaults.get("show_interview_tips", True), key="show_interview_tips")
        st.number_input(
            "Questions per page",
            min_value=5,
            max_value=100,
            value=int(display_defaults.get("questions_per_page", 25)),
            step=5,
            key="questions_per_page",
        )

    filtered = []
    for item in questions:
        item_tags = set(item.get("tags", []))

        topic_ok = item.get("topic") in selected_topics
        difficulty_ok = item.get("difficulty") in selected_difficulties
        status_ok = item.get("status") in selected_statuses
        search_ok = match_search_scoped(item, search_text, scope=search_scope)
        tags_ok = True if not selected_tags else bool(item_tags.intersection(selected_tags))
        derivation_ok = True if not only_derivations else bool(item.get("derivation"))
        code_ok = True if not only_code else bool(item.get("code"))

        if topic_ok and difficulty_ok and status_ok and search_ok and tags_ok and derivation_ok and code_ok:
            filtered.append(item)

    filtered = sort_questions(
        filtered,
        sort_by=sort_by,
        ascending=(sort_direction == "Ascending"),
    )

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total questions", len(questions))
    col2.metric("Filtered questions", len(filtered))
    col3.metric("Topics", len(topics))
    col4.metric("Verified", sum(q.get("status") == "Verified" for q in questions))
    col5.metric("With derivations", n_derivations)
    col6.metric("With code", n_code)

    tab_home, tab_navigator, tab_bank, tab_practice, tab_quiz, tab_mock, tab_coding, tab_review, tab_analytics, tab_formula_revision, tab_formula, tab_quality, tab_curation, tab_workflow, tab_status, tab_about = st.tabs(
        ["Home", "Topic Navigator", "Question Bank", "Practice Mode", "Quiz Mode", "Mock Interview", "Coding Exercise", "Review Mode", "Performance Analytics", "Formula Revision", "Formula Sheet", "Content Dashboard", "Curation Workspace", "Content Workflow", "App Status", "About"]
    )


    with tab_home:
        render_home_tab(questions, formulas)


    with tab_navigator:
        render_topic_navigator(questions)


    with tab_bank:
        st.subheader("Question Bank")

        if not filtered:
            st.info("No questions match the current filters.")
        else:
            questions_per_page = int(st.session_state.get("questions_per_page", 25))
            total_pages = max(1, (len(filtered) + questions_per_page - 1) // questions_per_page)

            if total_pages > 1:
                page = st.selectbox(
                    "Page",
                    options=list(range(1, total_pages + 1)),
                    format_func=lambda x: f"Page {x} of {total_pages}",
                    key="question_bank_page",
                )
            else:
                page = 1

            start_idx = (page - 1) * questions_per_page
            end_idx = start_idx + questions_per_page
            displayed_questions = filtered[start_idx:end_idx]

            st.caption(
                f"Showing questions {start_idx + 1}–{min(end_idx, len(filtered))} "
                f"of {len(filtered)} filtered questions."
            )

            for i, item in enumerate(displayed_questions, start=start_idx + 1):
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


    with tab_mock:
        render_mock_interview(questions, topics, difficulties, statuses)


    with tab_coding:
        render_coding_exercise_mode(questions, difficulties, statuses)


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


    with tab_analytics:
        render_performance_analytics(questions, formulas)


    with tab_formula_revision:
        render_formula_revision_mode(formulas)


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


    with tab_workflow:
        render_content_workflow(app_config)


    with tab_status:
        render_app_status(questions, formulas)


    with tab_about:
        st.subheader("About this app")

        st.markdown(
            """
            This is the Quant Interview Trainer, designed as both an interview-preparation tool and a public portfolio project.

            **Current features**

            - Portfolio-friendly landing page
            - Searchable question bank
            - Topic Navigator for topic/subtopic exploration
            - Scoped search and sorting controls
            - Topic, difficulty, status, and tag filters
            - Expandable intuition and solution sections
            - Optional math derivation sections
            - Optional code example sections
            - Optional complexity analysis sections
            - Optional common mistake and interview tip sections
            - Random practice mode
            - Session-based quiz mode with self-assessment
            - Preset Mock Interview tracks
            - Dedicated Coding Exercise Mode
            - Formula Revision Mode
            - Performance Analytics dashboard
            - App Status and final roadmap tab
            - Quiz result export to CSV and JSON
            - Review Mode for weak questions
            - Formula sheet / quick reference tab
            - Content Quality Dashboard for JSON validation
            - Content Curation Workspace for manual review
            - Content Workflow for long-term content management
            - Config-driven app settings
            - JSON-based data structure

            **Suggested next versions**

            - Version 1.20A: Screenshot refresh and deployment check
            - Version 1.21A: Optional small bug-fix / stabilization release
            - Version 2.0: Optional persistent progress tracking
            """
        )

if __name__ == "__main__":
    main()
