import json
import random
from pathlib import Path

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


def main():
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="📈",
        layout="wide",
    )

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

    tab_bank, tab_practice, tab_formula, tab_about = st.tabs(
        ["Question Bank", "Practice Mode", "Formula Sheet", "About"]
    )

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

    with tab_about:
        st.subheader("About this app")

        st.markdown(
            """
            This is the Quant Interview Trainer.

            **Current features**
            - Searchable question bank
            - Topic, difficulty, status, and tag filters
            - Expandable intuition and solution sections
            - Optional math derivation sections
            - Optional code example sections
            - Optional complexity analysis sections
            - Optional common mistake and interview tip sections
            - Random practice mode
            - Formula sheet / quick reference tab
            - JSON-based data structure

            **Suggested next versions**
            - Version 1.5B: Add more C++ and data-structure questions
            - Version 1.6: Statistics, time series, and machine learning question bank
            - Version 1.7: Better practice mode / quiz mode
            - Version 2.0: Progress tracking and polished portfolio version
            """
        )


if __name__ == "__main__":
    main()
