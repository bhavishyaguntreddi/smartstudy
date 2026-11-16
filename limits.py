# limits.py - cap how many Claude calls a visitor (and everyone together) can make
import sqlite3
from datetime import date
import streamlit as st

USAGE_DB = "usage.db"     # local file; *.db is already in .gitignore
DAILY_LIMIT = 300         # Claude calls per day, all visitors together
SESSION_LIMIT = 40      # Claude calls per visitor session

def use_one_call():
    """Count one Claude call. Returns (True, "") or (False, a plain-English message)."""
    if st.session_state.get("calls", 0) >= SESSION_LIMIT:
        return False, ("You have reached the limit for this visit (40 AI requests). "
                       "Please come back later.")
    con = sqlite3.connect(USAGE_DB)
    con.execute("CREATE TABLE IF NOT EXISTS usage (day TEXT PRIMARY KEY, n INTEGER)")
    today = date.today().isoformat()
    con.execute("INSERT OR IGNORE INTO usage VALUES (?, 0)", (today,))
    n = con.execute("SELECT n FROM usage WHERE day=?", (today,)).fetchone()[0]
    if n >= DAILY_LIMIT:
        con.close()
        return False, "SmartStudy has reached its daily limit. Please try again tomorrow."
    con.execute("UPDATE usage SET n = n + 1 WHERE day=?", (today,))
    con.commit()
    con.close()
    st.session_state.calls = st.session_state.get("calls", 0) + 1
    return True, ""