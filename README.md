# SmartStudy
 
An accessible study assistant for university students. Upload your own notes, ask questions, and practise with quizzes. Answers come only from your notes and always show where they came from.
 
**Live demo:** https://smartstudy-cun5cfk3p6qzedh3bx9xre.streamlit.app
(Please use the sample notes in `sample_notes/` and do not upload personal documents.)
 
This is the working version of my MSc Intelligent User Interfaces (KV7005) project. I built the core version in about 8 hours.
 
## Who it is designed for
 
One app for four kinds of users: an international student who works part time, a blind or low-vision student, a deaf or hard-of-hearing student, and a non-speaking student. Typed input is always available, nothing is audio-only, and every result is written as text and not only shown in colour.
 
## What it does
 
- **Upload notes** (PDF or text). They are split into short pieces and stored in ChromaDB.
- **Ask questions.** Answers use only your notes and cite their sources. If the notes do not cover the question, it says "I don't know based on your notes."
- **Quizzes** at three levels (easy, medium, hard) per topic. Getting 4 or 5 of the last 5 right unlocks the next level. Getting fewer than half right moves you to easier practice.
- **Explanations.** When an answer is wrong, it explains why the right answer is right and what the idea means, using only your notes.
- **Progress** saved per topic (SQLite).
- **"Why this?" panel** on answers, quiz questions and progress, showing the data and the rule behind each one.
- **My data page** showing everything stored, with a delete button.
- **Accessibility settings:** high contrast, large text, plain English mode, a read-aloud button, text labels for every result, and keyboard use.
## Design principles
 
Personalisation, transparency (every recommendation is explained), learner control, accessibility, and minimal data use.
 
## Privacy
 
- No accounts. Each browser session gets a random ID, and its notes and results are stored under that ID only.
- Uploaded files are read, split into pieces and then discarded. Only the pieces are kept.
- When you ask a question or take a quiz, the closest pieces of your notes are sent to Claude through Anthropic's API. The "Why this?" panel says so.
- The **My data** page deletes your notes and results.
- Settings (contrast, text size, plain English) are not stored.
## How it is built
 
Python, Streamlit, the Claude API (`claude-haiku-5-5`, through the `anthropic` library), ChromaDB with its built-in embeddings, SQLite, pypdf and python-dotenv. No LangChain. Library versions are pinned in `requirements.txt`.
 
- `ingest.py` reads files and splits them into pieces
- `store.py` stores and searches pieces (one private ChromaDB collection per session)
- `answer.py` answers from the notes only, with citations
- `quiz.py` writes multiple-choice questions at three levels
- `explain.py` explains wrong answers from the notes
- `database.py` saves results and applies the level rules
- `limits.py` caps AI use at 40 requests per visit and 300 per day
- `accessibility.py` holds the settings and the read-aloud button
- `Home.py` and `pages/` are the Streamlit screens
- `check_grounded.py` runs the 15-question check described below
## How well it answers from the notes
 
I wrote 15 test questions over the two sample notes and graded the answers by hand. The script is `check_grounded.py` and the answers are in `results/grounded_check.csv`.
 
- **10 of 10** questions covered by the notes: the answer was correct, supported by the cited passage, and added nothing from outside the notes.
- **5 of 5** questions not covered by the notes (including 2 trap questions where the model knows the answer from general knowledge): all answered "I don't know based on your notes."
Limits of this check: 15 questions, two short generic files, questions written by me, graded by one person. It shows the approach works, but it is not a benchmark. Search-distance scores for covered and uncovered questions overlapped, so the "I don't know" behaviour comes from the prompt and not from a distance cutoff.
 
## Accessibility testing
 
Keyboard-only use passed my own manual test. I have not yet tested with a screen reader, or with blind, deaf or non-speaking students, so I make no claim of formal accessibility compliance.
 
## Cost
 
Total API spend for building, testing and deploying this project, as shown in the Anthropic console on 16 November 2026: about $0.02. In my test runs, one answer used roughly 1,150 input tokens and 40 to 190 output tokens, and one quiz question used roughly 770 to 780 input tokens and 85 to 750 output tokens (from the usage counts the API returns).
 
## Known limits
 
- Tested with two short sample files only. Not tested with long or messy PDFs.
- Scanned PDFs (pictures of pages) do not work, because there is no text to read.
- Read-aloud uses the browser's built-in speech, so voices differ between computers. It uses a Streamlit function that Streamlit has marked as deprecated, so I pinned the Streamlit version.
- The visit limit resets when the page is refreshed. The daily limit is the real safety net.
- Data lives in the server's temporary storage. If a visitor leaves without using "Delete all my data", it stays there until the app restarts. Automatic clean-up is not built yet.
- The upload box says 200 MB, but files over 5 MB are rejected.
## Not built yet
 
Voice input, a morning/afternoon/evening study feed with accept/delay/decline, RAGAS evaluation, accounts, an anonymous leaderboard, push notifications, and image or video upload.
 
## Run it yourself
 
1. Clone the repository and create a virtual environment.
2. Install the libraries:
```
pip install -r requirements.txt
```
 
3. Create a file named `.env` containing `ANTHROPIC_API_KEY=your-key`. Never commit this file.
4. Start the app:
```
streamlit run Home.py
```
 
To deploy on Streamlit Community Cloud, set the main file to `Home.py` and put `ANTHROPIC_API_KEY = "your-key"` in the app's Secrets.
 
