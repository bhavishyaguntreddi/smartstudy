# ingest.py - read notes (PDF or text) and split them into chunks
import re
from pathlib import Path
from pypdf import PdfReader

MAX_CHARS = 800  # target chunk size, roughly a short paragraph

def read_pages(path):
    """Return a list of (page_number, text). A text file counts as page 1."""
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(path)
        return [(i + 1, page.extract_text() or "") for i, page in enumerate(reader.pages)]
    return [(1, path.read_text(encoding="utf-8"))]

def split_text(text, max_chars=MAX_CHARS):
    """Pack whole sentences into chunks of up to max_chars, with 1-sentence overlap."""
    text = re.sub(r"\s+", " ", text).strip()   # tidy line breaks and extra spaces
    sentences = re.split(r"(?<=[.!?]) ", text)  # cut after . ! or ?
    chunks, current = [], []
    for s in sentences:
        if current and len(" ".join(current + [s])) > max_chars:
            chunks.append(" ".join(current))
            current = [current[-1]]             # overlap: keep the last sentence
        current.append(s)
    if current:
        chunks.append(" ".join(current))
    return chunks

def build_chunks(path):
    """Turn one file into chunk records that carry their source, for citations."""
    path = Path(path)
    records = []
    for page, text in read_pages(path):
        for n, chunk in enumerate(split_text(text)):
            records.append({
                "id": f"{path.stem}-p{page}-c{n}",  # unique ID for each chunk
                "text": chunk,
                "source": path.name,                # shown in citations
                "page": page,                       # shown in citations
                "topic": path.stem,                 # file name = topic, for now
            })
    return records

if __name__ == "__main__":  # quick test: python ingest.py
    for f in Path("sample_notes").glob("*.txt"):
        chunks = build_chunks(f)
        print(f.name, "->", len(chunks), "chunks")
        print("  first chunk:", chunks[0]["text"][:100], "...")