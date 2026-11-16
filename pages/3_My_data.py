# pages/3_My_data.py - show everything stored for this visitor, with a delete button
import streamlit as st
from session import get_session_id
from store import get_collection, delete_all
from database import export_results, delete_progress
from accessibility import apply_settings

st.set_page_config(page_title="SmartStudy - My data")
sid = get_session_id()          # this visitor's private ID
settings = apply_settings()     # Settings sidebar (high contrast, large text, plain English)

if st.session_state.pop("just_deleted", False):   # message after a delete
    st.success("Done. Your notes and results have been deleted.")

st.title("My data")
st.write("This page lists everything SmartStudy has stored for you in this browser session.")

st.header("Your notes")
col = get_collection(sid)
metas = col.get()["metadatas"] if col.count() else []
files = {}
for m in metas:
    files[m["source"]] = files.get(m["source"], 0) + 1
if files:
    st.table([{"File": f, "Pieces stored": n} for f, n in files.items()])
else:
    st.write("Status: no notes stored.")

st.header("Your quiz results")
rows = export_results(sid)
if rows:
    st.table([{"Topic": r["topic"], "Level": r["level"], "Question": r["question"],
               "Your answer": r["chosen"],
               "Result": "Correct" if r["is_correct"] else "Wrong"} for r in rows])
else:
    st.write("Status: no quiz results stored.")

st.header("What is not stored")
st.write("The questions you type on the main page and the answers you get are not saved. "
         "They disappear when you close the tab. Your uploaded files are read, split into "
         "pieces and then the original file is discarded; only the pieces are kept.")
st.write("When you ask a question or take a quiz, the closest pieces of your notes are "
         "sent to Claude through Anthropic's API to write the answer.")

st.header("Delete my data")
st.write("This removes your notes and quiz results from SmartStudy. It cannot be undone.")
sure = st.checkbox("I understand this cannot be undone")
if st.button("Delete all my data"):
    if not sure:
        st.warning("Please tick the box first.")
    else:
        delete_all(sid)                    # notes in ChromaDB
        delete_progress(sid)               # results in SQLite
        for k in ("quiz", "quiz_result", "quiz_topic", "asked", "last"):
            st.session_state.pop(k, None)  # forget the current quiz and answer
        st.session_state.just_deleted = True
        st.rerun()