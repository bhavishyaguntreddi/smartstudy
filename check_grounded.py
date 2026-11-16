# check_grounded.py - run 15 test questions against the sample notes and save the answers
# to a CSV for MANUAL grading. Uses a throwaway session that is deleted at the end.
import csv
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from store import add_file, delete_all
from answer import answer

SID = "grounded_check"
QUESTIONS = [   # (is it covered by the notes?, question)
    (True,  "Where in a plant cell does photosynthesis happen?"),
    (True,  "Why do leaves look green?"),
    (True,  "What happens in the Calvin cycle?"),
    (True,  "What is a limiting factor?"),
    (True,  "Why does a very high temperature lower the rate of photosynthesis?"),
    (True,  "What is the equilibrium price?"),
    (True,  "What tends to happen when the price is below the equilibrium price?"),
    (True,  "What is the difference between a movement along the demand curve and a shift of the curve?"),
    (True,  "Why does petrol tend to have inelastic demand?"),
    (True,  "Name two things that can shift the demand curve."),
    (False, "What do mitochondria do?"),
    (False, "What is GDP?"),
    (False, "What is the formula for price elasticity of demand?"),            # trap
    (False, "How many ATP molecules does the Calvin cycle use?"),              # trap
    (False, "Who discovered photosynthesis?"),
]

delete_all(SID)
for f in sorted(Path("sample_notes").glob("*.txt")):
    add_file(f, SID)

rows = []
for n, (covered, q) in enumerate(QUESTIONS, 1):
    try:
        r = answer(q, SID)
        text, tokens = r["answer"], r["tokens"]
        sources = "; ".join(f"{s['source']} p{s['page']}" for s in r["sources"])
        passages = " || ".join(s["text"] for s in r["sources"])
        dist = round(r["best_distance"], 3) if r["best_distance"] is not None else ""
    except Exception as e:
        text, tokens, sources, passages, dist = f"ERROR: {e}", (0, 0), "", "", ""
    rows.append({"n": n, "covered_by_notes": "yes" if covered else "no", "question": q,
                 "answer": text, "sources": sources, "best_distance": dist,
                 "tokens_in": tokens[0], "tokens_out": tokens[1], "cited_passages": passages,
                 "grade_correct": "", "grade_supported": "", "grade_clean": "", "grader_notes": ""})
    print(f"{n:>2} | covered={'yes' if covered else 'no ':<3} | dist={dist} | {text[:90]}")

delete_all(SID)                      # remove the throwaway session
Path("results").mkdir(exist_ok=True)
with open("results/grounded_check.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print("\nSaved results/grounded_check.csv")