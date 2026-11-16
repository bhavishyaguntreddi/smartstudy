# database.py - save quiz results in SQLite and decide the next level
import sqlite3
from datetime import datetime, timezone

DB_PATH = "progress.db"        # stays on this computer; *.db is in .gitignore
LEVELS = ["easy", "medium", "hard"]
WINDOW = 5                     # look at the last 5 answers
UP_AT, DOWN_BELOW = 0.8, 0.5   # 80%+ moves up, below 50% moves down

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row   # read columns by name
    con.execute("""CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, level TEXT, question TEXT,
        chosen TEXT, correct_answer TEXT, is_correct INTEGER, created_at TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS topic_level (
        topic TEXT PRIMARY KEY, level TEXT, since_id INTEGER)""")
    return con

def get_state(con, topic):
    """Current level for a topic, and the id after which we count answers."""
    row = con.execute("SELECT level, since_id FROM topic_level WHERE topic=?", (topic,)).fetchone()
    return (row["level"], row["since_id"]) if row else ("easy", 0)

def recent(con, topic, since_id):
    """The last WINDOW answers given since the level last changed (oldest first)."""
    rows = con.execute("SELECT * FROM results WHERE topic=? AND id>? ORDER BY id DESC LIMIT ?",
                       (topic, since_id, WINDOW)).fetchall()
    return rows[::-1]

def save_result(topic, level, question, chosen, correct_answer):
    """Store one answer, then move the topic's level up or down if the rules say so."""
    con = connect()
    is_correct = int(chosen == correct_answer)
    cur = con.execute(
        "INSERT INTO results (topic, level, question, chosen, correct_answer, is_correct, created_at)"
        " VALUES (?,?,?,?,?,?,?)",
        (topic, level, question, chosen, correct_answer, is_correct,
         datetime.now(timezone.utc).isoformat()))
    new_id = cur.lastrowid
    level_now, since = get_state(con, topic)
    rows = recent(con, topic, since)
    if len(rows) == WINDOW:                       # only decide once we have 5 answers
        score = sum(r["is_correct"] for r in rows) / WINDOW
        i, new_level = LEVELS.index(level_now), level_now
        if score >= UP_AT and i < len(LEVELS) - 1:
            new_level = LEVELS[i + 1]             # unlock the next level
        elif score < DOWN_BELOW and i > 0:
            new_level = LEVELS[i - 1]             # easier practice
        if new_level != level_now:                # restart counting from this answer
            con.execute("INSERT OR REPLACE INTO topic_level VALUES (?,?,?)",
                        (topic, new_level, new_id))
    con.commit()
    con.close()
    return is_correct

def why_this(topic):
    """Everything the 'Why this?' panel will show: the rule and the data it used."""
    con = connect()
    level, since = get_state(con, topic)
    rows = recent(con, topic, since)
    con.close()
    return {"level": level, "answered": len(rows),
            "correct": sum(r["is_correct"] for r in rows),
            "rule": f"The last {WINDOW} answers decide: 80% or more moves you up, "
                    f"below 50% moves you to easier practice."}

if __name__ == "__main__":   # test with FAKE answers in a separate database file
    import os
    DB_PATH = "test_progress.db"
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    for i in range(5):
        save_result("demo", "easy", f"Q{i}", "A", "A")     # 5 right
    print("after 5 right:", why_this("demo")["level"])      # I expect: medium
    for i in range(5):
        save_result("demo", "medium", f"Q{i}", "B", "A")   # 5 wrong
    print("after 5 wrong:", why_this("demo")["level"])      # I expect: easy
    for i in range(5):
        save_result("demo", "easy", f"Q{i}", "A" if i < 3 else "B", "A")   # 3 right, 2 wrong
    print("after 3 of 5 right:", why_this("demo")["level"]) # I expect: easy (60% stays)