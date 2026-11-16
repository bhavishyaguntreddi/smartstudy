# session.py - one private session ID per visitor, shared by every page
import uuid
import streamlit as st
from store import get_collection

def get_session_id():
    if "session_id" not in st.session_state:        # new visitor: make a random ID
        st.session_state.session_id = uuid.uuid4().hex[:12]
    return st.session_state.session_id

def get_topics(sid):
    """Topic names (one per uploaded file) in this visitor's notes."""
    col = get_collection(sid)
    return sorted({m["topic"] for m in col.get()["metadatas"]}) if col.count() else []