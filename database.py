# database.py - save quiz results in SQLite, per visitor, and decide the next level
import sqlite3
from datetime import datetime, timezone

DB_PATH = "progress.db"        # stays on the server/computer; *.db is in .gitignore
LEVELS = ["easy", "medium", "hard"]
WINDOW = 5                     # look at the last 5 answers
UP_AT, DOWN_BELOW = 0.8, 0.5   # 80%+ moves up, below 50% moves down

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row   # read columns by name
    con.execute("""CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, topic TEXT, level TEXT,
        question TEXT, chosen TEXT, correct_answer TEXT, is_correct INTEGER, created_at TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS topic_level (
        session_id TEXT, topic TEXT, level TEXT, since_id INTEGER,
        PRIMARY KEY (session_id, topic))""")
    return con

def get_state(con, session_id, topic):
    """Current level for this visitor's topic, and the id after which we count answers."""
    row = con.execute("SELECT level, since_id FROM topic_level WHERE session_id=? AND topic=?",
                      (session_id, topic)).fetchone()
    return (row["level"], row["since_id"]) if row else ("easy", 0)

def recent(con, session_id, topic, since_id):
    """The last WINDOW answers given since the level last changed (oldest first)."""
    rows = con.execute(
        "SELECT * FROM results WHERE session_id=? AND topic=? AND id>? ORDER BY id DESC LIMIT ?",
        (session_id, topic, since_id, WINDOW)).fetchall()
    return rows[::-1]

def save_result(session_id, topic, level, question, chosen, correct_answer):
    """Store one answer, then move this visitor's level up or down if the rules say so."""
    con = connect()
    is_correct = int(chosen == correct_answer)
    cur = con.execute(
        "INSERT INTO results (session_id, topic, level, question, chosen, correct_answer,"
        " is_correct, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (session_id, topic, level, question, chosen, correct_answer, is_correct,
         datetime.now(timezone.utc).isoformat()))
    new_id = cur.lastrowid
    level_now, since = get_state(con, session_id, topic)
    rows = recent(con, session_id, topic, since)
    if len(rows) == WINDOW:                       # only decide once we have 5 answers
        score = sum(r["is_correct"] for r in rows) / WINDOW
        i, new_level = LEVELS.index(level_now), level_now
        if score >= UP_AT and i < len(LEVELS) - 1:
            new_level = LEVELS[i + 1]             # unlock the next level
        elif score < DOWN_BELOW and i > 0:
            new_level = LEVELS[i - 1]             # easier practice
        if new_level != level_now:                # restart counting from this answer
            con.execute("INSERT OR REPLACE INTO topic_level VALUES (?,?,?,?)",
                        (session_id, topic, new_level, new_id))
    con.commit()
    con.close()
    return is_correct

def why_this(session_id, topic):
    """Everything the 'Why this?' panel will show: the rule and the data it used."""
    con = connect()
    level, since = get_state(con, session_id, topic)
    rows = recent(con, session_id, topic, since)
    con.close()
    return {"level": level, "answered": len(rows),
            "correct": sum(r["is_correct"] for r in rows),
            "rule": f"The last {WINDOW} answers decide: 80% or more moves you up, "
                    f"below 50% moves you to easier practice."}

def progress_summary(session_id):
    """One row per topic: current level, total answered, total correct (for the Progress page)."""
    con = connect()
    topics = [r["topic"] for r in con.execute(
        "SELECT DISTINCT topic FROM results WHERE session_id=?", (session_id,))]
    out = []
    for t in topics:
        level, _ = get_state(con, session_id, t)
        row = con.execute("SELECT COUNT(*) n, SUM(is_correct) c FROM results "
                          "WHERE session_id=? AND topic=?", (session_id, t)).fetchone()
        out.append({"topic": t, "level": level, "answered": row["n"], "correct": row["c"] or 0})
    con.close()
    return out

def export_results(session_id):
    """Every stored answer for this visitor (the My data page shows this)."""
    con = connect()
    rows = [dict(r) for r in con.execute(
        "SELECT topic, level, question, chosen, correct_answer, is_correct, created_at "
        "FROM results WHERE session_id=? ORDER BY id", (session_id,))]
    con.close()
    return rows

def delete_progress(session_id):
    """Delete everything stored for this visitor."""
    con = connect()
    con.execute("DELETE FROM results WHERE session_id=?", (session_id,))
    con.execute("DELETE FROM topic_level WHERE session_id=?", (session_id,))
    con.commit()
    con.close()

if __name__ == "__main__":   # test with FAKE answers in a separate database file
    import os
    DB_PATH = "test_progress.db"
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    for i in range(5):
        save_result("s1", "demo", "easy", f"Q{i}", "A", "A")     # visitor s1: 5 right
    save_result("s2", "demo", "easy", "Q0", "B", "A")            # visitor s2: 1 wrong
    print("s1 level after 5 right:", why_this("s1", "demo")["level"])      # I expect: medium
    print("s2 level (own data only):", why_this("s2", "demo")["level"])    # I expect: easy
    print("s1 answers stored:", len(export_results("s1")))                  # I expect: 5
    print("s2 answers stored:", len(export_results("s2")))                  # I expect: 1
    delete_progress("s1")
    print("s1 after delete:", len(export_results("s1")), "| s2 untouched:", len(export_results("s2")))