import json
from pathlib import Path

import streamlit as st


APP_TITLE = "Quant Interview Trainer"
DATA_PATH = Path(__file__).parent / "data" / "questions.json"


@st.cache_data
def load_questions(file_mtime):
    """Load question data from JSON. Cache refreshes when the JSON file changes."""
    if not DATA_PATH.exists():
        return []
    with DATA_PATH.open("r", encoding="utf-8") as f:
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

    text = " ".join(
        [
            item.get("question", ""),
            item.get("solution", ""),
            item.get("intuition", ""),
            item.get("topic", ""),
            item.get("subtopic", ""),
            " ".join(item.get("tags", [])),
        ]
    ).lower()

    return search_text.lower() in text


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

        with st.expander("Interview intuition"):
            st.write(item.get("intuition", "No intuition added yet."))

        with st.expander("Full solution"):
            st.write(item.get("solution", "No solution added yet."))

            formula = item.get("formula", "")
            if formula:
                st.markdown("**Key formula**")
                st.code(formula, language="text")


def main():
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="📈",
        layout="wide",
    )


    file_mtime = DATA_PATH.stat().st_mtime if DATA_PATH.exists() else 0
    questions = load_questions(file_mtime)


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

    st.sidebar.header("Filters")

    search_text = st.sidebar.text_input("Search questions, answers, or tags")

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

    filtered = []
    for item in questions:
        item_tags = set(item.get("tags", []))

        topic_ok = item.get("topic") in selected_topics
        difficulty_ok = item.get("difficulty") in selected_difficulties
        status_ok = item.get("status") in selected_statuses
        search_ok = match_search(item, search_text)
        tags_ok = True if not selected_tags else bool(item_tags.intersection(selected_tags))

        if topic_ok and difficulty_ok and status_ok and search_ok and tags_ok:
            filtered.append(item)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total questions", len(questions))
    col2.metric("Filtered questions", len(filtered))
    col3.metric("Topics", len(topics))
    col4.metric("Verified", sum(q.get("status") == "Verified" for q in questions))

    tab_bank, tab_practice, tab_about = st.tabs(
        ["Question Bank", "Practice Mode", "About"]
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
                st.session_state.practice_question = filtered[
                    st.session_state.get("practice_index", 0) % len(filtered)
                ]
                st.session_state.practice_index = st.session_state.get("practice_index", 0) + 1

        if st.session_state.practice_question:
            question_card(st.session_state.practice_question, 1)
        else:
            st.info("Generate a question to start practice mode.")

    with tab_about:
        st.subheader("About this MVP")

        st.markdown(
            """
            This is Version 1.0 of the Quant Interview Trainer.

            **Current features**
            - Searchable question bank
            - Topic, difficulty, status, and tag filters
            - Expandable intuition and solution sections
            - Simple random practice mode
            - JSON-based data structure

            **Suggested next versions**
            - Version 1.1: better tags and subtopics
            - Version 1.2: difficulty levels and verification workflow
            - Version 1.3: stronger random practice mode
            - Version 1.4: formula sheet
            - Version 1.5: Python/C++ coding questions
            - Version 2.0: progress tracking and quiz mode
            """
        )


if __name__ == "__main__":
    main()
