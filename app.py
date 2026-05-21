import json
import random
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

    review_items = [
        v["question"]
        for v in results.values()
        if v["result"] in {"Wrong", "Need review", "Partially correct"}
    ]

    st.markdown("### Review list")
    if not review_items:
        st.info("No review items. Excellent work.")
    else:
        st.caption("Questions marked Wrong, Partially correct, or Need review.")
        for i, item in enumerate(review_items, start=1):
            question_card(item, i)

    if st.button("Start a new quiz"):
        reset_quiz()


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

    tab_bank, tab_practice, tab_quiz, tab_formula, tab_about = st.tabs(
        ["Question Bank", "Practice Mode", "Quiz Mode", "Formula Sheet", "About"]
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
            - Session-based quiz mode with self-assessment
            - Formula sheet / quick reference tab
            - JSON-based data structure

            **Suggested next versions**
            - Version 1.7B: Weak-topic review and quiz history export
            - Version 1.8: README polish + screenshots + LinkedIn-ready presentation
            - Version 1.9: More C++ and quant developer questions
            - Version 2.0: Persistent progress tracking
            """
        )


if __name__ == "__main__":
    main()
