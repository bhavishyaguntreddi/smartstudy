# pages/1_Quiz.py - practise questions on one topic, save results, explain wrong answers
import streamlit as st
from session import get_session_id, get_topics
from quiz import make_question
from explain import explain
from database import save_result, why_this, LEVELS
from accessibility import apply_settings, read_aloud

st.set_page_config(page_title="SmartStudy - Quiz")
sid = get_session_id()          # this visitor's private ID
settings = apply_settings()     # Settings sidebar (high contrast, large text, plain English)
topics = get_topics(sid)

st.title("Quiz")
if not topics:
    st.write("Status: no notes yet. Go to the main page and upload notes first.")
    st.stop()                       # nothing more to show on this page

topic = st.selectbox("Topic", topics)
info = why_this(sid, topic)         # this visitor's current level and recent answers
level = info["level"]
st.write(f"Your level in this topic: {level}")   # text, not colour

if st.session_state.get("quiz_topic") != topic:  # topic changed: start fresh
    st.session_state.update(quiz=None, quiz_result=None, quiz_topic=topic, asked=[])

q = st.session_state.quiz
result = st.session_state.quiz_result

# --- A question is waiting for an answer ---
if q and result is None:
    read_aloud(q["question"] + ". " + ". ".join(f"{o['label']}. {o['text']}" for o in q["options"]),
               label="Read question aloud", contrast=settings["contrast"])
    with st.form("answer"):
        st.subheader(q["question"])
        picked = st.radio("Choose one answer",
                          [f"{o['label']}. {o['text']}" for o in q["options"]], index=None)
        submitted = st.form_submit_button("Check answer")
    if submitted and picked is None:
        st.warning("Please choose an answer first.")
    elif submitted:
        chosen = picked.split(". ", 1)[1]            # remove the "A. " label
        ok = save_result(sid, topic, level, q["question"], chosen, q["correct_answer"])
        expl = None
        if not ok:                                   # wrong: explain from the notes
            try:
                with st.spinner("Writing an explanation..."):
                    expl = explain(q["question"], chosen, q["correct_answer"], q["source_text"],
                                   plain=settings["plain"])["text"]
            except Exception:
                expl = "Sorry, the explanation could not be written this time."
        st.session_state.quiz_result = {"ok": ok, "chosen": chosen, "expl": expl, "before": level}
        st.rerun()

# --- The answer has been checked ---
if q and result is not None:
    st.subheader(q["question"])
    st.write(f"Your answer: {result['chosen']}")
    if result["ok"]:
        st.success("Correct.")                       # words as well as colour
    else:
        st.error(f"Not quite. The right answer is: {q['correct_answer']}")
        st.write(result["expl"])
        read_aloud(result["expl"], label="Read explanation aloud", contrast=settings["contrast"])
    with st.expander("Check this in your notes"):
        st.write(f"{q['source_file']}, page {q['source_page']}")
        st.write(q["source_text"])
    if level != result["before"]:                    # the level rules fired: say so
        up = LEVELS.index(level) > LEVELS.index(result["before"])
        st.info(f"Level change: you moved {'up' if up else 'down'} from "
                f"{result['before']} to {level}. "
                + ("You got at least 4 of your last 5 right." if up
                   else "You got fewer than half of your last 5 right."))

# --- Ask for the next question ---
if q is None or result is not None:
    if st.button("New question" if q is None else "Next question"):
        try:
            with st.spinner("Writing a question from your notes..."):
                new_q = make_question(sid, topic, level, avoid=st.session_state.asked[-5:])
        except Exception:
            st.error("Could not write a question this time. Please try again.")
        else:
            st.session_state.update(quiz=new_q, quiz_result=None)
            st.session_state.asked.append(new_q["question"])
            st.rerun()

# --- Why this? ---
with st.expander("Why this?"):
    info = why_this(sid, topic)
    st.write(f"- Your level now: {info['level']}.")
    st.write(f"- Data used: your answers in this topic since your level last changed "
             f"({info['correct']} correct out of {info['answered']} so far).")
    st.write(f"- Rule: {info['rule']}")
    st.write("- Questions are written by Claude from passages of your notes. "
             "Those passages are sent to Claude through Anthropic's API.")