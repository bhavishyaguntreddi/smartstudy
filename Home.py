# app.py - SmartStudy: upload notes and ask questions (main page)
import tempfile
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

load_dotenv()   # reads your key from .env when running on your computer
from store import add_file
from answer import answer, N_CHUNKS
from session import get_session_id, get_topics
from accessibility import apply_settings, read_aloud

st.set_page_config(page_title="SmartStudy")

sid = get_session_id()          # each visitor gets a random ID, so notes and results stay private
settings = apply_settings()     # shows the Settings sidebar and applies the look

MAX_MB = 5   # reject big files (keeps the free server from running out of memory)

st.title("SmartStudy")
st.write("Upload your notes, then ask questions. Answers use only your notes.")

# ---------- 1. Upload ----------
st.header("1. Upload your notes")
files = st.file_uploader("Choose PDF or text files", type=["pdf", "txt"],
                         accept_multiple_files=True)
if files and st.button("Add these notes"):
    for f in files:
        if f.size > MAX_MB * 1024 * 1024:
            st.error(f"Skipped {f.name}: the file is bigger than {MAX_MB} MB.")
            continue
        with tempfile.TemporaryDirectory() as tmp:        # temp copy is deleted right after
            path = Path(tmp) / Path(f.name).name
            path.write_bytes(f.getvalue())
            try:
                n = add_file(path, sid)
                st.write(f"Added {f.name}: {n} pieces.")
            except Exception:
                st.error(f"Could not read any text from {f.name}. "
                         "Scanned PDFs (pictures of pages) do not work yet.")

topics = get_topics(sid)

# ---------- 2. Ask ----------
st.header("2. Ask a question")
if not topics:
    st.write("Status: no notes yet. Upload a file above first.")
else:
    st.write("Your topics: " + ", ".join(topics))
    scope = st.selectbox("Ask about", ["All my notes"] + topics)
    with st.form("ask"):
        question = st.text_input("Your question")
        submitted = st.form_submit_button("Ask")
    if submitted and question.strip():
        topic = None if scope == "All my notes" else scope
        try:
            with st.spinner("Searching your notes..."):
                result = answer(question.strip(), sid, topic=topic, plain=settings["plain"])
            st.session_state.last = result
        except Exception:
            st.error("Something went wrong while answering. Please try again.")

# ---------- Answer, sources, Why this? ----------
r = st.session_state.get("last")
if r:
    st.subheader("Answer")
    st.write(r["answer"])
    read_aloud(r["answer"], contrast=settings["contrast"])   # text stays on screen too
    if r["sources"]:
        st.write("Sources (open one to read the passage):")
        for s in r["sources"]:
            with st.expander(f"{s['source']}, page {s['page']}"):
                st.write(s["text"])
    with st.expander("Why this?"):
        dist = r["best_distance"]
        st.write(f"- Data used: your question and up to {N_CHUNKS} closest passages from your notes. Nothing else.")
        st.write("- Where it went: those passages and your question were sent to Claude, "
                 "through Anthropic's API, to write the answer. Other users cannot see your notes.")
        if dist is not None:
            st.write(f"- How close the best passage was: {dist:.2f} (a lower number means a closer match).")
        st.write("- Rule: the answer may use only those passages. "
                 "If they do not cover the question, it says it does not know.")
        st.write(f"- Passages cited in this answer: {len(r['sources'])}.")