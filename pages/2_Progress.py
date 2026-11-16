# pages/2_Progress.py - show this visitor's scores per topic, with a "Why this?" panel
import streamlit as st
from session import get_session_id
from database import progress_summary, why_this, WINDOW

st.set_page_config(page_title="SmartStudy - Progress")
sid = get_session_id()

st.title("My progress")
rows = progress_summary(sid)
if not rows:
    st.write("Status: no quiz answers yet. Take a quiz first.")
    st.stop()

# A plain table (readable by screen readers); the level is written as text
st.table([{"Topic": r["topic"], "Level": r["level"], "Answered": r["answered"],
           "Correct": r["correct"],
           "Score": f"{round(100 * r['correct'] / r['answered'])}%"} for r in rows])

st.subheader("Where you are in each topic")
for r in rows:
    info = why_this(sid, r["topic"])
    if info["answered"] < WINDOW:
        nxt = f"Answer {WINDOW - info['answered']} more to see if your level changes."
    else:
        nxt = f"Your last {WINDOW} answers decide your level."
    st.write(f"- {r['topic']}: level {info['level']}. Since your level last changed: "
             f"{info['correct']} correct out of {info['answered']}. {nxt}")

with st.expander("Why this?"):
    st.write("- Data used: only your own quiz answers, saved in this session.")
    st.write(f"- Rule: the last {WINDOW} answers decide. 80% or more moves you up a level; "
             "below 50% moves you to easier practice.")
    st.write("- Nothing here comes from other users.")